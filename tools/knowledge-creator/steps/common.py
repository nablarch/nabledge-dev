"""Common utilities for knowledge-creator steps"""

import json
import subprocess
import os
from typing import Any
from openpyxl import load_workbook


def load_json(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json(path: str, data: Any):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def read_excel_as_markdown(path: str) -> str:
    workbook = load_workbook(path, read_only=True, data_only=True)
    markdown_parts = []

    for sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]
        markdown_parts.append(f"## {sheet_name}\n")
        rows = list(sheet.iter_rows(values_only=True))

        if not rows:
            markdown_parts.append("(Empty sheet)\n")
            continue

        max_cols = max(len(row) for row in rows) if rows else 0
        if max_cols == 0:
            markdown_parts.append("(Empty sheet)\n")
            continue

        for i, row in enumerate(rows):
            padded_row = list(row) + [None] * (max_cols - len(row))
            cells = [str(cell) if cell is not None else "" for cell in padded_row]
            markdown_parts.append("| " + " | ".join(cells) + " |")
            if i == 0:
                markdown_parts.append("| " + " | ".join(["---"] * max_cols) + " |")
        markdown_parts.append("")

    workbook.close()
    return "\n".join(markdown_parts)


def read_file(path: str) -> str:
    if path.endswith('.xlsx'):
        return read_excel_as_markdown(path)
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(path: str, content: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def run_claude(prompt: str, timeout: int = 600, json_schema: dict = None) -> subprocess.CompletedProcess:
    """Run claude -p via stdin.

    Args:
        prompt: Prompt text
        timeout: Timeout in seconds
        json_schema: JSON Schema for structured output (optional)

    Returns:
        CompletedProcess. When json_schema is provided, stdout contains the structured_output JSON.
    """
    cmd = ["claude", "-p"]

    if json_schema:
        cmd.extend(["--output-format", "json"])
        cmd.extend(["--json-schema", json.dumps(json_schema)])

    env = os.environ.copy()
    env.pop('CLAUDECODE', None)

    result = subprocess.run(
        cmd, input=prompt, capture_output=True, text=True, timeout=timeout, env=env
    )

    if json_schema and result.returncode == 0:
        try:
            response = json.loads(result.stdout)
            subtype = response.get("subtype", "")

            if subtype == "success":
                structured_output = response.get("structured_output")
                if structured_output is not None:
                    result = subprocess.CompletedProcess(
                        args=result.args, returncode=0,
                        stdout=json.dumps(structured_output, ensure_ascii=False),
                        stderr=""
                    )
                else:
                    result = subprocess.CompletedProcess(
                        args=result.args, returncode=1,
                        stdout="", stderr="structured_output field is missing"
                    )
            elif subtype == "error_max_structured_output_retries":
                error_msg = response.get("result", "Failed to generate valid structured output")
                result = subprocess.CompletedProcess(
                    args=result.args, returncode=1,
                    stdout="", stderr=f"Structured output error: {error_msg}"
                )
            else:
                result = subprocess.CompletedProcess(
                    args=result.args, returncode=1,
                    stdout="", stderr=f"Unknown response subtype: {subtype}"
                )
        except json.JSONDecodeError as e:
            result = subprocess.CompletedProcess(
                args=result.args, returncode=1,
                stdout="", stderr=f"Failed to parse claude response JSON: {e}"
            )

    return result

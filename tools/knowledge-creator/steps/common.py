"""Common utilities for knowledge-creator steps"""

import json
import subprocess
import os
from typing import Any
from openpyxl import load_workbook


def load_json(path: str) -> dict:
    """Load JSON file"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json(path: str, data: Any):
    """Write JSON file with pretty formatting"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def read_excel_as_markdown(path: str) -> str:
    """
    Read Excel file and convert to markdown format

    Args:
        path: Path to .xlsx file

    Returns:
        Markdown formatted string with all sheets
    """
    workbook = load_workbook(path, read_only=True, data_only=True)
    markdown_parts = []

    for sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]

        # Add sheet heading
        markdown_parts.append(f"## {sheet_name}\n")

        # Get all rows as list
        rows = list(sheet.iter_rows(values_only=True))

        if not rows:
            markdown_parts.append("(Empty sheet)\n")
            continue

        # Find max column count
        max_cols = max(len(row) for row in rows) if rows else 0

        if max_cols == 0:
            markdown_parts.append("(Empty sheet)\n")
            continue

        # Convert to markdown table
        for i, row in enumerate(rows):
            # Pad row to max_cols length
            padded_row = list(row) + [None] * (max_cols - len(row))

            # Convert cells to strings, handle None
            cells = [str(cell) if cell is not None else "" for cell in padded_row]

            # Add table row
            markdown_parts.append("| " + " | ".join(cells) + " |")

            # Add separator after first row (header)
            if i == 0:
                markdown_parts.append("| " + " | ".join(["---"] * max_cols) + " |")

        markdown_parts.append("")  # Empty line between sheets

    workbook.close()
    return "\n".join(markdown_parts)


def read_file(path: str) -> str:
    """
    Read file content

    - For .xlsx files: Convert to markdown table format
    - For other files: Read as UTF-8 text
    """
    if path.endswith('.xlsx'):
        return read_excel_as_markdown(path)

    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(path: str, content: str):
    """Write text file"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def run_claude(prompt: str, timeout: int = 300, json_schema: dict = None) -> subprocess.CompletedProcess:
    """
    Run claude -p via stdin

    Args:
        prompt: Prompt text to send to claude
        timeout: Timeout in seconds (default: 300)
        json_schema: JSON Schema for structured output validation (optional)

    Returns:
        CompletedProcess with stdout, stderr, returncode
        When json_schema is provided, stdout contains the structured_output JSON
    """
    cmd = ["claude", "-p"]

    # Add --json-schema and --output-format json if schema provided
    if json_schema:
        cmd.extend(["--output-format", "json"])
        cmd.extend(["--json-schema", json.dumps(json_schema)])

    # Create environment without CLAUDECODE to allow nested execution
    env = os.environ.copy()
    env.pop('CLAUDECODE', None)

    result = subprocess.run(
        cmd,
        input=prompt,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )

    # If json_schema was used, extract structured_output from response
    if json_schema and result.returncode == 0:
        try:
            response = json.loads(result.stdout)

            # Check subtype for success/failure
            subtype = response.get("subtype", "")

            if subtype == "success":
                # Extract structured_output and return it as stdout
                structured_output = response.get("structured_output")
                if structured_output is not None:
                    result = subprocess.CompletedProcess(
                        args=result.args,
                        returncode=0,
                        stdout=json.dumps(structured_output, ensure_ascii=False),
                        stderr=""
                    )
                else:
                    # structured_output is missing
                    result = subprocess.CompletedProcess(
                        args=result.args,
                        returncode=1,
                        stdout="",
                        stderr="structured_output field is missing in response"
                    )
            elif subtype == "error_max_structured_output_retries":
                # Agent failed to produce valid output after retries
                error_msg = response.get("result", "Failed to generate valid structured output")
                result = subprocess.CompletedProcess(
                    args=result.args,
                    returncode=1,
                    stdout="",
                    stderr=f"Structured output error: {error_msg}"
                )
            else:
                # Unknown subtype
                result = subprocess.CompletedProcess(
                    args=result.args,
                    returncode=1,
                    stdout="",
                    stderr=f"Unknown response subtype: {subtype}"
                )
        except json.JSONDecodeError as e:
            # Failed to parse response JSON
            result = subprocess.CompletedProcess(
                args=result.args,
                returncode=1,
                stdout="",
                stderr=f"Failed to parse claude response JSON: {e}"
            )

    return result

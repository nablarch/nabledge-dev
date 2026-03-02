"""Utility functions shared across steps."""

import json
import os
import subprocess
from datetime import datetime
from typing import Any


def load_json(path: str) -> dict:
    """Load JSON file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json(path: str, data: Any):
    """Write JSON file with pretty formatting."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')


def read_file(path: str) -> str:
    """Read text file."""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(path: str, content: str):
    """Write text file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def run_claude(prompt: str, timeout: int = 300) -> subprocess.CompletedProcess:
    """Execute claude -p via stdin.

    Args:
        prompt: Prompt text to send to claude -p
        timeout: Timeout in seconds (default: 300)

    Returns:
        CompletedProcess object with stdout/stderr
    """
    return subprocess.run(
        ["claude", "-p", "--model", "claude-sonnet-4-5-20250929"],
        input=prompt,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def extract_json(output: str) -> dict:
    """Extract JSON from claude -p output.

    Tries to extract JSON from code blocks first, then parses entire output.
    """
    import re

    # Try to extract JSON from code block
    match = re.search(r'```json?\s*\n(.*?)\n```', output, re.DOTALL)
    if match:
        return json.loads(match.group(1))

    # Try to parse entire output as JSON
    return json.loads(output.strip())


def utcnow_iso() -> str:
    """Return current UTC time in ISO format with Z suffix."""
    return datetime.utcnow().isoformat() + "Z"


def log_info(message: str):
    """Log info message to stdout."""
    print(f"[INFO] {message}")


def log_error(message: str):
    """Log error message to stderr."""
    import sys
    print(f"[ERROR] {message}", file=sys.stderr)


def log_warning(message: str):
    """Log warning message to stdout."""
    print(f"[WARNING] {message}")


def log_skip(file_id: str):
    """Log that a file was skipped."""
    print(f"  [SKIP] {file_id} (already exists)")


def log_success(file_id: str):
    """Log successful processing of a file."""
    print(f"  [OK] {file_id}")


def log_fail(file_id: str, error: str):
    """Log failed processing of a file."""
    print(f"  [FAIL] {file_id}: {error}")

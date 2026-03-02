"""Common utilities for knowledge-creator steps"""

import json
import subprocess
import os
from typing import Any


def load_json(path: str) -> dict:
    """Load JSON file"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json(path: str, data: Any):
    """Write JSON file with pretty formatting"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def read_file(path: str) -> str:
    """Read text file"""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(path: str, content: str):
    """Write text file"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def run_claude(prompt: str, timeout: int = 300) -> subprocess.CompletedProcess:
    """
    Run claude -p via stdin

    Args:
        prompt: Prompt text to send to claude
        timeout: Timeout in seconds (default: 300)

    Returns:
        CompletedProcess with stdout, stderr, returncode
    """
    return subprocess.run(
        ["claude", "-p", "--model", "claude-sonnet-4-5-20250929"],
        input=prompt,
        capture_output=True,
        text=True,
        timeout=timeout,
    )

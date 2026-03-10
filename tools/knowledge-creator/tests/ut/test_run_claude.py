"""Unit tests for run_claude log writing in common.py.

Verifies that every execution log contains prompt (IN) and structured_output (OUT).
subprocess.run is mocked to avoid actual Claude CLI calls.
"""
import json
import os
import subprocess
import sys
from unittest.mock import patch

import pytest

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(TOOL_DIR, "scripts"))

from common import run_claude


SAMPLE_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"}
    },
    "required": ["answer"]
}

SAMPLE_STRUCTURED_OUTPUT = {"answer": "42"}

SAMPLE_CC_RESPONSE = {
    "subtype": "success",
    "structured_output": SAMPLE_STRUCTURED_OUTPUT,
    "duration_ms": 1234,
    "duration_api_ms": 1000,
    "num_turns": 1,
    "total_cost_usd": 0.001,
    "usage": {
        "input_tokens": 100,
        "output_tokens": 50,
        "cache_creation_input_tokens": 0,
        "cache_read_input_tokens": 0,
    },
}


def _find_log_file(log_dir):
    files = [f for f in os.listdir(log_dir) if f.endswith(".json")]
    assert len(files) == 1, f"Expected 1 log file, got {len(files)}: {files}"
    return os.path.join(log_dir, files[0])


class TestRunClaudeLog:
    """Verify execution log format written by run_claude."""

    def test_log_contains_prompt_and_structured_output(self, tmp_path):
        """run_claude writes prompt (IN) and structured_output (OUT) to execution log."""
        log_dir = str(tmp_path / "executions")
        prompt_text = "What is the answer to life, the universe, and everything?"
        file_id = "test-file-id"

        fake_result = subprocess.CompletedProcess(
            args=["claude", "-p"],
            returncode=0,
            stdout=json.dumps(SAMPLE_CC_RESPONSE),
            stderr="",
        )

        with patch("subprocess.run", return_value=fake_result):
            result = run_claude(
                prompt=prompt_text,
                json_schema=SAMPLE_SCHEMA,
                log_dir=log_dir,
                file_id=file_id,
            )

        assert result.returncode == 0
        assert json.loads(result.stdout) == SAMPLE_STRUCTURED_OUTPUT

        log_path = _find_log_file(log_dir)
        with open(log_path, encoding="utf-8") as f:
            log = json.load(f)

        # Exact equality for required fields
        assert log["file_id"] == file_id
        assert log["subtype"] == "success"
        assert log["prompt"] == prompt_text
        assert log["structured_output"] == SAMPLE_STRUCTURED_OUTPUT

    def test_log_cc_metrics_fields(self, tmp_path):
        """run_claude writes all cc_metrics fields to execution log."""
        log_dir = str(tmp_path / "executions")

        fake_result = subprocess.CompletedProcess(
            args=["claude", "-p"],
            returncode=0,
            stdout=json.dumps(SAMPLE_CC_RESPONSE),
            stderr="",
        )

        with patch("subprocess.run", return_value=fake_result):
            run_claude(
                prompt="test prompt",
                json_schema=SAMPLE_SCHEMA,
                log_dir=log_dir,
                file_id="metrics-test",
            )

        log_path = _find_log_file(log_dir)
        with open(log_path, encoding="utf-8") as f:
            log = json.load(f)

        cc = log["cc_metrics"]
        assert cc["duration_ms"] == 1234
        assert cc["duration_api_ms"] == 1000
        assert cc["num_turns"] == 1
        assert cc["total_cost_usd"] == 0.001
        assert cc["usage"] == {
            "input_tokens": 100,
            "output_tokens": 50,
            "cache_creation_input_tokens": 0,
            "cache_read_input_tokens": 0,
        }

    def test_log_exact_structure(self, tmp_path):
        """Execution log contains exactly the expected top-level keys."""
        log_dir = str(tmp_path / "executions")

        fake_result = subprocess.CompletedProcess(
            args=["claude", "-p"],
            returncode=0,
            stdout=json.dumps(SAMPLE_CC_RESPONSE),
            stderr="",
        )

        with patch("subprocess.run", return_value=fake_result):
            run_claude(
                prompt="structure test",
                json_schema=SAMPLE_SCHEMA,
                log_dir=log_dir,
                file_id="structure-test",
            )

        log_path = _find_log_file(log_dir)
        with open(log_path, encoding="utf-8") as f:
            log = json.load(f)

        expected_keys = {"file_id", "timestamp", "subtype", "cc_metrics", "prompt", "structured_output"}
        assert set(log.keys()) == expected_keys, (
            f"Log keys mismatch: got {set(log.keys())}, expected {expected_keys}"
        )

    def test_no_log_written_on_subprocess_error(self, tmp_path):
        """No log file is written when subprocess.run returns non-zero returncode."""
        log_dir = str(tmp_path / "executions")

        fake_result = subprocess.CompletedProcess(
            args=["claude", "-p"],
            returncode=1,
            stdout="",
            stderr="connection error",
        )

        with patch("subprocess.run", return_value=fake_result):
            result = run_claude(
                prompt="error test",
                json_schema=SAMPLE_SCHEMA,
                log_dir=log_dir,
                file_id="error-test",
            )

        assert result.returncode == 1
        # log_dir may not even be created
        if os.path.exists(log_dir):
            assert len(os.listdir(log_dir)) == 0, "No log file should be written on error"

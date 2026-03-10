"""Unit tests for run_claude log writing in common.py.

Verifies the 4-file output structure written per CC invocation:
  {file_id}_{timestamp}.json     - metadata (cc_metrics, stop_reason, tool_calls)
  {file_id}_{timestamp}.in.txt   - prompt (IN)
  {file_id}_{timestamp}.out.json - structured_output (OUT)
  {file_id}_{timestamp}.ndjson   - raw stream-json output

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
    "properties": {"answer": {"type": "string"}},
    "required": ["answer"],
}

SAMPLE_STRUCTURED_OUTPUT = {"answer": "42"}

SAMPLE_TOOL_INPUT = {"file_path": "/nablarch/doc/sample.rst"}

# Simulated stream-json (ndjson) output from Claude CLI --output-format stream-json
SAMPLE_NDJSON_LINES = [
    {"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": "Read", "id": "tool1", "input": SAMPLE_TOOL_INPUT}
    ]}},
    {"type": "result", "subtype": "success", "is_error": False,
     "duration_ms": 1234, "duration_api_ms": 1000,
     "num_turns": 1, "total_cost_usd": 0.001,
     "stop_reason": "end_turn",
     "usage": {
         "input_tokens": 100, "output_tokens": 50,
         "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0,
     },
     "structured_output": SAMPLE_STRUCTURED_OUTPUT},
]
SAMPLE_NDJSON = "\n".join(json.dumps(line) for line in SAMPLE_NDJSON_LINES)


def _make_fake_result(ndjson=SAMPLE_NDJSON, returncode=0):
    return subprocess.CompletedProcess(
        args=["claude", "-p"], returncode=returncode,
        stdout=ndjson if returncode == 0 else "",
        stderr="" if returncode == 0 else "connection error",
    )


def _find_files(log_dir):
    """Return dict of extension → filepath for all files in log_dir."""
    result = {}
    for f in os.listdir(log_dir):
        path = os.path.join(log_dir, f)
        if f.endswith(".out.json"):
            result["out.json"] = path
        elif f.endswith(".in.txt"):
            result["in.txt"] = path
        elif f.endswith(".ndjson"):
            result["ndjson"] = path
        elif f.endswith(".json"):
            result["json"] = path
    return result


class TestRunClaudeLog:
    """Verify 4-file execution log structure written by run_claude."""

    def test_four_files_are_written(self, tmp_path):
        """run_claude writes exactly 4 output files per invocation."""
        log_dir = str(tmp_path / "executions")

        with patch("subprocess.run", return_value=_make_fake_result()):
            run_claude(prompt="test prompt", json_schema=SAMPLE_SCHEMA,
                       log_dir=log_dir, file_id="test-file")

        files = os.listdir(log_dir)
        assert len(files) == 4, f"Expected 4 files, got {len(files)}: {files}"

        exts = {f.split(os.sep)[-1].split(".", 1)[1] for f in files}
        assert exts == {"json", "in.txt", "out.json", "ndjson"}, (
            f"Unexpected file extensions: {exts}"
        )

    def test_metadata_json_exact_keys(self, tmp_path):
        """Metadata .json contains exactly the expected top-level keys (no prompt, no structured_output)."""
        log_dir = str(tmp_path / "executions")

        with patch("subprocess.run", return_value=_make_fake_result()):
            run_claude(prompt="test", json_schema=SAMPLE_SCHEMA,
                       log_dir=log_dir, file_id="meta-test")

        meta_path = _find_files(log_dir)["json"]
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)

        assert set(meta.keys()) == {
            "file_id", "timestamp", "subtype", "cc_metrics", "stop_reason", "tool_calls"
        }
        assert meta["file_id"] == "meta-test"
        assert meta["subtype"] == "success"
        assert meta["stop_reason"] == "end_turn"

    def test_metadata_json_cc_metrics(self, tmp_path):
        """Metadata .json cc_metrics fields match CC response exactly."""
        log_dir = str(tmp_path / "executions")

        with patch("subprocess.run", return_value=_make_fake_result()):
            run_claude(prompt="test", json_schema=SAMPLE_SCHEMA,
                       log_dir=log_dir, file_id="metrics-test")

        meta_path = _find_files(log_dir)["json"]
        with open(meta_path, encoding="utf-8") as f:
            cc = json.load(f)["cc_metrics"]

        assert cc["duration_ms"] == 1234
        assert cc["duration_api_ms"] == 1000
        assert cc["num_turns"] == 1
        assert cc["total_cost_usd"] == 0.001
        assert cc["usage"] == {
            "input_tokens": 100, "output_tokens": 50,
            "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0,
        }

    def test_metadata_json_tool_calls(self, tmp_path):
        """Metadata .json tool_calls extracted from stream-json."""
        log_dir = str(tmp_path / "executions")

        with patch("subprocess.run", return_value=_make_fake_result()):
            run_claude(prompt="test", json_schema=SAMPLE_SCHEMA,
                       log_dir=log_dir, file_id="tools-test")

        meta_path = _find_files(log_dir)["json"]
        with open(meta_path, encoding="utf-8") as f:
            tool_calls = json.load(f)["tool_calls"]

        assert len(tool_calls) == 1
        assert tool_calls[0]["tool_name"] == "Read"
        assert tool_calls[0]["input_summary"] == {
            k: str(v) for k, v in SAMPLE_TOOL_INPUT.items()
        }

    def test_in_txt_contains_exact_prompt(self, tmp_path):
        """IN file (.in.txt) contains the exact prompt string."""
        log_dir = str(tmp_path / "executions")
        prompt_text = "Nablarch のハンドラとは何ですか？詳しく説明してください。"

        with patch("subprocess.run", return_value=_make_fake_result()):
            run_claude(prompt=prompt_text, json_schema=SAMPLE_SCHEMA,
                       log_dir=log_dir, file_id="in-test")

        in_path = _find_files(log_dir)["in.txt"]
        with open(in_path, encoding="utf-8") as f:
            content = f.read()

        assert content == prompt_text

    def test_out_json_contains_exact_structured_output(self, tmp_path):
        """OUT file (.out.json) contains the exact structured_output from CC response."""
        log_dir = str(tmp_path / "executions")

        with patch("subprocess.run", return_value=_make_fake_result()):
            result = run_claude(prompt="test", json_schema=SAMPLE_SCHEMA,
                                log_dir=log_dir, file_id="out-test")

        assert result.returncode == 0
        assert json.loads(result.stdout) == SAMPLE_STRUCTURED_OUTPUT

        out_path = _find_files(log_dir)["out.json"]
        with open(out_path, encoding="utf-8") as f:
            content = json.load(f)

        assert content == SAMPLE_STRUCTURED_OUTPUT

    def test_ndjson_contains_raw_stream_output(self, tmp_path):
        """NDJSON file contains the raw stream-json output from Claude CLI."""
        log_dir = str(tmp_path / "executions")

        with patch("subprocess.run", return_value=_make_fake_result()):
            run_claude(prompt="test", json_schema=SAMPLE_SCHEMA,
                       log_dir=log_dir, file_id="ndjson-test")

        ndjson_path = _find_files(log_dir)["ndjson"]
        with open(ndjson_path, encoding="utf-8") as f:
            content = f.read()

        assert content == SAMPLE_NDJSON

    def test_no_files_written_on_subprocess_error(self, tmp_path):
        """No files are written when subprocess.run returns non-zero returncode."""
        log_dir = str(tmp_path / "executions")

        with patch("subprocess.run", return_value=_make_fake_result(returncode=1)):
            result = run_claude(prompt="error test", json_schema=SAMPLE_SCHEMA,
                                log_dir=log_dir, file_id="error-test")

        assert result.returncode == 1
        if os.path.exists(log_dir):
            assert len(os.listdir(log_dir)) == 0, "No files should be written on error"

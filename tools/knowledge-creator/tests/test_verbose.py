"""Tests for --verbose flag (stream-json + tool call recording)."""
import json
import os
import subprocess
import pytest
from unittest.mock import patch
from common import write_json


class TestRunClaudeVerbose:
    """Unit tests for run_claude verbose parameter."""

    def _make_stream_json_output(self, subtype="success", structured_output=None,
                                  stop_reason="end_turn", tool_uses=None):
        """Build mock stream-json NDJSON output."""
        lines = []
        if tool_uses:
            for tu in tool_uses:
                lines.append(json.dumps({
                    "message": {
                        "content": [{
                            "type": "tool_use",
                            "id": f"toolu_{tu['name']}",
                            "name": tu["name"],
                            "input": tu.get("input", {})
                        }]
                    }
                }))
        result = {
            "type": "result",
            "subtype": subtype,
            "stop_reason": stop_reason,
            "duration_ms": 1000,
            "duration_api_ms": 990,
            "num_turns": 4,
            "total_cost_usd": 0.01,
            "usage": {
                "input_tokens": 10,
                "cache_creation_input_tokens": 100,
                "cache_read_input_tokens": 200,
                "output_tokens": 50,
                "server_tool_use": {"web_search_requests": 0, "web_fetch_requests": 0},
                "service_tier": "standard",
                "cache_creation": {"ephemeral_1h_input_tokens": 0, "ephemeral_5m_input_tokens": 100},
                "inference_geo": "",
                "iterations": [],
                "speed": "standard"
            },
        }
        if structured_output is not None:
            result["structured_output"] = structured_output
        lines.append(json.dumps(result))
        return "\n".join(lines) + "\n"

    def _make_json_output(self, subtype="success", structured_output=None):
        """Build mock json mode output (single JSON object)."""
        result = {
            "type": "result",
            "subtype": subtype,
            "duration_ms": 1000,
            "duration_api_ms": 990,
            "num_turns": 4,
            "total_cost_usd": 0.01,
            "usage": {
                "input_tokens": 10,
                "cache_creation_input_tokens": 100,
                "cache_read_input_tokens": 200,
                "output_tokens": 50,
                "server_tool_use": {"web_search_requests": 0, "web_fetch_requests": 0},
                "service_tier": "standard",
                "cache_creation": {"ephemeral_1h_input_tokens": 0, "ephemeral_5m_input_tokens": 100},
                "inference_geo": "",
                "iterations": [],
                "speed": "standard"
            },
        }
        if structured_output is not None:
            result["structured_output"] = structured_output
        return json.dumps(result)

    @patch("common.subprocess.run")
    def test_verbose_false_uses_json_format(self, mock_run, tmp_path):
        """verbose=False (default) uses --output-format json."""
        from common import run_claude
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0,
            stdout=self._make_json_output(
                subtype="success",
                structured_output={"id": "test", "title": "Test"}
            ), stderr=""
        )
        run_claude(prompt="test", json_schema={"type": "object"},
                   log_dir=str(tmp_path), file_id="test-file")
        cmd = mock_run.call_args[0][0]
        fmt_idx = cmd.index("--output-format")
        assert cmd[fmt_idx + 1] == "json"
        assert "--verbose" not in cmd
        assert len(list(tmp_path.glob("*.ndjson"))) == 0
        log_data = json.load(open(list(tmp_path.glob("*.json"))[0]))
        assert "stop_reason" not in log_data
        assert "tool_calls" not in log_data

    @patch("common.subprocess.run")
    def test_verbose_true_uses_stream_json_format(self, mock_run, tmp_path):
        """verbose=True uses --output-format stream-json --verbose."""
        from common import run_claude
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0,
            stdout=self._make_stream_json_output(
                subtype="success",
                structured_output={"id": "test", "title": "Test"}
            ), stderr=""
        )
        run_claude(prompt="test", json_schema={"type": "object"},
                   log_dir=str(tmp_path), file_id="test-file", verbose=True)
        cmd = mock_run.call_args[0][0]
        fmt_idx = cmd.index("--output-format")
        assert cmd[fmt_idx + 1] == "stream-json"
        assert "--verbose" in cmd

    @patch("common.subprocess.run")
    def test_verbose_saves_ndjson_file(self, mock_run, tmp_path):
        """verbose=True saves raw NDJSON output."""
        from common import run_claude
        ndjson_content = self._make_stream_json_output(
            subtype="success", structured_output={"id": "test", "title": "Test"})
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=ndjson_content, stderr="")
        run_claude(prompt="test", json_schema={"type": "object"},
                   log_dir=str(tmp_path), file_id="test-file", verbose=True)
        ndjson_files = list(tmp_path.glob("*.ndjson"))
        assert len(ndjson_files) == 1
        assert ndjson_files[0].read_text() == ndjson_content

    @patch("common.subprocess.run")
    def test_verbose_log_contains_stop_reason_and_tool_calls(self, mock_run, tmp_path):
        """verbose=True adds stop_reason and tool_calls to log."""
        from common import run_claude
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0,
            stdout=self._make_stream_json_output(
                subtype="error_max_turns", stop_reason="tool_use",
                tool_uses=[
                    {"name": "Read", "input": {"file_path": "/some/file.md"}},
                    {"name": "Bash", "input": {"command": "cat foo.txt"}},
                ]
            ), stderr=""
        )
        run_claude(prompt="test", json_schema={"type": "object"},
                   log_dir=str(tmp_path), file_id="test-file", verbose=True)
        log_data = json.load(open(list(tmp_path.glob("*.json"))[0]))
        assert log_data["stop_reason"] == "tool_use"
        assert log_data["subtype"] == "error_max_turns"
        assert len(log_data["tool_calls"]) == 2
        assert log_data["tool_calls"][0]["tool_name"] == "Read"
        assert log_data["tool_calls"][1]["tool_name"] == "Bash"
        assert "file_path" in log_data["tool_calls"][0]["input_summary"]

    @patch("common.subprocess.run")
    def test_verbose_success_returns_structured_output(self, mock_run, tmp_path):
        """verbose=True with success still returns structured_output correctly."""
        from common import run_claude
        expected = {"id": "test", "title": "Test", "sections": {"a": "content"}}
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0,
            stdout=self._make_stream_json_output(
                subtype="success", structured_output=expected
            ), stderr=""
        )
        result = run_claude(prompt="test", json_schema={"type": "object"},
                            log_dir=str(tmp_path), file_id="test-file", verbose=True)
        assert result.returncode == 0
        assert json.loads(result.stdout) == expected

    @patch("common.subprocess.run")
    def test_verbose_no_result_line_returns_error(self, mock_run, tmp_path):
        """verbose=True with no result line in NDJSON returns error."""
        from common import run_claude
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0,
            stdout='{"type": "stream_event", "data": "something"}\n', stderr=""
        )
        result = run_claude(prompt="test", json_schema={"type": "object"},
                            log_dir=str(tmp_path), file_id="test-file", verbose=True)
        assert result.returncode == 1
        assert "No result line" in result.stderr

    @patch("common.subprocess.run")
    def test_verbose_tool_call_input_truncated(self, mock_run, tmp_path):
        """verbose=True truncates large tool_call input values at 200 chars."""
        from common import run_claude
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0,
            stdout=self._make_stream_json_output(
                subtype="success", structured_output={"id": "test"},
                tool_uses=[{"name": "Write", "input": {"content": "x" * 500}}]
            ), stderr=""
        )
        run_claude(prompt="test", json_schema={"type": "object"},
                   log_dir=str(tmp_path), file_id="test-file", verbose=True)
        log_data = json.load(open(list(tmp_path.glob("*.json"))[0]))
        content_val = log_data["tool_calls"][0]["input_summary"]["content"]
        assert len(content_val) <= 203
        assert content_val.endswith("...")


class TestContextVerbose:
    """Test verbose flag propagation through Context."""

    def test_context_default_verbose_false(self, tmp_path):
        from run import Context
        ctx = Context(version="6", repo=str(tmp_path), concurrency=1)
        assert ctx.verbose is False

    def test_context_verbose_true(self, tmp_path):
        from run import Context
        ctx = Context(version="6", repo=str(tmp_path), concurrency=1, verbose=True)
        assert ctx.verbose is True


class TestPhaseEVerbosePropagation:
    """Test that Phase E passes verbose to run_claude."""

    def test_phase_e_passes_verbose(self, ctx):
        ctx.verbose = True
        calls = []
        def tracking_mock(prompt, json_schema=None, log_dir=None, file_id=None, **kwargs):
            calls.append(kwargs)
            knowledge = {"id": file_id, "no_knowledge_content": False,
                         "title": "T", "official_doc_urls": [],
                         "index": [{"id": "s", "title": "S", "hints": ["h"]}],
                         "sections": {"s": "content"}}
            return subprocess.CompletedProcess(
                args=[], returncode=0,
                stdout=json.dumps(knowledge), stderr="")
        from phase_e_fix import PhaseEFix
        write_json(f"{ctx.knowledge_cache_dir}/component/handlers/handlers-sample-handler.json",
                    {"id": "test-file", "no_knowledge_content": False, "title": "T",
                     "official_doc_urls": [],
                     "index": [{"id": "s", "title": "S", "hints": ["h"]}],
                     "sections": {"s": "content"}})
        os.makedirs(ctx.findings_dir, exist_ok=True)
        write_json(f"{ctx.findings_dir}/handlers-sample-handler.json",
                    {"file_id": "handlers-sample-handler", "status": "has_issues",
                     "findings": [{"category": "hints_missing", "severity": "minor",
                                   "location": "s", "description": "missing X"}]})
        PhaseEFix(ctx, run_claude_fn=tracking_mock).run(target_ids=["handlers-sample-handler"])
        assert len(calls) >= 1
        assert calls[0].get("verbose") is True

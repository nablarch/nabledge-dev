"""Clean history tracking tests — 2 consecutive critical-zero confirms clean."""
import os
import json
import pytest
import sys

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(TOOL_DIR, "scripts"))


class TestCleanHistory:

    def test_load_returns_empty_when_no_file(self, ctx):
        """First run: no history file exists, returns empty dict."""
        from run import _load_clean_history
        history = _load_clean_history(ctx)
        assert history == {}

    def test_save_and_load_roundtrip(self, ctx):
        """Saved history is readable in next load."""
        from run import _load_clean_history, _save_clean_history
        _save_clean_history(ctx, {"file-a": 1, "file-b": 2})
        history = _load_clean_history(ctx)
        assert history == {"file-a": 1, "file-b": 2}

    def test_confirmed_clean_at_2(self, ctx):
        """File with count >= 2 is confirmed clean."""
        from run import _load_clean_history, _save_clean_history, _is_confirmed_clean
        _save_clean_history(ctx, {"file-a": 2, "file-b": 1})
        history = _load_clean_history(ctx)
        assert _is_confirmed_clean(history, "file-a") is True
        assert _is_confirmed_clean(history, "file-b") is False
        assert _is_confirmed_clean(history, "file-c") is False

    def test_critical_finding_resets_count(self, ctx):
        """File with critical finding resets to 0."""
        from run import _update_clean_history
        history = {"file-a": 1}
        findings = {"findings": [
            {"category": "omission", "severity": "critical", "location": "s1", "description": "x"}
        ]}
        _update_clean_history(history, "file-a", findings)
        assert history["file-a"] == 0

    def test_minor_only_increments_count(self, ctx):
        """File with only minor findings increments clean count."""
        from run import _update_clean_history
        history = {"file-a": 1}
        findings = {"findings": [
            {"category": "hints_missing", "severity": "minor", "location": "s1", "description": "x"}
        ]}
        _update_clean_history(history, "file-a", findings)
        assert history["file-a"] == 2

    def test_no_findings_increments_count(self, ctx):
        """File with no findings (clean) increments clean count."""
        from run import _update_clean_history
        history = {"file-a": 0}
        findings = {"findings": []}
        _update_clean_history(history, "file-a", findings)
        assert history["file-a"] == 1

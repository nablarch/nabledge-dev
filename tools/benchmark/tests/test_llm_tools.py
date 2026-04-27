"""Tests for tools/benchmark/llm_tools scripts."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
LLM_TOOLS = Path(__file__).resolve().parent.parent / "llm_tools"
VERIFY_SCRIPT = LLM_TOOLS / "verify_kb_evidence.py"


def _run(knowledge_root: str, file_rel: str, sid: str, quote: str) -> str:
    result = subprocess.run(
        [sys.executable, str(VERIFY_SCRIPT), knowledge_root, file_rel, sid, quote],
        capture_output=True, text=True,
    )
    return result.stdout.strip()


def _make_kb(tmp_path: Path, file_rel: str, sections: dict[str, str]) -> str:
    """Create a minimal knowledge JSON and return the knowledge_root path."""
    kb_root = tmp_path / "knowledge"
    kb_root.mkdir()
    target = kb_root / file_rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps({"sections": sections}, ensure_ascii=False),
        encoding="utf-8",
    )
    return str(kb_root)


class TestVerifyKbEvidence:
    def test_match_verbatim(self, tmp_path):
        root = _make_kb(tmp_path, "foo.json", {"s1": "ThymeleafResponseWriter is used here"})
        assert _run(root, "foo.json", "s1", "ThymeleafResponseWriter") == "match"

    def test_mismatch_quote_not_in_sid(self, tmp_path):
        root = _make_kb(tmp_path, "foo.json", {
            "s1": "something else entirely",
            "s2": "ThymeleafResponseWriter is here",
        })
        out = _run(root, "foo.json", "s1", "ThymeleafResponseWriter")
        assert out.startswith("mismatch")

    def test_mismatch_file_not_found(self, tmp_path):
        root = str(tmp_path / "knowledge")
        (tmp_path / "knowledge").mkdir()
        out = _run(root, "nonexistent.json", "s1", "some quote")
        assert out.startswith("mismatch")

    def test_mismatch_sid_not_found(self, tmp_path):
        root = _make_kb(tmp_path, "foo.json", {"s1": "body text"})
        out = _run(root, "foo.json", "s99", "body text")
        assert out.startswith("mismatch")

    def test_match_normalized_whitespace(self, tmp_path):
        root = _make_kb(tmp_path, "foo.json", {"s1": "hello  world\nfoo"})
        assert _run(root, "foo.json", "s1", "hello world foo") == "match"

    def test_mismatch_empty_quote(self, tmp_path):
        root = _make_kb(tmp_path, "foo.json", {"s1": "some body"})
        out = _run(root, "foo.json", "s1", "")
        assert out.startswith("mismatch")

    def test_section_body_as_dict(self, tmp_path):
        """Sections whose value is a dict with a 'body' key."""
        kb_root = tmp_path / "knowledge"
        kb_root.mkdir()
        target = kb_root / "foo.json"
        target.write_text(
            json.dumps({"sections": {"s1": {"body": "ThymeleafResponseWriter here"}}}),
            encoding="utf-8",
        )
        assert _run(str(kb_root), "foo.json", "s1", "ThymeleafResponseWriter") == "match"

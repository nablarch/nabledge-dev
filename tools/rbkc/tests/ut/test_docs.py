"""Unit tests for docs MD generation with top-level content (Phase 21-D)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.create.docs import generate_docs


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


class TestTopLevelContent:
    def test_top_level_content_rendered_under_h1(self, tmp_path):
        kn = tmp_path / "knowledge"
        docs = tmp_path / "docs"
        _write_json(kn / "other/sample.json", {
            "id": "sample",
            "title": "Title",
            "content": "これは前書きの段落。",
            "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "A", "content": "A本文。", "hints": []}],
        })
        generate_docs(kn, docs, "6")
        md = (docs / "other" / "sample.md").read_text(encoding="utf-8")
        lines = md.split("\n")
        assert lines[0] == "# Title"
        # Preamble appears before any ## heading
        h1_idx = 0
        first_h2_idx = next(i for i, l in enumerate(lines) if l.startswith("## "))
        preamble = "\n".join(lines[h1_idx + 1:first_h2_idx])
        assert "これは前書きの段落" in preamble

    def test_no_double_h2_when_sections_empty(self, tmp_path):
        kn = tmp_path / "knowledge"
        docs = tmp_path / "docs"
        _write_json(kn / "other/solo.json", {
            "id": "solo",
            "title": "Solo",
            "content": "唯一の段落。",
            "no_knowledge_content": False,
            "sections": [],
        })
        generate_docs(kn, docs, "6")
        md = (docs / "other" / "solo.md").read_text(encoding="utf-8")
        # No ## heading should appear since sections is empty
        assert not any(l.startswith("## ") for l in md.split("\n"))
        assert "唯一の段落" in md

    def test_empty_top_level_content_omitted(self, tmp_path):
        kn = tmp_path / "knowledge"
        docs = tmp_path / "docs"
        _write_json(kn / "other/nopre.json", {
            "id": "nopre",
            "title": "T",
            "content": "",
            "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "A", "content": "A本文。", "hints": []}],
        })
        generate_docs(kn, docs, "6")
        md = (docs / "other" / "nopre.md").read_text(encoding="utf-8")
        # No stray blank paragraphs after h1 before the first h2
        lines = md.split("\n")
        assert lines[0] == "# T"
        # First non-blank line after h1 should be the first ## heading
        i = 1
        while i < len(lines) and not lines[i].strip():
            i += 1
        assert lines[i] == "## A"

    def test_no_knowledge_content_only_h1(self, tmp_path):
        kn = tmp_path / "knowledge"
        docs = tmp_path / "docs"
        _write_json(kn / "other/nav.json", {
            "id": "nav",
            "title": "Nav",
            "content": "",
            "no_knowledge_content": True,
            "sections": [],
        })
        generate_docs(kn, docs, "6")
        md = (docs / "other" / "nav.md").read_text(encoding="utf-8")
        assert md.splitlines()[0] == "# Nav"
        assert not any(l.startswith("## ") for l in md.splitlines())

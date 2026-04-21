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

    def test_top_level_hints_rendered_between_h1_and_content(self, tmp_path):
        """Phase 21-D session 37: top-level hints emit a keywords block before preamble."""
        kn = tmp_path / "knowledge"
        docs = tmp_path / "docs"
        _write_json(kn / "other/fh.json", {
            "id": "fh",
            "title": "Title",
            "content": "前書き。",
            "hints": ["file-kw-1", "file-kw-2"],
            "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "A", "content": "A本文。", "hints": []}],
        })
        generate_docs(kn, docs, "6")
        md = (docs / "other" / "fh.md").read_text(encoding="utf-8")
        # Keywords block must appear before preamble, after h1
        h1_line = md.index("# Title")
        details_line = md.index("<details>")
        summary_line = md.index("<summary>keywords</summary>")
        preamble_line = md.index("前書き。")
        assert h1_line < details_line < summary_line < preamble_line
        # Block contains the file-level keywords
        assert "file-kw-1, file-kw-2" in md
        # Section-level keywords block is not emitted (hints is empty)
        assert md.count("<summary>keywords</summary>") == 1

    def test_top_level_hints_omitted_when_empty(self, tmp_path):
        """No keywords block is emitted when top-level hints is empty."""
        kn = tmp_path / "knowledge"
        docs = tmp_path / "docs"
        _write_json(kn / "other/nofh.json", {
            "id": "nofh",
            "title": "Title",
            "content": "前書き。",
            "hints": [],
            "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "A", "content": "A本文。", "hints": []}],
        })
        generate_docs(kn, docs, "6")
        md = (docs / "other" / "nofh.md").read_text(encoding="utf-8")
        assert "<summary>keywords</summary>" not in md

    def test_top_level_hints_rendered_even_when_content_empty(self, tmp_path):
        """File-level hints attach to top-level content; they render even if content is empty."""
        kn = tmp_path / "knowledge"
        docs = tmp_path / "docs"
        _write_json(kn / "other/emptycontent.json", {
            "id": "emptycontent",
            "title": "Title",
            "content": "",
            "hints": ["kw"],
            "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "A", "content": "A.", "hints": []}],
        })
        generate_docs(kn, docs, "6")
        md = (docs / "other" / "emptycontent.md").read_text(encoding="utf-8")
        assert "<summary>keywords</summary>" in md
        assert "kw" in md

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

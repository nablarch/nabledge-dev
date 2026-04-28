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
            "sections": [{"id": "s1", "title": "A", "content": "A本文。"}],
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
            "sections": [{"id": "s1", "title": "A", "content": "A本文。"}],
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

    def test_top_level_hints_field_must_not_render_keywords_block(self, tmp_path):
        """RBKC is content-only (Phase 21-K): even if JSON carries a stray top-level
        `hints` field, docs.py must NOT render a keywords block.

        Regression guard: the pre-Phase-21-K implementation wrapped top_hints in a
        `<details><summary>keywords</summary>...</details>` block. This test
        injects such input and asserts the block is absent in output.
        """
        kn = tmp_path / "knowledge"
        docs = tmp_path / "docs"
        _write_json(kn / "other/top.json", {
            "id": "top",
            "title": "Title",
            "content": "前書き。",
            "hints": ["stray-top-kw-1", "stray-top-kw-2"],
            "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "A", "content": "A本文。"}],
        })
        generate_docs(kn, docs, "6")
        md = (docs / "other" / "top.md").read_text(encoding="utf-8")
        assert "<details>" not in md
        assert "<summary>keywords</summary>" not in md
        assert "stray-top-kw-1" not in md
        assert "stray-top-kw-2" not in md

    def test_section_hints_field_must_not_render_keywords_block(self, tmp_path):
        """RBKC is content-only (Phase 21-K): even if JSON sections carry a stray
        `hints` field, docs.py must NOT render a per-section keywords block.

        Regression guard: the pre-Phase-21-K implementation wrapped section hints
        in a per-section `<details>` block. This test injects such input and
        asserts no block renders.
        """
        kn = tmp_path / "knowledge"
        docs = tmp_path / "docs"
        _write_json(kn / "other/sec.json", {
            "id": "sec",
            "title": "Title",
            "content": "",
            "no_knowledge_content": False,
            "sections": [
                {"id": "s1", "title": "A", "content": "A本文。",
                 "hints": ["stray-sec-kw-1", "stray-sec-kw-2"]},
            ],
        })
        generate_docs(kn, docs, "6")
        md = (docs / "other" / "sec.md").read_text(encoding="utf-8")
        assert "<details>" not in md
        assert "<summary>keywords</summary>" not in md
        assert "stray-sec-kw-1" not in md
        assert "stray-sec-kw-2" not in md

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


class TestLeadingBlankLineSuppression:
    """When title is empty, the rendered MD must not start with a blank line.

    Root cause: `lines = [f"# {title}" if title else "", ""]` produces
    `["", ""]` when title is empty, causing the file to open with two blank
    lines. This manifests after Bug 1 fix (invisible image suppression) exposed
    the leading blank lines in handler docs for v1.x.
    """

    def test_full_empty_title_no_leading_blank(self, tmp_path):
        kn = tmp_path / "knowledge"
        docs = tmp_path / "docs"
        _write_json(kn / "other/notitle.json", {
            "id": "notitle",
            "title": "",
            "content": "本文。",
            "no_knowledge_content": False,
            "sections": [],
        })
        generate_docs(kn, docs, "6")
        md = (docs / "other" / "notitle.md").read_text(encoding="utf-8")
        assert not md.startswith("\n"), "MD must not start with a blank line when title is empty"

    def test_no_knowledge_empty_title_no_leading_blank(self, tmp_path):
        kn = tmp_path / "knowledge"
        docs = tmp_path / "docs"
        _write_json(kn / "other/notitle2.json", {
            "id": "notitle2",
            "title": "",
            "content": "",
            "no_knowledge_content": True,
            "sections": [],
        })
        generate_docs(kn, docs, "6")
        md = (docs / "other" / "notitle2.md").read_text(encoding="utf-8")
        assert not md.startswith("\n"), "MD must not start with a blank line when title is empty"

    def test_full_with_title_starts_with_h1(self, tmp_path):
        """Regression: title present must still render # heading at line 0."""
        kn = tmp_path / "knowledge"
        docs = tmp_path / "docs"
        _write_json(kn / "other/withtitle.json", {
            "id": "withtitle",
            "title": "MyTitle",
            "content": "前書き。",
            "no_knowledge_content": False,
            "sections": [],
        })
        generate_docs(kn, docs, "6")
        md = (docs / "other" / "withtitle.md").read_text(encoding="utf-8")
        assert md.startswith("# MyTitle"), "MD with title must start with # heading"


class TestAssetsExcluded:
    """generate_docs must ignore JSON files under knowledge/assets/.

    These are literalinclude source copies made by resolver.copy_assets,
    not content JSON. Treating them as knowledge JSON causes json.loads
    to crash on valid-but-non-JSON source (e.g. JavaScript-style comments).
    """

    def test_asset_json_does_not_crash_generation(self, tmp_path):
        kn = tmp_path / "knowledge"
        docs = tmp_path / "docs"
        _write_json(kn / "other/a.json", {
            "id": "a",
            "title": "A",
            "content": "",
            "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "S", "content": "body"}],
        })
        # Non-JSON-parseable file under assets/ — must be skipped.
        (kn / "assets" / "etl-etl").mkdir(parents=True)
        (kn / "assets" / "etl-etl" / "chunk_replace.json").write_text(
            '{ "mode": "ABORT"  // a comment\n}', encoding="utf-8"
        )
        generate_docs(kn, docs, "6")
        # Content JSON rendered normally.
        assert (docs / "other" / "a.md").exists()
        # No MD written for the asset.
        assert not (docs / "assets" / "etl-etl" / "chunk_replace.md").exists()

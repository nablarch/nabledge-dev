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


class TestRenderXlsxP2Subtypes:
    """docs MD rendering for P2-1 (column-indent→headings) and P2-3 (LF→hard line break)."""

    def _render(self, data: dict) -> str:
        from scripts.create.docs import _render_full
        return _render_full(data, docs_md_path=None, knowledge_dir=None)

    def test_p2_1_col3_is_body_not_heading(self):
        """P2-1: col-3 rows must be body paragraphs, not #### headings.

        Regression: security-check-1.概要 has col_dist {1:H2, 2:H3, 3:body}.
        Before the fix, the relative-offset logic treated col-3 (offset=2 from
        base_col=1) as H4 (####).  After the fix, absolute-column logic treats
        col-3 as body (min_cx=3 > 2).
        """
        # Simulate security-check-1.概要: base_col=1, col-3 rows are body text
        # p2_raw_lines: each row is [(col_index, text)]
        data = {
            "id": "f", "title": "1.概要", "content": "",
            "sections": [], "no_knowledge_content": False,
            "sheet_type": "P2",
            "p2_headings": [
                {"text": "1.概要", "level": 3},       # col-1 → H3
                {"text": "1.1 本書の位置づけ", "level": 4},  # col-2 → H4
            ],
            "p2_raw_lines": [
                [(1, "1.概要")],                          # col-1 → H3
                [(2, "1.1 本書の位置づけ")],              # col-2 → H4
                [(3, "本文テキストA")],                   # col-3 → body (NOT ####)
                [(3, "本文テキストB")],                   # col-3 → body
            ],
            "p2_base_col": 1,
        }
        md = self._render(data)
        assert "### 1.概要" in md
        assert "#### 1.1 本書の位置づけ" in md
        assert "本文テキストA" in md
        assert "本文テキストB" in md
        assert "#### 本文テキストA" not in md, "col-3 must be body, not #### heading"
        assert "#### 本文テキストB" not in md

    def test_p2_1_multicell_row_is_body_not_heading(self):
        """P2-1: rows with multiple cells (comparison tables) must be body, not headings.

        Regression: 変更前/変更後 pairs like (col-1,'変更前'),(col-10,'変更後') have
        min_cx=1, but they are comparison table rows — not ### headings.
        """
        data = {
            "id": "f", "title": "修正内容", "content": "",
            "sections": [], "no_knowledge_content": False,
            "sheet_type": "P2",
            "p2_headings": [
                {"text": "見出し", "level": 3},
            ],
            "p2_raw_lines": [
                [(1, "見出し")],                            # single-cell col-1 → H3
                [(1, "変更前"), (10, "変更後")],            # multi-cell → body
                [(1, "旧クラス名"), (10, "新クラス名")],    # multi-cell → body
            ],
            "p2_base_col": 0,
        }
        md = self._render(data)
        assert "### 見出し" in md
        assert "変更前  変更後" in md
        assert "### 変更前" not in md, "multi-cell row must not become ### heading"

    def test_p2_1_col0_becomes_h2(self):
        """P2-1: col-0 entries in p2_headings level=2 become ## headings."""
        data = {
            "id": "f", "title": "概要", "content": "",
            "sections": [], "no_knowledge_content": False,
            "sheet_type": "P2",
            "p2_headings": [
                {"text": "セクションA", "level": 2},
                {"text": "サブB", "level": 3},
            ],
        }
        md = self._render(data)
        assert "## セクションA" in md
        assert "### サブB" in md

    def test_p2_1_no_h2_when_no_p2_headings(self):
        """P2 without p2_headings renders plain text, no ## headings."""
        data = {
            "id": "f", "title": "T", "content": "本文テキスト",
            "sections": [], "no_knowledge_content": False,
            "sheet_type": "P2",
        }
        md = self._render(data)
        assert "## " not in md
        assert "本文テキスト" in md

    def test_p2_3_lf_becomes_hard_line_break(self):
        """P2-3: embedded LF in content becomes Markdown hard line break (  \\n)."""
        data = {
            "id": "f", "title": "T",
            "content": "行1 行2 行3",
            "sections": [], "no_knowledge_content": False,
            "sheet_type": "P2",
            "sheet_subtype": "P2-3",
            "p2_raw_content": "行1\n行2\n行3",
        }
        md = self._render(data)
        assert "行1  \n行2  \n行3" in md

    def test_p2_2_no_change(self):
        """P2-2 (neither p2_headings nor sheet_subtype P2-3): plain text output."""
        data = {
            "id": "f", "title": "T", "content": "ステップ1  ステップ2",
            "sections": [], "no_knowledge_content": False,
            "sheet_type": "P2",
        }
        md = self._render(data)
        assert "ステップ1" in md
        assert "## " not in md


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

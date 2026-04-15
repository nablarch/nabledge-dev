"""Unit tests for RST parser edge cases — Phase 2."""
import pytest
from scripts.converters.rst import (
    _detect_heading_chars,
    _is_underline,
    _parse_grid_table,
    _parse_simple_table,
    _parse_simple_table_cjk,
    convert,
)


# ---------------------------------------------------------------------------
# _is_underline
# ---------------------------------------------------------------------------

class TestIsUnderline:
    def test_equals_signs(self):
        assert _is_underline("=====") is True

    def test_dashes(self):
        assert _is_underline("-----") is True

    def test_tildes(self):
        assert _is_underline("~~~~~") is True

    def test_short_line_false(self):
        assert _is_underline("==") is False

    def test_mixed_chars_false(self):
        assert _is_underline("=-===") is False

    def test_text_line_false(self):
        assert _is_underline("Hello") is False

    def test_blank_false(self):
        assert _is_underline("") is False

    def test_trailing_newline_ok(self):
        assert _is_underline("=====\n") is True


# ---------------------------------------------------------------------------
# _detect_heading_chars — overline edge cases
# ---------------------------------------------------------------------------

class TestDetectHeadingChars:
    def test_overline_and_underline(self):
        rst = "#######\nTitle\n#######\n\nSection\n=======\n"
        chars = _detect_heading_chars(rst.splitlines())
        assert chars[0] == "#"
        assert chars[1] == "="

    def test_same_char_overline_not_double_counted(self):
        rst = "=======\nTitle\n=======\n\nSection\n-------\n"
        chars = _detect_heading_chars(rst.splitlines())
        assert chars.count("=") == 1

    def test_no_headings(self):
        rst = "Just a paragraph.\n"
        chars = _detect_heading_chars(rst.splitlines())
        assert chars == []

    def test_h4_detected(self):
        rst = "Title\n=====\n\nH2\n---\n\nH3\n~~~\n\nH4\n^^^\n"
        chars = _detect_heading_chars(rst.splitlines())
        assert "^" in chars
        assert chars.index("^") > chars.index("~")


# ---------------------------------------------------------------------------
# Section splitting
# ---------------------------------------------------------------------------

class TestSectionSplitting:
    def test_no_h2_all_content_one_section(self):
        rst = "Title\n=====\n\nContent paragraph.\n"
        result = convert(rst, "t")
        assert len(result.sections) == 1
        assert "Content paragraph." in result.sections[0].content

    def test_preamble_becomes_overview_section(self):
        rst = "Title\n=====\n\nIntro paragraph.\n\nSection A\n---------\n\nBody.\n"
        result = convert(rst, "t")
        titles = [s.title for s in result.sections]
        assert "概要" in titles
        overview = next(s for s in result.sections if s.title == "概要")
        assert "Intro paragraph." in overview.content

    def test_preamble_preserved_when_pre_h1_label_exists(self):
        """h1 前に .. _label: がある場合、h1〜最初のh2 間のコンテンツが消えないことを確認。"""
        rst = (
            ".. _my-label:\n"
            "\n"
            "Title\n"
            "=====\n"
            "\n"
            "Intro paragraph.\n"
            "\n"
            "Section A\n"
            "---------\n"
            "\n"
            "Body.\n"
        )
        result = convert(rst, "t")
        titles = [s.title for s in result.sections]
        assert "概要" in titles
        overview = next(s for s in result.sections if s.title == "概要")
        assert "Intro paragraph." in overview.content

    def test_h4_kept_as_subheading_in_section(self):
        rst = "Title\n=====\n\nH2\n---\n\nH3\n~~~\n\nH4\n^^^\n\nContent.\n"
        result = convert(rst, "t")
        # H4 is not a section boundary — content goes into H3 section
        titles = [s.title for s in result.sections]
        assert "H4" not in titles
        h3_section = next(s for s in result.sections if s.title == "H3")
        assert "H4" in h3_section.content or "####" in h3_section.content

    def test_no_knowledge_content_all_empty_sections(self):
        rst = "Title\n=====\n\n.. toctree::\n\n   page1\n   page2\n"
        result = convert(rst, "t")
        assert result.no_knowledge_content is True

    def test_content_not_no_knowledge(self):
        rst = "Title\n=====\n\nSome real content here.\n"
        result = convert(rst, "t")
        assert result.no_knowledge_content is False


# ---------------------------------------------------------------------------
# Grid table edge cases
# ---------------------------------------------------------------------------

class TestGridTableEdgeCases:
    def test_simple_two_col_table(self):
        block = [
            "+-------+-------+",
            "| Col A | Col B |",
            "+=======+=======+",
            "| R1C1  | R1C2  |",
            "+-------+-------+",
            "| R2C1  | R2C2  |",
            "+-------+-------+",
        ]
        result = _parse_grid_table(block)
        html = "\n".join(result)
        assert "<thead>" in html
        assert "<th>Col A</th>" in html
        assert "<td>R1C1</td>" in html
        assert "<td>R2C2</td>" in html

    def test_no_header_table(self):
        block = [
            "+-------+-------+",
            "| R1C1  | R1C2  |",
            "+-------+-------+",
            "| R2C1  | R2C2  |",
            "+-------+-------+",
        ]
        result = _parse_grid_table(block)
        html = "\n".join(result)
        # No header separator → no thead
        assert "<thead>" not in html

    def test_empty_block(self):
        assert _parse_grid_table([]) == []

    def test_cjk_content(self):
        """Japanese content must not break parsing."""
        block = [
            "+----------+----------+",
            "| 見出し１ | 見出し２ |",
            "+==========+==========+",
            "| データ１ | データ２ |",
            "+----------+----------+",
        ]
        result = _parse_grid_table(block)
        html = "\n".join(result)
        assert "見出し１" in html
        assert "データ２" in html


# ---------------------------------------------------------------------------
# Simple table edge cases (via docutils)
# ---------------------------------------------------------------------------

class TestSimpleTableEdgeCases:
    def test_basic_two_col(self):
        block = [
            "======  ======",
            "Col1    Col2",
            "======  ======",
            "R1C1    R1C2",
            "======  ======",
        ]
        result = _parse_simple_table(block)
        md = "\n".join(result)
        assert "Col1" in md
        assert "R1C1" in md
        assert "|" in md

    def test_empty_block(self):
        assert _parse_simple_table([]) == []

    def test_cjk_falls_back_to_cjk_parser(self):
        """CJK content triggers CJK-safe fallback — no raw code block."""
        block = [
            "======================================================================== ===============================================================",
            "用途                                                                     セッションストア",
            "======================================================================== ===============================================================",
            "入力～確認～完了画面間で入力情報の保持(複数タブでの画面操作を許容しない) DBストア",
            "認証情報の保持                                                           HTTPセッションストア",
            "======================================================================== ===============================================================",
        ]
        result = _parse_simple_table(block)
        md = "\n".join(result)
        assert "```" not in md
        assert "|" in md
        assert "DBストア" in md
        assert "HTTPセッションストア" in md


# ---------------------------------------------------------------------------
# CJK-safe simple table parser
# ---------------------------------------------------------------------------

class TestSimpleTableCjk:
    def test_two_col_cjk_content(self):
        """Japanese content in column 1, ref-style content in column 2."""
        block = [
            "======================================================================== ===============================================================",
            "用途                                                                     セッションストア",
            "======================================================================== ===============================================================",
            "入力～確認～完了画面間で入力情報の保持(複数タブでの画面操作を許容しない) DBストア",
            "認証情報の保持                                                           HTTPセッションストア",
            "======================================================================== ===============================================================",
        ]
        result = _parse_simple_table_cjk(block)
        md = "\n".join(result)
        assert "|" in md
        assert "DBストア" in md
        assert "HTTPセッションストア" in md
        assert "認証情報の保持" in md

    def test_header_separator_detected(self):
        """Second === separator marks end of header rows."""
        block = [
            "======= =======",
            "Col1    Col2",
            "======= =======",
            "R1C1    R1C2",
            "======= =======",
        ]
        result = _parse_simple_table_cjk(block)
        md = "\n".join(result)
        # Header row + separator + data row
        assert "Col1" in md
        assert "R1C1" in md
        assert "---" in md  # Markdown header separator

    def test_empty_block(self):
        assert _parse_simple_table_cjk([]) == []

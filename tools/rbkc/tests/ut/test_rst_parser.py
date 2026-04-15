"""Unit tests for RST parser edge cases — Phase 2."""
import pytest
from scripts.converters.rst import (
    _detect_heading_chars,
    _is_underline,
    _parse_grid_table,
    _parse_handler_js,
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
# Footnote handling
# ---------------------------------------------------------------------------

class TestFootnoteHandling:
    def test_footnote_inline_text_in_content(self):
        """.. [N] テキスト がセクション content に含まれることを確認。"""
        rst = (
            "Title\n"
            "=====\n"
            "\n"
            "Main text.\n"
            "\n"
            ".. [1] First footnote.\n"
        )
        result = convert(rst, "t")
        assert len(result.sections) == 1
        assert "First footnote." in result.sections[0].content

    def test_footnote_multiline_in_content(self):
        """複数行にわたる脚注本文が content に含まれることを確認。"""
        rst = (
            "Title\n"
            "=====\n"
            "\n"
            "Main text.\n"
            "\n"
            ".. [2] Line one of footnote.\n"
            "   Line two of footnote.\n"
        )
        result = convert(rst, "t")
        content = result.sections[0].content
        assert "Line one of footnote." in content
        assert "Line two of footnote." in content

    def test_footnote_in_section_appended_to_that_section(self):
        """セクション内の脚注は、そのセクションの content に追記される。"""
        rst = (
            "Title\n"
            "=====\n"
            "\n"
            "Section A\n"
            "---------\n"
            "\n"
            "Body text.\n"
            "\n"
            ".. [1] Footnote for section A.\n"
            "\n"
            "Section B\n"
            "---------\n"
            "\n"
            "Other text.\n"
        )
        result = convert(rst, "t")
        sec_a = next(s for s in result.sections if s.title == "Section A")
        sec_b = next(s for s in result.sections if s.title == "Section B")
        assert "Footnote for section A." in sec_a.content
        assert "Footnote for section A." not in sec_b.content


# ---------------------------------------------------------------------------
# class directive handling
# ---------------------------------------------------------------------------

class TestClassDirective:
    def test_class_directive_block_in_content(self):
        """.. class:: ディレクティブのブロックが content に含まれることを確認。"""
        rst = (
            "Title\n"
            "=====\n"
            "\n"
            ".. class:: some-class\n"
            "\n"
            "   API description here.\n"
        )
        result = convert(rst, "t")
        assert "API description here." in result.sections[0].content

    def test_class_directive_block_multiline(self):
        """複数行の class ディレクティブブロックが content に含まれることを確認。"""
        rst = (
            "Title\n"
            "=====\n"
            "\n"
            ".. class:: highlight\n"
            "\n"
            "   Line one.\n"
            "   Line two.\n"
        )
        result = convert(rst, "t")
        content = result.sections[0].content
        assert "Line one." in content
        assert "Line two." in content


# ---------------------------------------------------------------------------
# Named link resolution
# ---------------------------------------------------------------------------

class TestNamedLinkResolution:
    def test_same_file_target_resolved_to_markdown_link(self):
        """同ファイル内の .. _Name: url が `Name`_ を [Name](URL) に変換する。"""
        rst = (
            "Title\n"
            "=====\n"
            "\n"
            "See `APILink`_ for details.\n"
            "\n"
            ".. _APILink: https://example.com/api\n"
        )
        result = convert(rst, "t")
        assert "[APILink](https://example.com/api)" in result.sections[0].content

    def test_backtick_quoted_target_resolved(self):
        """バッククォートで囲まれた名前のターゲット定義が解決される。"""
        rst = (
            "Title\n"
            "=====\n"
            "\n"
            "See `My API`_ for details.\n"
            "\n"
            ".. _`My API`: https://example.com/myapi\n"
        )
        result = convert(rst, "t")
        assert "[My API](https://example.com/myapi)" in result.sections[0].content

    def test_extra_targets_from_include_resolved(self):
        """extra_targets パラメータ経由のターゲット（include ファイル由来）が解決される。"""
        rst = (
            "Title\n"
            "=====\n"
            "\n"
            "See `JavaDoc`_ for reference.\n"
        )
        extra = {"JavaDoc": "https://javadoc.example.com/"}
        result = convert(rst, "t", extra_targets=extra)
        assert "[JavaDoc](https://javadoc.example.com/)" in result.sections[0].content

    def test_unresolved_named_ref_becomes_plain_text(self):
        """ターゲット定義がない `Name`_ はプレーンテキストになる（URLなし）。"""
        rst = (
            "Title\n"
            "=====\n"
            "\n"
            "See `Unknown`_ for details.\n"
        )
        result = convert(rst, "t")
        assert "Unknown" in result.sections[0].content
        assert "](http" not in result.sections[0].content


# ---------------------------------------------------------------------------
# raw :file: Handler.js
# ---------------------------------------------------------------------------

_HANDLER_JS = """\
var Handler = {
ForwardingHandler: {
  name: "内部フォーワードハンドラ"
, package: "nablarch.fw.web.handler"
, behavior: {
    inbound:  ""
  , outbound: "遷移先に内部フォーワードパスが指定されていた場合、"
            + "HTTPリクエストオブジェクトのリクエストURIを内部フォーワードパスに書き換えた後、"
            + "後続のハンドラを再実行する。 "
  , error:    ""
  }
}
};
"""


class TestRawFileHandlerJs:
    def test_handler_behavior_in_content(self, tmp_path):
        """.. raw:: html :file: ../Handler.js の動作説明が content に含まれる。"""
        handler_dir = tmp_path / "handler"
        handler_dir.mkdir()
        fw_dir = tmp_path
        (fw_dir / "Handler.js").write_text(_HANDLER_JS, encoding="utf-8")

        rst = (
            "ForwardingHandler\n"
            "=================\n"
            "\n"
            "ハンドラ処理概要\n"
            "----------------\n"
            "\n"
            ".. raw:: html\n"
            "   :file: ../Handler.js\n"
        )
        rst_path = handler_dir / "ForwardingHandler.rst"
        rst_path.write_text(rst, encoding="utf-8")

        result = convert(rst, "ForwardingHandler", source_path=rst_path)
        content = " ".join(s.content for s in result.sections)
        assert "内部フォーワードハンドラ" in content
        assert "HTTPリクエストオブジェクト" in content

    def test_handler_behavior_empty_string_skipped(self, tmp_path):
        """behavior が空文字のフィールドは出力されない。"""
        (tmp_path / "Handler.js").write_text(_HANDLER_JS, encoding="utf-8")
        rst_dir = tmp_path / "handler"
        rst_dir.mkdir()

        rst = (
            "ForwardingHandler\n"
            "=================\n"
            "\n"
            ".. raw:: html\n"
            "   :file: ../Handler.js\n"
        )
        rst_path = rst_dir / "ForwardingHandler.rst"
        rst_path.write_text(rst, encoding="utf-8")

        result = convert(rst, "ForwardingHandler", source_path=rst_path)
        content = result.sections[0].content
        # inbound/error are empty string → should not appear as label
        assert "inbound:" not in content
        assert "error:" not in content


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


# ---------------------------------------------------------------------------
# Issue 1: _parse_handler_js — None safety (re.search result used without guard)
# ---------------------------------------------------------------------------

class TestParseHandlerJsNullSafety:
    def test_inline_entry_no_crash(self):
        """name/package on same line as braces (no trailing newline) must not crash."""
        # Compact JS without newlines after each field — lookahead (?=\n|,\\s*\\n) fails
        js = 'H: { name: "テスト", package: "foo.bar", behavior: { inbound: "入力処理" } }'
        # Must not raise AttributeError
        result = _parse_handler_js(js, "H")
        assert len(result) == 1
        assert result[0]["name"] == "テスト"
        assert result[0]["package"] == "foo.bar"

    def test_package_field_missing_no_crash(self):
        """Entry without package field returns empty string, not crash."""
        js = 'H: {\n  name: "テスト"\n, behavior: { inbound: "入力" }\n}'
        result = _parse_handler_js(js, "H")
        assert len(result) == 1
        assert result[0]["package"] == ""

    def test_name_field_missing_no_crash(self):
        """Entry without name field returns empty string, not crash."""
        js = 'H: {\n  package: "foo"\n, behavior: { inbound: "入力" }\n}'
        result = _parse_handler_js(js, "H")
        assert len(result) == 1
        assert result[0]["name"] == ""


# ---------------------------------------------------------------------------
# Issue 3: Unknown directive — must skip (not raise ValueError)
# ---------------------------------------------------------------------------

class TestUnknownDirectiveSkip:
    def test_unknown_directive_does_not_raise(self):
        """Unknown RST directives are skipped with a warning, not raised."""
        rst = (
            "Title\n"
            "=====\n"
            "\n"
            "Section\n"
            "-------\n"
            "\n"
            ".. mycustomdir:: arg\n"
            "   body line\n"
            "\n"
            "Normal text.\n"
        )
        # Must not raise ValueError
        result = convert(rst, "test-file")
        full_content = " ".join(s.content for s in result.sections)
        assert "Normal text." in full_content

    def test_content_after_unknown_directive_preserved(self):
        """Text following an unknown directive is still output."""
        rst = (
            "Title\n"
            "=====\n"
            "\n"
            ".. specialblock::\n"
            "\n"
            "After directive.\n"
        )
        result = convert(rst, "test-file")
        assert "After directive." in result.sections[0].content


# ---------------------------------------------------------------------------
# Issue 5: _parse_grid_table — <tbody> must be present after </thead>
# ---------------------------------------------------------------------------

class TestGridTableTbody:
    def test_header_table_has_tbody(self):
        """Table with header separator (=) must wrap body rows in <tbody>."""
        block = [
            "+--------+--------+",
            "| Head A | Head B |",
            "+========+========+",
            "| Cell 1 | Cell 2 |",
            "+--------+--------+",
        ]
        html = "\n".join(_parse_grid_table(block))
        assert "<tbody>" in html
        assert "</tbody>" in html

    def test_tbody_comes_after_thead(self):
        """<tbody> must appear after </thead>, not before."""
        block = [
            "+--------+--------+",
            "| Head A | Head B |",
            "+========+========+",
            "| Cell 1 | Cell 2 |",
            "+--------+--------+",
        ]
        html = "\n".join(_parse_grid_table(block))
        assert html.index("<tbody>") > html.index("</thead>")

    def test_no_header_table_has_tbody(self):
        """Table without header separator must still have <tbody>."""
        block = [
            "+--------+--------+",
            "| Cell 1 | Cell 2 |",
            "+--------+--------+",
        ]
        html = "\n".join(_parse_grid_table(block))
        assert "<tbody>" in html
        assert "</tbody>" in html
        assert "<thead>" not in html

    def test_tbody_not_duplicated_for_no_header_table(self):
        """No-header table should have exactly one <tbody> opening tag."""
        block = [
            "+--------+--------+",
            "| Cell 1 | Cell 2 |",
            "+--------+--------+",
            "| Cell 3 | Cell 4 |",
            "+--------+--------+",
        ]
        html = "\n".join(_parse_grid_table(block))
        assert html.count("<tbody>") == 1


# ---------------------------------------------------------------------------
# Issue 11: code-block option lines — must not strip code content starting with ':'
# ---------------------------------------------------------------------------

class TestCodeBlockOptionFilter:
    def test_rst_option_lines_stripped(self):
        """RST directive options (:linenos: etc.) are stripped from code output."""
        rst = (
            "Title\n"
            "=====\n"
            "\n"
            "Section\n"
            "-------\n"
            "\n"
            ".. code-block:: python\n"
            "   :linenos:\n"
            "   :emphasize-lines: 1\n"
            "\n"
            "   def foo():\n"
            "       pass\n"
        )
        result = convert(rst, "t")
        content = result.sections[0].content
        assert ":linenos:" not in content
        assert ":emphasize-lines:" not in content
        assert "def foo():" in content

    def test_code_line_starting_with_colon_preserved(self):
        """Code content lines starting with ':' must not be stripped."""
        rst = (
            "Title\n"
            "=====\n"
            "\n"
            "Section\n"
            "-------\n"
            "\n"
            ".. code-block:: yaml\n"
            "\n"
            "   :tag: value\n"
            "   normal: data\n"
        )
        result = convert(rst, "t")
        content = result.sections[0].content
        assert ":tag: value" in content
        assert "normal: data" in content

"""E2E tests for RST converter — Phase 2.

Uses actual Nablarch v6 official documentation as input.
"""
import glob
from pathlib import Path

import pytest

from scripts.create.converters.rst import (
    RSTResult,
    Section,
    _detect_heading_chars,
    convert,
)

# Path to the v6 Nablarch official documentation root (ja)
_REPO_ROOT = Path(__file__).parents[4]
V6_DOC_ROOT = _REPO_ROOT / ".lw/nab-official/v6/nablarch-document/ja"
UNIVERSAL_DAO_RST = (
    V6_DOC_ROOT
    / "application_framework/application_framework/libraries/database/universal_dao.rst"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _section(result: RSTResult, title: str) -> Section:
    return next(s for s in result.sections if s.title == title)


# ---------------------------------------------------------------------------
# E2E: universal_dao.rst — structure
# ---------------------------------------------------------------------------

class TestUniversalDaoStructure:
    @pytest.fixture(scope="class")
    def result(self):
        return convert(UNIVERSAL_DAO_RST.read_text(), "libraries-universal_dao")

    def test_title(self, result):
        assert result.title == "ユニバーサルDAO"

    def test_not_no_knowledge_content(self, result):
        assert result.no_knowledge_content is False

    def test_section_count(self, result):
        # Count h2/h3 headings dynamically from source so this test survives RST updates.
        lines = UNIVERSAL_DAO_RST.read_text().splitlines()
        heading_chars = _detect_heading_chars(lines)
        section_chars = set(heading_chars[1:3]) if len(heading_chars) >= 2 else set()
        # An underline line: single repeated char in section_chars, preceded by non-empty text,
        # not preceded by an identical line (which would be an overline).
        h_count = sum(
            1 for i, line in enumerate(lines)
            if (line and len(set(line)) == 1 and line[0] in section_chars
                and len(line) >= 2 and i > 0 and lines[i - 1].strip()
                and not (i >= 2
                         and set(lines[i - 2]) == set(line)
                         and len(lines[i - 2]) >= 2))
        )
        # Converter may add one preamble section (content before first h2/h3)
        assert h_count <= len(result.sections) <= h_count + 1

    def test_section_titles_include_h2(self, result):
        titles = [s.title for s in result.sections]
        assert "機能概要" in titles
        assert "モジュール一覧" in titles
        assert "使用方法" in titles
        assert "拡張例" in titles
        assert "Entityに使用できるJakarta Persistenceアノテーション" in titles
        assert "Beanに使用できるデータタイプ" in titles

    def test_section_titles_include_h3(self, result):
        titles = [s.title for s in result.sections]
        assert "SQLを書かなくても単純なCRUDができる" in titles
        assert "ページングを行う" in titles
        assert "楽観的ロックを行う" in titles

    def test_no_split_suffix_in_titles(self, result):
        for s in result.sections:
            assert "--s" not in s.title


# ---------------------------------------------------------------------------
# E2E: universal_dao.rst — directive conversions
# ---------------------------------------------------------------------------

class TestUniversalDaoDirectives:
    @pytest.fixture(scope="class")
    def result(self):
        return convert(UNIVERSAL_DAO_RST.read_text(), "libraries-universal_dao")

    def test_code_block_converted(self, result):
        s = _section(result, "モジュール一覧")
        assert "```xml" in s.content
        assert "nablarch-common-dao" in s.content
        assert "```" in s.content

    def test_tip_admonition_converted(self, result):
        s = _section(result, "SQLを書かなくても単純なCRUDができる")
        assert "> **Tip:**" in s.content

    def test_important_admonition_converted(self, result):
        s = _section(result, "使用方法")
        assert "> **Important:**" in s.content

    def test_java_extdoc_converted_to_inline_code(self, result):
        # :java:extdoc:`UniversalDao <...>` → `UniversalDao`
        full_content = "\n".join(s.content for s in result.sections)
        assert ":java:extdoc:" not in full_content

    def test_ref_resolved_to_plain_text(self, result):
        # :ref:`label` → label (no RST markup remaining)
        full_content = "\n".join(s.content for s in result.sections)
        assert ":ref:" not in full_content

    def test_double_backtick_converted(self, result):
        full_content = "\n".join(s.content for s in result.sections)
        # RST ``code`` inline markup should be converted to `code`.
        # Code fences (```lang / ```) are Markdown and allowed;
        # only RST-style ``word`` (double-backtick NOT at line start followed by another `) is wrong.
        import re
        # Remove code fence lines before checking
        non_fence_content = "\n".join(
            line for line in full_content.splitlines()
            if not line.startswith("```")
        )
        assert "``" not in non_fence_content, \
            "RST double-backtick inline code was not converted"

    def test_contents_directive_removed(self, result):
        full_content = "\n".join(s.content for s in result.sections)
        assert ".. contents::" not in full_content

    def test_rst_labels_removed(self, result):
        full_content = "\n".join(s.content for s in result.sections)
        assert ".. _universal_dao:" not in full_content
        assert ".. _universal_dao-spec:" not in full_content


# ---------------------------------------------------------------------------
# E2E: grid table (biz_samples/08/index.rst)
# ---------------------------------------------------------------------------

class TestGridTable:
    @pytest.fixture(scope="class")
    def result(self):
        path = V6_DOC_ROOT / "biz_samples/08/index.rst"
        return convert(path.read_text(), "biz-samples-08")

    def test_grid_table_converted_to_html(self, result):
        s = _section(result, "メールの形式")
        assert "<table>" in s.content
        assert "<thead>" in s.content
        assert "<th>" in s.content
        assert "<td>" in s.content

    def test_grid_table_header_content(self, result):
        s = _section(result, "メールの形式")
        assert "メール形式" in s.content
        assert "添付ファイル" in s.content

    def test_grid_table_body_content(self, result):
        s = _section(result, "メールの形式")
        assert "TemplateMailContext" in s.content
        assert "TEXT" in s.content
        assert "HTML" in s.content


# ---------------------------------------------------------------------------
# E2E: no_knowledge_content detection (index.rst files)
# ---------------------------------------------------------------------------

class TestNoKnowledgeContent:
    def test_toctree_only_file_detected(self):
        # index.rst files are typically toctree-only
        rst = """\
ユニバーサルDAO
================

.. toctree::
   :maxdepth: 1

   getting_started
   feature
"""
        result = convert(rst, "test-index")
        assert result.no_knowledge_content is True

    def test_content_file_not_detected(self):
        result = convert(UNIVERSAL_DAO_RST.read_text(), "libraries-universal_dao")
        assert result.no_knowledge_content is False


# ---------------------------------------------------------------------------
# E2E: all v6 RST files — no errors
# ---------------------------------------------------------------------------

def test_all_v6_rst_files_convert_without_error():
    """Every v6 RST file must convert without raising an exception."""
    rst_files = list(V6_DOC_ROOT.rglob("*.rst"))
    assert len(rst_files) > 300, f"Expected >300 RST files, got {len(rst_files)}"

    errors = []
    for path in rst_files:
        try:
            convert(path.read_text(), path.stem)
        except Exception as e:
            errors.append(f"{path.name}: {e}")

    assert not errors, "Conversion errors:\n" + "\n".join(errors)


# ---------------------------------------------------------------------------
# Unit tests: heading detection
# ---------------------------------------------------------------------------

class TestHeadingDetection:
    def test_underline_only_order(self):
        rst = "Title\n=====\n\nSection\n-------\n\nSubsection\n~~~~~~~~~~\n"
        chars = _detect_heading_chars(rst.splitlines())
        assert chars == ["=", "-", "~"]

    def test_overline_detected(self):
        rst = "========\nTitle\n========\n\nSection\n--------\n"
        chars = _detect_heading_chars(rst.splitlines())
        assert chars[0] == "="

    def test_mixed_overline_and_underline(self):
        rst = "========\nTitle\n========\n\nSection A\n---------\n\nSection B\n---------\n"
        chars = _detect_heading_chars(rst.splitlines())
        assert "=" in chars
        assert "-" in chars
        assert chars.index("=") < chars.index("-")


# ---------------------------------------------------------------------------
# Unit tests: no_knowledge_content edge cases
# ---------------------------------------------------------------------------

class TestNoKnowledgeContentEdgeCases:
    def test_empty_string(self):
        result = convert("", "empty")
        assert result.no_knowledge_content is True
        assert result.title == ""

    def test_labels_only(self):
        rst = ".. _foo:\n\n.. _bar:\n"
        result = convert(rst, "labels-only")
        assert result.no_knowledge_content is True

    def test_toctree_and_labels(self):
        rst = """\
Index
=====

.. _index:

.. toctree::

   page1
   page2
"""
        result = convert(rst, "nav")
        assert result.no_knowledge_content is True

    def test_single_paragraph_is_content(self):
        rst = "Title\n=====\n\nThis is content.\n"
        result = convert(rst, "with-content")
        assert result.no_knowledge_content is False

"""Tests for scripts/common/rst_normaliser.py — Phase 21-X.

Spec: rbkc-verify-quality-design.md §3-1 手順 0 (tokenizer).

Covers:
  - inline transforms (10 forms)
  - directive groups (7: code/admonition/table/figure/image/include/drop)
  - section headings, bullet/enum lists, field lists, line blocks, comments
  - line-continuation
  - unknown syntax detection
"""
from __future__ import annotations

import textwrap

import pytest


def _normalise(text, **kw):
    from scripts.common.rst_normaliser import normalise_rst
    return normalise_rst(text, **kw)


# ---------------------------------------------------------------------------
# Inline (10 forms)
# ---------------------------------------------------------------------------

class TestInline:
    def test_role_target(self):
        out = _normalise(":ref:`Doma config <doma_config>`", label_map={"doma_config": "Doma設定"})
        # Role with target — text part is preserved (per spec); label target
        # is also resolved for context but the visible text wins.
        assert "Doma config" in out or "Doma設定" in out

    def test_role_target_label_resolution(self):
        out = _normalise(":ref:`doma_config`", label_map={"doma_config": "Doma設定"})
        assert "Doma設定" in out
        assert ":ref:" not in out
        assert "`" not in out

    def test_role_simple_ref_unknown_label_kept(self):
        # Unknown label — keep the text as-is so verify can decide what to do
        out = _normalise(":ref:`mystery_label`", label_map={})
        assert "mystery_label" in out

    def test_role_doc(self):
        out = _normalise(":doc:`../foo/bar`")
        assert ":doc:" not in out
        assert "`" not in out

    def test_double_backtick_to_single(self):
        assert _normalise("``code``") == "`code`"

    def test_ext_link_named(self):
        out = _normalise("`text <https://example.com>`_")
        assert out == "[text](https://example.com)"

    def test_ext_link_anonymous(self):
        out = _normalise("`text <https://example.com>`__")
        assert out == "[text](https://example.com)"

    def test_named_ref(self):
        assert _normalise("`text`_") == "text"

    def test_footnote_ref_preserved(self):
        # Footnote refs appear in converter's JSON output verbatim
        assert "[1]_" in _normalise("See [1]_ for details")

    def test_interpreted_text(self):
        assert _normalise("`emph`") == "emph"

    def test_strong_preserved(self):
        # Strong markup is identical in RST and MD
        assert _normalise("**bold**") == "**bold**"

    def test_emphasis_preserved(self):
        assert _normalise("*em*") == "*em*"


# ---------------------------------------------------------------------------
# Substitution references inside prose
# ---------------------------------------------------------------------------

class TestSubstitutionReferences:
    def test_br_expands_to_newline(self):
        src = ".. |br| raw:: html\n\n   <br>\n\nHello|br|World\n"
        out = _normalise(src)
        assert "Hello\nWorld" in out

    def test_replace_substitution(self):
        src = ".. |name| replace:: Nablarch\n\nUse |name| here.\n"
        out = _normalise(src)
        assert "Use Nablarch here." in out


# ---------------------------------------------------------------------------
# Directives — 7 groups
# ---------------------------------------------------------------------------

class TestDirectiveCodeBlock:
    def test_code_block_body_fenced(self):
        src = ".. code-block:: java\n\n   public class X {}\n"
        out = _normalise(src)
        assert "```java" in out
        assert "public class X {}" in out
        assert "```" in out


class TestDirectiveAdmonition:
    def test_note(self):
        src = ".. note::\n\n   Read carefully.\n"
        out = _normalise(src)
        assert "Read carefully." in out

    def test_tip(self):
        src = ".. tip::\n\n   Use X instead of Y.\n"
        out = _normalise(src)
        assert "Use X instead of Y." in out

    def test_warning_multiline(self):
        src = ".. warning::\n\n   Line 1.\n\n   Line 2.\n"
        out = _normalise(src)
        assert "Line 1." in out
        assert "Line 2." in out


class TestDirectiveTable:
    def test_list_table_cells_extracted(self):
        src = textwrap.dedent("""\
            .. list-table:: Java EE 対応表
               :header-rows: 1
               :widths: 10 20

               * - Col A
                 - Col B
               * - v1
                 - v2
            """)
        out = _normalise(src)
        # argument (title) dropped — converter doesn't emit it
        assert "Java EE 対応表" not in out
        # header options dropped
        assert ":header-rows:" not in out
        assert ":widths:" not in out
        # cells reconstructed as MD table
        assert "Col A" in out
        assert "v1" in out

    def test_table_directive_cells_extracted(self):
        src = textwrap.dedent("""\
            .. table:: Title Here

               ===== =====
               A     B
               ===== =====
               a     b
               ===== =====
            """)
        out = _normalise(src)
        # argument (title) dropped
        assert "Title Here" not in out
        assert "A" in out
        assert "b" in out


class TestDirectiveFigure:
    def test_figure_caption_preserved_alt_dropped(self):
        src = textwrap.dedent("""\
            .. figure:: image.png
               :alt: Alt text dropped

               Caption text is kept.
            """)
        out = _normalise(src)
        assert "Caption text is kept." in out
        assert "Alt text dropped" not in out


class TestDirectiveImage:
    def test_image_fully_dropped(self):
        src = textwrap.dedent("""\
            .. image:: foo.png
               :scale: 50%
               :alt: anything
            """)
        out = _normalise(src)
        assert "foo.png" not in out
        assert "50%" not in out
        assert "anything" not in out


class TestDirectiveDropBody:
    def test_toctree_dropped(self):
        src = ".. toctree::\n   :maxdepth: 2\n\n   foo\n   bar\n"
        assert _normalise(src).strip() == ""

    def test_contents_dropped(self):
        src = ".. contents::\n   :local:\n"
        assert _normalise(src).strip() == ""

    def test_raw_dropped(self):
        src = ".. raw:: html\n\n   <div>x</div>\n"
        out = _normalise(src)
        assert "<div>" not in out


# ---------------------------------------------------------------------------
# Simple / grid tables
# ---------------------------------------------------------------------------

class TestTables:
    def test_simple_table_cells_extracted(self):
        src = textwrap.dedent("""\
            ===== =====
            A     B
            ===== =====
            a     b
            ===== =====
            """)
        out = _normalise(src)
        assert "A" in out
        assert "b" in out

    def test_grid_table_cells_extracted(self):
        src = textwrap.dedent("""\
            +----+----+
            | A  | B  |
            +====+====+
            | a  | b  |
            +----+----+
            """)
        out = _normalise(src)
        assert "A" in out
        assert "b" in out


# ---------------------------------------------------------------------------
# Section headings, lists, line blocks
# ---------------------------------------------------------------------------

class TestHeadings:
    def test_heading_underline_dropped_title_kept(self):
        src = "Title\n=====\n"
        out = _normalise(src)
        assert "Title" in out
        assert "=====" not in out

    def test_subheading_with_dashes(self):
        src = "Sub\n---\n"
        assert "Sub" in _normalise(src)
        assert "---" not in _normalise(src)


class TestLists:
    def test_bullet_asterisk(self):
        src = "* item one\n* item two\n"
        out = _normalise(src)
        assert "item one" in out
        assert "item two" in out

    def test_bullet_hyphen(self):
        src = "- a\n- b\n"
        out = _normalise(src)
        assert "a" in out
        assert "b" in out

    def test_enumerated(self):
        src = "1. first\n2. second\n"
        out = _normalise(src)
        assert "first" in out
        assert "second" in out


class TestLineBlock:
    def test_line_block(self):
        src = "| line 1\n| line 2\n"
        out = _normalise(src)
        assert "line 1" in out
        assert "line 2" in out


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

class TestComments:
    def test_standalone_comment_dropped(self):
        src = ".. This is a comment\n\nKeep me.\n"
        out = _normalise(src)
        assert "This is a comment" not in out
        assert "Keep me." in out


# ---------------------------------------------------------------------------
# Field lists — context-aware
# ---------------------------------------------------------------------------

class TestFieldLists:
    def test_directive_option_dropped(self):
        src = ".. code-block:: java\n   :emphasize-lines: 3\n\n   body\n"
        out = _normalise(src)
        assert ":emphasize-lines:" not in out
        assert "body" in out

    def test_standalone_field_list_preserved(self):
        # Standalone field lists (not directive options) are rendered as
        # definition-list text by the converter — keep both name and value.
        src = ":author: John\n:date: 2024-01-01\n"
        out = _normalise(src)
        assert "John" in out
        assert "author" in out


# ---------------------------------------------------------------------------
# Line-continuation
# ---------------------------------------------------------------------------

class TestLineContinuation:
    def test_backslash_newline_preserved(self):
        # Converter emits the literal `\` in MD output, so normaliser
        # maps "\<newline>" to "\ " (backslash + space) for alignment.
        src = "foo \\\nbar\n"
        out = _normalise(src)
        assert "foo \\ bar" in out


# ---------------------------------------------------------------------------
# Unknown syntax detection
# ---------------------------------------------------------------------------

class TestUnknownSyntax:
    def test_known_directive_passes(self):
        # Not raising means no unknown syntax
        _normalise(".. note::\n\n   body\n")

    def test_unknown_directive_raises(self):
        from scripts.common.rst_normaliser import UnknownSyntaxError
        with pytest.raises(UnknownSyntaxError):
            _normalise(".. unknowndirective::\n\n   body\n")

"""Unit tests for `scripts/common/md_ast_visitor` (Phase 21-Z Z-2).

TDD-first tests: each block/inline token handled by the Visitor gets its
own minimal-fixture assertion. The Visitor produces a :class:`DocumentParts`
value object used by create (JSON) and verify (normalised MD).

References: rbkc-converter-design.md §7, rbkc-verify-quality-design.md §3-2.
"""
from __future__ import annotations

import pytest

from scripts.common import md_ast
from scripts.common.md_ast_visitor import (
    DocumentParts,
    Section,
    UnknownTokenError,
    extract_document,
)


def _run(src: str) -> DocumentParts:
    return extract_document(md_ast.parse(src))


# ---------------------------------------------------------------------------
# Document structure (heading level 1 = title, >=2 = section)
# ---------------------------------------------------------------------------


class TestDocumentStructure:
    def test_h1_becomes_title(self):
        parts = _run("# Title\n")
        assert parts.title == "Title"
        assert parts.content == ""
        assert parts.sections == []

    def test_preamble_before_h2_is_top_level_content(self):
        src = "# T\n\n前書き。\n\n## A\n\nA本文。\n"
        parts = _run(src)
        assert parts.title == "T"
        assert "前書き" in parts.content
        assert len(parts.sections) == 1
        assert parts.sections[0].title == "A"
        assert "A本文" in parts.sections[0].content

    def test_multiple_h2_become_sections(self):
        src = "# T\n\n## A\n\nAA\n\n## B\n\nBB\n"
        parts = _run(src)
        assert [s.title for s in parts.sections] == ["A", "B"]
        assert "AA" in parts.sections[0].content
        assert "BB" in parts.sections[1].content

    def test_h3_becomes_section(self):
        """All heading levels >= 2 open a new section (no nesting)."""
        src = "# T\n\n## A\n\nX\n\n### A1\n\nY\n"
        parts = _run(src)
        assert [s.title for s in parts.sections] == ["A", "A1"]

    def test_no_h1_means_empty_title(self):
        parts = _run("段落のみ。\n")
        assert parts.title == ""
        assert "段落のみ" in parts.content


# ---------------------------------------------------------------------------
# Inline tokens
# ---------------------------------------------------------------------------


class TestInlineTokens:
    def test_strong(self):
        parts = _run("**bold**\n")
        assert "**bold**" in parts.content

    def test_em(self):
        parts = _run("*em*\n")
        assert "*em*" in parts.content

    def test_code_inline(self):
        parts = _run("use `foo` here\n")
        assert "`foo`" in parts.content

    def test_link(self):
        parts = _run("see [docs](https://example.com/x)\n")
        # Link emits [text](href)
        assert "[docs](https://example.com/x)" in parts.content

    def test_image(self):
        parts = _run("![alt text](./img.png)\n")
        assert "![alt text](./img.png)" in parts.content

    def test_softbreak_is_space(self):
        parts = _run("line1\nline2\n")
        # CommonMark treats a line break inside a paragraph as soft = space
        assert "line1" in parts.content and "line2" in parts.content

    def test_hardbreak(self):
        parts = _run("line1  \nline2\n")
        assert "line1" in parts.content and "line2" in parts.content


# ---------------------------------------------------------------------------
# Block tokens
# ---------------------------------------------------------------------------


class TestBlockTokens:
    def test_bullet_list(self):
        parts = _run("# T\n\n- one\n- two\n")
        assert "* one" in parts.content or "- one" in parts.content
        assert "two" in parts.content

    def test_ordered_list(self):
        parts = _run("# T\n\n1. a\n2. b\n")
        assert "1." in parts.content
        assert "a" in parts.content and "b" in parts.content

    def test_fence(self):
        parts = _run("# T\n\n```java\nint x = 1;\n```\n")
        assert "```" in parts.content
        assert "int x = 1;" in parts.content

    def test_fence_language_is_preserved(self):
        parts = _run("# T\n\n```python\nx = 1\n```\n")
        assert "```python" in parts.content

    def test_table(self):
        src = "# T\n\n| a | b |\n|---|---|\n| 1 | 2 |\n"
        parts = _run(src)
        assert "| a | b |" in parts.content
        assert "| 1 | 2 |" in parts.content
        # Separator row
        assert "| --- | --- |" in parts.content or "|---|---|" in parts.content

    def test_blockquote(self):
        parts = _run("# T\n\n> quoted\n")
        assert "> quoted" in parts.content

    def test_html_block_br_becomes_newline(self):
        # `<br>` appears between two paragraphs — the normalised newline
        # must not cause the paragraphs to run together.
        parts = _run("# T\n\nfirst\n\n<br>\n\nsecond\n")
        assert "first" in parts.content and "second" in parts.content
        # The two paragraphs stay separated after normalisation
        idx_first = parts.content.index("first")
        idx_second = parts.content.index("second")
        assert "\n" in parts.content[idx_first:idx_second]

    def test_hr(self):
        parts = _run("# T\n\ntext\n\n---\n\nmore\n")
        assert "-----" in parts.content or "---" in parts.content


# ---------------------------------------------------------------------------
# QL extraction (link_open href)
# ---------------------------------------------------------------------------


class TestLinkExtraction:
    def test_external_url_is_collected(self):
        parts = _run("see [x](https://example.com/a)\n")
        assert "https://example.com/a" in parts.external_urls

    def test_internal_link_is_collected(self):
        parts = _run("see [x](./other.md)\n")
        assert ("x", "./other.md") in parts.internal_links

    def test_image_src_is_collected(self):
        parts = _run("![alt](./img.png)\n")
        assert ("alt", "./img.png") in parts.images


# ---------------------------------------------------------------------------
# Zero-exception: unknown token MUST raise
# ---------------------------------------------------------------------------


class TestZeroException:
    def test_unknown_block_token_raises(self):
        from markdown_it.token import Token

        tokens = [Token("bogus_open", "", 1)]
        with pytest.raises(UnknownTokenError):
            extract_document(tokens)

    def test_unknown_inline_token_raises(self):
        from markdown_it.token import Token

        inline = Token("inline", "", 0)
        inline.children = [Token("bogus_inline", "", 0)]
        tokens = [
            Token("paragraph_open", "p", 1),
            inline,
            Token("paragraph_close", "p", -1),
        ]
        with pytest.raises(UnknownTokenError):
            extract_document(tokens)

"""markdown-it-py wrapper for Markdown → normalised Markdown.

Both the RBKC converter (create side) and the verify link check consume
Markdown by calling this module. Keeping parser configuration and shared
helpers in one place prevents create and verify from drifting in their
CommonMark-spec interpretation.

Design reference:
- tools/rbkc/docs/rbkc-verify-quality-design.md §2-2 / §3-2
- tools/rbkc/docs/rbkc-converter-design.md §7
"""
from __future__ import annotations

from markdown_it import MarkdownIt
from markdown_it.token import Token


_PARSER: MarkdownIt | None = None


def _get_parser() -> MarkdownIt:
    global _PARSER
    if _PARSER is None:
        # CommonMark base + GFM table + strikethrough (actual usage in
        # Nablarch MD corpus: tables appear in the 6 in-scope files).
        _PARSER = MarkdownIt("commonmark").enable("table").enable("strikethrough")
    return _PARSER


def parse(source: str) -> list[Token]:
    """Parse *source* into a flat token stream.

    markdown-it-py returns a flat list where block tokens appear in
    document order and an ``inline`` block carries a ``children`` list
    of inline tokens. The Visitor walks the token list in order and
    recurses into ``children`` for inline trees.
    """
    return _get_parser().parse(source)


__all__ = ["parse"]

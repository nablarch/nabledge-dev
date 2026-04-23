"""verify-side MD normaliser (markdown-it-py AST + Visitor).

Public API:

    normalise_md(text, *, strict_unknown=True) -> str

Parses the Markdown via ``scripts.common.md_ast`` and walks the token
stream with the shared Visitor to produce a single normalised-MD string
(the "normalised source" for QC1–QC4 sequential-delete).

Zero-exception (§3-1b): unknown tokens raise errors from the Visitor —
callers decide whether to treat them as FAIL or to relax.
"""
from __future__ import annotations

import re

from . import md_ast, md_ast_visitor
from .md_ast_visitor import UnknownTokenError, VisitorError


class UnknownSyntaxError(Exception):
    """Raised when MD content cannot be normalised under strict rules."""


_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def _build_flat_md(parts: md_ast_visitor.DocumentParts) -> str:
    out: list[str] = []
    if parts.title:
        out.append(parts.title)
        out.append("")
    if parts.content:
        out.append(parts.content)
        out.append("")
    for sec in parts.sections:
        out.append(sec.title)
        out.append("")
        if sec.content:
            out.append(sec.content)
            out.append("")
    return "\n".join(out).strip() + "\n"


def normalise_md(text: str, *, strict_unknown: bool = True) -> str:
    """Normalise MD *text* to a flat normalised-MD string via AST.

    HTML comments are stripped beforehand (they are elided by the
    converter; verify must match that behaviour).

    ``strict_unknown=True``: re-raise Visitor errors as
    :class:`UnknownSyntaxError` so verify can report them as QC1 FAIL.
    """
    cleaned = _HTML_COMMENT_RE.sub("", text)
    tokens = md_ast.parse(cleaned)
    try:
        parts = md_ast_visitor.extract_document(tokens)
    except VisitorError as exc:
        if strict_unknown:
            raise UnknownSyntaxError(str(exc)) from exc
        return ""
    return _build_flat_md(parts)


__all__ = [
    "normalise_md",
    "UnknownSyntaxError",
    "UnknownTokenError",
]

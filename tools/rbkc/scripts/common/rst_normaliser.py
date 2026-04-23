"""verify-side RST normaliser (docutils AST + Visitor).

Public API:

    normalise_rst(text, *, label_map=None, source_path=None, strict_unknown=True) -> str

Parses the RST via ``scripts.common.rst_ast`` and walks the doctree with
the shared Visitor to produce a single normalised-MD string (the
"normalised source" for QC1–QC4 sequential-delete).

Zero-exception (§3-1b): unknown nodes / unknown roles / unresolved
references raise errors from the Visitor — callers decide whether to
treat them as FAIL or to relax (``strict_unknown=False``).
"""
from __future__ import annotations

from pathlib import Path

from . import rst_ast, rst_ast_visitor
from .rst_ast_visitor import (
    UnknownNodeError,
    UnknownRoleError,
    UnresolvedReferenceError,
    VisitorError,
)


class UnknownSyntaxError(Exception):
    """Raised when RST content cannot be normalised under strict rules."""


def normalise_rst(
    text: str,
    *,
    label_map: dict[str, str] | None = None,
    source_path: Path | str | None = None,
    strict_unknown: bool = True,
) -> str:
    """Normalise RST *text* to an MD-equivalent string via docutils AST.

    ``strict_unknown=True``: re-raise Visitor errors as
    :class:`UnknownSyntaxError` so verify can report them as QC1 FAIL.

    ``strict_unknown=False``: caller accepts partial output (used by the
    verify content-completeness path which still wants best-effort
    normalisation even when one reference fails to resolve).
    """
    path: Path | None = None
    if source_path is not None:
        path = Path(source_path) if not isinstance(source_path, Path) else source_path

    doctree, _warnings = rst_ast.parse(text, source_path=path)
    try:
        parts = rst_ast_visitor.extract_document(doctree, label_map=label_map)
    except VisitorError as exc:
        if strict_unknown:
            raise UnknownSyntaxError(str(exc)) from exc
        return ""

    return parts.to_flat_md()


__all__ = [
    "normalise_rst",
    "UnknownSyntaxError",
    "UnknownNodeError",
    "UnknownRoleError",
    "UnresolvedReferenceError",
]

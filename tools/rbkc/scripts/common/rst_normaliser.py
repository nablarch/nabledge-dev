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
    label_map: dict | None = None,
    doc_map: dict | None = None,
    source_path: Path | str | None = None,
    strict_unknown: bool = True,
    warnings_out: list | None = None,
    file_id: str = "",
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

    doctree, warnings = rst_ast.parse(text, source_path=path)

    # Spec §3-1b: docutils parse errors (level ≥ 3) → QC1 FAIL. docutils
    # writes them to the warning stream without necessarily embedding them
    # in the doctree (e.g. "Undefined substitution referenced"), so we
    # scan the stream for the (ERROR/3) / (SEVERE/4) markers.
    if strict_unknown and warnings:
        for line in warnings.splitlines():
            # Spec §3-2-3 Sphinx 追従原則: docutils が halt_level=5 下で
            # parse を継続し Sphinx 本体もビルドを継続する ERROR/3 は
            # QC1 FAIL ではなく warning 記録扱い。SEVERE/4 は doctree が
            # 信用できない破壊的状態なので QC1 FAIL を維持。
            # silent skip 禁止のため warnings_out には全て記録する。
            if "(SEVERE/4)" in line:
                raise UnknownSyntaxError(f"docutils parse error: {line.strip()}")
            if "(ERROR/3)" in line:
                if warnings_out is not None:
                    warnings_out.append(line.strip())
                continue

    try:
        parts = rst_ast_visitor.extract_document(
            doctree,
            label_map=label_map,
            doc_map=doc_map,
            source_path=path,
            file_id=file_id,
        )
    except VisitorError as exc:
        if strict_unknown:
            raise UnknownSyntaxError(str(exc)) from exc
        return ""

    # Phase 22-B-16b step 2b F1 fix: propagate visitor warnings so
    # callers can surface dangling-link events.  Spec §3-2-2 requires
    # "WARNING ログ + display text fallback" — without this plumbing the
    # display-text fallback happens silently, which violates "silent
    # skip 禁止は維持".
    if warnings_out is not None:
        warnings_out.extend(parts.warnings)

    return parts.to_flat_md()


__all__ = [
    "normalise_rst",
    "UnknownSyntaxError",
    "UnknownNodeError",
    "UnknownRoleError",
    "UnresolvedReferenceError",
]

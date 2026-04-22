"""verify-side RST normaliser (docutils AST + Visitor).

Public API kept for backwards compatibility with ``scripts.verify.verify``:

    normalise_rst(text, *, label_map=None, source_path=None, strict_unknown=True) -> str

Under the hood this simply parses the RST via ``scripts.common.rst_ast``
and walks the doctree with the shared Visitor to produce a single
normalised-MD string (the "normalised source" for QC1–QC4
sequential-delete). ``label_map`` / ``strict_unknown`` are accepted for
signature compatibility; docutils resolves labels itself on the doctree.
"""
from __future__ import annotations

from pathlib import Path

from . import rst_ast, rst_ast_visitor


class UnknownSyntaxError(Exception):
    """Raised when an unknown RST construct is encountered.

    Preserved for API compatibility with the legacy tokenizer; the new
    AST-based normaliser produces this for unresolved substitutions or
    unmapped nodes when ``strict_unknown=True``.
    """


def normalise_rst(
    text: str,
    *,
    label_map: dict[str, str] | None = None,
    source_path: Path | str | None = None,
    strict_unknown: bool = True,
) -> str:
    """Normalise RST *text* to an MD-equivalent string via docutils AST."""
    path: Path | None = None
    if source_path is not None:
        path = Path(source_path) if not isinstance(source_path, Path) else source_path

    doctree, _warnings = rst_ast.parse(text, source_path=path)
    parts = rst_ast_visitor.extract_document(doctree, label_map=label_map)

    if strict_unknown and parts.warnings:
        # Filter for the warning categories that matter for QC1 FAIL:
        hard = [w for w in parts.warnings if w.startswith(("unmapped node", "unresolved-substitution"))]
        if hard:
            raise UnknownSyntaxError("; ".join(hard))

    return parts.to_flat_md()


__all__ = ["normalise_rst", "UnknownSyntaxError"]

"""RST → RSTResult converter (docutils AST + Visitor).

This is the create-side entry point. It parses RST via
``scripts.common.rst_ast`` and walks the doctree via
``scripts.common.rst_ast_visitor`` to produce an :class:`RSTResult`.

Design reference:
- tools/rbkc/docs/rbkc-verify-quality-design.md
- tools/rbkc/docs/rbkc-converter-design.md
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from scripts.common import rst_ast, rst_ast_visitor


@dataclass
class Section:
    title: str
    content: str
    level: int = 2  # Phase 22-B-16a: heading depth (h2=2, h3=3, ...)


@dataclass
class RSTResult:
    title: str
    no_knowledge_content: bool
    content: str = ""
    sections: list[Section] = field(default_factory=list)
    # Phase 22-B: populated by xlsx converters.  Carries sheet metadata that
    # flows through to the JSON output ("sheet_type": "P1"|"P2" and, for P1,
    # the restored column/row matrix used by docs.py to render an MD table).
    # None for non-xlsx formats.
    meta: dict | None = None


def _detect_no_knowledge_content(parts: rst_ast_visitor.DocumentParts) -> bool:
    """A file has "no knowledge content" when it is a pure toctree page.

    Heuristic: no top-level content and every section has empty content.
    """
    if parts.top_content.strip():
        return False
    for s in parts.sections:
        if s.content.strip():
            return False
    return True


def convert(
    source: str,
    file_id: str = "",
    extra_targets: dict[str, str] | None = None,
    source_path: "Path | None" = None,
    label_map: dict | None = None,
    doc_map: dict | None = None,
) -> RSTResult:
    """Convert RST *source* to :class:`RSTResult`.

    Phase 22-B-16b: ``label_map`` values may be :class:`LabelTarget`
    (yielding CommonMark MD links) or bare ``str`` (legacy single-dir
    title-only rendering).  ``doc_map`` resolves ``:doc:`` targets; pass
    ``source_path`` so the visitor can resolve relative targets.
    """
    doctree, _warnings = rst_ast.parse(source, source_path=source_path)
    parts = rst_ast_visitor.extract_document(
        doctree,
        label_map=label_map,
        doc_map=doc_map,
        source_path=source_path,
    )

    title = parts.top_title or ""
    content = parts.top_content
    sections = [
        Section(title=s.title, content=s.content, level=s.level)
        for s in parts.sections
    ]
    no_kc = _detect_no_knowledge_content(parts)

    return RSTResult(
        title=title,
        no_knowledge_content=no_kc,
        content=content,
        sections=sections,
    )

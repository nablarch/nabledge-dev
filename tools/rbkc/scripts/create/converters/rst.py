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


@dataclass
class RSTResult:
    title: str
    no_knowledge_content: bool
    content: str = ""
    sections: list[Section] = field(default_factory=list)


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
    label_map: dict[str, str] | None = None,
) -> RSTResult:
    """Convert RST *source* to :class:`RSTResult`.

    ``extra_targets`` / ``label_map`` are accepted for signature compatibility
    with the legacy converter; label resolution is delegated to docutils
    transforms on the doctree and does not currently consume these maps.
    They may become useful when cross-document references are added.
    """
    doctree, _warnings = rst_ast.parse(source, source_path=source_path)
    parts = rst_ast_visitor.extract_document(doctree, label_map=label_map)

    title = parts.top_title or ""
    content = parts.top_content
    sections = [Section(title=s.title, content=s.content) for s in parts.sections]
    no_kc = _detect_no_knowledge_content(parts)

    return RSTResult(
        title=title,
        no_knowledge_content=no_kc,
        content=content,
        sections=sections,
    )

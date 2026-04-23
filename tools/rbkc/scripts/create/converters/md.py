"""MD → structured Markdown converter for RBKC.

Converts Nablarch official Markdown documentation into section-split form
suitable for knowledge JSON files.  No AI, no external API calls.

**Parser**: CommonMark via ``scripts.common.md_ast`` (markdown-it-py).
The Visitor in ``scripts.common.md_ast_visitor`` walks the token stream
and produces the same DocumentParts shape that RST uses, so create and
verify share one interpretation of Markdown.

**Asset copying**: This converter is a stateless text transformer.  Image
references are preserved as-is in the output content.  Asset copying is the
responsibility of the CLI pipeline (Phase 8): call
``resolver.collect_asset_refs(md_path, file_id)`` then
``resolver.copy_assets(refs, dest_dir)`` after conversion — identical to the
RST pipeline.

**Section splitting**: ``#`` (h1) becomes the document title.  All heading
levels ``##`` and deeper (h2, h3, h4…) create new ``Section`` objects,
consistent with the RST converter behaviour.

Public API:
    convert(source: str, file_id: str = "") -> RSTResult
"""
from __future__ import annotations

import re

from scripts.common import md_ast
from scripts.common.md_ast_visitor import extract_document
from scripts.create.converters.rst import RSTResult, Section


# HTML comment block: <!-- ... --> (possibly multi-line). markdown-it
# treats HTML comments as html_block; we strip them before parsing so the
# Visitor does not encounter arbitrary HTML content.
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)

# file_ids for files that have no knowledge value
_NO_KNOWLEDGE_STEMS = {"readme", "changelog"}


def _strip_html_comments(text: str) -> str:
    return _HTML_COMMENT_RE.sub("", text)


def _is_no_knowledge(file_id: str) -> bool:
    stem = file_id.lower().rstrip("/").split("/")[-1].split(".")[0]
    return stem in _NO_KNOWLEDGE_STEMS


def convert(
    source: str,
    file_id: str = "",
    source_path=None,
    doc_map: dict | None = None,
) -> RSTResult:
    """Convert Markdown *source* to :class:`RSTResult`.

    Phase 22-B-16b step 3: ``doc_map`` + ``source_path`` enable rewriting
    of relative MD links to cross-document MD link form.
    """
    cleaned = _strip_html_comments(source)
    tokens = md_ast.parse(cleaned)
    parts = extract_document(tokens, doc_map=doc_map, source_path=source_path)

    sections = [
        Section(title=s.title, content=s.content, level=s.level)
        for s in parts.sections
    ]

    return RSTResult(
        title=parts.title,
        no_knowledge_content=_is_no_knowledge(file_id),
        content=parts.content,
        sections=sections,
        warnings=list(getattr(parts, "warnings", []) or []),
    )

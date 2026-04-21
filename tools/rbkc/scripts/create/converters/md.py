"""MD → structured Markdown converter for RBKC.

Converts Nablarch official Markdown documentation into section-split form
suitable for knowledge JSON files.  No AI, no external API calls.

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
from dataclasses import dataclass, field

from scripts.create.converters.rst import RSTResult, Section


# ---------------------------------------------------------------------------
# Regex helpers
# ---------------------------------------------------------------------------

# ATX heading: ``# Title`` — capture level (count of #) and title text
_ATX_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")

# HTML comment block: <!-- ... --> (possibly multi-line)
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)

# file_ids for files that have no knowledge value
_NO_KNOWLEDGE_STEMS = {"readme", "changelog"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _strip_html_comments(text: str) -> str:
    """Remove HTML comment blocks (e.g. textlint directives) from text."""
    return _HTML_COMMENT_RE.sub("", text)


def _is_no_knowledge(file_id: str) -> bool:
    stem = file_id.lower().rstrip("/").split("/")[-1].split(".")[0]
    return stem in _NO_KNOWLEDGE_STEMS


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def _split_sections(lines: list[str]) -> tuple[str, list[str], list[tuple[str, list[str]]]]:
    """Split Markdown lines into (title, preamble_lines, sections).

    ``#`` (h1) is extracted as the document title.  Content between h1 and
    the first h2+ heading is returned as ``preamble_lines``.  ``##`` and
    deeper ATX headings create entries in ``sections``.

    Returns:
        (title, preamble_lines, [(section_title, section_lines), ...])
    """
    title = ""
    preamble_lines: list[str] = []
    sections: list[tuple[str, list[str]]] = []
    current_title: str | None = None
    current_lines: list[str] = []

    for line in lines:
        m = _ATX_RE.match(line)
        if m:
            level = len(m.group(1))
            heading_text = m.group(2)
            if level == 1:
                title = heading_text
                continue
            # h2+ → new section boundary
            if current_title is None:
                preamble_lines.extend(current_lines)
            else:
                sections.append((current_title, current_lines))
            current_title = heading_text
            current_lines = []
            continue
        current_lines.append(line)

    if current_title is None:
        preamble_lines.extend(current_lines)
    else:
        sections.append((current_title, current_lines))

    return title, preamble_lines, sections


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def convert(source: str, file_id: str = "") -> RSTResult:
    """Convert Markdown *source* to :class:`RSTResult`.

    Args:
        source: Full Markdown file content.
        file_id: Knowledge file id (used for no_knowledge_content detection).
                 Asset copying is **not** performed here; call
                 ``resolver.collect_asset_refs`` / ``resolver.copy_assets``
                 separately in the pipeline (Phase 8).

    Returns:
        :class:`RSTResult` with title, no_knowledge_content flag, and sections.
    """
    # Strip HTML comments first
    cleaned = _strip_html_comments(source)

    lines = cleaned.splitlines(keepends=False)
    title, preamble_lines, raw_sections = _split_sections(lines)

    preamble_content = "\n".join(preamble_lines).strip()

    sections: list[Section] = []
    for sec_title, sec_lines in raw_sections:
        content = "\n".join(sec_lines).strip()
        sections.append(Section(title=sec_title, content=content))

    no_knowledge = _is_no_knowledge(file_id)

    return RSTResult(
        title=title,
        no_knowledge_content=no_knowledge,
        content=preamble_content,
        sections=sections,
    )

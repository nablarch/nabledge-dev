"""Browsable docs generator for RBKC.

Generates human-readable Markdown files from knowledge JSON files.
These files are for developer reference only (not deployed to the skill).

**Output format** for each knowledge file:
    # {title}

    ## {section_title}

    {section_content}

    <details>
    <summary>keywords</summary>

    keyword1, keyword2, ...

    </details>

For files with ``no_knowledge_content: true``, only a minimal header is
generated (title + official doc URLs if present) so that link targets exist.

**Output path**: ``{docs_dir}/{type}/{category}/{file_id}.md``

Where type/category are derived from the JSON file's path relative to the
knowledge root — consistent with ``scripts/index.py``.

Public API:
    generate_docs(knowledge_dir: Path, docs_dir: Path) -> int
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from scripts.index import _derive_type_category

# Matches Markdown image and link syntax: ![alt](url) or [text](url)
_MD_LINK_RE = re.compile(r'(!?\[[^\]]*\])\(([^)]+)\)')


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _rewrite_asset_links(text: str, docs_md_path: Path, knowledge_dir: Path) -> str:
    """Rewrite assets/ links so they resolve relative to the docs MD file location.

    JSON content uses ``assets/...`` paths relative to ``knowledge_dir``.
    Docs MD files live under ``docs_dir``, which is separate from ``knowledge_dir``.
    Without rewriting, ``assets/...`` links would not resolve from the docs MD location.

    Args:
        text: Section content (may contain Markdown image/link syntax).
        docs_md_path: Absolute path where the docs MD file will be written.
        knowledge_dir: Root of the knowledge directory (assets/ lives here).

    Returns:
        Text with ``assets/`` prefixes replaced by paths relative to ``docs_md_path.parent``.
    """
    assets_dir = knowledge_dir / "assets"
    rel_prefix = os.path.relpath(assets_dir, docs_md_path.parent)

    def _replace(m: re.Match) -> str:
        bracket = m.group(1)
        url = m.group(2)
        if url.startswith("assets/"):
            rest = url[len("assets/"):]
            url = f"{rel_prefix}/{rest}"
        return f"{bracket}({url})"

    return _MD_LINK_RE.sub(_replace, text)


def _render_no_knowledge(data: dict) -> str:
    """Minimal MD for no_knowledge_content files (title only)."""
    lines = [f"# {data.get('title', '')}", ""]
    return "\n".join(lines)


def _render_full(data: dict, docs_md_path: Path, knowledge_dir: Path) -> str:
    """Full MD for normal knowledge files."""
    lines = [f"# {data.get('title', '')}", ""]

    for section in data.get("sections", []):
        title = section.get("title", "")
        content = section.get("content", "")
        hints = section.get("hints", [])

        lines.append(f"## {title}")
        lines.append("")
        if content:
            lines.append(_rewrite_asset_links(content, docs_md_path, knowledge_dir))
            lines.append("")

        if hints:
            lines.append("<details>")
            lines.append("<summary>keywords</summary>")
            lines.append("")
            lines.append(", ".join(hints))
            lines.append("")
            lines.append("</details>")
            lines.append("")

    return "\n".join(lines)


def generate_docs(knowledge_dir: Path, docs_dir: Path) -> int:
    """Generate browsable Markdown docs from knowledge JSON files.

    Args:
        knowledge_dir: Root directory containing knowledge JSON files.
        docs_dir: Destination root directory for generated ``.md`` files.

    Returns:
        Number of MD files written.
    """
    count = 0
    for json_path in sorted(knowledge_dir.rglob("*.json")):
        data = _load_json(json_path)
        rel_path = json_path.relative_to(knowledge_dir)
        type_, category = _derive_type_category(rel_path)
        file_id = json_path.stem

        if category:
            md_dir = docs_dir / type_ / category
        else:
            md_dir = docs_dir / type_
        md_dir.mkdir(parents=True, exist_ok=True)
        docs_md_path = md_dir / f"{file_id}.md"

        if data.get("no_knowledge_content") is True:
            md_content = _render_no_knowledge(data)
        else:
            md_content = _render_full(data, docs_md_path, knowledge_dir)

        docs_md_path.write_text(md_content, encoding="utf-8")
        count += 1

    return count

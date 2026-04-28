"""Browsable docs generator for RBKC.

Generates human-readable Markdown files from knowledge JSON files.
These files are for developer reference only (not deployed to the skill).

**Output format** for each knowledge file:
    # {title}

    {top-level content (preamble)}

    ## {section_title}

    {section_content}

For files with ``no_knowledge_content: true``, only a minimal header is
generated (title + official doc URLs if present) so that link targets exist.

**Output path**: ``{docs_dir}/{type}/{category}/{file_id}.md``

Where type/category are derived from the JSON file's path relative to the
knowledge root — consistent with ``scripts/create/index.py``.

Public API:
    generate_docs(knowledge_dir: Path, docs_dir: Path, version: str = "") -> int
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from scripts.create.index import _derive_type_category

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
    title = data.get("title", "")
    lines = [f"# {title}", ""] if title else [""]
    return "\n".join(lines)


def _render_full(data: dict, docs_md_path: Path, knowledge_dir: Path) -> str:
    """Full MD for normal knowledge files.

    When the JSON title is empty we omit the `#` heading entirely so QO1
    (title must match H1) does not flag a spurious mismatch. A missing
    title is itself a converter bug, but emitting `# ` would paper over it.
    """
    # Phase 22-B: xlsx sheets are rendered per sheet_type.  P1 uses a
    # restored MD table so a human can read the original Excel back out.
    # P2 uses plain-text flow.  Non-xlsx JSON has no sheet_type and falls
    # through to the default section layout.
    sheet_type = data.get("sheet_type")
    if sheet_type == "P1":
        return _render_xlsx_p1(data)
    if sheet_type == "P2":
        return _render_xlsx_p2(data)

    title = data.get("title", "")
    lines = [f"# {title}", ""] if title else []

    top_content = data.get("content", "")
    if top_content:
        lines.append(_rewrite_asset_links(top_content, docs_md_path, knowledge_dir))
        lines.append("")

    for section in data.get("sections", []):
        title = section.get("title", "")
        content = section.get("content", "")
        # Phase 22-B-16a: emit heading at declared depth (spec
        # rbkc-json-schema-design.md §4-2).  level=2 → `##`, level=3 →
        # `###`, level=4 → `####`.  Missing level defaults to 2 only when
        # the key is absent entirely (legacy JSON); a normal 22-B-16a
        # build always writes level.
        level = section.get("level", 2)
        hashes = "#" * max(1, int(level))
        lines.append(f"{hashes} {title}")
        lines.append("")
        if content:
            lines.append(_rewrite_asset_links(content, docs_md_path, knowledge_dir))
            lines.append("")

    return "\n".join(lines)


def _md_table_cell(s: str) -> str:
    """Escape a cell value for a Markdown pipe table.

    * Pipe ``|`` is the column separator → must be escaped.
    * Whitespace (including embedded newlines) is collapsed to single
      spaces.  Spec §8-4 stores P1 values line-flattened in JSON so the
      ``{列名}: {値}`` format is parseable; keeping the docs MD cell in
      the same flattened form lets verify's QO2 P1 one-way containment
      check succeed on a direct substring lookup.
    """
    return " ".join(s.replace("|", "\\|").split())


def _render_xlsx_p1(data: dict) -> str:
    """Render an Excel P1 sheet as title + restored MD table."""
    title = data.get("title", "")
    columns = data.get("columns", [])
    rows = data.get("data_rows", [])
    top = data.get("content", "")

    lines: list[str] = [f"# {title}", ""] if title else []
    if top:
        lines.append(top)
        lines.append("")
    if columns:
        header = "| " + " | ".join(_md_table_cell(c) for c in columns) + " |"
        sep = "|" + "|".join("---" for _ in columns) + "|"
        lines.append(header)
        lines.append(sep)
        width = len(columns)
        for r in rows:
            padded = list(r) + [""] * max(0, width - len(r))
            lines.append("| " + " | ".join(_md_table_cell(v) for v in padded[:width]) + " |")
        lines.append("")
    return "\n".join(lines)


def _render_xlsx_p2(data: dict) -> str:
    """Render an Excel P2 sheet as title + body text.

    P2-1 (p2_headings present): emit each heading at its declared level,
    interleaved with body paragraphs from content (lines not matching any
    heading text are emitted as plain paragraphs between headings).
    P2-3 (sheet_subtype == "P2-3"): use p2_raw_content and convert embedded
    LF to Markdown hard line break (  \\n).
    P2-2 (neither): emit content as-is.
    """
    title = data.get("title", "")
    lines: list[str] = [f"# {title}" if title else "", ""]

    p2_headings = data.get("p2_headings")
    if p2_headings is not None:
        # P2-1: p2_raw_lines holds original row data as [[(col, text), ...], ...]
        # Fall back to reconstructing from p2_headings alone if raw lines absent.
        raw_lines = data.get("p2_raw_lines")
        if raw_lines is not None:
            # Each element is a list of (col_index, cell_text) pairs for one row.
            # Absolute column: col-0 → H2 (##), col-1 → H3 (###), col-2 → H4 (####),
            # col-3+ → body paragraph. Multi-cell rows are always body (comparison tables).
            for row in raw_lines:
                if not row:
                    continue
                min_cx = min(cx for cx, _ in row if _)
                if len(row) == 1 and min_cx <= 2:
                    text = next(v for cx, v in row if cx == min_cx)
                    hashes = "#" * (2 + min_cx)
                    lines.append(f"{hashes} {text}")
                    lines.append("")
                else:
                    body = "  ".join(v for _, v in row if v)
                    if body:
                        lines.append(body)
                        lines.append("")
        else:
            # Minimal fallback: emit headings in order (no body paragraphs)
            for h in p2_headings:
                lvl = h.get("level", 2)
                lines.append(f"{'#' * lvl} {h['text']}")
                lines.append("")
        return "\n".join(lines)

    if data.get("sheet_subtype") == "P2-3":
        # P2-3: use raw content (LF preserved), convert LF → hard line break
        raw = data.get("p2_raw_content", data.get("content", ""))
        if raw:
            converted = re.sub(r'\n', '  \n', raw.rstrip('\n'))
            lines.append(converted)
            lines.append("")
        return "\n".join(lines)

    # P2-2: plain text
    top = data.get("content", "")
    if top:
        lines.append(top)
        lines.append("")
    return "\n".join(lines)


def _generate_readme(entries: list[tuple[str, str, str, str]], docs_dir: Path, version: str) -> None:
    """Write README.md index file to docs_dir.

    Args:
        entries: List of (type_, category, title, rel_md_path) tuples.
        docs_dir: Docs root directory where README.md will be written.
        version: Nablarch version string (e.g. "6", "5").
    """
    version_label = f"Nablarch {version} " if version else "Nablarch "
    lines = [f"# {version_label}ドキュメント", "", f"{len(entries)} ページ", ""]

    # Sort by type_ then category to ensure contiguous grouping
    sorted_entries = sorted(entries, key=lambda e: (e[0], e[1]))

    current_type = None
    current_category = None
    for type_, category, title, rel_path in sorted_entries:
        if type_ != current_type:
            lines.append(f"## {type_}")
            lines.append("")
            current_type = type_
            current_category = None
        if category and category != current_category:
            lines.append(f"### {category}")
            lines.append("")
            current_category = category
        lines.append(f"- [{title}]({rel_path})")

    lines.append("")
    (docs_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


def generate_docs(knowledge_dir: Path, docs_dir: Path, version: str = "") -> int:
    """Generate browsable Markdown docs from knowledge JSON files.

    Args:
        knowledge_dir: Root directory containing knowledge JSON files.
        docs_dir: Destination root directory for generated ``.md`` files.
        version: Nablarch version string for README.md header.

    Returns:
        Number of MD files written.
    """
    docs_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    readme_entries: list[tuple[str, str, str, str]] = []

    for json_path in sorted(knowledge_dir.rglob("*.json")):
        # Skip literalinclude source copies under assets/ — these are not
        # content JSON and may contain non-JSON syntax (JS-style comments
        # in e.g. ETL config samples).
        if "assets" in json_path.relative_to(knowledge_dir).parts:
            continue
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

        title = data.get("title") or file_id
        rel_md = str(docs_md_path.relative_to(docs_dir)).replace("\\", "/")
        readme_entries.append((type_, category, title, rel_md))

    _generate_readme(readme_entries, docs_dir, version)
    return count

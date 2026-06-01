"""Index generator for RBKC.

Generates index.md from knowledge JSON files:

- ``index.md`` — Markdown format for semantic search (Stage 1 page selection).
  Format: H2 per category → H3 per file → list of section IDs and titles.

Files with ``no_knowledge_content: true`` are excluded.

Public API:
    generate_index_md(knowledge_dir, output_path) -> None
"""
from __future__ import annotations

import json
from pathlib import Path

_SKIP_SECTION_TITLES = frozenset([
    "モジュール一覧",
    "アプリケーションフレームワーク",
    "制約",
    "ハンドラクラス名",
])


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))



def _build_section_lines(sections: list[dict]) -> list[str]:
    """Format section list into index.md lines (L2/L3 tree or flat for Excel)."""
    if not sections:
        return []

    has_level = any("level" in s for s in sections)
    lines: list[str] = []

    if has_level:
        current_l2: dict | None = None
        for s in sections:
            title = s["title"]
            if title in _SKIP_SECTION_TITLES:
                continue
            level = s.get("level")
            sid = s["id"]
            if level == 2:
                current_l2 = s
                lines.append(f"- {sid}: {title}")
            elif level == 3 and current_l2 is not None:
                lines.append(f"  - {sid}: {title}")
            # L4+ omitted
    else:
        for s in sections:
            title = s["title"]
            if title in _SKIP_SECTION_TITLES:
                continue
            lines.append(f"- {s['id']}: {title}")

    return lines


def generate_index_md(knowledge_dir: Path, output_path: Path) -> None:
    """Write ``index.md`` to *output_path* from knowledge JSON files.

    Scans *knowledge_dir* recursively for JSON files. Files with
    ``no_knowledge_content: true`` and index-named files are excluded.
    Categories (first two path components) form H2 sections; each file
    forms an H3 entry with path and section list.

    Args:
        knowledge_dir: Root directory containing knowledge JSON files.
        output_path: Destination path for ``index.md``.
    """
    files_by_category: dict[str, list[tuple[str, dict]]] = {}

    for json_path in sorted(knowledge_dir.rglob("*.json")):
        if json_path.stem.startswith("index") or json_path.stem.startswith("terms"):
            continue
        rel = json_path.relative_to(knowledge_dir)
        parts = rel.parts
        # Skip literalinclude source copies under assets/ — not content JSON.
        if "assets" in parts:
            continue
        # Issue #363: Javadoc knowledge files are reached via :java:extdoc: links
        # only; they are intentionally excluded from index.md (semantic search
        # would break with 750+ extra entries per rbkc-converter-design.md §5-2).
        if "javadoc" in parts:
            continue
        if len(parts) < 2:
            continue
        category = "/".join(parts[:2])
        try:
            data = _load_json(json_path)
        except (json.JSONDecodeError, OSError):
            continue
        if data.get("no_knowledge_content") is True:
            continue
        files_by_category.setdefault(category, []).append((str(rel), data))

    lines = ["# Knowledge Index", ""]

    for category in sorted(files_by_category.keys()):
        lines.append(f"## {category}")
        lines.append("")
        for rel_path, data in files_by_category[category]:
            title = data.get("title", Path(rel_path).stem)
            lines.append(f"### {title}")
            lines.append(f"path: {rel_path}")
            section_lines = _build_section_lines(data.get("sections", []))
            lines.extend(section_lines)
            lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")

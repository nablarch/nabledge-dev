"""Index generator for RBKC.

Generates two index formats from knowledge JSON files:

1. ``index.toon`` — TOON format for Nabledge skills (legacy lookup).
   Entry format: {title}, {type}, {category}, {processing_patterns}, {relative_path}

2. ``index.md`` — Markdown format for semantic search (Stage 1 page selection).
   Format: H2 per category → H3 per file → list of section IDs and titles.

Files with ``no_knowledge_content: true`` are excluded from both outputs.

Public API:
    generate_index(file_infos, knowledge_dir, version, output_path) -> int
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


def _derive_type_category(rel_path: Path) -> tuple[str, str]:
    """Derive (type, category) from a path relative to the knowledge root.

    Used by docs.py for README grouping — kept for backward compatibility
    with path-based derivation when FileInfo is not available.

    Examples:
        component/handlers/handlers-error.json  -> ('component', 'handlers')
        about/release-notes/file.json           -> ('about', 'release-notes')
        single-level/file.json                  -> ('single-level', '')
    """
    parts = rel_path.parts
    type_ = parts[0] if len(parts) >= 1 else ""
    category = parts[1] if len(parts) >= 3 else ""
    return type_, category


def generate_index(
    file_infos: list,
    knowledge_dir: Path,
    version: str,
    output_path: Path,
) -> int:
    """Write ``index.toon`` to *output_path* from classified file infos.

    ``processing_patterns`` is derived from the mapping-assigned type/category:
    ``type == "processing-pattern"`` → ``category`` (e.g. ``nablarch-batch``);
    any other type → empty string. This matches KC's semantics
    (``phase_f_finalize.py:303``).

    Args:
        file_infos: List of FileInfo objects from classify_sources().
        knowledge_dir: Root directory containing knowledge JSON files.
        version: Nabledge version string (e.g. "6", "5").
        output_path: Destination path for ``index.toon``.

    Returns:
        Number of entries written (excludes ``no_knowledge_content`` files).
    """
    entries: list[dict] = []

    for fi in file_infos:
        json_path = knowledge_dir / fi.output_path
        if not json_path.exists():
            continue
        data = _load_json(json_path)
        if data.get("no_knowledge_content") is True:
            continue

        title = data.get("title", json_path.stem)
        # Commas in title would break TOON format — replace with Japanese comma
        title = title.replace(",", "、")

        pp = fi.category if fi.type == "processing-pattern" else ""

        entries.append({
            "title": title,
            "type": fi.type,
            "category": fi.category,
            "processing_patterns": pp,
            "path": fi.output_path.replace("\\", "/"),
        })

    # Preserve deterministic order: sort by path
    entries.sort(key=lambda e: e["path"])

    lines = [f"# Nabledge-{version} Knowledge Index", ""]
    lines.append(f"files[{len(entries)},]{{title,type,category,processing_patterns,path}}:")
    for e in entries:
        fields = [e["title"], e["type"], e["category"], e["processing_patterns"], e["path"]]
        lines.append(f"  {', '.join(fields)}")
    lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return len(entries)


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

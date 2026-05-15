"""Index generator for RBKC.

Generates two index formats from classified knowledge JSON files:

1. ``index.toon`` (TOON format) — used by the current skill's keyword search.
2. ``index.md`` (Markdown format) — used by the new semantic search Stage1.

Files with ``no_knowledge_content: true`` are excluded from both formats.

Public API:
    generate_index(file_infos, knowledge_dir, version, output_path) -> int
    generate_index_md(file_infos, knowledge_dir, output_path) -> None
"""
from __future__ import annotations

import json
from pathlib import Path


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


_SKIP_SECTION_TITLES = frozenset([
    "モジュール一覧",
    "アプリケーションフレームワーク",
    "制約",
    "ハンドラクラス名",
])


def generate_index_md(
    file_infos: list,
    knowledge_dir: Path,
    output_path: Path,
) -> None:
    """Write ``index.md`` to *output_path* from classified file infos.

    Format (for semantic search Stage1):
      # Knowledge Index

      ## {category_path}

      ### {file_title}
      path: {relative_path}
      - sN: {section_title}        (level 2)
        - sN: {section_title}      (level 3, indented)

    Sections at level 4+ are omitted. Sections without a level field
    (Excel-derived) appear as flat list items (level 2 equivalent).
    Section titles in _SKIP_SECTION_TITLES are omitted.
    """
    # Build entries, skip no_knowledge_content files
    entries: list[dict] = []
    for fi in file_infos:
        json_path = knowledge_dir / fi.output_path
        if not json_path.exists():
            continue
        data = _load_json(json_path)
        if data.get("no_knowledge_content") is True:
            continue
        rel_path = fi.output_path.replace("\\", "/")
        # category = parent directory of the file (e.g. "component/libraries")
        parts = Path(rel_path).parts
        category = "/".join(parts[:-1]) if len(parts) > 1 else parts[0]
        entries.append({
            "title": data.get("title", Path(rel_path).stem),
            "path": rel_path,
            "category": category,
            "sections": data.get("sections", []),
        })

    entries.sort(key=lambda e: e["path"])

    # Group by category
    from itertools import groupby
    lines = ["# Knowledge Index"]
    for category, group in groupby(entries, key=lambda e: e["category"]):
        lines.append("")
        lines.append(f"## {category}")
        for entry in group:
            lines.append("")
            lines.append(f"### {entry['title']}")
            lines.append(f"path: {entry['path']}")
            for sec in entry["sections"]:
                title = sec.get("title", "")
                if title in _SKIP_SECTION_TITLES:
                    continue
                sid = sec.get("id", "")
                level = sec.get("level")
                if level is None:
                    lines.append(f"- {sid}: {title}")
                elif level == 2:
                    lines.append(f"- {sid}: {title}")
                elif level == 3:
                    lines.append(f"  - {sid}: {title}")
                # level 4+ omitted

    lines.append("")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")

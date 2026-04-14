"""Index generator for RBKC.

Scans a directory of knowledge JSON files and generates an ``index.toon``
file in TOON format — the format used by Nabledge skills for knowledge lookup.

**Entry format** (one per data line):
    {title}, {type}, {category}, {processing_patterns}, {relative_path}

Where:
- ``title``: from JSON ``title`` field
- ``type``: first directory component relative to *knowledge_dir*
             (e.g. ``component`` for ``component/handlers/file.json``)
- ``category``: second directory component (e.g. ``handlers``)
- ``processing_patterns``: space-joined hints aggregated from all sections
- ``relative_path``: path relative to *knowledge_dir*

Files with ``no_knowledge_content: true`` are excluded.

Public API:
    generate_index(knowledge_dir: Path, version: str, output_path: Path) -> int
"""
from __future__ import annotations

import json
from pathlib import Path


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _derive_type_category(rel_path: Path) -> tuple[str, str]:
    """Derive (type, category) from a path relative to the knowledge root.

    Examples:
        component/handlers/handlers-error.json  -> ('component', 'handlers')
        about/release-notes/file.json           -> ('about', 'release-notes')
        single-level/file.json                  -> ('single-level', '')
    """
    parts = rel_path.parts
    type_ = parts[0] if len(parts) >= 1 else ""
    category = parts[1] if len(parts) >= 3 else ""
    return type_, category


def _collect_hints(data: dict) -> str:
    """Aggregate all hints from all sections, deduplicated, space-joined."""
    seen: list[str] = []
    seen_set: set[str] = set()
    for section in data.get("sections", []):
        for h in section.get("hints", []):
            if h and h not in seen_set:
                seen.append(h)
                seen_set.add(h)
    return " ".join(seen)


def generate_index(knowledge_dir: Path, version: str, output_path: Path) -> int:
    """Scan *knowledge_dir* and write ``index.toon`` to *output_path*.

    Args:
        knowledge_dir: Root directory containing knowledge JSON files.
        version: Nabledge version string (e.g. "6", "5").
        output_path: Destination path for ``index.toon``.

    Returns:
        Number of entries written (excludes ``no_knowledge_content`` files).
    """
    entries: list[dict] = []

    for json_path in sorted(knowledge_dir.rglob("*.json")):
        data = _load_json(json_path)
        if data.get("no_knowledge_content") is True:
            continue

        rel_path = json_path.relative_to(knowledge_dir)
        type_, category = _derive_type_category(rel_path)
        title = data.get("title", json_path.stem)
        # Commas in title would break TOON format — replace with Japanese comma
        title = title.replace(",", "、")
        processing_patterns = _collect_hints(data)

        entries.append({
            "title": title,
            "type": type_,
            "category": category,
            "processing_patterns": processing_patterns,
            "path": str(rel_path).replace("\\", "/"),
        })

    lines = [f"# Nabledge-{version} Knowledge Index", ""]
    lines.append(f"files[{len(entries)},]{{title,type,category,processing_patterns,path}}:")
    for e in entries:
        fields = [e["title"], e["type"], e["category"], e["processing_patterns"], e["path"]]
        lines.append(f"  {', '.join(fields)}")
    lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return len(entries)

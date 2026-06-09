"""Class index generator for RBKC (Issue #368).

Generates classes.md — a reverse index from class name to knowledge page.
Counterpart to index.md; used by semantic-search Step 2 for class-name lookup.

Target categories: component, processing-pattern, development-tools.

Public API:
    generate_classes_md(knowledge_dir, output_path) -> None
"""
from __future__ import annotations

import json
import re
from pathlib import Path

_TARGET_CATEGORIES = frozenset(["component", "processing-pattern", "development-tools"])

_JAVADOC_LINK_RE = re.compile(r"\[([^\]]+)\]\(../../javadoc/javadoc-[^)]+\.json\)")

_NO_CLASSES_MESSAGE = (
    "_No class index available for this version "
    "(no Javadoc references in knowledge files)._"
)


def _extract_classes(text: str) -> list[str]:
    """Return deduplicated class names from Javadoc link patterns in *text*.

    Strips #method suffixes and preserves first-occurrence order.
    """
    seen: set[str] = set()
    result: list[str] = []
    for m in _JAVADOC_LINK_RE.finditer(text):
        raw = m.group(1)
        cls = raw.split("#", 1)[0]
        if cls not in seen:
            seen.add(cls)
            result.append(cls)
    return result


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def generate_classes_md(knowledge_dir: Path, output_path: Path) -> None:
    """Write classes.md to *output_path* from knowledge JSON files.

    Scans *knowledge_dir* for JSON files in the 3 target categories.
    Pages with at least one Javadoc link get an H3 entry listing class names.
    When no class-bearing page exists (old versions without Javadoc), a fixed
    fallback message is emitted so semantic-search can read the file unconditionally.

    Args:
        knowledge_dir: Root directory containing knowledge JSON files.
        output_path: Destination path for classes.md.
    """
    files_by_category: dict[str, list[tuple[str, list[str]]]] = {}

    for json_path in sorted(knowledge_dir.rglob("*.json")):
        rel = json_path.relative_to(knowledge_dir)
        parts = rel.parts

        if "assets" in parts or "javadoc" in parts:
            continue
        if len(parts) < 2:
            continue

        top_category = parts[0]
        if top_category not in _TARGET_CATEGORIES:
            continue

        try:
            data = _load_json(json_path)
        except (json.JSONDecodeError, OSError):
            continue

        if data.get("no_knowledge_content") is True:
            continue

        all_text = data.get("content", "") or ""
        for section in data.get("sections", []):
            all_text += " " + (section.get("content", "") or "")

        classes = _extract_classes(all_text)
        if not classes:
            continue

        files_by_category.setdefault(top_category, []).append((str(rel), classes))

    lines = ["# Class Index", ""]

    if not files_by_category:
        lines.append(_NO_CLASSES_MESSAGE)
    else:
        for category in sorted(files_by_category.keys()):
            lines.append(f"## {category}")
            lines.append("")
            for rel_path, classes in files_by_category[category]:
                title_data: dict = {}
                try:
                    title_data = _load_json(knowledge_dir / rel_path)
                except (json.JSONDecodeError, OSError):
                    pass
                title = title_data.get("title", Path(rel_path).stem)
                lines.append(f"### {title}")
                lines.append(f"path: {rel_path}")
                for cls in classes:
                    lines.append(f"- {cls}")
                lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")

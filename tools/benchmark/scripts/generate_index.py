"""Generate index.md from knowledge JSON files.

Follows the index.md design in semantic-search-design.md:
- H2 for category (directory path)
- H3 for each file (title + path)
- L2 sections as list items
- L3 sections indented under L2
- L4+ omitted
- Skip rules for boilerplate titles
- Excel-derived (check): flat list
- releases: file entry only (no sections)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

SKIP_TITLES = frozenset([
    "モジュール一覧",
    "アプリケーションフレームワーク",
    "制約",
    "ハンドラクラス名",
])

RELEASES_CATEGORY = "releases"


def load_knowledge_file(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_section_tree(sections: list[dict]) -> list[dict]:
    """Build L2→L3 tree from flat section list. Returns L2 nodes with children."""
    tree: list[dict] = []
    current_l2: dict | None = None
    for s in sections:
        level = s.get("level")
        title = s["title"]
        sid = s["id"]
        if title in SKIP_TITLES:
            continue
        if level == 2:
            current_l2 = {"id": sid, "title": title, "children": []}
            tree.append(current_l2)
        elif level == 3 and current_l2 is not None:
            current_l2["children"].append({"id": sid, "title": title})
        elif level == 3 and current_l2 is None:
            print(f"WARNING: orphan L3 section {sid} '{title}' (no parent L2), skipping", file=sys.stderr)
    return tree


def format_file_entry(
    rel_path: str,
    title: str,
    sections: list[dict],
    category_top: str,
) -> list[str]:
    """Format a single knowledge file for index.md."""
    lines = [f"### {title}", f"path: {rel_path}"]

    if category_top == RELEASES_CATEGORY:
        return lines

    has_level = any(s.get("level") is not None for s in sections)

    if has_level:
        tree = build_section_tree(sections)
        for node in tree:
            lines.append(f"- {node['id']}: {node['title']}")
            for child in node["children"]:
                lines.append(f"  - {child['id']}: {child['title']}")
    else:
        for s in sections:
            if s["title"] in SKIP_TITLES:
                continue
            lines.append(f"- {s['id']}: {s['title']}")

    return lines


def generate_index(knowledge_dir: str | Path) -> str:
    """Generate index.md content from knowledge directory."""
    knowledge_dir = Path(knowledge_dir)
    files_by_category: dict[str, list[tuple[str, dict]]] = {}

    for json_path in sorted(knowledge_dir.rglob("*.json")):
        if json_path.name.startswith("index"):
            continue
        rel = json_path.relative_to(knowledge_dir)
        parts = rel.parts
        if len(parts) < 2:
            continue
        category = "/".join(parts[:2])
        rel_str = str(rel)
        data = load_knowledge_file(json_path)
        files_by_category.setdefault(category, []).append((rel_str, data))

    lines = ["# Knowledge Index", ""]

    for category in sorted(files_by_category.keys()):
        lines.append(f"## {category}")
        lines.append("")
        category_top = category.split("/")[0]
        for rel_path, data in files_by_category[category]:
            title = data.get("title", rel_path)
            sections = data.get("sections", [])
            entry_lines = format_file_entry(rel_path, title, sections, category_top)
            lines.extend(entry_lines)
            lines.append("")

    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate index.md from knowledge JSON")
    parser.add_argument("knowledge_dir", help="Path to knowledge directory")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    args = parser.parse_args()

    content = generate_index(args.knowledge_dir)

    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
    else:
        print(content)


if __name__ == "__main__":
    main()

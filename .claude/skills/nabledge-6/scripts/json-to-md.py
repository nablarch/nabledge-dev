#!/usr/bin/env python3
"""
Convert JSON knowledge files to Markdown format.

Simple, straightforward conversion that preserves all JSON content in readable MD.

Usage:
    python json-to-md.py INPUT.json OUTPUT.md
"""

import sys
import json
from pathlib import Path


def json_value_to_md(value, indent_level=0):
    """
    Convert JSON value to Markdown text.

    Simple conversion rules:
    - strings: output as-is
    - lists: convert to markdown list
    - dicts: convert to key-value format
    - primitives: convert to string
    """
    indent = "  " * indent_level

    if isinstance(value, str):
        return value
    elif isinstance(value, list):
        if not value:
            return ""
        # Check if list contains simple values or complex objects
        if all(isinstance(item, (str, int, float, bool)) for item in value):
            return "\n".join(f"{indent}- {item}" for item in value)
        else:
            # List of objects - each gets its own section
            parts = []
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    parts.append(json_dict_to_md(item, indent_level))
                else:
                    parts.append(f"{indent}- {item}")
            return "\n\n".join(parts)
    elif isinstance(value, dict):
        return json_dict_to_md(value, indent_level)
    elif isinstance(value, bool):
        return "はい" if value else "いいえ"
    elif value is None:
        return ""
    else:
        return str(value)


def json_dict_to_md(data, indent_level=0):
    """Convert JSON dictionary to Markdown key-value format."""
    indent = "  " * indent_level
    lines = []

    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{indent}**{key}**:")
            lines.append(json_dict_to_md(value, indent_level + 1))
        elif isinstance(value, list):
            lines.append(f"{indent}**{key}**:")
            lines.append(json_value_to_md(value, indent_level + 1))
        else:
            lines.append(f"{indent}**{key}**: {value}")

    return "\n".join(lines)


def convert_json_to_md(json_path, md_path):
    """Convert JSON knowledge file to Markdown format."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    md_lines = []

    # Title
    if 'title' in data:
        md_lines.append(f"# {data['title']}")
        md_lines.append("")

    # ID
    if 'id' in data:
        md_lines.append(f"**ID**: {data['id']}")
        md_lines.append("")

    # Official doc URLs
    if 'official_doc_urls' in data:
        md_lines.append("## 公式ドキュメント")
        md_lines.append("")
        for url in data['official_doc_urls']:
            md_lines.append(f"- {url}")
        md_lines.append("")

    # Index
    if 'index' in data:
        md_lines.append("## インデックス")
        md_lines.append("")
        for entry in data['index']:
            hints = ", ".join(entry.get('hints', []))
            md_lines.append(f"- **{entry.get('id', '')}**: {hints}")
        md_lines.append("")

    # Sections
    if 'sections' in data:
        md_lines.append("## セクション")
        md_lines.append("")
        for section_id, section_data in data['sections'].items():
            md_lines.append(f"### {section_id}")
            md_lines.append("")
            md_lines.append(json_value_to_md(section_data))
            md_lines.append("")

    # Write MD file
    md_content = "\n".join(md_lines)
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"Converted {json_path} → {md_path}")


def main():
    if len(sys.argv) != 3:
        print("Usage: json-to-md.py INPUT.json OUTPUT.md", file=sys.stderr)
        sys.exit(1)

    json_path = sys.argv[1]
    md_path = sys.argv[2]

    if not Path(json_path).exists():
        print(f"Error: JSON file not found: {json_path}", file=sys.stderr)
        sys.exit(1)

    convert_json_to_md(json_path, md_path)
    sys.exit(0)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Convert knowledge JSON files to human-readable Markdown.

Preserves directory structure and converts JSON data to Markdown format
suitable for human review.

Exit codes:
  0: Success
  1: Error
"""

import sys
import json
from pathlib import Path
from typing import Any, Dict, List


def format_value(key: str, value: Any, indent: int = 0) -> str:
    """Format a value based on its type."""
    prefix = '  ' * indent

    # Code examples
    if key.endswith('_example'):
        lang = 'xml' if 'xml' in key else 'java' if 'java' in key else 'sql' if 'sql' in key else ''
        return f"\n{prefix}```{lang}\n{value}\n{prefix}```\n"

    # String
    if isinstance(value, str):
        return value

    # Array of strings
    if isinstance(value, list) and all(isinstance(v, str) for v in value):
        if len(value) == 0:
            return "なし"
        lines = [f"{prefix}- {v}" for v in value]
        return '\n' + '\n'.join(lines)

    # Array of objects (check if keys are uniform for table format)
    if isinstance(value, list) and all(isinstance(v, dict) for v in value):
        if len(value) == 0:
            return "なし"

        # Get all keys
        all_keys = set()
        for obj in value:
            all_keys.update(obj.keys())

        # If keys are uniform, use table format
        if len(all_keys) > 0:
            # Check if this looks like a property/setup table
            if 'name' in all_keys and 'description' in all_keys:
                return format_property_table(value, indent)
            # Otherwise use nested list
            return format_object_list(value, indent)

    # Flat object
    if isinstance(value, dict):
        # Check if all values are simple (string, bool, number)
        if all(isinstance(v, (str, bool, int, float, type(None))) for v in value.values()):
            lines = [f"{prefix}**{k}**: {v}" for k, v in value.items()]
            return '\n' + '\n'.join(lines)
        # Otherwise, nested object
        return format_nested_object(value, indent)

    # Boolean, number, None
    return str(value)


def format_property_table(props: List[Dict], indent: int = 0) -> str:
    """Format property list as Markdown table."""
    prefix = '  ' * indent

    # Determine columns
    all_keys = set()
    for prop in props:
        all_keys.update(prop.keys())

    # Common column order
    col_order = ['name', 'type', 'required', 'default', 'description']
    cols = [c for c in col_order if c in all_keys]
    # Add any remaining columns
    cols.extend([c for c in sorted(all_keys) if c not in cols])

    # Build table
    lines = [prefix]
    # Header
    header = '| ' + ' | '.join(cols) + ' |'
    lines.append(header)
    # Separator
    sep = '|' + '|'.join(['---' for _ in cols]) + '|'
    lines.append(sep)
    # Rows
    for prop in props:
        row = '| ' + ' | '.join([str(prop.get(c, '')) for c in cols]) + ' |'
        lines.append(row)

    return '\n' + '\n'.join(lines) + '\n'


def format_object_list(objs: List[Dict], indent: int = 0) -> str:
    """Format object list as nested bullet list."""
    prefix = '  ' * indent
    lines = []

    for i, obj in enumerate(objs, 1):
        lines.append(f"{prefix}{i}. **{obj.get('name', obj.get('pattern', obj.get('exception', f'Item {i}')))}**")
        for k, v in obj.items():
            if k in ['name', 'pattern', 'exception']:
                continue
            lines.append(f"{prefix}   - {k}: {v}")

    return '\n' + '\n'.join(lines)


def format_nested_object(obj: Dict, indent: int = 0) -> str:
    """Format nested object."""
    prefix = '  ' * indent
    lines = []

    for k, v in obj.items():
        if isinstance(v, dict):
            lines.append(f"{prefix}**{k}**:")
            lines.append(format_value(k, v, indent + 1))
        else:
            lines.append(f"{prefix}**{k}**: {format_value(k, v, indent)}")

    return '\n' + '\n'.join(lines)


def convert_section(section_id: str, section_content, indent: int = 0) -> str:
    """Convert a section to Markdown."""
    lines = []
    prefix = '  ' * indent

    # Handle list sections (like setup)
    if isinstance(section_content, list):
        return format_value(section_id, section_content, indent)

    # Handle dict sections
    if not isinstance(section_content, dict):
        return str(section_content)

    for key, value in section_content.items():
        # Skip if empty
        if value is None or value == [] or value == {}:
            continue

        # Format key as subheading or label
        if isinstance(value, dict) and len(value) > 3:
            lines.append(f"{prefix}### {key}\n")
            lines.append(format_value(key, value, indent))
        else:
            key_label = key.replace('_', ' ').title()
            lines.append(f"{prefix}**{key_label}**: {format_value(key, value, indent)}")
        lines.append("")

    return '\n'.join(lines)


def convert_json_to_md(json_path: Path, output_dir: Path, base_dir: Path):
    """Convert a single JSON file to Markdown."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Calculate output path (preserve directory structure)
    relative_path = json_path.relative_to(base_dir)
    md_path = output_dir / relative_path.with_suffix('.md')
    md_path.parent.mkdir(parents=True, exist_ok=True)

    # Build Markdown content
    lines = []

    # Title
    lines.append(f"# {data.get('title', 'Untitled')}\n")

    # Overview description
    overview = data.get('sections', {}).get('overview', {})
    if 'description' in overview:
        lines.append(overview['description'])
        lines.append("")

    # Purpose
    if 'purpose' in overview:
        lines.append(f"**目的**: {overview['purpose']}")
        lines.append("")

    # Other overview properties
    for key, value in overview.items():
        if key in ['description', 'purpose']:
            continue
        key_label = key.replace('_', ' ').title()
        lines.append(f"**{key_label}**: {format_value(key, value)}")
        lines.append("")

    # Official docs
    if 'official_doc_urls' in data:
        lines.append("**公式ドキュメント**:")
        for url in data['official_doc_urls']:
            lines.append(f"- [{url}]({url})")
        lines.append("")

    lines.append("---\n")

    # Other sections
    sections = data.get('sections', {})
    for section_id in sorted(sections.keys()):
        if section_id == 'overview':
            continue

        lines.append(f"## {section_id}\n")
        lines.append(convert_section(section_id, sections[section_id]))
        lines.append("")

    # Write to file
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"Converted: {json_path.name} -> {md_path.name}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python convert-knowledge-md.py INPUT_DIR [--output-dir DIR]")
        print()
        print("Convert knowledge JSON files to Markdown format.")
        print()
        print("Options:")
        print("  --output-dir DIR  Output directory (default: INPUT_DIR/../docs/)")
        sys.exit(1)

    input_dir = Path(sys.argv[1])
    output_dir = None

    if '--output-dir' in sys.argv:
        idx = sys.argv.index('--output-dir')
        if idx + 1 < len(sys.argv):
            output_dir = Path(sys.argv[idx + 1])

    if not output_dir:
        # Default: sibling docs/ directory
        output_dir = input_dir.parent / 'docs'

    if not input_dir.exists():
        print(f"ERROR: Input directory not found: {input_dir}")
        sys.exit(1)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all JSON files (exclude index.toon)
    json_files = [f for f in input_dir.rglob('*.json') if f.name != 'index.toon']

    if not json_files:
        print(f"No JSON files found in {input_dir}")
        sys.exit(0)

    print(f"Converting {len(json_files)} JSON files...")
    print(f"Output directory: {output_dir}")
    print()

    for json_file in sorted(json_files):
        try:
            convert_json_to_md(json_file, output_dir, input_dir)
        except Exception as e:
            print(f"ERROR converting {json_file}: {e}")

    print()
    print(f"Conversion complete. {len(json_files)} files processed.")
    sys.exit(0)


if __name__ == '__main__':
    main()

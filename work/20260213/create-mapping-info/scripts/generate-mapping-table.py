#!/usr/bin/env python3
"""
Generate Markdown table from mapping files.

Outputs:
- mapping-table-v6.md: Markdown table of all v6 mappings
- mapping-table-v5.md: Markdown table of all v5 mappings
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

def load_json(file_path: Path) -> Dict:
    """Load JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def escape_markdown(text: str) -> str:
    """Escape markdown special characters."""
    if not text:
        return ""
    return text.replace('|', '\\|')

def generate_mapping_table(mapping: Dict, version: str) -> str:
    """Generate markdown table for mapping."""
    mappings = mapping['mappings']

    # Sort by source_file
    mappings_sorted = sorted(mappings, key=lambda x: x['source_file'])

    lines = []
    lines.append(f"# Mapping Table - V{version}")
    lines.append("")
    lines.append(f"Total entries: {len(mappings_sorted)}")
    lines.append(f"In scope: {mapping['statistics']['in_scope']}")
    lines.append(f"Out of scope: {mapping['statistics']['out_of_scope']}")
    lines.append("")

    # Table header
    lines.append("| Source File | Title | In Scope | Categories | Reason for Exclusion | Target Files |")
    lines.append("|-------------|-------|----------|------------|----------------------|--------------|")

    # Table rows
    for entry in mappings_sorted:
        source_file = escape_markdown(entry['source_file'])
        title = escape_markdown(entry['title'][:50])  # Truncate long titles
        in_scope = "✓" if entry['in_scope'] else "✗"
        categories = escape_markdown(", ".join(entry['categories'])) if entry['categories'] else ""
        reason = escape_markdown(entry['reason_for_exclusion'] or "")
        targets = escape_markdown(", ".join(entry['target_files'])) if entry['target_files'] else ""

        lines.append(f"| {source_file} | {title} | {in_scope} | {categories} | {reason} | {targets} |")

    return "\n".join(lines)

def generate_summary_table(mapping: Dict, version: str) -> str:
    """Generate simplified summary table (source file + in_scope only)."""
    mappings = mapping['mappings']

    # Sort by source_file
    mappings_sorted = sorted(mappings, key=lambda x: x['source_file'])

    lines = []
    lines.append(f"# Mapping Summary - V{version}")
    lines.append("")
    lines.append(f"Total entries: {len(mappings_sorted)}")
    lines.append(f"In scope: {mapping['statistics']['in_scope']} (✓)")
    lines.append(f"Out of scope: {mapping['statistics']['out_of_scope']} (✗)")
    lines.append("")

    # Table header
    lines.append("| # | Source File | Status | Categories |")
    lines.append("|---|-------------|--------|------------|")

    # Table rows
    for idx, entry in enumerate(mappings_sorted, 1):
        source_file = entry['source_file']
        status = "✓" if entry['in_scope'] else "✗"
        categories = ", ".join(entry['categories'][:3]) if entry['categories'] else ""
        if len(entry['categories']) > 3:
            categories += f" (+{len(entry['categories']) - 3} more)"

        lines.append(f"| {idx} | {source_file} | {status} | {categories} |")

    return "\n".join(lines)

def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    work_dir = script_dir.parent

    # Process V6
    print("Generating V6 mapping tables...")
    mapping_v6_file = work_dir / 'mapping-v6.json'
    mapping_v6 = load_json(mapping_v6_file)

    # Full table
    table_v6 = generate_mapping_table(mapping_v6, '6')
    output_v6 = work_dir / 'mapping-table-v6.md'
    with open(output_v6, 'w', encoding='utf-8') as f:
        f.write(table_v6)
    print(f"Wrote {output_v6}")

    # Summary table
    summary_v6 = generate_summary_table(mapping_v6, '6')
    output_v6_summary = work_dir / 'mapping-summary-v6.md'
    with open(output_v6_summary, 'w', encoding='utf-8') as f:
        f.write(summary_v6)
    print(f"Wrote {output_v6_summary}")

    # Process V5
    print("\nGenerating V5 mapping tables...")
    mapping_v5_file = work_dir / 'mapping-v5.json'
    mapping_v5 = load_json(mapping_v5_file)

    # Full table
    table_v5 = generate_mapping_table(mapping_v5, '5')
    output_v5 = work_dir / 'mapping-table-v5.md'
    with open(output_v5, 'w', encoding='utf-8') as f:
        f.write(table_v5)
    print(f"Wrote {output_v5}")

    # Summary table
    summary_v5 = generate_summary_table(mapping_v5, '5')
    output_v5_summary = work_dir / 'mapping-summary-v5.md'
    with open(output_v5_summary, 'w', encoding='utf-8') as f:
        f.write(summary_v5)
    print(f"Wrote {output_v5_summary}")

    print("\nMapping tables generated!")
    print("  - mapping-table-vX.md: Full table with all columns")
    print("  - mapping-summary-vX.md: Summary table (file path + status only)")

if __name__ == '__main__':
    main()

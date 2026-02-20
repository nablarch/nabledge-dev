#!/usr/bin/env python3
"""
Generate verification checklist from mapping file.

Exit codes:
  0: Success
  1: Error
"""

import sys
import re
from pathlib import Path
from typing import List, Dict
from datetime import date


def parse_mapping_file(file_path: str) -> List[Dict]:
    """Parse mapping Markdown file."""
    rows = []

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    in_table = False
    for line in lines:
        if line.startswith('|') and 'Source Path' in line:
            in_table = True
            continue
        elif in_table and line.startswith('|---'):
            continue
        elif in_table and line.startswith('|'):
            cols = [c.strip() for c in line.split('|')[1:-1]]
            if len(cols) == 8:
                rows.append({
                    'source_path': cols[0],
                    'title': cols[1],
                    'title_ja': cols[2],
                    'official_url': cols[3],
                    'type': cols[4],
                    'category': cols[5],
                    'pp': cols[6],
                    'target_path': cols[7],
                })
        elif in_table and not line.startswith('|'):
            break

    return rows


def select_classification_checks(rows: List[Dict], sample_rate: int = 3) -> List[Dict]:
    """
    Select rows for classification checking.
    Includes:
    - Mandatory: needs_content rows (originally had low confidence)
    - Mandatory: PP != Category for processing-pattern
    - Mandatory: handlers/standalone/
    - Sampling: Every Nth row
    """
    checks = []

    for i, row in enumerate(rows):
        reason = None

        # Mandatory checks
        if '/standalone/' in row['source_path']:
            reason = 'standalone handler (needs content verification)'
        elif row['type'] == 'processing-pattern' and row['pp'] and row['pp'] != row['category']:
            reason = 'PP != Category for processing-pattern'
        elif i % sample_rate == 0:
            reason = 'sampling'

        if reason:
            checks.append({
                'row_num': i + 1,
                'source_path': row['source_path'],
                'type': row['type'],
                'category': row['category'],
                'pp': row['pp'],
                'reason': reason,
            })

    return checks


def select_target_path_checks(rows: List[Dict], sample_rate: int = 5) -> List[Dict]:
    """
    Select rows for target path checking.
    Includes:
    - Mandatory: component/handlers with subdirectories
    - Mandatory: index.rst files
    - Sampling: Every Nth row
    """
    checks = []

    for i, row in enumerate(rows):
        reason = None

        if 'component/handlers/' in row['target_path'] and row['target_path'].count('/') > 3:
            reason = 'subdirectory preservation'
        elif 'index' in row['source_path'].lower():
            reason = 'index.rst naming'
        elif i % sample_rate == 0:
            reason = 'sampling'

        if reason:
            checks.append({
                'row_num': i + 1,
                'source_path': row['source_path'],
                'target_path': row['target_path'],
                'reason': reason,
            })

    return checks


def generate_checklist(mapping_path: str, source_dir: str, output_path: str, sample_rate: int):
    """Generate verification checklist."""
    rows = parse_mapping_file(mapping_path)

    classification_checks = select_classification_checks(rows, sample_rate)
    target_path_checks = select_target_path_checks(rows, sample_rate)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# Verification Checklist: {Path(mapping_path).name}\n\n")
        f.write(f"**Generated**: {date.today().strftime('%Y-%m-%d')}\n")
        f.write(f"**Total Mapping Rows**: {len(rows)}\n")
        f.write(f"**Classification Checks**: {len(classification_checks)}\n")
        f.write(f"**Target Path Checks**: {len(target_path_checks)}\n\n")
        f.write("---\n\n")

        # Classification checks
        f.write("## Classification Verification\n\n")
        f.write("For each row, read the RST source file and verify:\n")
        f.write("1. Type matches the content scope\n")
        f.write("2. Category correctly categorizes the technical area\n")
        f.write("3. Processing Pattern is assigned appropriately\n\n")

        f.write("| # | Source Path | Type | Category | PP | Check Reason | Judgment |\n")
        f.write("|---|---|---|---|---|---|---|\n")

        for check in classification_checks:
            f.write(f"| {check['row_num']} | {check['source_path']} | {check['type']} | {check['category']} | {check['pp']} | {check['reason']} | |\n")

        f.write("\n**Instructions**:\n")
        f.write("- Read the first 50 lines of the RST file at `{source_dir}/{source_path}`\n")
        f.write("- Check if classification matches the content\n")
        f.write("- Mark ✓ if correct, ✗ if incorrect (note correct classification)\n\n")

        f.write("---\n\n")

        # Target path checks
        f.write("## Target Path Verification\n\n")
        f.write("For each row, verify:\n")
        f.write("1. Target path starts with Type\n")
        f.write("2. Filename correctly converts `_` to `-`\n")
        f.write("3. Extension changed from `.rst` to `.md`\n")
        f.write("4. Subdirectories preserved where appropriate\n\n")

        f.write("| # | Source Path | Target Path | Check Reason | Judgment |\n")
        f.write("|---|---|---|---|---|\n")

        for check in target_path_checks:
            f.write(f"| {check['row_num']} | {check['source_path']} | {check['target_path']} | {check['reason']} | |\n")

        f.write("\n**Instructions**:\n")
        f.write("- Verify path conversion rules are followed\n")
        f.write("- Mark ✓ if correct, ✗ if incorrect (note correct path)\n\n")

    print(f"Generated checklist: {output_path}", file=sys.stderr)
    print(f"  Classification checks: {len(classification_checks)}", file=sys.stderr)
    print(f"  Target path checks: {len(target_path_checks)}", file=sys.stderr)


def main():
    if len(sys.argv) < 2:
        print("Usage: generate-mapping-checklist.py MAPPING_FILE --source-dir DIR [--output PATH] [--sample-rate N]", file=sys.stderr)
        sys.exit(1)

    mapping_file = sys.argv[1]
    source_dir = None
    output_path = None
    sample_rate = 3

    if '--source-dir' in sys.argv:
        idx = sys.argv.index('--source-dir')
        if idx + 1 < len(sys.argv):
            source_dir = sys.argv[idx + 1]

    if '--output' in sys.argv:
        idx = sys.argv.index('--output')
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    if '--sample-rate' in sys.argv:
        idx = sys.argv.index('--sample-rate')
        if idx + 1 < len(sys.argv):
            sample_rate = int(sys.argv[idx + 1])

    if not source_dir:
        print("Error: --source-dir is required", file=sys.stderr)
        sys.exit(1)

    if not output_path:
        output_path = mapping_file.replace('.md', '.checklist.md')

    generate_checklist(mapping_file, source_dir, output_path, sample_rate)
    sys.exit(0)


if __name__ == '__main__':
    main()

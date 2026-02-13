#!/usr/bin/env python3
"""
Generate out-of-scope review reports.

Reads:
- mapping-vX.json: Complete mapping with categorization

Outputs:
- out-of-scope-vX.md: Markdown report of all out-of-scope files
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

def load_json(file_path: Path) -> Dict:
    """Load JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_out_of_scope_report(mapping: Dict, version: str) -> str:
    """Generate markdown report for out-of-scope files."""
    mappings = mapping['mappings']

    # Group by reason_for_exclusion
    by_reason = defaultdict(list)

    for entry in mappings:
        if not entry['in_scope']:
            reason = entry['reason_for_exclusion'] or 'Unknown reason'
            by_reason[reason].append(entry)

    # Generate markdown
    lines = []
    lines.append(f"# Out of Scope Files - V{version}")
    lines.append("")
    lines.append("This document lists all files excluded from scope with their reasons.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total out-of-scope files**: {len([m for m in mappings if not m['in_scope']])}")
    lines.append(f"- **Exclusion reasons**: {len(by_reason)}")
    lines.append("")

    # Table of contents
    lines.append("## Exclusion Reasons")
    lines.append("")
    for idx, (reason, files) in enumerate(sorted(by_reason.items()), 1):
        lines.append(f"{idx}. [{reason}](#{_anchor(reason)}) ({len(files)} files)")
    lines.append("")

    # Detailed sections
    for reason, files in sorted(by_reason.items()):
        lines.append(f"## {reason}")
        lines.append("")
        lines.append(f"**Total files**: {len(files)}")
        lines.append("")

        for entry in sorted(files, key=lambda x: x['source_file']):
            lines.append(f"### {entry['title']}")
            lines.append("")
            lines.append(f"- **File**: `{entry['source_file']}`")
            lines.append(f"- **Categories**: {', '.join(entry['categories']) if entry['categories'] else 'None'}")
            lines.append("")

    return "\n".join(lines)

def _anchor(text: str) -> str:
    """Convert text to markdown anchor."""
    import re
    anchor = text.lower()
    anchor = re.sub(r'[^\w\s-]', '', anchor)
    anchor = re.sub(r'[\s_-]+', '-', anchor)
    return anchor.strip('-')

def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    work_dir = script_dir.parent

    # Process V6
    print("Generating V6 out-of-scope report...")
    mapping_v6_file = work_dir / 'mapping-v6.json'
    mapping_v6 = load_json(mapping_v6_file)

    report_v6 = generate_out_of_scope_report(mapping_v6, '6')

    output_v6 = work_dir / 'out-of-scope-v6.md'
    with open(output_v6, 'w', encoding='utf-8') as f:
        f.write(report_v6)

    print(f"Wrote {output_v6}")

    out_of_scope_count_v6 = len([m for m in mapping_v6['mappings'] if not m['in_scope']])
    print(f"  {out_of_scope_count_v6} out-of-scope files")

    # Process V5
    print("\nGenerating V5 out-of-scope report...")
    mapping_v5_file = work_dir / 'mapping-v5.json'
    mapping_v5 = load_json(mapping_v5_file)

    report_v5 = generate_out_of_scope_report(mapping_v5, '5')

    output_v5 = work_dir / 'out-of-scope-v5.md'
    with open(output_v5, 'w', encoding='utf-8') as f:
        f.write(report_v5)

    print(f"Wrote {output_v5}")

    out_of_scope_count_v5 = len([m for m in mapping_v5['mappings'] if not m['in_scope']])
    print(f"  {out_of_scope_count_v5} out-of-scope files")

    print("\nOut-of-scope reports generated!")
    print("\nPlease review these files to verify they are truly out of scope.")
    print("Pay special attention to:")
    print("  - Nablarch Batch (On-demand) files incorrectly marked as out-of-scope")
    print("  - RESTful Web Services files incorrectly marked as out-of-scope")
    print("  - HTTP Messaging files incorrectly marked as out-of-scope")
    print("  - Generic handlers/libraries incorrectly marked as out-of-scope")

if __name__ == '__main__':
    main()

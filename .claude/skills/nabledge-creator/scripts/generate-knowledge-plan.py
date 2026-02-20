#!/usr/bin/env python3
"""
Generate knowledge-file-plan.md from mapping file.

This script analyzes the mapping file and creates a knowledge file plan
that groups source documents according to the integration patterns specified
in the design document.

Integration patterns:
- Processing patterns: N:1 (same Category ID merged into one JSON)
- Handlers: 1:1 (one RST to one JSON)
- Libraries: 1:1 or N:1 (sub-features can be merged)
- Adapters: 1:1
- Tools: N:1 (group by tool category)
- Checks: 1:1
- About: Special handling
"""

import sys
import re
from pathlib import Path
from typing import Dict, List
from collections import defaultdict


def parse_mapping_file(file_path: str) -> List[Dict]:
    """Parse mapping file into list of rows."""
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


def group_by_knowledge_file(rows: List[Dict]) -> Dict[str, List[Dict]]:
    """Group rows into knowledge files according to integration patterns."""
    knowledge_files = defaultdict(list)

    for row in rows:
        type_val = row['type']
        category = row['category']
        pp = row['pp']

        # Skip setup, guide, and about for now (special handling)
        if type_val in ['setup', 'guide', 'about', 'check']:
            continue

        # Processing patterns: N:1 by PP
        if type_val == 'processing-pattern':
            if pp:
                # Group by processing pattern
                kf_path = f"features/processing/{pp}.json"
                knowledge_files[kf_path].append(row)

        # Handlers: 1:1 for each handler file
        elif category == 'handlers':
            # Extract handler name from source path
            # e.g., handlers/common/database_connection_management_handler.rst
            # -> database-connection-management-handler
            source = row['source_path']
            handler_name = Path(source).stem

            # Determine subdirectory from path
            if '/handlers/common/' in source:
                subdir = 'common'
            elif '/handlers/batch/' in source:
                subdir = 'batch'
            elif '/handlers/standalone/' in source:
                subdir = 'batch'
            elif '/handlers/web/' in source:
                subdir = 'web'
            elif '/handlers/rest/' in source:
                subdir = 'rest'
            elif '/handlers/http_messaging/' in source:
                subdir = 'http-messaging'
            elif '/handlers/mom_messaging/' in source:
                subdir = 'mom-messaging'
            else:
                subdir = 'other'

            kf_path = f"features/handlers/{subdir}/{handler_name}.json"
            knowledge_files[kf_path].append(row)

        # Adapters: 1:1
        elif category == 'adapters':
            adapter_name = Path(row['source_path']).stem
            kf_path = f"features/adapters/{adapter_name}.json"
            knowledge_files[kf_path].append(row)

        # Libraries: 1:1 (can be N:1 for sub-features, but default to 1:1)
        elif category == 'libraries':
            lib_name = Path(row['source_path']).stem
            kf_path = f"features/libraries/{lib_name}.json"
            knowledge_files[kf_path].append(row)

        # Testing framework: N:1 by major component
        elif category == 'testing-framework':
            source = row['source_path']
            # Group NTF files by major component
            if 'testing/guide/' in source or 'testing/index' in source:
                kf_path = "features/tools/nablarch-testing-framework.json"
            else:
                # Create separate files for each NTF component
                component = Path(source).stem
                kf_path = f"features/tools/ntf-{component}.json"
            knowledge_files[kf_path].append(row)

        # Toolbox: N:1 by tool
        elif category == 'toolbox':
            source = row['source_path']
            if 'unpublished_api_checker' in source:
                kf_path = "features/tools/unpublished-api-checker.json"
            elif 'log_verifier' in source:
                kf_path = "features/tools/log-verifier.json"
            else:
                tool_name = Path(source).stem
                kf_path = f"features/tools/{tool_name}.json"
            knowledge_files[kf_path].append(row)

    return knowledge_files


def extract_url_from_markdown(url_cell: str) -> str:
    """Extract URL from markdown link format."""
    # Format: [🔗](https://...)
    match = re.search(r'\(https?://[^)]+\)', url_cell)
    if match:
        return match.group(0)[1:-1]  # Remove parentheses
    return ""


def generate_plan(knowledge_files: Dict[str, List[Dict]], output_path: str):
    """Generate knowledge-file-plan.md."""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Knowledge File Plan\n\n")
        f.write("生成対象の知識ファイル一覧とソースドキュメントの対応。\n\n")
        f.write("## 統合パターン\n\n")
        f.write("| 知識ファイルの種類 | マッピング行との関係 |\n")
        f.write("|---|---|\n")
        f.write("| 処理方式 | N:1（同じCategory IDのprocessing-pattern行を統合） |\n")
        f.write("| ハンドラ | 1:1 |\n")
        f.write("| ライブラリ | 1:1 基本。サブ機能別ファイルならN:1 |\n")
        f.write("| ツール | N:1 |\n")
        f.write("| アダプタ | 1:1 |\n")
        f.write("| チェック | 1:1 |\n")
        f.write("| リリースノート | 特殊 |\n")
        f.write("| 概要 | 特殊 |\n\n")

        f.write("## 知識ファイル一覧\n\n")

        # Sort by path
        for kf_path in sorted(knowledge_files.keys()):
            rows = knowledge_files[kf_path]

            # Extract information from first row (for title and tags)
            first_row = rows[0]
            title_ja = first_row['title_ja']
            category = first_row['category']
            pp = first_row['pp']

            # Determine tags
            tags = []
            if pp:
                tags.append(pp)
            if category:
                tags.append(category)

            f.write(f"### {kf_path}\n\n")
            f.write(f"**title**: {title_ja}\n\n")
            f.write(f"**tags**: {', '.join(tags) if tags else 'なし'}\n\n")
            f.write(f"**sources**:\n\n")

            for row in rows:
                source_path = row['source_path']
                title = row['title']
                url = extract_url_from_markdown(row['official_url'])
                f.write(f"- `{source_path}`\n")
                f.write(f"  - Title: {title}\n")
                f.write(f"  - URL: {url}\n")

            f.write("\n")

    print(f"Knowledge file plan generated: {output_path}")
    print(f"Total knowledge files: {len(knowledge_files)}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate-knowledge-plan.py MAPPING_FILE [--output OUTPUT_FILE]")
        print()
        print("Generate knowledge-file-plan.md from mapping file.")
        sys.exit(1)

    mapping_file = sys.argv[1]
    output_file = 'references/knowledge-file-plan.md'

    if '--output' in sys.argv:
        output_idx = sys.argv.index('--output')
        if output_idx + 1 < len(sys.argv):
            output_file = sys.argv[output_idx + 1]

    if not Path(mapping_file).exists():
        print(f"ERROR: Mapping file not found: {mapping_file}")
        sys.exit(1)

    # Parse mapping file
    print(f"Parsing mapping file: {mapping_file}")
    rows = parse_mapping_file(mapping_file)
    print(f"Total mapping rows: {len(rows)}")

    # Group by knowledge file
    print("Grouping by knowledge file...")
    knowledge_files = group_by_knowledge_file(rows)

    # Generate plan
    generate_plan(knowledge_files, output_file)

    return 0


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""
Verify that Title (ja) in mapping file matches actual file titles at Official URLs.

This script:
1. Reads mapping-v6.md
2. For each row, extracts title from the Japanese source file
3. Compares with Title (ja) column
4. Reports any mismatches

Usage:
    python scripts/mapping/verify-title-match.py
"""

import re
import sys
from pathlib import Path
from typing import Optional, List, Dict

# File paths
REPO_ROOT = Path(__file__).parent.parent.parent
MAPPING_MD = REPO_ROOT / "doc/mapping/mapping-v6.md"
NABLARCH_DOC_JA = REPO_ROOT / ".lw/nab-official/v6/nablarch-document/ja"
NABLARCH_GUIDE_BASE = REPO_ROOT / ".lw/nab-official/v6/nablarch-system-development-guide"

def extract_rst_title(file_path: Path) -> Optional[str]:
    """Extract title from rst file header."""
    try:
        if not file_path.exists():
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for i in range(min(20, len(lines))):
            line = lines[i].strip()

            if line.startswith('..'):
                continue
            if not line:
                continue

            if i > 0:
                prev = lines[i-1].strip()
                if prev and all(c in '=-' for c in prev) and len(prev) >= len(line) * 0.8:
                    return line

            if i < len(lines) - 1:
                next_line = lines[i+1].strip()
                if next_line and all(c in '=-' for c in next_line) and len(next_line) >= len(line) * 0.8:
                    return line

        return None
    except Exception:
        return None

def extract_md_title(file_path: Path) -> Optional[str]:
    """Extract title from markdown file (first # heading)."""
    try:
        if not file_path.exists():
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('# '):
                    return line[2:].strip()

        return None
    except Exception:
        return None

def extract_url_from_markdown(md_link: str) -> Optional[str]:
    """Extract URL from Markdown link format [🔗](url)."""
    import re
    match = re.search(r'\[.*?\]\((https://.*?)\)', md_link)
    if match:
        return match.group(1)
    return None

def get_file_path_from_url(official_url: str, source_path: str) -> Optional[Path]:
    """Get file path from Official URL (for verification)."""
    # Extract URL from markdown link
    url = extract_url_from_markdown(official_url)
    if url is None:
        return None

    if 'nablarch-system-development-guide' in url:
        # Extract path from GitHub URL
        # Format: https://github.com/Fintan-contents/nablarch-system-development-guide/blob/main/{path}
        if '/blob/main/' in url:
            path_part = url.split('/blob/main/', 1)[1]
            return NABLARCH_GUIDE_BASE / path_part
    elif 'nablarch.github.io' in url:
        # Extract path from docs URL
        # Format: https://nablarch.github.io/docs/6u3/doc/{path}.html
        if '/doc/' in url:
            html_path = url.split('/doc/', 1)[1]
            # Convert .html back to .rst (or .md)
            if source_path.endswith('.md'):
                rst_path = html_path.replace('.html', '.md')
            else:
                rst_path = html_path.replace('.html', '.rst')

            # Map to Japanese path
            return get_ja_file_path_from_source(rst_path)

    return None

def get_ja_file_path_from_source(source_path: str) -> Optional[Path]:
    """Get Japanese file path from source path."""
    if source_path.startswith('en/Nablarch-system-development-guide/'):
        # nablarch-system-development-guide
        ja_path = source_path.replace(
            'en/Nablarch-system-development-guide/',
            'Nablarchシステム開発ガイド/'
        )

        # Map English filenames to Japanese
        filename_mapping = {
            'Asynchronous_operation_in_Nablarch.md': 'Nablarchでの非同期処理.md',
            'Nablarch_anti-pattern.md': 'Nablarchアンチパターン.md',
            'Nablarch_batch_processing_pattern.md': 'Nablarchバッチ処理パターン.md',
        }

        for en_name, ja_name in filename_mapping.items():
            if ja_path.endswith(en_name):
                ja_path = ja_path.replace(en_name, ja_name)
                break

        return NABLARCH_GUIDE_BASE / ja_path
    elif source_path.startswith('Sample_Project/'):
        # Sample_Project is in nablarch-system-development-guide
        return NABLARCH_GUIDE_BASE / source_path
    else:
        # nablarch-document
        ja_source_path = source_path

        # Handle filename mapping for renamed files
        nablarch_doc_filename_mapping = {
            'duplicate_form_submission.rst': 'double_transmission.rst',
        }

        for en_name, ja_name in nablarch_doc_filename_mapping.items():
            if source_path.endswith(en_name):
                ja_source_path = source_path.replace(en_name, ja_name)
                break

        return NABLARCH_DOC_JA / ja_source_path

def extract_title_from_url(official_url: str, source_path: str) -> Optional[str]:
    """Extract Japanese title from file pointed by Official URL."""
    file_path = get_file_path_from_url(official_url, source_path)

    if file_path is None or not file_path.exists():
        return None

    # Skip non-text files (Excel, images, etc.)
    if source_path.endswith(('.xlsx', '.xls', '.png', '.jpg', '.gif', '.svg')):
        return None

    if source_path.endswith('.md'):
        return extract_md_title(file_path)
    else:
        return extract_rst_title(file_path)

def parse_mapping_table(file_path: Path) -> List[Dict[str, str]]:
    """Parse mapping table."""
    rows = []

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    in_table = False

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if line.startswith('| Source Path |'):
            in_table = True
            continue

        if in_table and line.startswith('|---'):
            continue

        if in_table and line.startswith('|'):
            cells = [cell.strip() for cell in line.split('|')[1:-1]]

            if len(cells) >= 8:
                rows.append({
                    'source_path': cells[0],
                    'title': cells[1],
                    'title_ja': cells[2],
                    'official_url': cells[3],
                })

    return rows

def main():
    """Main execution"""
    print(f"📖 Reading {MAPPING_MD}")
    rows = parse_mapping_table(MAPPING_MD)
    print(f"✅ Parsed {len(rows)} rows")
    print()

    print("=" * 70)
    print("TITLE VERIFICATION REPORT")
    print("=" * 70)
    print()

    mismatches = []
    missing_files = []
    checked = 0

    for i, row in enumerate(rows, 1):
        source_path = row['source_path']
        title_ja_in_table = row['title_ja']
        official_url = row['official_url']

        # Extract title from actual file pointed by Official URL
        actual_title = extract_title_from_url(official_url, source_path)

        if actual_title is None:
            file_path = get_file_path_from_url(official_url, source_path)
            if file_path and not file_path.exists():
                missing_files.append({
                    'row': i,
                    'source_path': source_path,
                    'file_path': str(file_path),
                })
            continue

        checked += 1

        # Compare
        if actual_title != title_ja_in_table:
            mismatches.append({
                'row': i,
                'source_path': source_path,
                'table_title': title_ja_in_table,
                'actual_title': actual_title,
            })

    # Report
    print(f"📊 Verification Results")
    print(f"   Total rows: {len(rows)}")
    print(f"   Checked: {checked}")
    print(f"   Missing files: {len(missing_files)}")
    print(f"   Mismatches: {len(mismatches)}")
    print()

    if missing_files:
        print("⚠️  Missing Files:")
        for item in missing_files[:10]:
            print(f"   Row {item['row']}: {item['source_path']}")
            print(f"      Expected: {item['file_path']}")
        if len(missing_files) > 10:
            print(f"   ... and {len(missing_files) - 10} more")
        print()

    if mismatches:
        print("❌ Title Mismatches:")
        for item in mismatches[:10]:
            print(f"   Row {item['row']}: {item['source_path']}")
            print(f"      Table:  {item['table_title']}")
            print(f"      Actual: {item['actual_title']}")
        if len(mismatches) > 10:
            print(f"   ... and {len(mismatches) - 10} more")
        print()

    print("=" * 70)

    if mismatches or missing_files:
        print("❌ VERIFICATION FAILED")
        return 1
    else:
        print("✅ VERIFICATION PASSED: All titles match")
        return 0

if __name__ == '__main__':
    sys.exit(main())

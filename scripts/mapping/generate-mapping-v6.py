#!/usr/bin/env python3
"""
Generate mapping-v6.md from all-files-mapping-v6.md following updated design.

This script:
1. Parses existing mapping table
2. Extracts titles from rst/md files (English and Japanese)
3. Generates Official URLs with Markdown link format
4. Assigns Processing Pattern based on rules
5. Fixes Target Path subdirectory structure
6. Outputs new mapping table

Usage:
    python scripts/generate-mapping-v6.py [--test]

    --test: Output to mapping-v6.md.test instead of mapping-v6.md
"""

import re
import sys
from pathlib import Path
from typing import Optional, Tuple
import argparse

# Base directories
REPO_ROOT = Path(__file__).parent.parent.parent
NABLARCH_DOC_EN = REPO_ROOT / ".lw/nab-official/v6/nablarch-document/en"
NABLARCH_DOC_JA = REPO_ROOT / ".lw/nab-official/v6/nablarch-document/ja"
NABLARCH_GUIDE_BASE = REPO_ROOT / ".lw/nab-official/v6/nablarch-system-development-guide"

# Processing patterns
PROCESSING_PATTERNS = [
    "nablarch-batch",
    "jakarta-batch",
    "restful-web-service",
    "http-messaging",
    "web-application",
    "mom-messaging",
    "db-messaging",
]

# Logging
warnings = []
errors = []

def log_warning(msg: str):
    """Log warning message"""
    warnings.append(msg)
    print(f"⚠️  {msg}", file=sys.stderr)

def log_error(msg: str):
    """Log error message"""
    errors.append(msg)
    print(f"❌ {msg}", file=sys.stderr)

def extract_rst_title(file_path: Path) -> Optional[str]:
    """
    Extract title from rst file header.

    Expected format:
    ==================================================
    Title Text
    ==================================================

    or:
    Title Text
    ----------
    """
    try:
        if not file_path.exists():
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Look for title in first 20 lines (skip rst directives)
        for i in range(min(20, len(lines))):
            line = lines[i].strip()

            # Skip rst directives (lines starting with ..)
            if line.startswith('..'):
                continue

            # Skip empty lines
            if not line:
                continue

            # Check if next line or previous line is === or ---
            if i > 0:
                prev = lines[i-1].strip()
                if prev and all(c in '=-' for c in prev) and len(prev) >= len(line) * 0.8:
                    # Title is current line (underlined by previous line)
                    return line

            if i < len(lines) - 1:
                next_line = lines[i+1].strip()
                if next_line and all(c in '=-' for c in next_line) and len(next_line) >= len(line) * 0.8:
                    # Title is current line (underlined by next line)
                    return line

        return None
    except Exception as e:
        log_error(f"Failed to read {file_path}: {e}")
        return None

def extract_md_title(file_path: Path) -> Optional[str]:
    """Extract title from markdown file (first # heading)"""
    try:
        if not file_path.exists():
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('# '):
                    return line[2:].strip()

        return None
    except Exception as e:
        log_error(f"Failed to read {file_path}: {e}")
        return None

def extract_title(source_path: str, lang: str = 'en') -> Tuple[Optional[str], str]:
    """
    Extract title from source file.

    Args:
        source_path: Relative path from base directory
        lang: 'en' or 'ja'

    Returns:
        (title, status) where status is 'ok', 'missing_file', or 'parse_failed'
    """
    # Determine file type and base directory
    if source_path.startswith('en/Nablarch-system-development-guide/'):
        # nablarch-system-development-guide
        if lang == 'ja':
            # Replace en/ with Japanese path and map English filenames to Japanese
            ja_path = source_path.replace(
                'en/Nablarch-system-development-guide/',
                'Nablarchシステム開発ガイド/'
            )

            # Map English filenames to Japanese filenames
            filename_mapping = {
                'Asynchronous_operation_in_Nablarch.md': 'Nablarchでの非同期処理.md',
                'Nablarch_anti-pattern.md': 'Nablarchアンチパターン.md',
                'Nablarch_batch_processing_pattern.md': 'Nablarchバッチ処理パターン.md',
            }

            for en_name, ja_name in filename_mapping.items():
                if ja_path.endswith(en_name):
                    ja_path = ja_path.replace(en_name, ja_name)
                    break

            file_path = NABLARCH_GUIDE_BASE / ja_path
        else:
            file_path = NABLARCH_GUIDE_BASE / source_path

        title = extract_md_title(file_path)
    else:
        # nablarch-document
        if lang == 'ja':
            # Map English filenames to Japanese filenames (for renamed files in v6)
            ja_source_path = source_path
            nablarch_doc_filename_mapping = {
                'duplicate_form_submission.rst': 'double_transmission.rst',
            }

            for en_name, ja_name in nablarch_doc_filename_mapping.items():
                if source_path.endswith(en_name):
                    ja_source_path = source_path.replace(en_name, ja_name)
                    break

            # Check if ja version exists
            ja_file = NABLARCH_DOC_JA / ja_source_path
            if not ja_file.exists():
                return None, 'missing_file'
            file_path = ja_file
        else:
            file_path = NABLARCH_DOC_EN / source_path

        if source_path.endswith('.md'):
            title = extract_md_title(file_path)
        else:
            title = extract_rst_title(file_path)

    if title is None:
        if not file_path.exists():
            return None, 'missing_file'
        return None, 'parse_failed'

    return title, 'ok'

def generate_official_url(source_path: str) -> str:
    """Generate official URL with Markdown link format (Japanese version)"""
    if source_path.startswith('en/Nablarch-system-development-guide/'):
        # nablarch-system-development-guide
        # Convert to Japanese directory and filename
        ja_path = source_path.replace(
            'en/Nablarch-system-development-guide/',
            'Nablarchシステム開発ガイド/'
        )

        # Map English filenames to Japanese
        filename_map = {
            'Asynchronous_operation_in_Nablarch.md': 'Nablarchでの非同期処理.md',
            'Nablarch_anti-pattern.md': 'Nablarchアンチパターン.md',
            'Nablarch_batch_processing_pattern.md': 'Nablarchバッチ処理パターン.md'
        }

        for en_name, ja_name in filename_map.items():
            if en_name in ja_path:
                ja_path = ja_path.replace(en_name, ja_name)
                break

        url = f"https://github.com/Fintan-contents/nablarch-system-development-guide/blob/main/{ja_path}"
    else:
        # nablarch-document
        # Change .rst to .html, keep path
        html_path = source_path.replace('.rst', '.html').replace('.md', '.html')
        url = f"https://nablarch.github.io/docs/6u3/doc/{html_path}"

    return f"[🔗]({url})"

def assign_processing_pattern(source_path: str, type_: str, category: str, title: str = '') -> str:
    """
    Assign processing pattern based on rules.

    Returns processing pattern ID or empty string for generic files.
    """
    # Rule 1: Type = processing-pattern → use category
    if type_ == 'processing-pattern':
        return category

    lower_path = source_path.lower()
    lower_title = title.lower()

    # Rule 2: Component categories - check path
    if category in ['handlers', 'libraries', 'adapters']:
        # Check subdirectory patterns
        if '/batch/' in source_path or source_path.endswith('batch.rst'):
            return 'nablarch-batch'
        if '/jsr352/' in source_path:
            return 'jakarta-batch'
        if '/standalone/' in source_path:
            # Standalone handlers are used by nablarch-batch
            # Based on nablarch-batch architecture.rst: data_read_handler, multi_thread_execution_handler,
            # retry_handler, process_stop_handler, duplicate_process_check_handler, etc.
            return 'nablarch-batch'
        if '/web/' in source_path and '/web_interceptor/' not in source_path:
            return 'web-application'
        if '/web_interceptor/' in source_path:
            # Web interceptors are used by web-application
            # Based on web/getting_started usage: InjectForm, OnError, OnDoubleSubmission, UseToken
            return 'web-application'
        if '/rest/' in source_path or '/jaxrs/' in source_path:
            return 'restful-web-service'
        if '/http_messaging/' in source_path:
            return 'http-messaging'
        if '/mom_messaging/' in source_path:
            return 'mom-messaging'
        if '/messaging/' in source_path:
            # Could be mom or db, need more context
            if '/mom/' in source_path:
                return 'mom-messaging'
            if '/db/' in source_path:
                return 'db-messaging'
            # Ambiguous
            log_warning(f"Ambiguous messaging pattern for: {source_path}")
            return ''
        if '/common/' in source_path:
            return ''  # Generic (shared across all patterns)

    # Rule 3: Development tools - check filename and title
    if category in ['testing-framework', 'toolbox']:
        # Check for batch patterns
        if 'batch' in lower_path or 'batch' in lower_title:
            if 'jsr352' in lower_path or 'jbatch' in lower_path or 'jakarta batch' in lower_title:
                return 'jakarta-batch'
            return 'nablarch-batch'
        # Check for REST patterns
        if 'rest' in lower_path or 'jaxrs' in lower_path or 'restful' in lower_title:
            return 'restful-web-service'
        # Check for Web patterns (but not webservice)
        if ('web' in lower_path or 'web' in lower_title) and 'webservice' not in lower_path and 'service' not in lower_title:
            return 'web-application'

    # Rule 4: Setup categories - check filename and title
    if category in ['blank-project', 'configuration', 'setting-guide', 'cloud-native']:
        # Nablarch Batch patterns
        if any(pattern in lower_path for pattern in ['nablarchbatch', 'setup_nablarchbatch', 'containerbatch']) \
           or 'nablarch batch' in lower_title or 'nablarchバッチ' in title:
            return 'nablarch-batch'

        # Jakarta Batch patterns
        if 'jbatch' in lower_path or 'setup_jbatch' in lower_path or 'jakarta batch' in lower_title:
            return 'jakarta-batch'

        # RESTful Web Service patterns
        if 'webservice' in lower_path or 'setup_webservice' in lower_path or 'setup_containerwebservice' in lower_path \
           or 'restful' in lower_title or 'restfulウェブサービス' in title:
            return 'restful-web-service'

        # Web Application patterns (but not webservice)
        if ('web' in lower_path or 'containerweb' in lower_path) and 'webservice' not in lower_path and 'service' not in lower_title \
           or ('web project' in lower_title or 'ウェブプロジェクト' in title):
            return 'web-application'

    # Default: empty (generic/shared)
    return ''

def fix_target_path(source_path: str, type_: str, category: str, old_target: str) -> str:
    """
    Fix target path to follow subdirectory rules.

    Component categories: Preserve subdirectories
    Other types: Flat structure (use old_target)
    """
    if category not in ['handlers', 'libraries', 'adapters']:
        # Non-component: use existing target path
        return old_target

    # Component: Preserve subdirectories
    # Extract source subdirectories
    parts = source_path.split('/')

    # Find category in path
    category_mapping = {
        'handlers': 'handlers',
        'libraries': 'libraries',
        'adapters': 'adaptors',  # Note: source uses 'adaptors'
    }

    source_category = category_mapping.get(category, category)

    try:
        # Find index of category directory in path
        category_idx = None
        for i, part in enumerate(parts):
            if source_category in part:
                category_idx = i
                break

        if category_idx is None:
            log_warning(f"Category '{source_category}' not found in path: {source_path}")
            return old_target

        # Extract subdirectories between category and filename
        subdirs = parts[category_idx + 1:-1]  # Exclude category and filename

        # Exclude 'images' directories
        subdirs = [d for d in subdirs if d != 'images']

        # Get filename from source
        source_filename = parts[-1]
        # Convert to target filename: .rst → .md, underscores → hyphens
        target_filename = source_filename.replace('.rst', '.md').replace('.md', '.md')
        target_filename = target_filename.replace('_', '-')

        # If filename is index, use more descriptive name
        if target_filename == 'index.md':
            # Use parent directory name or generic name
            if subdirs:
                target_filename = f"{subdirs[-1]}.md"
            else:
                target_filename = 'overview.md'

        # Construct target path
        path_parts = [type_, category] + subdirs + [target_filename]
        return '/'.join(path_parts)

    except Exception as e:
        log_error(f"Failed to fix target path for {source_path}: {e}")
        return old_target

def parse_source_path_link(text: str) -> Optional[str]:
    """Extract source path from Markdown link [path](url)"""
    match = re.match(r'\[(.*?)\]\(.*?\)', text)
    if match:
        return match.group(1)
    return text  # If not a link, return as-is

def parse_existing_mapping(input_file: Path) -> list:
    """Parse existing all-files-mapping-v6.md"""
    rows = []

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find table start
    in_table = False
    header_found = False

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if line.startswith('| Source Path |'):
            in_table = True
            header_found = True
            continue

        if in_table and line.startswith('|---'):
            continue

        if in_table and line.startswith('|'):
            # Parse table row
            cells = [cell.strip() for cell in line.split('|')[1:-1]]  # Remove empty first/last

            if len(cells) >= 5:
                source_path_raw = cells[0]
                type_ = cells[1]
                category = cells[2]
                # Skip source_path_pattern (cells[3])
                target_path = cells[4]

                # Extract source path from link
                source_path = parse_source_path_link(source_path_raw)

                # Skip n/a rows
                if category == 'n/a':
                    continue

                rows.append({
                    'source_path': source_path,
                    'type': type_,
                    'category': category,
                    'target_path': target_path,
                })

    return rows

def generate_mapping_table(input_file: Path, output_file: Path):
    """Main function to generate new mapping table"""
    print(f"📖 Reading {input_file}")
    rows = parse_existing_mapping(input_file)
    print(f"✅ Parsed {len(rows)} rows")

    print("\n🔄 Processing rows...")
    output_rows = []

    for i, row in enumerate(rows, 1):
        source_path = row['source_path']
        type_ = row['type']
        category = row['category']
        old_target = row['target_path']

        if i % 50 == 0:
            print(f"  Processed {i}/{len(rows)} rows...")

        # Extract titles
        title_en, status_en = extract_title(source_path, 'en')
        if status_en != 'ok':
            log_warning(f"Title (en) {status_en} for: {source_path}")
            # Generate title from filename
            filename = source_path.split('/')[-1]
            if filename.endswith('.xlsx'):
                # For Excel files, use filename as-is (may contain Japanese)
                title_en = filename.replace('.xlsx', '')
            else:
                title_en = filename.replace('.rst', '').replace('.md', '').replace('_', ' ').title()

        title_ja, status_ja = extract_title(source_path, 'ja')
        if status_ja == 'missing_file':
            # Special cases
            if source_path.endswith('.xlsx'):
                # For Excel files with Japanese names, extract from filename
                filename = source_path.split('/')[-1]
                if 'セキュリティ対応表' in filename:
                    title_ja = 'Nablarchセキュリティ対応表'
                else:
                    title_ja = filename.replace('.xlsx', '')
            elif 'duplicate_form_submission' in source_path:
                # Known English-only file - leave empty
                title_ja = ''
            else:
                log_warning(f"Title (ja) missing (no ja/ file) for: {source_path}")
                title_ja = ''
        elif status_ja == 'parse_failed':
            log_warning(f"Title (ja) parse failed for: {source_path}")
            title_ja = ''

        # Generate official URL
        official_url = generate_official_url(source_path)

        # Assign processing pattern (use title for better detection)
        title_for_pattern = title_ja if title_ja else title_en if title_en else ''
        processing_pattern = assign_processing_pattern(source_path, type_, category, title_for_pattern)

        # Fix target path
        target_path = fix_target_path(source_path, type_, category, old_target)

        output_rows.append({
            'source_path': source_path,
            'title': title_en or '',
            'title_ja': title_ja or '',
            'official_url': official_url,
            'type': type_,
            'category': category,
            'processing_pattern': processing_pattern,
            'target_path': target_path,
        })

    print(f"✅ Processed all {len(output_rows)} rows")

    # Write output
    print(f"\n📝 Writing to {output_file}")
    write_output(output_rows, output_file)
    print(f"✅ Wrote {output_file}")

    # Print summary
    print(f"\n{'='*60}")
    print("📊 SUMMARY")
    print(f"{'='*60}")
    print(f"Total rows: {len(output_rows)}")
    print(f"Warnings: {len(warnings)}")
    print(f"Errors: {len(errors)}")

    if warnings:
        print(f"\n⚠️  {len(warnings)} warnings (see stderr for details)")
    if errors:
        print(f"\n❌ {len(errors)} errors (see stderr for details)")

    return len(errors) == 0

def write_output(rows: list, output_file: Path):
    """Write new mapping table"""
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write("# Nablarch v6 Documentation Mapping\n\n")
        f.write(f"**Generated**: 2026-02-19\n")
        f.write(f"**Total Files**: {len(rows)}\n\n")
        f.write("This table maps Nablarch v6 documentation files to nabledge-6 knowledge files.\n\n")

        # Write table header
        f.write("| Source Path | Title | Title (ja) | Official URL | Type | Category ID | Processing Pattern | Target Path |\n")
        f.write("|-------------|-------|------------|--------------|------|-------------|-------------------|-------------|\n")

        # Write rows
        for row in rows:
            f.write(f"| {row['source_path']} ")
            f.write(f"| {row['title']} ")
            f.write(f"| {row['title_ja']} ")
            f.write(f"| {row['official_url']} ")
            f.write(f"| {row['type']} ")
            f.write(f"| {row['category']} ")
            f.write(f"| {row['processing_pattern']} ")
            f.write(f"| {row['target_path']} |\n")

def main():
    parser = argparse.ArgumentParser(description='Generate mapping-v6.md from all-files-mapping-v6.md')
    parser.add_argument('--test', action='store_true', help='Output to .test file instead of actual file')
    args = parser.parse_args()

    input_file = REPO_ROOT / "doc/mapping/all-files-mapping-v6.md"

    if args.test:
        output_file = REPO_ROOT / "doc/mapping/mapping-v6.md.test"
        print("🧪 TEST MODE: Output to mapping-v6.md.test\n")
    else:
        output_file = REPO_ROOT / "doc/mapping/mapping-v6.md"
        print("🚀 PRODUCTION MODE: Output to mapping-v6.md\n")

    success = generate_mapping_table(input_file, output_file)

    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()

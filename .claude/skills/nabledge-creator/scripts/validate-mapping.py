#!/usr/bin/env python3
"""
Validate mapping file structure and content.

Exit codes:
  0: All checks passed
  1: Warnings only
  2: Errors found
"""

import sys
import re
from pathlib import Path
from typing import List, Dict, Tuple


# Valid taxonomy
VALID_TYPES = {
    'processing-pattern': ['nablarch-batch', 'jakarta-batch', 'restful-web-service',
                           'http-messaging', 'web-application', 'mom-messaging', 'db-messaging'],
    'component': ['handlers', 'libraries', 'adapters'],
    'development-tools': ['testing-framework', 'toolbox', 'java-static-analysis'],
    'setup': ['blank-project', 'configuration', 'setting-guide', 'cloud-native'],
    'guide': ['nablarch-patterns', 'business-samples'],
    'check': ['security-check'],
    'about': ['about-nablarch', 'migration', 'release-notes'],
}


def parse_mapping_file(file_path: str) -> List[Dict]:
    """Parse mapping Markdown file into list of rows."""
    rows = []

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find table start (after header)
    in_table = False
    for line in lines:
        if line.startswith('|') and 'Source Path' in line:
            in_table = True
            continue
        elif in_table and line.startswith('|---'):
            continue
        elif in_table and line.startswith('|'):
            # Parse row
            cols = [c.strip() for c in line.split('|')[1:-1]]  # Remove empty first and last
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


def check_structure(rows: List[Dict]) -> Tuple[int, int]:
    """Check structure: all rows have 8 columns, required fields non-empty."""
    errors = 0
    warnings = 0

    for i, row in enumerate(rows, 1):
        # Check all required fields
        if not row['source_path']:
            print(f"ERROR row {i}: source_path is empty")
            errors += 1
        if not row['title']:
            print(f"WARNING row {i}: title is empty")
            warnings += 1
        if not row['type']:
            print(f"ERROR row {i}: type is empty")
            errors += 1
        if not row['category']:
            print(f"ERROR row {i}: category is empty")
            errors += 1
        if not row['target_path']:
            print(f"ERROR row {i}: target_path is empty")
            errors += 1
        # PP can be empty

    return errors, warnings


def check_taxonomy(rows: List[Dict]) -> int:
    """Check Type/Category combinations are valid."""
    errors = 0

    for i, row in enumerate(rows, 1):
        type_val = row['type']
        category = row['category']

        if type_val not in VALID_TYPES:
            print(f"ERROR row {i}: invalid type '{type_val}'")
            errors += 1
            continue

        if category not in VALID_TYPES[type_val]:
            print(f"ERROR row {i}: invalid category '{category}' for type '{type_val}'")
            errors += 1

    return errors


def check_source_files(rows: List[Dict], source_dir: str) -> Tuple[int, int]:
    """Check source files exist."""
    errors = 0
    warnings = 0

    base_paths = {
        'nablarch-document-en': Path(source_dir) / 'nablarch-document' / 'en',
        'system-development-guide': Path(source_dir) / 'nablarch-system-development-guide',
    }

    for i, row in enumerate(rows, 1):
        source_path = row['source_path']

        # Try both repositories
        found = False
        for base in base_paths.values():
            full_path = base / source_path
            if full_path.exists():
                found = True
                break

        if not found:
            print(f"ERROR row {i}: source file not found: {source_path}")
            errors += 1

        # Check Japanese file (warning only)
        if 'system-development-guide' not in source_path:
            ja_path = source_path
            if 'duplicate_form_submission.rst' in ja_path:
                ja_path = ja_path.replace('duplicate_form_submission.rst', 'double_transmission.rst')

            ja_base = Path(source_dir) / 'nablarch-document' / 'ja'
            ja_full = ja_base / ja_path
            if not ja_full.exists():
                print(f"WARNING row {i}: Japanese file not found: {ja_path}")
                warnings += 1

    return errors, warnings


def check_target_paths(rows: List[Dict]) -> int:
    """Check target path format and uniqueness."""
    errors = 0
    seen_targets = {}

    for i, row in enumerate(rows, 1):
        target_path = row['target_path']
        type_val = row['type']
        category = row['category']

        # Check starts with type
        if not target_path.startswith(f"{type_val}/"):
            print(f"ERROR row {i}: target_path doesn't start with type '{type_val}': {target_path}")
            errors += 1

        # Check contains category
        if f"/{category}/" not in target_path and not target_path.endswith(f"/{category}"):
            print(f"ERROR row {i}: target_path doesn't contain category '{category}': {target_path}")
            errors += 1

        # Check filename conversion (_ to -)
        filename = target_path.split('/')[-1]
        if '_' in filename and not filename.endswith('.xlsx'):
            print(f"ERROR row {i}: target filename contains underscore: {filename}")
            errors += 1

        # Check .rst extension converted
        if '.rst' in target_path:
            print(f"ERROR row {i}: target path still contains .rst: {target_path}")
            errors += 1

        # Check uniqueness
        if target_path in seen_targets:
            print(f"ERROR row {i}: duplicate target_path '{target_path}' (first seen at row {seen_targets[target_path]})")
            errors += 1
        else:
            seen_targets[target_path] = i

    return errors


def check_url_format(rows: List[Dict]) -> int:
    """Check official URL format."""
    errors = 0

    url_pattern = re.compile(r'\[\U0001F517\]\(https://.*\)')

    for i, row in enumerate(rows, 1):
        url = row['official_url']

        if not url_pattern.match(url):
            print(f"ERROR row {i}: invalid URL format: {url}")
            errors += 1

        # Check version number in nablarch.github.io URLs
        if 'nablarch.github.io' in url and '6u3' not in url:
            print(f"ERROR row {i}: URL missing version '6u3': {url}")
            errors += 1

    return errors


def check_consistency(rows: List[Dict]) -> int:
    """Check consistency rules."""
    errors = 0

    for i, row in enumerate(rows, 1):
        type_val = row['type']
        category = row['category']
        pp = row['pp']

        # Rule 1: processing-pattern type → PP should equal category or be empty
        if type_val == 'processing-pattern':
            if pp and pp != category:
                print(f"ERROR row {i}: PP '{pp}' doesn't match category '{category}' for processing-pattern")
                errors += 1

        # Rule 2: common handlers → PP should be empty
        if 'handlers/common/' in row['target_path'] and pp:
            print(f"ERROR row {i}: common handler has non-empty PP: {pp}")
            errors += 1

    return errors


def main():
    if len(sys.argv) < 2:
        print("Usage: validate-mapping.py MAPPING_FILE [--source-dir DIR]", file=sys.stderr)
        sys.exit(2)

    mapping_file = sys.argv[1]
    source_dir = '.lw/nab-official/v6'

    if '--source-dir' in sys.argv:
        idx = sys.argv.index('--source-dir')
        if idx + 1 < len(sys.argv):
            source_dir = sys.argv[idx + 1]

    # Parse mapping
    print(f"Parsing {mapping_file}...", file=sys.stderr)
    rows = parse_mapping_file(mapping_file)

    print(f"\n=== Validation Report ===", file=sys.stderr)
    print(f"Total rows: {len(rows)}", file=sys.stderr)
    print()

    # Run checks
    total_errors = 0
    total_warnings = 0

    errors, warnings = check_structure(rows)
    print(f"Structure:     {'PASS' if errors == 0 else 'FAIL'} ({len(rows)-errors}/{len(rows)})")
    total_errors += errors
    total_warnings += warnings

    errors = check_taxonomy(rows)
    print(f"Taxonomy:      {'PASS' if errors == 0 else 'FAIL'} ({len(rows)-errors}/{len(rows)})")
    total_errors += errors

    errors, warnings = check_source_files(rows, source_dir)
    print(f"Source files:  {'PASS' if errors == 0 else 'FAIL'} (en: {len(rows)-errors}/{len(rows)}, ja: {len(rows)-warnings}/{len(rows)})")
    total_errors += errors
    total_warnings += warnings

    errors = check_target_paths(rows)
    print(f"Target paths:  {'PASS' if errors == 0 else 'FAIL'} ({len(set(row['target_path'] for row in rows))} unique, {errors} issues)")
    total_errors += errors

    errors = check_url_format(rows)
    print(f"URL format:    {'PASS' if errors == 0 else 'FAIL'} ({len(rows)-errors}/{len(rows)})")
    total_errors += errors

    errors = check_consistency(rows)
    print(f"Consistency:   {'PASS' if errors == 0 else 'FAIL'} ({len(rows)-errors}/{len(rows)})")
    total_errors += errors

    print()
    if total_errors > 0:
        print(f"Result: FAILED ({total_errors} errors, {total_warnings} warnings)")
        sys.exit(2)
    elif total_warnings > 0:
        print(f"Result: PASSED with warnings ({total_warnings} warnings)")
        sys.exit(1)
    else:
        print("Result: ALL PASSED")
        sys.exit(0)


if __name__ == '__main__':
    main()

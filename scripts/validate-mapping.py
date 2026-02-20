#!/usr/bin/env python3
"""
Validate mapping-v6.md against design specifications.

This script checks:
1. Column completeness
2. Title extraction success rate
3. Title (ja) extraction success rate
4. Processing Pattern validity
5. Target Path naming conventions
6. Category ID validation
7. Type consistency

Usage:
    python scripts/validate-mapping.py [mapping-file]

    Default: doc/mapping/mapping-v6.md.test
"""

import sys
from pathlib import Path
from typing import List, Dict
import argparse

# Valid values
VALID_TYPES = [
    'processing-pattern',
    'component',
    'development-tools',
    'setup',
    'guide',
    'check',
    'about',
]

VALID_CATEGORIES = {
    'processing-pattern': ['nablarch-batch', 'jakarta-batch', 'restful-web-service', 'http-messaging', 'web-application', 'mom-messaging', 'db-messaging'],
    'component': ['handlers', 'libraries', 'adapters'],
    'development-tools': ['testing-framework', 'toolbox', 'java-static-analysis'],
    'setup': ['blank-project', 'configuration', 'setting-guide', 'cloud-native'],
    'guide': ['nablarch-patterns', 'business-samples'],
    'check': ['security-check'],
    'about': ['about-nablarch', 'migration', 'release-notes'],
}

VALID_PROCESSING_PATTERNS = [
    'nablarch-batch',
    'jakarta-batch',
    'restful-web-service',
    'http-messaging',
    'web-application',
    'mom-messaging',
    'db-messaging',
]

COMPONENT_CATEGORIES = ['handlers', 'libraries', 'adapters']

def parse_mapping_table(file_path: Path) -> List[Dict[str, str]]:
    """Parse mapping table"""
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
                    'type': cells[4],
                    'category': cells[5],
                    'processing_pattern': cells[6],
                    'target_path': cells[7],
                })

    return rows

def validate_columns(rows: List[Dict[str, str]]) -> Dict:
    """Validate column completeness"""
    results = {
        'total': len(rows),
        'missing_source_path': [],
        'missing_title': [],
        'missing_title_ja': [],
        'missing_official_url': [],
        'missing_type': [],
        'missing_category': [],
        'missing_target_path': [],
    }

    for i, row in enumerate(rows, 1):
        if not row['source_path']:
            results['missing_source_path'].append(i)
        if not row['title']:
            results['missing_title'].append((i, row['source_path']))
        if not row['title_ja']:
            results['missing_title_ja'].append((i, row['source_path']))
        if not row['official_url']:
            results['missing_official_url'].append(i)
        if not row['type']:
            results['missing_type'].append(i)
        if not row['category']:
            results['missing_category'].append(i)
        if not row['target_path']:
            results['missing_target_path'].append(i)
        # processing_pattern can be empty (generic files)

    return results

def validate_processing_patterns(rows: List[Dict[str, str]]) -> Dict:
    """Validate processing pattern assignments"""
    results = {
        'total': len(rows),
        'assigned': [],
        'empty_generic': [],
        'invalid': [],
    }

    for i, row in enumerate(rows, 1):
        pp = row['processing_pattern']

        if not pp:
            results['empty_generic'].append((i, row['source_path']))
        elif pp in VALID_PROCESSING_PATTERNS:
            results['assigned'].append((i, row['source_path'], pp))
        else:
            results['invalid'].append((i, row['source_path'], pp))

    return results

def validate_target_paths(rows: List[Dict[str, str]]) -> Dict:
    """Validate target path naming conventions"""
    results = {
        'total': len(rows),
        'valid': [],
        'invalid': [],
        'component_missing_subdir': [],
    }

    for i, row in enumerate(rows, 1):
        target = row['target_path']
        type_ = row['type']
        category = row['category']

        if not target:
            continue

        # Check format: type/category/...
        parts = target.split('/')

        if len(parts) < 2:
            results['invalid'].append((i, row['source_path'], target, 'Too few path components'))
            continue

        if parts[0] != type_:
            results['invalid'].append((i, row['source_path'], target, f'Type mismatch: {parts[0]} != {type_}'))
            continue

        if parts[1] != category:
            results['invalid'].append((i, row['source_path'], target, f'Category mismatch: {parts[1]} != {category}'))
            continue

        # Component categories should preserve subdirectories
        if category in COMPONENT_CATEGORIES:
            # Check if source has subdirectories
            source = row['source_path']
            source_parts = source.split('/')

            # Find category in source path
            category_idx = None
            for idx, part in enumerate(source_parts):
                if category in part or (category == 'adapters' and 'adaptors' in part):
                    category_idx = idx
                    break

            if category_idx is not None:
                source_subdirs = source_parts[category_idx + 1:-1]  # Between category and filename
                source_subdirs = [d for d in source_subdirs if d != 'images']

                target_subdirs = parts[2:-1]  # Between category and filename

                if source_subdirs and not target_subdirs:
                    results['component_missing_subdir'].append((
                        i,
                        row['source_path'],
                        target,
                        f'Missing subdirs: {"/".join(source_subdirs)}'
                    ))
                    continue

        results['valid'].append((i, row['source_path'], target))

    return results

def validate_categories(rows: List[Dict[str, str]]) -> Dict:
    """Validate category IDs"""
    results = {
        'total': len(rows),
        'valid': [],
        'invalid_type': [],
        'invalid_category': [],
    }

    for i, row in enumerate(rows, 1):
        type_ = row['type']
        category = row['category']

        if type_ not in VALID_TYPES:
            results['invalid_type'].append((i, row['source_path'], type_))
            continue

        if type_ not in VALID_CATEGORIES:
            results['invalid_category'].append((i, row['source_path'], category, f'Unknown type: {type_}'))
            continue

        if category not in VALID_CATEGORIES[type_]:
            results['invalid_category'].append((i, row['source_path'], category, f'Invalid for type {type_}'))
            continue

        results['valid'].append((i, row['source_path'], type_, category))

    return results

def print_report(rows: List[Dict[str, str]]):
    """Print validation report"""
    print("=" * 70)
    print("VALIDATION REPORT")
    print("=" * 70)
    print()

    # Column completeness
    print("📋 Column Completeness")
    print("-" * 70)
    col_results = validate_columns(rows)
    print(f"Total Rows: {col_results['total']}")
    print()

    for field in ['title', 'title_ja', 'official_url', 'type', 'category', 'target_path']:
        missing = col_results[f'missing_{field}']
        count = len(missing)
        rate = (col_results['total'] - count) / col_results['total'] * 100 if col_results['total'] > 0 else 0

        if count == 0:
            print(f"  ✅ {field}: {rate:.1f}% ({col_results['total']}/{col_results['total']})")
        else:
            print(f"  ⚠️  {field}: {rate:.1f}% ({col_results['total'] - count}/{col_results['total']})")
            if field in ['title', 'title_ja']:
                for item in missing[:5]:
                    if isinstance(item, tuple):
                        print(f"       Row {item[0]}: {item[1]}")
                    else:
                        print(f"       Row {item}")
                if count > 5:
                    print(f"       ... and {count - 5} more")

    print()

    # Processing patterns
    print("🔄 Processing Pattern Assignment")
    print("-" * 70)
    pp_results = validate_processing_patterns(rows)
    print(f"Total Rows: {pp_results['total']}")
    print(f"  ✅ Assigned: {len(pp_results['assigned'])} ({len(pp_results['assigned']) / pp_results['total'] * 100:.1f}%)")
    print(f"  ⚪ Empty (generic): {len(pp_results['empty_generic'])} ({len(pp_results['empty_generic']) / pp_results['total'] * 100:.1f}%)")

    if pp_results['invalid']:
        print(f"  ❌ Invalid: {len(pp_results['invalid'])}")
        for item in pp_results['invalid'][:5]:
            print(f"       Row {item[0]}: {item[1]} → {item[2]}")
        if len(pp_results['invalid']) > 5:
            print(f"       ... and {len(pp_results['invalid']) - 5} more")
    else:
        print(f"  ✅ Invalid: 0")

    print()

    # Target paths
    print("📁 Target Path Naming Conventions")
    print("-" * 70)
    path_results = validate_target_paths(rows)
    print(f"Total Rows: {path_results['total']}")
    print(f"  ✅ Valid: {len(path_results['valid'])} ({len(path_results['valid']) / path_results['total'] * 100:.1f}%)")

    if path_results['invalid']:
        print(f"  ❌ Invalid: {len(path_results['invalid'])}")
        for item in path_results['invalid'][:5]:
            print(f"       Row {item[0]}: {item[2]}")
            print(f"           Reason: {item[3]}")
        if len(path_results['invalid']) > 5:
            print(f"       ... and {len(path_results['invalid']) - 5} more")

    if path_results['component_missing_subdir']:
        print(f"  ⚠️  Component missing subdirs: {len(path_results['component_missing_subdir'])}")
        for item in path_results['component_missing_subdir'][:5]:
            print(f"       Row {item[0]}: {item[1]}")
            print(f"           Target: {item[2]}")
            print(f"           {item[3]}")
        if len(path_results['component_missing_subdir']) > 5:
            print(f"       ... and {len(path_results['component_missing_subdir']) - 5} more")

    print()

    # Categories
    print("🏷️  Category Validation")
    print("-" * 70)
    cat_results = validate_categories(rows)
    print(f"Total Rows: {cat_results['total']}")
    print(f"  ✅ Valid: {len(cat_results['valid'])} ({len(cat_results['valid']) / cat_results['total'] * 100:.1f}%)")

    if cat_results['invalid_type']:
        print(f"  ❌ Invalid Type: {len(cat_results['invalid_type'])}")
        for item in cat_results['invalid_type'][:5]:
            print(f"       Row {item[0]}: {item[2]}")

    if cat_results['invalid_category']:
        print(f"  ❌ Invalid Category: {len(cat_results['invalid_category'])}")
        for item in cat_results['invalid_category'][:5]:
            print(f"       Row {item[0]}: {item[2]} (Reason: {item[3]})")

    print()

    # Overall summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    total_issues = (
        len(col_results['missing_title']) +
        len(col_results['missing_title_ja']) +
        len(pp_results['invalid']) +
        len(path_results['invalid']) +
        len(path_results['component_missing_subdir']) +
        len(cat_results['invalid_type']) +
        len(cat_results['invalid_category'])
    )

    if total_issues == 0:
        print("✅ All validations passed!")
    else:
        print(f"⚠️  Found {total_issues} issues requiring review:")
        if len(col_results['missing_title']) > 0:
            print(f"   - {len(col_results['missing_title'])} missing titles")
        if len(col_results['missing_title_ja']) > 0:
            print(f"   - {len(col_results['missing_title_ja'])} missing Japanese titles")
        if len(pp_results['invalid']) > 0:
            print(f"   - {len(pp_results['invalid'])} invalid processing patterns")
        if len(path_results['invalid']) > 0:
            print(f"   - {len(path_results['invalid'])} invalid target paths")
        if len(path_results['component_missing_subdir']) > 0:
            print(f"   - {len(path_results['component_missing_subdir'])} component paths missing subdirectories")
        if len(cat_results['invalid_type']) > 0:
            print(f"   - {len(cat_results['invalid_type'])} invalid types")
        if len(cat_results['invalid_category']) > 0:
            print(f"   - {len(cat_results['invalid_category'])} invalid categories")

    print()

    automation_rate = ((col_results['total'] - total_issues) / col_results['total'] * 100) if col_results['total'] > 0 else 0
    print(f"Automation Success Rate: {automation_rate:.1f}%")
    print(f"Items Needing Manual Review: {total_issues}")
    print()

def main():
    parser = argparse.ArgumentParser(description='Validate mapping-v6.md')
    parser.add_argument('file', nargs='?', default='doc/mapping/mapping-v6.md.test', help='Mapping file to validate')
    args = parser.parse_args()

    file_path = Path(args.file)

    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)

    print(f"📖 Reading {file_path}")
    rows = parse_mapping_table(file_path)
    print(f"✅ Parsed {len(rows)} rows\n")

    print_report(rows)

if __name__ == '__main__':
    main()

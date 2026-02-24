#!/usr/bin/env python3
"""
Validate knowledge search index (index.toon) structure and quality.

Usage:
    python validate-index.py INDEX_PATH [--knowledge-dir DIR]

Exit codes:
  0: All validation passed (no errors, no warnings)
  1: Validation passed with warnings (quality suggestions)
  2: Validation failed (schema errors, must fix)

Validation checks:
  - Schema: Header format, entry structure, field completeness
  - Files: Created file paths exist and are valid JSON
  - Quality: Hint count, duplicates, language coverage, sorting
  - Consistency: No duplicate titles or paths
"""

import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Tuple


def parse_index_file(file_path: str) -> Tuple[int, List[Dict], List[str]]:
    """Parse index.toon file and extract header count, entries, and issues."""
    entries = []
    issues = []
    header_count = None

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find header line
    header_pattern = re.compile(r'^files\[(\d+),\]\{title,hints,path\}:')
    entry_in_progress = False

    for line_num, line in enumerate(lines, 1):
        line = line.rstrip('\n')

        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue

        # Check header
        header_match = header_pattern.match(line)
        if header_match:
            header_count = int(header_match.group(1))
            entry_in_progress = True
            continue

        # Parse entries (must start with exactly 2 spaces)
        if entry_in_progress and line.startswith('  ') and not line.startswith('   '):
            # Remove leading spaces
            content = line[2:]

            # Split by comma (careful with commas in fields)
            # Format: title, hints, path
            parts = content.split(', ')

            if len(parts) < 3:
                issues.append(f"Line {line_num}: Entry has fewer than 3 fields")
                continue

            # Title is first part
            title = parts[0]

            # Path is last part
            path = parts[-1]

            # Hints are everything in between (joined back in case there were commas)
            hints = ', '.join(parts[1:-1])

            entries.append({
                'line_num': line_num,
                'title': title,
                'hints': hints,
                'path': path
            })

    return header_count, entries, issues


def check_schema(header_count: int, entries: List[Dict], parse_issues: List[str]) -> int:
    """Check schema validation: header format, entry count, field completeness."""
    errors = 0

    print("=== Schema Validation ===")

    # Report parse issues first
    if parse_issues:
        for issue in parse_issues:
            print(f"ERROR: {issue}")
        errors += len(parse_issues)

    # Check header count matches
    if header_count is None:
        print("ERROR: Header line not found or invalid format")
        print("       Expected: files[{count},]{title,hints,path}:")
        errors += 1
    elif header_count != len(entries):
        print(f"ERROR: Header count {header_count} does not match actual entries {len(entries)}")
        errors += 1
    else:
        print(f"✓ Entry count matches ({len(entries)} entries)")

    # Check all entries have non-empty fields
    empty_title_count = 0
    empty_hints_count = 0
    empty_path_count = 0

    for entry in entries:
        if not entry['title']:
            empty_title_count += 1
            print(f"ERROR: Line {entry['line_num']} - Entry has empty title")
        if not entry['hints']:
            empty_hints_count += 1
            print(f"ERROR: Line {entry['line_num']} - Entry has empty hints")
        if not entry['path']:
            empty_path_count += 1
            print(f"ERROR: Line {entry['line_num']} - Entry has empty path")

    errors += empty_title_count + empty_hints_count + empty_path_count

    if empty_title_count + empty_hints_count + empty_path_count == 0:
        print("✓ All entries have non-empty fields")

    # Check minimum hints (3 hints minimum)
    insufficient_hints_count = 0
    for entry in entries:
        if entry['hints']:
            hint_list = entry['hints'].split()
            if len(hint_list) < 3:
                insufficient_hints_count += 1
                print(f"ERROR: Line {entry['line_num']} - Entry '{entry['title']}' has only {len(hint_list)} hints (minimum 3)")

    errors += insufficient_hints_count

    if insufficient_hints_count == 0:
        print("✓ All entries have >= 3 hints")

    print()
    return errors


def check_file_existence(entries: List[Dict], knowledge_dir: Path) -> int:
    """Check that created file paths exist and are valid JSON."""
    errors = 0

    print("=== File Existence Validation ===")

    created_files = [e for e in entries if e['path'] != 'not yet created']

    if len(created_files) == 0:
        print("✓ All created file paths exist (0 created files)")
        print()
        return 0

    missing_count = 0
    invalid_json_count = 0

    for entry in created_files:
        file_path = knowledge_dir / entry['path']

        if not file_path.exists():
            print(f"ERROR: Line {entry['line_num']} - File not found: {entry['path']}")
            missing_count += 1
            errors += 1
        else:
            # Check if valid JSON
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                print(f"ERROR: Line {entry['line_num']} - Invalid JSON in {entry['path']}: {e}")
                invalid_json_count += 1
                errors += 1

    if missing_count == 0 and invalid_json_count == 0:
        print(f"✓ All created file paths exist and are valid JSON ({len(created_files)} created files)")

    print()
    return errors


def check_quality(entries: List[Dict]) -> int:
    """Check quality: hint count, duplicates, language coverage, sorting."""
    warnings = 0

    print("=== Quality Validation ===")

    # Check hint count (3-8 recommended)
    low_hint_count = 0
    high_hint_count = 0

    for entry in entries:
        if entry['hints']:
            hint_list = entry['hints'].split()
            if len(hint_list) < 3:
                low_hint_count += 1
                print(f"⚠ Line {entry['line_num']} - Entry '{entry['title']}' has only {len(hint_list)} hints (3-8 recommended)")
            elif len(hint_list) > 8:
                high_hint_count += 1
                print(f"⚠ Line {entry['line_num']} - Entry '{entry['title']}' has {len(hint_list)} hints (3-8 recommended)")

    warnings += low_hint_count + high_hint_count

    if low_hint_count + high_hint_count == 0:
        print("✓ Hint count within range (3-8)")

    # Check duplicate hints within entries
    duplicate_hints_count = 0

    for entry in entries:
        if entry['hints']:
            hint_list = entry['hints'].split()
            unique_hints = set(hint_list)
            if len(hint_list) != len(unique_hints):
                duplicates = [h for h in unique_hints if hint_list.count(h) > 1]
                print(f"⚠ Line {entry['line_num']} - Entry '{entry['title']}' has duplicate hints: {', '.join(duplicates)}")
                duplicate_hints_count += 1

    warnings += duplicate_hints_count

    if duplicate_hints_count == 0:
        print("✓ No duplicate hints within entries")

    # Check for empty hints (after splitting)
    empty_hints_count = 0

    for entry in entries:
        if entry['hints']:
            hint_list = entry['hints'].split()
            if '' in hint_list:
                print(f"⚠ Line {entry['line_num']} - Entry '{entry['title']}' has empty hints after splitting")
                empty_hints_count += 1

    warnings += empty_hints_count

    if empty_hints_count == 0:
        print("✓ No empty hints")

    # Check Japanese coverage (at least one Japanese character in hints or title)
    japanese_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]')
    no_japanese_count = 0

    for entry in entries:
        has_japanese = japanese_pattern.search(entry['title']) or japanese_pattern.search(entry['hints'])
        if not has_japanese:
            print(f"⚠ Line {entry['line_num']} - Entry '{entry['title']}' has no Japanese keywords")
            no_japanese_count += 1

    warnings += no_japanese_count

    if no_japanese_count == 0:
        print("✓ Japanese keywords present in all entries")

    # Check sorting (by title)
    unsorted_count = 0
    unsorted_entries = []

    for i in range(len(entries) - 1):
        current_title = entries[i]['title']
        next_title = entries[i + 1]['title']

        if current_title > next_title:
            unsorted_count += 1
            unsorted_entries.append((entries[i + 1]['line_num'], next_title, current_title))

    warnings += unsorted_count

    if unsorted_count == 0:
        print("✓ Entries sorted by title")
    else:
        print(f"⚠ Sorting: {unsorted_count} entries out of order")

    print()
    return warnings, unsorted_entries


def check_consistency(entries: List[Dict]) -> int:
    """Check consistency: no duplicate titles or paths."""
    errors = 0

    print("=== Consistency Validation ===")

    # Check duplicate titles
    seen_titles = {}
    duplicate_titles = []

    for entry in entries:
        title = entry['title']
        if title in seen_titles:
            duplicate_titles.append((entry['line_num'], title, seen_titles[title]))
        else:
            seen_titles[title] = entry['line_num']

    errors += len(duplicate_titles)

    if duplicate_titles:
        print(f"ERROR: Found {len(duplicate_titles)} duplicate titles")
        for line_num, title, first_line in duplicate_titles:
            print(f"       Line {line_num}: '{title}' (first seen at line {first_line})")
    else:
        print("✓ No duplicate titles")

    # Check duplicate paths (excluding "not yet created")
    seen_paths = {}
    duplicate_paths = []

    for entry in entries:
        path = entry['path']
        if path != 'not yet created':
            if path in seen_paths:
                duplicate_paths.append((entry['line_num'], path, seen_paths[path]))
            else:
                seen_paths[path] = entry['line_num']

    errors += len(duplicate_paths)

    if duplicate_paths:
        print(f"ERROR: Found {len(duplicate_paths)} duplicate paths")
        for line_num, path, first_line in duplicate_paths:
            print(f"       Line {line_num}: '{path}' (first seen at line {first_line})")
    else:
        print("✓ No duplicate paths")

    print()
    return errors


def validate_inputs(index_path: str) -> None:
    """Validate input files exist before processing."""
    if not Path(index_path).exists():
        print(f"Error: Index file not found: {index_path}", file=sys.stderr)
        sys.exit(2)


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate-index.py INDEX_PATH [--knowledge-dir DIR]", file=sys.stderr)
        sys.exit(2)

    index_path = sys.argv[1]

    # Validate inputs
    validate_inputs(index_path)

    # Determine knowledge directory (default: same directory as index file)
    knowledge_dir = Path(index_path).parent

    if '--knowledge-dir' in sys.argv:
        idx = sys.argv.index('--knowledge-dir')
        if idx + 1 < len(sys.argv):
            knowledge_dir = Path(sys.argv[idx + 1])

    print(f"Validating: {index_path}\n")

    # Parse index file
    header_count, entries, parse_issues = parse_index_file(index_path)

    # Run validations
    total_errors = 0
    total_warnings = 0

    # 1. Schema validation (Exit 2 on failure)
    errors = check_schema(header_count, entries, parse_issues)
    total_errors += errors

    # 2. File existence validation (Exit 2 on failure)
    errors = check_file_existence(entries, knowledge_dir)
    total_errors += errors

    # 3. Quality validation (Exit 1 on warnings)
    warnings, unsorted_entries = check_quality(entries)
    total_warnings += warnings

    # 4. Consistency validation (Exit 2 on failure)
    errors = check_consistency(entries)
    total_errors += errors

    # Summary
    print("=== Summary ===")
    print(f"Total entries: {len(entries)}")

    created_count = len([e for e in entries if e['path'] != 'not yet created'])
    not_created_count = len([e for e in entries if e['path'] == 'not yet created'])

    print(f"Created files: {created_count}")
    print(f"Not yet created: {not_created_count}")
    print()

    # Determine exit code and print result
    if total_errors > 0:
        print(f"Result: FAILED ({total_errors} errors)")
        print()
        print("Errors must be fixed before commit.")
        sys.exit(2)
    elif total_warnings > 0:
        print(f"Result: PASSED with warnings ({total_warnings} warnings)")
        print()
        if unsorted_entries:
            print("Warnings:")
            for line_num, entry_title, prev_title in unsorted_entries:
                print(f"  - Line {line_num}: Entry \"{entry_title}\" appears before \"{prev_title}\"")
        sys.exit(1)
    else:
        print("Result: ALL PASSED")
        sys.exit(0)


if __name__ == '__main__':
    main()

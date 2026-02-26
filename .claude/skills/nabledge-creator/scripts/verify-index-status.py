#!/usr/bin/env python3
"""
Verify index.toon path field consistency with actual knowledge files.

Checks:
- Entries with paths (not "not yet created") have corresponding .json files
- All .json files in knowledge directory have index entries
- No orphaned files or missing entries

Exit codes:
  0: All checks passed
  1: Warnings (minor inconsistencies)
  2: Errors (missing files or entries)
"""

import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


def parse_index_toon(index_path: Path) -> Dict[str, str]:
    """
    Parse index.toon and extract title -> path mapping.

    Returns:
        Dict mapping title to path (or "not yet created")
    """
    if not index_path.exists():
        print(f"ERROR: Index file not found: {index_path}")
        sys.exit(2)

    entries = {}
    current_entry = {}

    with open(index_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Skip header
    in_entries = False
    for line in lines:
        line = line.rstrip('\n')

        if line.startswith('files['):
            in_entries = True
            continue

        if not in_entries:
            continue

        if line.startswith('title: '):
            if current_entry:
                # Save previous entry
                if 'title' in current_entry and 'path' in current_entry:
                    entries[current_entry['title']] = current_entry['path']
                current_entry = {}
            current_entry['title'] = line[7:]
        elif line.startswith('hints: '):
            current_entry['hints'] = line[7:]
        elif line.startswith('path: '):
            current_entry['path'] = line[6:]
        elif line == '---':
            # Entry separator
            if current_entry and 'title' in current_entry and 'path' in current_entry:
                entries[current_entry['title']] = current_entry['path']
                current_entry = {}

    # Last entry
    if current_entry and 'title' in current_entry and 'path' in current_entry:
        entries[current_entry['title']] = current_entry['path']

    return entries


def find_knowledge_files(knowledge_dir: Path) -> Set[str]:
    """
    Find all .json files in knowledge directory.

    Returns:
        Set of relative paths from knowledge_dir (e.g., "features/libraries/universal-dao.json")
    """
    if not knowledge_dir.exists():
        return set()

    json_files = set()
    for json_file in knowledge_dir.rglob('*.json'):
        # Skip index.toon and non-JSON files
        if json_file.name == 'index.toon':
            continue
        # Get relative path from knowledge_dir
        rel_path = json_file.relative_to(knowledge_dir)
        json_files.add(str(rel_path))

    return json_files


def verify_status(index_path: Path, knowledge_dir: Path) -> Tuple[int, int]:
    """
    Verify index.toon path consistency with actual files.

    Returns:
        (error_count, warning_count)
    """
    errors = 0
    warnings = 0

    print(f"\nVerifying index status...")
    print(f"  Index: {index_path}")
    print(f"  Knowledge dir: {knowledge_dir}\n")

    # Parse index.toon
    entries = parse_index_toon(index_path)
    print(f"Index entries: {len(entries)}")

    # Find actual files
    actual_files = find_knowledge_files(knowledge_dir)
    print(f"Actual .json files: {len(actual_files)}\n")

    # Check 1: Entries with paths should have corresponding files
    print("Check 1: Index paths → actual files")
    index_with_paths = {title: path for title, path in entries.items() if path != "not yet created"}
    print(f"  Entries with paths: {len(index_with_paths)}")

    missing_files = []
    for title, path in index_with_paths.items():
        file_path = knowledge_dir / path
        if not file_path.exists():
            missing_files.append((title, path))

    if missing_files:
        print(f"\n  ❌ ERROR: {len(missing_files)} entries have paths but files don't exist:")
        for title, path in missing_files[:10]:  # Show first 10
            print(f"    - {title}: {path}")
        if len(missing_files) > 10:
            print(f"    ... and {len(missing_files) - 10} more")
        errors += len(missing_files)
    else:
        print("  ✓ All indexed files exist")

    # Check 2: All actual files should have index entries
    print("\nCheck 2: Actual files → index entries")
    indexed_paths = set(index_with_paths.values())
    missing_entries = []

    for file_path in actual_files:
        if file_path not in indexed_paths:
            missing_entries.append(file_path)

    if missing_entries:
        print(f"\n  ❌ ERROR: {len(missing_entries)} files exist but not in index:")
        for path in missing_entries[:10]:  # Show first 10
            print(f"    - {path}")
        if len(missing_entries) > 10:
            print(f"    ... and {len(missing_entries) - 10} more")
        errors += len(missing_entries)
    else:
        print("  ✓ All actual files are indexed")

    # Check 3: "not yet created" entries
    not_created = [title for title, path in entries.items() if path == "not yet created"]
    if not_created:
        print(f"\nCheck 3: 'not yet created' entries")
        print(f"  ℹ INFO: {len(not_created)} entries marked as 'not yet created'")
        if len(not_created) <= 10:
            for title in not_created:
                print(f"    - {title}")

    # Summary
    print("\n" + "="*60)
    if errors == 0 and warnings == 0:
        print("✅ All checks passed")
        print(f"   - {len(index_with_paths)} files indexed and exist")
        print(f"   - {len(not_created)} entries pending creation")
    elif errors == 0:
        print(f"⚠ Passed with {warnings} warning(s)")
    else:
        print(f"❌ Failed with {errors} error(s) and {warnings} warning(s)")
    print("="*60)

    return errors, warnings


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Verify index.toon status consistency')
    parser.add_argument('index_path', type=Path, help='Path to index.toon')
    parser.add_argument('--knowledge-dir', type=Path, help='Knowledge directory (default: inferred from index path)')

    args = parser.parse_args()

    # Infer knowledge_dir from index_path if not provided
    if args.knowledge_dir:
        knowledge_dir = args.knowledge_dir
    else:
        # index.toon is in knowledge/ directory
        knowledge_dir = args.index_path.parent

    errors, warnings = verify_status(args.index_path, knowledge_dir)

    if errors > 0:
        sys.exit(2)
    elif warnings > 0:
        sys.exit(1)
    else:
        sys.exit(0)

#!/usr/bin/env python3
"""Finalize mapping with target names, titles, and validation (Steps 6-10).

This script:
1. Generates target file names (base name, prefix, directory, conflict resolution)
2. Extracts titles from source files
3. Builds final mapping JSON
4. Validates (duplicates, schema, categories, source files, target paths)
5. Writes output JSON and stats file

Input: pattern-verified-v6.json
Output: mapping-v6.json, mapping-v6.json.stats.txt
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Set, Tuple
from datetime import datetime


VERSION = "6"
SOURCE_BASE = Path(".lw/nab-official/v6")
CATEGORY_FILE = Path("doc/mapping-creation/categories-v6.json")
INPUT_FILE = Path("doc/mapping-creation/work-v6/pattern-verified-v6.json")
OUTPUT_FILE = Path("doc/mapping-creation/work-v6/mapping-v6.json")


# Generic names lacking context (Step 6.2)
GENERIC_NAMES = [
    'index', 'overview', 'main', 'introduction', 'readme',
    'summary', 'guide', 'concepts', 'getting-started'
]

# Category priority order (Step 6.3)
PRIORITY_ORDER = [
    # Processing patterns (tier 1)
    'batch-jsr352', 'batch-nablarch', 'http-messaging', 'messaging-db',
    'messaging-mom', 'rest', 'web',
    # Components (tier 2)
    'adaptor', 'handler', 'library', 'security-check', 'tool',
    # Setup (tier 3)
    'configuration', 'setup',
    # Guide (tier 4)
    'dev-guide-anti', 'dev-guide-other', 'dev-guide-pattern',
    # About (tier 5)
    'about', 'migration', 'release'
]

# Directory mapping (Step 6.3)
DIRECTORY_MAP = {
    # Processing patterns -> features/{pattern}/
    'batch-nablarch': 'features/batch-nablarch',
    'batch-jsr352': 'features/batch-jsr352',
    'rest': 'features/rest',
    'http-messaging': 'features/http-messaging',
    'web': 'features/web',
    'messaging-mom': 'features/messaging-mom',
    'messaging-db': 'features/messaging-db',
    # Components -> features/{component}/
    'handler': 'features/handler',
    'library': 'features/library',
    'adaptor': 'features/adaptor',
    'tool': 'features/tool',
    'security-check': 'features/security-check',
    # Setup -> guides/{type}/
    'setup': 'guides/setup',
    'configuration': 'guides/configuration',
    # Guide -> guides/patterns/
    'dev-guide-pattern': 'guides/patterns',
    'dev-guide-anti': 'guides/patterns',
    'dev-guide-other': 'guides/patterns',
    # About -> guides/{type}/
    'about': 'guides/about',
    'migration': 'guides/migration',
    'release': 'guides/releases'
}


def load_valid_category_ids() -> List[str]:
    """Load valid category IDs from category definitions."""
    with open(CATEGORY_FILE, 'r', encoding='utf-8') as f:
        category_defs = json.load(f)

    return [cat["id"] for cat in category_defs["categories"]]


def generate_base_name(source_path: str) -> str:
    """Generate base name from source file path (Step 6.1).

    Args:
        source_path: Source file path

    Returns:
        Base name (lowercase, hyphens)
    """
    filename = source_path.split('/')[-1]
    name = filename.rsplit('.', 1)[0]  # Remove extension
    name = name.lower()
    name = name.replace('_', '-')
    return name


def add_prefix_if_generic(name: str, source_path: str) -> str:
    """Add parent directory prefix for generic names (Step 6.2).

    Args:
        name: Base name
        source_path: Source file path

    Returns:
        Name with prefix if generic
    """
    if name in GENERIC_NAMES:
        parent_dir = source_path.split('/')[-2]
        parent_dir = parent_dir.lower().replace('_', '-')
        name = f"{parent_dir}-{name}"
    return name


def get_primary_category(categories: List[str]) -> str:
    """Get primary category based on priority order (Step 6.3).

    Args:
        categories: List of category IDs

    Returns:
        Primary category ID
    """
    for cat in PRIORITY_ORDER:
        if cat in categories:
            return cat

    # Fallback: use first category
    return categories[0] if categories else 'about'


def get_target_directory(categories: List[str]) -> str:
    """Determine target directory based on category priority (Step 6.3).

    Args:
        categories: List of category IDs

    Returns:
        Target directory path
    """
    primary_category = get_primary_category(categories)
    return DIRECTORY_MAP.get(primary_category, 'guides/other')


def resolve_conflict(name: str, source_path: str, categories: List[str],
                     existing_targets: Set[str]) -> str:
    """Resolve target name conflict using precedence order (Step 6.4).

    Strategies (in order):
    1. Add category prefix
    2. Add parent directory prefix
    3. Add numeric suffix

    Args:
        name: Base name
        source_path: Source file path
        categories: List of category IDs
        existing_targets: Set of existing target names

    Returns:
        Resolved target name (filename only, not full path)
    """
    target = f"{name}.json"

    if target not in existing_targets:
        return target

    # Strategy 1: Add category prefix
    primary_cat = get_primary_category(categories)
    target_1 = f"{primary_cat}-{name}.json"
    if target_1 not in existing_targets:
        print(f"  Conflict resolved: {target} -> {target_1} (category prefix)")
        return target_1

    # Strategy 2: Add parent directory prefix
    parent_dir = source_path.split('/')[-2].lower().replace('_', '-')
    target_2 = f"{parent_dir}-{name}.json"
    if target_2 not in existing_targets:
        print(f"  Conflict resolved: {target} -> {target_2} (parent prefix)")
        return target_2

    # Strategy 3: Add numeric suffix
    counter = 2
    while True:
        target_3 = f"{name}-{counter}.json"
        if target_3 not in existing_targets:
            print(f"  Conflict resolved: {target} -> {target_3} (numeric suffix)")
            return target_3
        counter += 1


def read_file_with_encoding(file_path: Path, encoding: str = 'utf-8') -> List[str]:
    """Read file with encoding fallback.

    Args:
        file_path: Path to file
        encoding: File encoding

    Returns:
        List of lines
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.readlines()
    except UnicodeDecodeError:
        if encoding == 'utf-8':
            return read_file_with_encoding(file_path, 'shift-jis')
        else:
            raise


def clean_title(title: str) -> str:
    """Clean title (remove special chars, limit length) (Step 7).

    Args:
        title: Raw title

    Returns:
        Cleaned title
    """
    # Remove leading/trailing whitespace
    title = title.strip()
    # Remove special markup characters
    title = title.replace('`', '').replace('*', '').replace('_', '')
    # Limit length
    if len(title) > 100:
        title = title[:97] + "..."
    return title


def filename_to_title(file_path: Path) -> str:
    """Generate title from filename (Step 7).

    Args:
        file_path: Path to file

    Returns:
        Generated title
    """
    filename = file_path.name
    name = filename.rsplit('.', 1)[0]
    name = name.replace('_', ' ').replace('-', ' ')
    return name.title()


def extract_rst_title(file_path: Path) -> str:
    """Extract title from RST file (Step 7).

    Args:
        file_path: Path to RST file

    Returns:
        Extracted title
    """
    try:
        lines = read_file_with_encoding(file_path, 'utf-8')
    except:
        return filename_to_title(file_path)

    # Look for: Title\n=====
    for i, line in enumerate(lines[:20]):
        if i+1 < len(lines):
            next_line = lines[i+1]
            if next_line.startswith('===') or next_line.startswith('---'):
                title = line.strip()
                if title:
                    return clean_title(title)

    return filename_to_title(file_path)


def extract_md_title(file_path: Path) -> str:
    """Extract title from Markdown file (Step 7).

    Args:
        file_path: Path to Markdown file

    Returns:
        Extracted title
    """
    try:
        lines = read_file_with_encoding(file_path, 'utf-8')
    except:
        return filename_to_title(file_path)

    # Look for: # Title
    for line in lines[:20]:
        if line.startswith('# '):
            title = line[2:].strip()
            if title:
                return clean_title(title)

    return filename_to_title(file_path)


def extract_title(file_path: Path) -> str:
    """Extract title from source file (Step 7).

    Args:
        file_path: Path to file

    Returns:
        Extracted title
    """
    ext = file_path.suffix.lower()

    if ext == '.rst':
        return extract_rst_title(file_path)
    elif ext == '.md':
        return extract_md_title(file_path)
    else:
        # XML or other: use filename
        return filename_to_title(file_path)


def build_mapping_json(verified_files: List[Dict], valid_category_ids: List[str]) -> Dict:
    """Build final mapping JSON (Step 8).

    Args:
        verified_files: List of verified file entries
        valid_category_ids: List of valid category IDs

    Returns:
        Mapping JSON structure
    """
    mapping = {
        "schema_version": "1.0",
        "version": VERSION,
        "created_at": datetime.now().isoformat(),
        "mappings": []
    }

    entry_id = 1
    existing_targets = set()

    print("Building mapping JSON...")

    for i, file_entry in enumerate(verified_files, 1):
        source_file = file_entry["source_file"]
        source_path = SOURCE_BASE / source_file
        categories = file_entry.get("categories", [])

        if i % 50 == 0:
            print(f"  Processed {i}/{len(verified_files)} files...")

        # Build entry
        entry = {
            "id": f"v{VERSION}-{entry_id:04d}",
            "source_file": source_file,
            "title": extract_title(source_path),
            "categories": categories
        }

        # Handle navigation-only files
        if file_entry.get("_no_content"):
            entry["_no_content"] = True
            entry["_no_content_reason"] = file_entry.get("_no_content_reason", "Unknown")
        else:
            # Check if target files are already assigned (from Step 1)
            if file_entry.get("_from_step") == 1 and "target_files" in file_entry:
                # Use existing target files from dev guide processing
                entry["target_files"] = file_entry["target_files"]
                # Add to existing targets to avoid conflicts
                for target in file_entry["target_files"]:
                    target_name = target.split("/")[-1]
                    existing_targets.add(target_name)
            else:
                # Generate target file
                base_name = generate_base_name(source_file)
                base_name = add_prefix_if_generic(base_name, source_file)
                directory = get_target_directory(categories)
                target_name = resolve_conflict(base_name, source_file, categories, existing_targets)
                target_path = f"{directory}/{target_name}"

                entry["target_files"] = [target_path]
                existing_targets.add(target_name)

        mapping["mappings"].append(entry)
        entry_id += 1

    print(f"✓ Built mapping with {len(mapping['mappings'])} entries")
    return mapping


def validate_mapping(mapping: Dict, valid_category_ids: List[str]) -> None:
    """Validate mapping (Step 9).

    Validates:
    - No duplicate targets
    - Schema compliance
    - Category validation
    - Source file existence
    - Target path consistency

    Args:
        mapping: Mapping JSON structure
        valid_category_ids: List of valid category IDs

    Raises:
        ValueError: If validation fails
    """
    print("Validating mapping...")

    entries = mapping["mappings"]

    # 9.1: No duplicate targets
    targets = [e["target_files"][0] for e in entries if "target_files" in e]
    target_counts = {}

    for target in targets:
        target_counts[target] = target_counts.get(target, 0) + 1

    duplicates = {t: c for t, c in target_counts.items() if c > 1}

    if duplicates:
        print(f"ERROR: {len(duplicates)} duplicate targets found:")
        for target, count in list(duplicates.items())[:10]:
            print(f"  {target}: {count} occurrences")
        raise ValueError("Duplicate targets detected")

    print("✓ No duplicate targets")

    # 9.2: Schema compliance
    for entry in entries:
        assert "id" in entry, f"Missing 'id' in entry"
        assert "source_file" in entry, f"Missing 'source_file' in entry {entry.get('id')}"
        assert "title" in entry, f"Missing 'title' in entry {entry.get('id')}"
        assert "categories" in entry, f"Missing 'categories' in entry {entry.get('id')}"

        has_target = "target_files" in entry
        has_no_content = entry.get("_no_content") == True
        assert has_target or has_no_content, f"Entry {entry['id']} needs target_files or _no_content"

        assert entry["id"].startswith(f"v{VERSION}-"), f"Invalid ID format: {entry['id']}"

        if "target_files" in entry:
            for target in entry["target_files"]:
                assert target.endswith(".json"), f"Target must end with .json: {target}"
                assert target == target.lower(), f"Target must be lowercase: {target}"
                assert "_" not in target, f"Target must not contain underscore: {target}"

    print("✓ Schema compliance validated")

    # 9.3: Category validation
    invalid_categories = []

    for entry in entries:
        for cat in entry["categories"]:
            if cat not in valid_category_ids:
                invalid_categories.append((entry['id'], cat))

    if invalid_categories:
        print(f"ERROR: {len(invalid_categories)} invalid categories:")
        for entry_id, cat in invalid_categories[:10]:
            print(f"  {entry_id}: {cat}")
        raise ValueError("Invalid categories detected")

    print("✓ Category validation passed")

    # 9.4: Source file existence
    missing_files = []

    for entry in entries:
        source_path = SOURCE_BASE / entry["source_file"]
        if not source_path.exists():
            missing_files.append(entry["source_file"])

    if missing_files:
        print(f"ERROR: {len(missing_files)} source files not found:")
        for file in missing_files[:10]:
            print(f"  {file}")
        raise FileNotFoundError("Source files missing")

    print("✓ All source files exist")

    # 9.5: Target path consistency
    valid_prefixes = ["features/", "guides/"]
    invalid_targets = []

    for entry in entries:
        if "target_files" in entry:
            for target in entry["target_files"]:
                if not any(target.startswith(prefix) for prefix in valid_prefixes):
                    invalid_targets.append((entry['id'], target))

    if invalid_targets:
        print(f"ERROR: {len(invalid_targets)} invalid target paths:")
        for entry_id, target in invalid_targets[:10]:
            print(f"  {entry_id}: {target}")
        raise ValueError("Invalid target paths detected")

    print("✓ Target path consistency validated")


def write_output(mapping: Dict) -> None:
    """Write output files (Step 10).

    Writes:
    - mapping-v6.json
    - mapping-v6.json.stats.txt

    Args:
        mapping: Mapping JSON structure
    """
    # Write JSON
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)

    print(f"✓ Written: {OUTPUT_FILE}")

    # Count stats
    entries = mapping["mappings"]
    with_targets = sum(1 for e in entries if 'target_files' in e)
    no_content = sum(1 for e in entries if e.get('_no_content'))

    print(f"  Total entries: {len(entries)}")
    print(f"  With targets: {with_targets}")
    print(f"  Navigation-only: {no_content}")

    # Count by category
    category_counts = {}
    for entry in entries:
        for cat in entry['categories']:
            category_counts[cat] = category_counts.get(cat, 0) + 1

    # Count by directory
    directory_counts = {}
    for entry in entries:
        if 'target_files' in entry:
            target = entry['target_files'][0]
            directory = '/'.join(target.split('/')[:2])
            directory_counts[directory] = directory_counts.get(directory, 0) + 1

    # Write stats file
    stats_content = f"""Mapping Statistics
==================

Version: {VERSION}
Created: {mapping['created_at']}

Totals
------
Total entries: {len(entries)}
With targets: {with_targets}
Navigation-only: {no_content}

By Category
-----------
"""

    for cat in sorted(category_counts.keys()):
        stats_content += f"{cat}: {category_counts[cat]}\n"

    stats_content += "\nBy Directory\n------------\n"

    for dir in sorted(directory_counts.keys()):
        stats_content += f"{dir}: {directory_counts[dir]}\n"

    stats_path = Path(f"{OUTPUT_FILE}.stats.txt")
    stats_path.write_text(stats_content, encoding='utf-8')

    print(f"✓ Written: {stats_path}")


def main():
    """Main execution."""
    print("=" * 80)
    print("Finalize Mapping - Steps 6-10")
    print("=" * 80)
    print()

    # Load valid category IDs
    print("Loading category definitions...")
    valid_category_ids = load_valid_category_ids()
    print(f"✓ Loaded {len(valid_category_ids)} valid categories")
    print()

    # Load input file
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    print(f"Loading: {INPUT_FILE}")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        input_data = json.load(f)

    verified_files = input_data["verified_files"]
    print(f"✓ Loaded {len(verified_files)} verified files")
    print()

    # Build mapping JSON (Steps 6-8)
    mapping = build_mapping_json(verified_files, valid_category_ids)
    print()

    # Validate mapping (Step 9)
    validate_mapping(mapping, valid_category_ids)
    print()

    # Write output (Step 10)
    write_output(mapping)
    print()

    print("=" * 80)
    print("Next step: Run export-to-excel-v6.py to create Excel export")
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

#!/usr/bin/env python3
"""Verify processing pattern coverage (Step 5).

This script:
1. Merges categorized files from Steps 1-4
2. Verifies all files for 7 processing patterns through content inspection
3. Adds missing processing pattern categories

Input: needs-ai-judgment-v6.json, categorized-ai-files-v6.json
Output: pattern-verified-v6.json
"""

import json
import sys
from pathlib import Path
from typing import List, Dict
from datetime import datetime


VERSION = "6"
SOURCE_BASE = Path(".lw/nab-official/v6")
CATEGORY_FILE = Path("doc/mapping-creation/categories-v6.json")
INPUT_FILE_1 = Path("doc/mapping-creation/work-v6/needs-ai-judgment-v6.json")
INPUT_FILE_2 = Path("doc/mapping-creation/work-v6/categorized-ai-files-v6.json")
OUTPUT_FILE = Path("doc/mapping-creation/work-v6/pattern-verified-v6.json")


# Processing pattern keywords (from Step 5 in prompt)
PATTERN_KEYWORDS = {
    "batch-nablarch": {
        "primary": ["nablarch batch", "file to db", "db to file", "db to db",
                    "nablarchbatchlet", "executioncontext"],
        "secondary": ["batch application", "batch process"]
    },
    "batch-jsr352": {
        "primary": ["jsr 352", "jsr352", "jakarta batch", "@batchproperty",
                    "itemreader", "itemwriter", "chunk", "batchlet"],
        "secondary": ["jakarta batch"]
    },
    "rest": {
        "primary": ["jax-rs", "@path", "@get", "@post", "rest api",
                    "restful", "bodyconverter"],
        "secondary": ["rest service", "restful web service"]
    },
    "http-messaging": {
        "primary": ["http messaging", "http send", "http receive",
                    "messagingprovider", "system integration"],
        "secondary": ["http message", "http communication"]
    },
    "web": {
        "primary": ["jsp", "html form", "web application", "httprequest",
                    "sessionstore", "hidden暗号化"],
        "secondary": ["web app", "jsp tag"]
    },
    "messaging-mom": {
        "primary": ["mom", "message queue", "jms", "messagesender",
                    "mom messaging"],
        "secondary": ["message oriented middleware"]
    },
    "messaging-db": {
        "primary": ["resident batch", "db messaging", "database polling",
                    "database queue", "テーブルをキュー"],
        "secondary": ["db message", "database messaging"]
    }
}


def load_processing_patterns() -> List[str]:
    """Load processing pattern IDs from category definitions.

    Returns:
        List of processing pattern IDs
    """
    with open(CATEGORY_FILE, 'r', encoding='utf-8') as f:
        category_defs = json.load(f)

    patterns = [
        cat["id"] for cat in category_defs["categories"]
        if cat["type"] == "processing-pattern"
    ]

    print(f"Processing patterns: {patterns}")
    return patterns


def read_file_content(file_path: Path, encoding: str = 'utf-8') -> str:
    """Read file content with encoding fallback.

    Args:
        file_path: Path to file
        encoding: File encoding

    Returns:
        File content as string
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError:
        if encoding == 'utf-8':
            return read_file_content(file_path, 'shift-jis')
        else:
            raise


def get_processing_patterns(file_path: Path, existing_categories: List[str]) -> List[str]:
    """Determine which processing patterns apply to this file (Step 5).

    Uses keyword matching with primary and secondary keywords.

    Args:
        file_path: Path to file
        existing_categories: Categories already assigned

    Returns:
        List of processing pattern IDs
    """
    patterns = []

    # Read file content
    try:
        content = read_file_content(file_path)
    except Exception:
        # If can't read, return existing patterns (if any)
        return [c for c in existing_categories if c in PATTERN_KEYWORDS.keys()]

    content_lower = content.lower()

    # Check each processing pattern
    for pattern, keywords in PATTERN_KEYWORDS.items():
        # Check primary keywords
        if any(kw in content_lower for kw in keywords["primary"]):
            patterns.append(pattern)
            continue

        # Check secondary keywords (if primary not found)
        if any(kw in content_lower for kw in keywords.get("secondary", [])):
            patterns.append(pattern)

    # Special case: avoid confusion between REST and HTTP messaging
    if "rest" in patterns and "http-messaging" in patterns:
        # If both detected, check which is more prominent
        rest_count = sum(content_lower.count(kw) for kw in PATTERN_KEYWORDS["rest"]["primary"])
        http_msg_count = sum(content_lower.count(kw) for kw in PATTERN_KEYWORDS["http-messaging"]["primary"])

        if rest_count > http_msg_count:
            patterns.remove("http-messaging")
        elif http_msg_count > rest_count:
            patterns.remove("rest")
        # If equal, keep both

    return patterns


def main():
    """Main execution."""
    print("=" * 80)
    print("Verify Processing Pattern Coverage - Step 5")
    print("=" * 80)
    print()

    # Load processing patterns
    print("Loading processing pattern definitions...")
    processing_patterns = load_processing_patterns()
    print()

    # Load input files
    print(f"Loading: {INPUT_FILE_1}")
    with open(INPUT_FILE_1, 'r', encoding='utf-8') as f:
        data1 = json.load(f)

    print(f"Loading: {INPUT_FILE_2}")
    with open(INPUT_FILE_2, 'r', encoding='utf-8') as f:
        data2 = json.load(f)

    # Merge all categorized files
    all_files = data1["categorized_files"] + data2["categorized_ai_files"]
    print(f"Total files to process: {len(all_files)}")
    print()

    # Verify processing patterns for all files
    print("Verifying processing pattern coverage...")
    pattern_added_count = 0
    files_with_patterns = 0

    for i, entry in enumerate(all_files, 1):
        # Skip files marked as no_content
        if entry.get("_no_content"):
            continue

        source_file = entry["source_file"]
        file_path = SOURCE_BASE / source_file
        existing_categories = entry.get("categories", [])

        if i % 50 == 0:
            print(f"  Processed {i}/{len(all_files)} files...")

        # Get processing patterns from content
        patterns = get_processing_patterns(file_path, existing_categories)

        # Add new patterns not already assigned
        patterns_added = []
        for pattern in patterns:
            if pattern not in existing_categories:
                existing_categories.append(pattern)
                patterns_added.append(pattern)

        if len(patterns_added) > 0:
            pattern_added_count += 1
            entry["categories"] = existing_categories
            entry["_patterns_added"] = patterns_added

        if len([p for p in existing_categories if p in processing_patterns]) > 0:
            files_with_patterns += 1

    print(f"✓ Pattern verification complete")
    print(f"  Files with patterns added: {pattern_added_count}")
    print(f"  Files with at least one pattern: {files_with_patterns}")
    print()

    # Count pattern statistics
    pattern_counts = {p: 0 for p in processing_patterns}
    for entry in all_files:
        if entry.get("_no_content"):
            continue
        for cat in entry.get("categories", []):
            if cat in pattern_counts:
                pattern_counts[cat] += 1

    # Prepare output
    output_data = {
        "schema_version": "1.0",
        "version": VERSION,
        "created_at": datetime.now().isoformat(),
        "verified_files": all_files,
        "stats": {
            "total_files": len(all_files),
            "files_with_patterns_added": pattern_added_count,
            "files_with_at_least_one_pattern": files_with_patterns,
            "pattern_counts": pattern_counts
        }
    }

    # Write output
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"✓ Written: {OUTPUT_FILE}")
    print()

    # Print summary
    print("Summary")
    print("-------")
    print(f"Total files: {output_data['stats']['total_files']}")
    print(f"Files with patterns added: {output_data['stats']['files_with_patterns_added']}")
    print(f"Files with at least one pattern: {output_data['stats']['files_with_at_least_one_pattern']}")
    print()
    print("Pattern counts:")
    for pattern, count in sorted(output_data['stats']['pattern_counts'].items()):
        print(f"  {pattern}: {count}")
    print()

    print("=" * 80)
    print("Next step: Run finalize-mapping-v6.py to generate final mapping")
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

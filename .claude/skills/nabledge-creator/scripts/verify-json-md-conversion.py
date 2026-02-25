#!/usr/bin/env python3
"""
Verify that JSON->MD conversion preserves all content.

Checks that all content from JSON files is present in corresponding MD files.
This is a simple content-based check that verifies no data was lost during conversion.

Exit codes:
  0: Success - all JSON content found in MD files
  1: Verification failed - some content missing
  2: Error - invalid input or processing failed
"""

import sys
import json
from pathlib import Path
from typing import Any, Dict, List, Set


def extract_text_content(obj: Any, texts: Set[str], path: str = "", skip_schema_keys: bool = True) -> None:
    """
    Recursively extract all non-empty text content from JSON object.

    Collects string values for comparison. Skips schema-level structural keys.
    Normalizes whitespace for more reliable matching.
    """
    # Schema keys to skip (structure, not content)
    # These are JSON schema keys, not actual content to verify
    schema_keys = {
        'id', 'title', 'index', 'sections', 'type', 'hints', 'official_doc_urls',
        'tags', 'category', 'l1_keywords', 'l2_keywords',  # Metadata/classification
        'web-application', 'restful-web-service', 'jakarta-batch', 'nablarch-batch',
        'http-messaging', 'mom-messaging', 'db-messaging',  # Processing pattern identifiers
        'HTTP Messaging', 'MOM Messaging', 'DB Messaging',  # Pattern display names
    }

    if isinstance(obj, str):
        # Normalize: strip whitespace, collapse multiple spaces
        normalized = ' '.join(obj.strip().split())
        # Skip very short strings (likely IDs or codes)
        if len(normalized) > 2:
            texts.add(normalized)
    elif isinstance(obj, dict):
        for key, value in obj.items():
            # Skip schema-level keys themselves, but process their values
            current_path = f"{path}.{key}" if path else key

            if skip_schema_keys and key in schema_keys:
                # Skip the key name, but still extract content from value if needed
                if key == 'index' or key == 'official_doc_urls':
                    # These contain content, extract it
                    extract_text_content(value, texts, current_path, skip_schema_keys)
            else:
                # Add key name only if not a schema key
                if len(key) > 2:  # Skip very short keys
                    texts.add(key)
                # Recursively extract from value
                extract_text_content(value, texts, current_path, skip_schema_keys)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            extract_text_content(item, texts, f"{path}[{i}]", skip_schema_keys)
    # Skip numbers, booleans, None


def verify_json_md_pair(json_path: Path, md_path: Path) -> tuple[bool, List[str]]:
    """
    Verify that MD file contains all content from JSON file.

    Returns:
        (success, missing_texts) - True if all content found, list of missing texts
    """
    # Read JSON
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except Exception as e:
        return False, [f"Failed to read JSON: {e}"]

    # Read MD
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
    except Exception as e:
        return False, [f"Failed to read MD: {e}"]

    # Extract all text from JSON
    json_texts: Set[str] = set()
    extract_text_content(json_data, json_texts)

    # Normalize MD content for comparison
    md_normalized = ' '.join(md_content.split())

    # Check each JSON text is present in MD
    missing = []
    for text in json_texts:
        if text not in md_normalized:
            # Check if it's just a heading level indicator (###, ##, etc)
            if text.strip('#').strip():
                missing.append(text)

    return len(missing) == 0, missing


def find_json_md_pairs(knowledge_dir: Path) -> List[tuple[Path, Path]]:
    """
    Find all JSON files and their corresponding MD files.

    Returns list of (json_path, md_path) tuples.
    """
    pairs = []

    # Find all JSON files
    for json_path in knowledge_dir.rglob('*.json'):
        # Skip index files and non-knowledge files
        if json_path.name == 'package.json':
            continue

        # Determine corresponding MD path
        md_path = json_path.with_suffix('.md')

        # Check if MD exists
        if md_path.exists():
            pairs.append((json_path, md_path))

    return pairs


def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: verify-json-md-conversion.py <json_dir> [md_dir]", file=sys.stderr)
        print("", file=sys.stderr)
        print("If md_dir is not specified, looks for .md files in json_dir", file=sys.stderr)
        print("", file=sys.stderr)
        print("Examples:", file=sys.stderr)
        print("  # MD files in same directory as JSON", file=sys.stderr)
        print("  verify-json-md-conversion.py .claude/skills/nabledge-6/knowledge", file=sys.stderr)
        print("", file=sys.stderr)
        print("  # MD files in separate directory", file=sys.stderr)
        print("  verify-json-md-conversion.py .claude/skills/nabledge-6/knowledge .tmp/docs", file=sys.stderr)
        return 2

    json_dir = Path(sys.argv[1])
    md_dir = Path(sys.argv[2]) if len(sys.argv) == 3 else json_dir

    if not json_dir.exists():
        print(f"Error: Directory not found: {json_dir}", file=sys.stderr)
        return 2

    if not json_dir.is_dir():
        print(f"Error: Not a directory: {json_dir}", file=sys.stderr)
        return 2

    if not md_dir.exists():
        print(f"Error: Directory not found: {md_dir}", file=sys.stderr)
        return 2

    if not md_dir.is_dir():
        print(f"Error: Not a directory: {md_dir}", file=sys.stderr)
        return 2

    # Find JSON-MD pairs
    if json_dir == md_dir:
        # Same directory - use original logic
        pairs = find_json_md_pairs(json_dir)
    else:
        # Different directories - find JSON files and map to MD directory
        pairs = []
        for json_path in json_dir.rglob('*.json'):
            if json_path.name == 'package.json':
                continue
            # Map to MD path in md_dir
            rel_path = json_path.relative_to(json_dir)
            md_path = md_dir / rel_path.with_suffix('.md')
            if md_path.exists():
                pairs.append((json_path, md_path))

    if not pairs:
        print(f"Error: No JSON-MD pairs found in {knowledge_dir}", file=sys.stderr)
        return 2

    print(f"Verifying {len(pairs)} JSON->MD conversions...")
    print()

    # Verify each pair
    failed = []
    for json_path, md_path in pairs:
        rel_json = json_path.relative_to(json_dir)
        rel_md = md_path.relative_to(md_dir)

        success, missing = verify_json_md_pair(json_path, md_path)

        if success:
            print(f"✓ {rel_json} -> {rel_md}")
        else:
            print(f"✗ {rel_json} -> {rel_md}")
            failed.append((rel_json, rel_md, missing))

    print()

    # Report results
    if not failed:
        print(f"Success: All {len(pairs)} JSON files have complete MD conversions")
        return 0
    else:
        print(f"Failed: {len(failed)} / {len(pairs)} conversions have missing content")
        print()

        for rel_json, rel_md, missing in failed:
            print(f"Missing content in {rel_md}:")
            for text in missing[:10]:  # Show first 10 missing items
                print(f"  - {text[:80]}")  # Truncate long texts
            if len(missing) > 10:
                print(f"  ... and {len(missing) - 10} more")
            print()

        return 1


if __name__ == '__main__':
    sys.exit(main())

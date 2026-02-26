#!/usr/bin/env python3
"""
Verify that JSON content is fully present in converted MD files.

This script checks that all text content from JSON knowledge files
is preserved in their converted Markdown versions.

Exit codes:
  0: All content verified successfully
  1: Content missing or mismatch found
  2: Script error (file not found, invalid arguments, etc.)
"""

import sys
import json
from pathlib import Path
from typing import Any, List, Tuple


def extract_text_from_value(value: Any) -> List[str]:
    """Extract all text strings from a JSON value recursively."""
    texts = []

    if isinstance(value, str):
        # Skip empty strings and whitespace-only
        cleaned = value.strip()
        if cleaned:
            texts.append(cleaned)
    elif isinstance(value, list):
        for item in value:
            texts.extend(extract_text_from_value(item))
    elif isinstance(value, dict):
        for v in value.values():
            texts.extend(extract_text_from_value(v))

    return texts


def extract_all_json_text(json_path: Path) -> List[str]:
    """Extract all text content from JSON file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    texts = []

    # Extract from all fields except metadata
    skip_fields = {'id', 'index'}  # Skip structural metadata

    for key, value in data.items():
        if key not in skip_fields:
            texts.extend(extract_text_from_value(value))

    return texts


def read_md_content(md_path: Path) -> str:
    """Read full content from Markdown file."""
    with open(md_path, 'r', encoding='utf-8') as f:
        return f.read()


def verify_content(json_path: Path, md_path: Path) -> Tuple[bool, List[str]]:
    """
    Verify that all JSON text content is present in MD file.

    Returns:
        (success, missing_texts): success is True if all content found,
                                  missing_texts contains any missing strings
    """
    # Extract all text from JSON
    json_texts = extract_all_json_text(json_path)

    if not md_path.exists():
        return False, [f"MD file not found: {md_path}"]

    # Read MD content
    md_content = read_md_content(md_path)

    # Check each JSON text is present in MD
    missing = []
    for text in json_texts:
        if text not in md_content:
            # For long texts, show first 100 chars
            display_text = text if len(text) <= 100 else text[:100] + "..."
            missing.append(display_text)

    return len(missing) == 0, missing


def main():
    if len(sys.argv) < 3:
        print("Usage: python verify-json-md-content.py JSON_DIR MD_DIR")
        print()
        print("Verify that JSON content is fully present in converted MD files.")
        print()
        print("Arguments:")
        print("  JSON_DIR  Directory containing JSON knowledge files")
        print("  MD_DIR    Directory containing converted MD files")
        print()
        print("Exit codes:")
        print("  0  All content verified successfully")
        print("  1  Content missing or mismatch found")
        print("  2  Script error (file not found, invalid arguments)")
        sys.exit(2)

    json_dir = Path(sys.argv[1])
    md_dir = Path(sys.argv[2])

    if not json_dir.exists():
        print(f"ERROR: JSON directory not found: {json_dir}")
        sys.exit(2)

    if not md_dir.exists():
        print(f"ERROR: MD directory not found: {md_dir}")
        sys.exit(2)

    # Find all JSON files (exclude index.toon)
    json_files = [f for f in json_dir.rglob('*.json') if f.name != 'index.toon']

    if not json_files:
        print(f"No JSON files found in {json_dir}")
        sys.exit(0)

    print(f"Verifying {len(json_files)} JSON-MD file pairs...")
    print()

    failed_files = []

    for json_file in sorted(json_files):
        # Calculate expected MD path
        relative_path = json_file.relative_to(json_dir)
        md_file = md_dir / relative_path.with_suffix('.md')

        # Verify content
        success, missing = verify_content(json_file, md_file)

        if success:
            print(f"✓ {json_file.name}")
        else:
            print(f"✗ {json_file.name}")
            print(f"  MD file: {md_file}")
            print(f"  Missing {len(missing)} text(s):")
            for i, text in enumerate(missing[:5], 1):  # Show first 5
                print(f"    {i}. {text}")
            if len(missing) > 5:
                print(f"    ... and {len(missing) - 5} more")
            print()
            failed_files.append(json_file.name)

    print()
    print("=" * 60)
    if failed_files:
        print(f"FAILED: {len(failed_files)} file(s) have missing content")
        print()
        print("Failed files:")
        for name in failed_files:
            print(f"  - {name}")
        sys.exit(1)
    else:
        print(f"SUCCESS: All {len(json_files)} file(s) verified")
        print("All JSON content is present in MD files")
        sys.exit(0)


if __name__ == '__main__':
    main()

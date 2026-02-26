#!/usr/bin/env python3
"""
Verify that all JSON content is present in converted MD file.

Exit codes:
  0: All JSON content found in MD
  1: Missing content detected
  2: Error (file not found, invalid JSON, etc.)

Usage:
    python verify-json-md-content.py INPUT.json OUTPUT.md
"""

import sys
import json
from pathlib import Path


def extract_all_string_values(obj, values=None, skip_keys=None):
    """
    Recursively extract all string values from JSON object.

    Returns a set of all non-empty string values found in the JSON.
    This includes:
    - String values in dictionaries (not keys)
    - String items in lists
    - Nested strings at any depth

    Args:
        obj: JSON object to extract from
        values: Set to accumulate values (internal use)
        skip_keys: Set of keys to skip (metadata keys like 'id', 'hints', etc.)
    """
    if values is None:
        values = set()
    if skip_keys is None:
        # Skip common metadata keys that might not appear in MD
        skip_keys = {'id', 'hints', 'index'}

    if isinstance(obj, dict):
        for key, value in obj.items():
            # Skip metadata keys
            if key in skip_keys:
                continue
            # Recurse into value (don't add keys themselves)
            extract_all_string_values(value, values, skip_keys)
    elif isinstance(obj, list):
        for item in obj:
            extract_all_string_values(item, values, skip_keys)
    elif isinstance(obj, str) and obj.strip():
        # Add non-empty string values only
        values.add(obj)

    return values


def verify_content(json_path, md_path):
    """
    Verify all JSON content is present in MD file.

    Returns:
        (bool, list): (success, list of missing values)
    """
    # Read JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    # Read MD
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Extract all string values from JSON
    json_values = extract_all_string_values(json_data)

    # Check which values are missing from MD
    missing = []
    for value in sorted(json_values):
        if value not in md_content:
            missing.append(value)

    return len(missing) == 0, missing


def main():
    if len(sys.argv) != 3:
        print("Usage: verify-json-md-content.py INPUT.json OUTPUT.md", file=sys.stderr)
        sys.exit(2)

    json_path = sys.argv[1]
    md_path = sys.argv[2]

    # Validate inputs
    if not Path(json_path).exists():
        print(f"Error: JSON file not found: {json_path}", file=sys.stderr)
        sys.exit(2)

    if not Path(md_path).exists():
        print(f"Error: MD file not found: {md_path}", file=sys.stderr)
        sys.exit(2)

    # Verify content
    try:
        success, missing = verify_content(json_path, md_path)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {json_path}: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)

    # Report results
    if success:
        print(f"✓ All JSON content found in MD")
        print(f"  JSON: {json_path}")
        print(f"  MD:   {md_path}")
        sys.exit(0)
    else:
        print(f"✗ Missing content detected", file=sys.stderr)
        print(f"  JSON: {json_path}", file=sys.stderr)
        print(f"  MD:   {md_path}", file=sys.stderr)
        print(f"  Missing values ({len(missing)}):", file=sys.stderr)
        for value in missing[:10]:  # Show first 10
            print(f"    - {value}", file=sys.stderr)
        if len(missing) > 10:
            print(f"    ... and {len(missing) - 10} more", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

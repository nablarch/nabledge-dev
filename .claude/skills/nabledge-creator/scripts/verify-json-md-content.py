#!/usr/bin/env python3
"""
Verify that all JSON knowledge file content is present in corresponding MD files.

This script ensures json->md conversion is complete and no content is lost.

Exit codes:
  0: Success (all content verified)
  1: Verification failed (content missing)
  2: Error (invalid input, file not found)
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Set


def extract_text_content(obj: Any, collected: Set[str]) -> None:
    """
    Recursively extract all text content from JSON object.

    Collects all string values (excluding keys) into the collected set.
    Normalizes whitespace for comparison.
    """
    if isinstance(obj, str):
        # Normalize whitespace and add non-empty strings
        normalized = ' '.join(obj.split())
        if normalized and len(normalized) > 2:  # Skip very short strings
            collected.add(normalized)
    elif isinstance(obj, list):
        for item in obj:
            extract_text_content(item, collected)
    elif isinstance(obj, dict):
        for value in obj.values():
            extract_text_content(value, collected)


def normalize_md_content(md_text: str) -> str:
    """
    Normalize MD content for comparison.

    - Remove markdown formatting (**, ##, -, |, etc.)
    - Normalize whitespace
    - Convert to lowercase for case-insensitive comparison
    """
    # Remove code block markers
    md_text = md_text.replace('```', '')
    # Remove markdown formatting
    for char in ['**', '##', '#', '-', '|', '*']:
        md_text = md_text.replace(char, ' ')
    # Normalize whitespace
    md_text = ' '.join(md_text.split())
    return md_text.lower()


def verify_json_md_pair(json_path: Path, md_path: Path) -> tuple[bool, List[str]]:
    """
    Verify JSON content is present in MD file.

    Returns (success, missing_content_list)
    """
    # Read JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    # Extract all text content from JSON
    json_content = set()
    extract_text_content(json_data, json_content)

    # Read MD
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Normalize MD content
    md_normalized = normalize_md_content(md_text)

    # Check each JSON content string is in MD
    missing = []
    for content in json_content:
        # Normalize JSON content for comparison
        content_normalized = normalize_md_content(content)
        if content_normalized not in md_normalized:
            missing.append(content)

    return len(missing) == 0, missing


def find_json_md_pairs(knowledge_dir: Path) -> List[tuple[Path, Path]]:
    """
    Find all JSON/MD file pairs in knowledge directory.

    Returns list of (json_path, md_path) tuples.
    """
    pairs = []

    for json_file in knowledge_dir.rglob('*.json'):
        # Skip index.json
        if json_file.name == 'index.json':
            continue

        # Find corresponding MD file
        md_file = json_file.with_suffix('.md')
        if md_file.exists():
            pairs.append((json_file, md_file))
        else:
            print(f"Warning: No MD file for {json_file.relative_to(knowledge_dir)}", file=sys.stderr)

    return pairs


def main():
    if len(sys.argv) < 2:
        print("Usage: verify-json-md-content.py KNOWLEDGE_DIR", file=sys.stderr)
        print("", file=sys.stderr)
        print("Example: verify-json-md-content.py .claude/skills/nabledge-6/knowledge", file=sys.stderr)
        sys.exit(2)

    knowledge_dir = Path(sys.argv[1])

    if not knowledge_dir.exists():
        print(f"Error: Knowledge directory not found: {knowledge_dir}", file=sys.stderr)
        sys.exit(2)

    # Find all JSON/MD pairs
    pairs = find_json_md_pairs(knowledge_dir)

    if len(pairs) == 0:
        print(f"Error: No JSON/MD pairs found in {knowledge_dir}", file=sys.stderr)
        sys.exit(2)

    print(f"Verifying {len(pairs)} JSON/MD pairs...", file=sys.stderr)

    # Verify each pair
    failed = []
    for json_path, md_path in pairs:
        success, missing = verify_json_md_pair(json_path, md_path)
        if not success:
            rel_path = json_path.relative_to(knowledge_dir)
            failed.append({
                'file': str(rel_path),
                'missing_count': len(missing),
                'missing_samples': missing[:3],  # Show first 3 missing items
            })

    # Report results
    if len(failed) == 0:
        print(f"\n✓ All {len(pairs)} files verified successfully", file=sys.stderr)
        print(f"  All JSON content is present in corresponding MD files", file=sys.stderr)
        sys.exit(0)
    else:
        print(f"\n✗ Verification failed for {len(failed)} files:", file=sys.stderr)
        for fail in failed:
            print(f"\n  File: {fail['file']}", file=sys.stderr)
            print(f"  Missing content items: {fail['missing_count']}", file=sys.stderr)
            print(f"  Sample missing content:", file=sys.stderr)
            for sample in fail['missing_samples']:
                # Truncate long samples
                truncated = sample[:100] + '...' if len(sample) > 100 else sample
                print(f"    - {truncated}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

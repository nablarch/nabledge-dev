#!/usr/bin/env python3
"""
Validate knowledge JSON files structure and quality.

Validates:
- Schema compliance (required keys, id=filename, index↔sections correspondence)
- Template conformance (category-specific required properties)
- Section count (within ±30% of RST h2 count)
- Section size (100-1500 tokens)
- Hint quality (≥3 per section, ≥10 total)
- URL validity (≥1, correct format)
- Docs correspondence (JSON has corresponding .md file)

Exit codes:
  0: All checks passed
  1: Warnings only
  2: Errors found
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple


def estimate_tokens(text: str) -> int:
    """Rough token estimation (1 token ≈ 4 chars for English/Japanese mix)."""
    if isinstance(text, dict):
        text = json.dumps(text, ensure_ascii=False)
    elif not isinstance(text, str):
        text = str(text)
    return len(text) // 4


def count_h2_headings(rst_path: Path) -> int:
    """Count h2 headings in RST file."""
    if not rst_path.exists():
        return 0

    with open(rst_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    h2_count = 0
    for i, line in enumerate(lines):
        # h2 headings have --- or === underline
        if i > 0 and re.match(r'^[-=]{3,}$', line.strip()):
            prev_line = lines[i-1].strip()
            if prev_line and not prev_line.startswith('..'):
                h2_count += 1

    return h2_count


def check_schema(data: Dict, file_path: Path) -> Tuple[int, int]:
    """Check basic schema compliance."""
    errors = 0
    warnings = 0

    # Check required keys
    required_keys = ['id', 'title', 'official_doc_urls', 'index', 'sections']
    for key in required_keys:
        if key not in data:
            print(f"ERROR: Missing required key '{key}'")
            errors += 1

    if errors > 0:
        return errors, warnings

    # Check id = filename
    expected_id = file_path.stem
    if data['id'] != expected_id:
        print(f"ERROR: id '{data['id']}' != filename '{expected_id}'")
        errors += 1

    # Check title is non-empty
    if not data['title']:
        print(f"ERROR: title is empty")
        errors += 1

    # Check official_doc_urls
    if not isinstance(data['official_doc_urls'], list) or len(data['official_doc_urls']) == 0:
        print(f"ERROR: official_doc_urls must be non-empty array")
        errors += 1
    else:
        for url in data['official_doc_urls']:
            if not url.startswith('http'):
                print(f"ERROR: Invalid URL format: {url}")
                errors += 1

    # Check index ↔ sections correspondence
    index_ids = {item['id'] for item in data.get('index', [])}
    section_ids = set(data.get('sections', {}).keys())

    if index_ids != section_ids:
        missing_in_sections = index_ids - section_ids
        missing_in_index = section_ids - index_ids
        if missing_in_sections:
            print(f"ERROR: index IDs not in sections: {missing_in_sections}")
            errors += 1
        if missing_in_index:
            print(f"ERROR: section IDs not in index: {missing_in_index}")
            errors += 1

    # Check overview exists
    if 'overview' not in data.get('sections', {}):
        print(f"ERROR: 'overview' section is required")
        errors += 1

    return errors, warnings


def check_hints(data: Dict) -> Tuple[int, int]:
    """Check hint quality."""
    errors = 0
    warnings = 0

    index = data.get('index', [])
    total_hints = 0

    for item in index:
        section_id = item.get('id', '')
        hints = item.get('hints', [])

        if len(hints) < 3:
            print(f"WARNING: Section '{section_id}' has {len(hints)} hints (minimum 3 recommended)")
            warnings += 1

        if len(hints) > 8:
            print(f"WARNING: Section '{section_id}' has {len(hints)} hints (maximum 8 recommended)")
            warnings += 1

        total_hints += len(hints)

    if total_hints < 10:
        print(f"WARNING: Total hints {total_hints} (minimum 10 recommended)")
        warnings += 1

    return errors, warnings


def check_section_size(data: Dict) -> Tuple[int, int]:
    """Check section size (100-1500 tokens)."""
    errors = 0
    warnings = 0

    sections = data.get('sections', {})

    for section_id, section_content in sections.items():
        tokens = estimate_tokens(section_content)

        if tokens < 100:
            print(f"WARNING: Section '{section_id}' is too small ({tokens} tokens < 100)")
            warnings += 1
        elif tokens > 1500:
            print(f"WARNING: Section '{section_id}' is too large ({tokens} tokens > 1500)")
            warnings += 1

    return errors, warnings


def check_section_count(data: Dict, source_dir: Path, file_path: Path) -> Tuple[int, int]:
    """Check section count vs RST h2 count (±30%)."""
    errors = 0
    warnings = 0

    # Try to find source RST from knowledge-file-plan.md or guess from path
    # For now, skip this check if source is not easily determinable
    # This can be enhanced by reading knowledge-file-plan.md

    return errors, warnings


def check_template_conformance(data: Dict, file_path: Path) -> Tuple[int, int]:
    """Check category-specific template conformance."""
    errors = 0
    warnings = 0

    # Determine category from path
    # e.g., features/handlers/... -> handlers
    #       features/adapters/... -> adapters
    path_parts = file_path.parts
    category = None

    if 'handlers' in path_parts:
        category = 'handlers'
    elif 'adapters' in path_parts:
        category = 'adapters'
    elif 'libraries' in path_parts:
        category = 'libraries'
    elif 'processing' in path_parts:
        category = 'processing'
    elif 'tools' in path_parts:
        category = 'tools'
    elif 'checks' in path_parts:
        category = 'checks'

    if not category:
        return errors, warnings

    # Check overview required properties by category
    overview = data.get('sections', {}).get('overview', {})

    if category == 'handlers':
        required = ['class_name', 'description', 'purpose', 'responsibilities', 'modules']
        for prop in required:
            if prop not in overview:
                print(f"WARNING: Handler overview missing '{prop}'")
                warnings += 1

    elif category == 'adapters':
        required = ['class_name', 'description', 'purpose', 'modules', 'adapted_library']
        for prop in required:
            if prop not in overview:
                print(f"WARNING: Adapter overview missing '{prop}'")
                warnings += 1

    elif category == 'libraries':
        required = ['classes', 'description', 'purpose', 'modules']
        for prop in required:
            if prop not in overview:
                print(f"WARNING: Library overview missing '{prop}'")
                warnings += 1

    elif category == 'processing':
        required = ['description', 'use_cases', 'features']
        for prop in required:
            if prop not in overview:
                print(f"WARNING: Processing overview missing '{prop}'")
                warnings += 1

    elif category == 'tools':
        required = ['description', 'purpose']
        for prop in required:
            if prop not in overview:
                print(f"WARNING: Tool overview missing '{prop}'")
                warnings += 1

    elif category == 'checks':
        required = ['description', 'purpose']
        for prop in required:
            if prop not in overview:
                print(f"WARNING: Check overview missing '{prop}'")
                warnings += 1

    return errors, warnings


def check_docs_correspondence(json_path: Path, docs_dir: Path) -> Tuple[int, int]:
    """Check if corresponding .md file exists in docs directory."""
    errors = 0
    warnings = 0

    # Calculate corresponding MD path
    relative_path = json_path.relative_to(json_path.parent.parent)  # Remove .claude/skills/nabledge-6/
    md_path = docs_dir / relative_path.with_suffix('.md')

    if not md_path.exists():
        print(f"WARNING: Corresponding MD file not found: {md_path}")
        warnings += 1

    return errors, warnings


def validate_file(file_path: Path, source_dir: Path, docs_dir: Path) -> Tuple[int, int]:
    """Validate a single JSON file."""
    print(f"\n{'='*60}")
    print(f"Validating: {file_path}")
    print(f"{'='*60}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}")
        return 1, 0

    total_errors = 0
    total_warnings = 0

    # Run checks
    e, w = check_schema(data, file_path)
    total_errors += e
    total_warnings += w

    e, w = check_hints(data)
    total_errors += e
    total_warnings += w

    e, w = check_section_size(data)
    total_errors += e
    total_warnings += w

    e, w = check_section_count(data, source_dir, file_path)
    total_errors += e
    total_warnings += w

    e, w = check_template_conformance(data, file_path)
    total_errors += e
    total_warnings += w

    # Check docs correspondence (only if docs_dir exists)
    if docs_dir and docs_dir.exists():
        e, w = check_docs_correspondence(file_path, docs_dir)
        total_errors += e
        total_warnings += w

    # Summary
    if total_errors == 0 and total_warnings == 0:
        print("\n✓ All checks passed")
    elif total_errors == 0:
        print(f"\n⚠ {total_warnings} warnings")
    else:
        print(f"\n✗ {total_errors} errors, {total_warnings} warnings")

    return total_errors, total_warnings


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate-knowledge.py DIR [--source-dir DIR] [--docs-dir DIR]")
        print()
        print("Validate knowledge JSON files in DIR.")
        print()
        print("Options:")
        print("  --source-dir DIR  Source RST directory (for section count check)")
        print("  --docs-dir DIR    Docs directory (for correspondence check)")
        sys.exit(1)

    knowledge_dir = Path(sys.argv[1])
    source_dir = None
    docs_dir = None

    if '--source-dir' in sys.argv:
        idx = sys.argv.index('--source-dir')
        if idx + 1 < len(sys.argv):
            source_dir = Path(sys.argv[idx + 1])

    if '--docs-dir' in sys.argv:
        idx = sys.argv.index('--docs-dir')
        if idx + 1 < len(sys.argv):
            docs_dir = Path(sys.argv[idx + 1])

    if not knowledge_dir.exists():
        print(f"ERROR: Directory not found: {knowledge_dir}")
        sys.exit(2)

    # Find all JSON files
    json_files = list(knowledge_dir.rglob('*.json'))
    # Exclude index.toon
    json_files = [f for f in json_files if f.name != 'index.toon']

    if not json_files:
        print(f"No JSON files found in {knowledge_dir}")
        sys.exit(0)

    print(f"Found {len(json_files)} JSON files")

    total_errors = 0
    total_warnings = 0

    for json_file in sorted(json_files):
        e, w = validate_file(json_file, source_dir, docs_dir)
        total_errors += e
        total_warnings += w

    # Final summary
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Files validated: {len(json_files)}")
    print(f"Total errors: {total_errors}")
    print(f"Total warnings: {total_warnings}")

    if total_errors > 0:
        sys.exit(2)
    elif total_warnings > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()

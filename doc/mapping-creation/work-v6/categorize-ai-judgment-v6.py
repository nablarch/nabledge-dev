#!/usr/bin/env python3
"""Categorize files needing AI judgment (Step 4).

This script:
1. Checks if files are navigation-only
2. Categorizes by content using technical indicators
3. Assigns default 'about' category if no match

Input: needs-ai-judgment-v6.json
Output: categorized-ai-files-v6.json
"""

import json
import sys
from pathlib import Path
from typing import List, Tuple
from datetime import datetime


VERSION = "6"
SOURCE_BASE = Path(".lw/nab-official/v6")
INPUT_FILE = Path("doc/mapping-creation/work-v6/needs-ai-judgment-v6.json")
OUTPUT_FILE = Path("doc/mapping-creation/work-v6/categorized-ai-files-v6.json")


# Technical indicators by category (from Step 4.2 in prompt)
CATEGORY_KEYWORDS = {
    "handler": ["handler", "handler queue", "handlerqueue", "request processing"],
    "library": ["library", "repository", "utility", "common library", "framework core"],
    "adaptor": ["adaptor", "integration", "third-party", "external system"],
    "tool": ["testing framework", "toolbox", "static analysis", "development tool"],
    "security-check": ["authentication", "authorization", "permission", "csrf", "xss", "security"],
    "setup": ["blank project", "project setup", "getting started", "first step", "tutorial", "client create"],
    "configuration": ["configuration", "settings", "environment", "properties", "xml config"],
    "migration": ["migration", "upgrade", "version change", "compatibility"],
    "release": ["release", "version", "リリース", "バージョン", "release note", "releasenote"],
    "about": ["overview", "introduction", "concept", "framework structure", "external content", "useful content", "biz sample", "implementation example", "use case"]
}


def read_file_content(file_path: Path, max_lines: int = None, encoding: str = 'utf-8') -> str:
    """Read file content with encoding fallback.

    Args:
        file_path: Path to file
        max_lines: Maximum lines to read (None = all)
        encoding: File encoding

    Returns:
        File content as string
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            if max_lines:
                lines = [f.readline() for _ in range(max_lines)]
                content = ''.join(lines)
            else:
                content = f.read()
        return content
    except UnicodeDecodeError:
        # Try alternate encoding
        if encoding == 'utf-8':
            return read_file_content(file_path, max_lines, 'shift-jis')
        else:
            raise


def is_navigation_only(file_path: Path) -> Tuple[bool, str]:
    """Check if file is navigation-only (Step 4.1).

    Indicators of navigation-only:
    - File contains only .. toctree:: directives (RST)
    - File contains only bulleted/numbered link lists
    - File has <50 words of prose (excluding directives and links)
    - No code examples, configurations, or technical explanations

    Args:
        file_path: Path to file

    Returns:
        Tuple of (is_nav_only, reason)
    """
    try:
        content = read_file_content(file_path, max_lines=100)
    except Exception as e:
        return (True, f"Unreadable: {e}")

    # Count toctree directives
    toctree_count = content.count('.. toctree::')

    # Count code blocks
    code_block_count = content.count('```') + content.count('::')

    # Count words (rough estimate - words with >3 characters)
    words = [w for w in content.split() if len(w) > 3]
    word_count = len(words)

    # Decision logic
    if toctree_count > 0 and code_block_count == 0 and word_count < 50:
        return (True, "Navigation only (toctree without technical content)")

    if word_count < 30:
        return (True, "Minimal content (< 30 words)")

    return (False, "")


def categorize_by_content(file_path: Path) -> List[str]:
    """Analyze file content and assign categories (Step 4.2).

    Uses technical indicator keywords to determine categories.
    Also uses path patterns as hints.
    Defaults to 'about' if no specific category found.

    Args:
        file_path: Path to file

    Returns:
        List of category IDs
    """
    categories = []
    path_str = str(file_path).lower()

    # Path-based hints (don't assign processing patterns, just component/setup/about)
    # These help when keywords don't match
    path_hints = []

    if '/external_contents/' in path_str or '/biz_samples/' in path_str:
        path_hints.append('about')

    if '/getting_started/' in path_str or '/client_create/' in path_str:
        path_hints.append('setup')

    if (('/application_design' in path_str or '/feature_details/' in path_str or
         '/architecture' in path_str) or
        (('/batch/' in path_str or '/web/' in path_str or '/rest/' in path_str or
          '/messaging/' in path_str) and '/index.rst' in path_str)):
        # These are processing-pattern specific, don't add 'about'
        # They will get processing patterns in Step 5
        path_hints.append('_pattern_specific')

    # Read content
    try:
        content = read_file_content(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        try:
            content = read_file_content(file_path, encoding='shift-jis')
        except:
            return []  # Will be marked as unreadable

    content_lower = content.lower()

    # Check for each category's indicators
    for category, keywords in CATEGORY_KEYWORDS.items():
        if category == "about":
            # 'about' is default, check last
            continue

        if any(kw in content_lower for kw in keywords):
            categories.append(category)

    # Apply path hints if no content-based match
    if len(categories) == 0:
        if '_pattern_specific' in path_hints:
            # Don't add 'about' - will get processing patterns in Step 5
            # Return empty to avoid warning (processing patterns will be added later)
            return []
        elif path_hints:
            categories.extend([h for h in path_hints if h != '_pattern_specific'])

    # Final fallback to 'about'
    if len(categories) == 0:
        if any(kw in content_lower for kw in CATEGORY_KEYWORDS["about"]):
            categories.append("about")

    return categories


def main():
    """Main execution."""
    print("=" * 80)
    print("Categorize Files Needing AI Judgment - Step 4")
    print("=" * 80)
    print()

    # Load input file
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    print(f"Loading: {INPUT_FILE}")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        input_data = json.load(f)

    needs_ai = input_data["needs_ai_judgment"]
    print(f"Files needing AI judgment: {len(needs_ai)}")
    print()

    # Process each file
    print("Processing files...")
    categorized_ai_files = []
    still_uncategorized = []

    for i, entry in enumerate(needs_ai, 1):
        source_file = entry["source_file"]
        file_path = SOURCE_BASE / source_file

        if i % 10 == 0:
            print(f"  Processed {i}/{len(needs_ai)} files...")

        # Check if navigation-only
        is_nav_only, reason = is_navigation_only(file_path)

        if is_nav_only:
            entry["_no_content"] = True
            entry["_no_content_reason"] = reason
            entry["categories"] = ["about"]  # Default category
            categorized_ai_files.append(entry)
            continue

        # Categorize by content
        categories = categorize_by_content(file_path)

        if len(categories) > 0:
            entry["categories"] = categories
            categorized_ai_files.append(entry)
        else:
            # Check if this is a processing-pattern specific file
            path_str = str(file_path).lower()
            is_pattern_specific = (
                '/application_design' in path_str or
                '/feature_details/' in path_str or
                '/architecture' in path_str or
                ('/batch/' in path_str and '/index.rst' in path_str) or
                ('/web/' in path_str and '/index.rst' in path_str) or
                ('/rest/' in path_str and '/index.rst' in path_str) or
                ('/messaging/' in path_str and '/index.rst' in path_str)
            )

            if is_pattern_specific:
                # No warning - processing patterns will be added in Step 5
                entry["categories"] = []
                entry["_pending_pattern"] = True
                categorized_ai_files.append(entry)
            else:
                # Last resort: default to 'about'
                print(f"Warning: No clear category for {source_file}, defaulting to 'about'")
                entry["categories"] = ["about"]
                entry["_low_confidence"] = True
                categorized_ai_files.append(entry)

    print(f"✓ Categorized {len(categorized_ai_files)} files")
    print()

    # Count statistics
    nav_only_count = sum(1 for e in categorized_ai_files if e.get("_no_content"))
    low_confidence_count = sum(1 for e in categorized_ai_files if e.get("_low_confidence"))

    # Prepare output
    output_data = {
        "schema_version": "1.0",
        "version": VERSION,
        "created_at": datetime.now().isoformat(),
        "categorized_ai_files": categorized_ai_files,
        "stats": {
            "total_files": len(categorized_ai_files),
            "navigation_only": nav_only_count,
            "low_confidence": low_confidence_count
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
    print(f"Total files categorized: {output_data['stats']['total_files']}")
    print(f"Navigation-only: {output_data['stats']['navigation_only']}")
    print(f"Low confidence: {output_data['stats']['low_confidence']}")
    print()

    print("=" * 80)
    print("Next step: Run verify-patterns-v6.py to verify processing patterns")
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

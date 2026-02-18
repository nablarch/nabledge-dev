#!/usr/bin/env python3
"""Create initial mapping for Nablarch documentation (Steps 1-3).

This script:
1. Processes development guide files (patterns, security matrix)
2. Extracts nab-doc file paths with language priority (EN > JA)
3. Applies path-based category rules (non-processing-pattern categories)

Output: needs-ai-judgment-v6.json (files needing AI categorization)
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime


VERSION = "6"
SOURCE_BASE = Path(".lw/nab-official/v6")
CATEGORY_FILE = Path("doc/mapping-creation/categories-v6.json")
OUTPUT_DIR = Path("doc/mapping-creation/work-v6")


def load_category_definitions() -> Tuple[List[str], Dict[str, str], List[str]]:
    """Load category definitions from categories-v6.json.

    Returns:
        Tuple of (valid_category_ids, category_types, processing_patterns)
    """
    if not CATEGORY_FILE.exists():
        raise FileNotFoundError(f"Category file not found: {CATEGORY_FILE}")

    with open(CATEGORY_FILE, 'r', encoding='utf-8') as f:
        category_defs = json.load(f)

    valid_ids = [cat["id"] for cat in category_defs["categories"]]
    category_types = {cat["id"]: cat["type"] for cat in category_defs["categories"]}
    processing_patterns = [
        cat["id"] for cat in category_defs["categories"]
        if cat["type"] == "processing-pattern"
    ]

    print(f"Loaded {len(valid_ids)} categories from {CATEGORY_FILE}")
    print(f"Processing patterns: {processing_patterns}")

    return valid_ids, category_types, processing_patterns


def process_dev_guide_files() -> List[Dict]:
    """Process development guide files (Step 1).

    Returns:
        List of mapping entries for dev guide files
    """
    entries = []

    # Determine dev guide base path
    if VERSION == "6":
        dev_guide_base = SOURCE_BASE / "nablarch-system-development-guide"
    elif VERSION == "5":
        # v5 uses v6 dev guide
        dev_guide_base = Path(str(SOURCE_BASE).replace("/v5/", "/v6/")) / "nablarch-system-development-guide"
        print("Note: Using v6 development guide for v5 mapping")
    else:
        raise ValueError(f"Unknown version: {VERSION}")

    if not dev_guide_base.exists():
        print(f"Warning: Development guide not found at {dev_guide_base}")
        print("Skipping Step 1 (dev guide processing)")
        return entries

    # Step 1.1: Nablarch Patterns
    pattern_dir = dev_guide_base / "Nablarchシステム開発ガイド/docs/nablarch-patterns"

    if pattern_dir.exists():
        pattern_files = list(pattern_dir.glob("*.md")) + list(pattern_dir.glob("*.adoc"))
        pattern_files = [f for f in pattern_files if f.name != "README.md"]

        for file in pattern_files:
            # Determine category based on filename
            if "アンチパターン" in file.name or "anti-pattern" in file.name:
                category = "dev-guide-anti"
            else:
                category = "dev-guide-pattern"

            # Generate target name (kebab-case)
            target_name = file.stem.lower().replace("_", "-").replace("アンチパターン", "anti-pattern")

            entry = {
                "source_file": str(file.relative_to(SOURCE_BASE)),
                "categories": [category],
                "target_files": [f"guides/patterns/{target_name}.json"],
                "_from_step": 1
            }
            entries.append(entry)

        print(f"Found {len(entries)} pattern files in development guide")
    else:
        print(f"Warning: Pattern directory not found: {pattern_dir}")

    # Step 1.2: Security Matrix
    security_matrix_dir = dev_guide_base / "Sample_Project/設計書"

    if security_matrix_dir.exists():
        security_files = list(security_matrix_dir.glob("*セキュリティ対応表.xlsx"))

        if security_files:
            for file in security_files:
                entry = {
                    "source_file": str(file.relative_to(SOURCE_BASE)),
                    "categories": ["dev-guide-other"],
                    "target_files": ["guides/patterns/nablarch-security-matrix.json"],
                    "_from_step": 1
                }
                entries.append(entry)
            print(f"Found security matrix file")
        else:
            print("Note: Security matrix file not found (optional)")
    else:
        print(f"Warning: Security matrix directory not found: {security_matrix_dir}")

    return entries


def extract_nab_doc_paths() -> List[Path]:
    """Extract nab-doc file paths with language priority (Step 2).

    Returns:
        List of file paths (English preferred over Japanese)
    """
    nab_doc_base = SOURCE_BASE / "nablarch-document"

    if not nab_doc_base.exists():
        raise FileNotFoundError(f"nablarch-document not found: {nab_doc_base}")

    # Find all documentation files
    all_files = []
    for ext in ["*.rst", "*.md", "*.xml"]:
        all_files.extend(nab_doc_base.rglob(ext))

    # Exclude .git directories
    all_files = [f for f in all_files if ".git" not in str(f)]

    if len(all_files) == 0:
        raise FileNotFoundError(f"No nab-doc files found in: {nab_doc_base}")

    print(f"Found {len(all_files)} nab-doc files")

    # Apply language priority (English > Japanese)
    paths_by_name = {}
    for path in all_files:
        path_str = str(path)

        if '/en/' in path_str:
            # English file - takes priority
            key = path_str.replace('/en/', '/')
            paths_by_name[key] = path
        elif '/ja/' in path_str:
            # Japanese file - only if no English version
            key = path_str.replace('/ja/', '/')
            if key not in paths_by_name:
                paths_by_name[key] = path

    final_paths = list(paths_by_name.values())
    print(f"After language priority: {len(final_paths)} files")

    # Validate file readability
    readable_paths = []
    empty_files = []
    unreadable_files = []

    for path in final_paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                if len(content.strip()) == 0:
                    print(f"Warning: Empty file: {path}")
                    empty_files.append((path, "Empty file"))
                    continue
            readable_paths.append(path)
        except (UnicodeDecodeError, IOError) as e:
            print(f"Warning: Unreadable file: {path} ({e})")
            unreadable_files.append((path, f"Unreadable: {e}"))
            continue

    print(f"Readable files: {len(readable_paths)}")
    print(f"Empty files: {len(empty_files)}")
    print(f"Unreadable files: {len(unreadable_files)}")

    return readable_paths, empty_files, unreadable_files


def categorize_by_path(file_path: Path) -> List[str]:
    """Apply path pattern rules (Step 3).

    Only assigns non-processing-pattern categories:
    - Component types: handler, library, adaptor, tool, security-check
    - Setup types: setup, configuration
    - About types: about, migration

    Args:
        file_path: Path to file

    Returns:
        List of category IDs
    """
    categories = []

    # Normalize path for matching
    norm_path = str(file_path).lower()

    # Handler patterns
    if '/handlers/' in norm_path:
        categories.append('handler')

    # Library patterns
    if '/libraries/' in norm_path:
        categories.append('library')
        # Security-specific libraries
        if '/libraries/authorization/' in norm_path:
            categories.append('security-check')

    # Adaptor patterns
    if '/adaptors/' in norm_path:
        categories.append('adaptor')

    # Tool patterns
    if '/development_tools/' in norm_path:
        categories.append('tool')

    # Security patterns (general)
    if '/security/' in norm_path and 'library' not in categories:
        categories.append('security-check')

    # Setup patterns
    if '/blank_project/' in norm_path:
        categories.append('setup')

    # Configuration patterns
    if '/configuration/' in norm_path or '/setting_guide/' in norm_path:
        categories.append('configuration')

    # About patterns
    about_patterns = [
        '/about_nablarch/', '/examples/', '/jakarta_ee/',
        '/terms_of_use/', '/nablarch_api/'
    ]
    if any(pattern in norm_path for pattern in about_patterns):
        categories.append('about')

    # Migration patterns
    if '/migration/' in norm_path:
        categories.append('migration')

    return categories


def main():
    """Main execution."""
    print("=" * 80)
    print("Mapping Creation - Steps 1-3")
    print("=" * 80)
    print()

    # Preparation: Load category definitions
    print("Loading category definitions...")
    valid_ids, category_types, processing_patterns = load_category_definitions()
    print()

    # Step 1: Process development guide files
    print("Step 1: Processing development guide files...")
    dev_guide_entries = process_dev_guide_files()
    print(f"✓ Processed {len(dev_guide_entries)} dev guide files")
    print()

    # Step 2: Extract nab-doc file paths
    print("Step 2: Extracting nab-doc file paths...")
    nab_doc_paths, empty_files, unreadable_files = extract_nab_doc_paths()
    print(f"✓ Extracted {len(nab_doc_paths)} readable nab-doc files")
    print()

    # Step 3: Apply path-based category rules
    print("Step 3: Applying path-based category rules...")
    categorized_files = []
    needs_ai_judgment = []

    for file_path in nab_doc_paths:
        categories = categorize_by_path(file_path)

        entry = {
            "source_file": str(file_path.relative_to(SOURCE_BASE)),
            "categories": categories,
            "_from_step": 3
        }

        if len(categories) > 0:
            categorized_files.append(entry)
        else:
            needs_ai_judgment.append(entry)

    print(f"Categorized by path: {len(categorized_files)}")
    print(f"Needs AI judgment: {len(needs_ai_judgment)}")
    print()

    # Handle empty and unreadable files
    for file_path, reason in empty_files + unreadable_files:
        entry = {
            "source_file": str(file_path.relative_to(SOURCE_BASE)),
            "categories": ["about"],  # Default category
            "_no_content": True,
            "_no_content_reason": reason,
            "_from_step": 2
        }
        categorized_files.append(entry)

    # Combine all entries
    all_entries = dev_guide_entries + categorized_files

    # Write output: needs-ai-judgment-v6.json
    output_file = OUTPUT_DIR / f"needs-ai-judgment-v{VERSION}.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    output_data = {
        "schema_version": "1.0",
        "version": VERSION,
        "created_at": datetime.now().isoformat(),
        "categorized_files": all_entries,
        "needs_ai_judgment": needs_ai_judgment,
        "stats": {
            "total_files": len(all_entries) + len(needs_ai_judgment),
            "dev_guide_files": len(dev_guide_entries),
            "categorized_by_path": len(categorized_files),
            "needs_ai_judgment": len(needs_ai_judgment),
            "empty_or_unreadable": len(empty_files) + len(unreadable_files)
        }
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"✓ Written: {output_file}")
    print()

    # Print summary
    print("Summary")
    print("-------")
    print(f"Total files: {output_data['stats']['total_files']}")
    print(f"Dev guide files: {output_data['stats']['dev_guide_files']}")
    print(f"Categorized by path: {output_data['stats']['categorized_by_path']}")
    print(f"Needs AI judgment: {output_data['stats']['needs_ai_judgment']}")
    print(f"Empty/unreadable: {output_data['stats']['empty_or_unreadable']}")
    print()

    print("=" * 80)
    print("Next step: Run categorize-ai-judgment-v6.py to categorize remaining files")
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

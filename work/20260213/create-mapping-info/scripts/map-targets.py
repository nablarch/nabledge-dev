#!/usr/bin/env python3
"""
Map source files to target knowledge files.

Reads:
- categorized-vX.json: Categorized source files
- categories-vX.json: Category definitions

Outputs:
- mapping-vX.json: Complete mapping with target_files assigned
"""

import json
import sys
import re
from pathlib import Path
from typing import Dict, List, Set

def load_json(file_path: Path) -> Dict:
    """Load JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def slugify(text: str) -> str:
    """Convert text to slug for filename."""
    # Remove special characters and convert to lowercase
    text = re.sub(r'[^\w\s-]', '', text.lower())
    # Replace spaces with hyphens
    text = re.sub(r'[\s_-]+', '-', text)
    # Remove leading/trailing hyphens
    return text.strip('-')

def map_category_to_target_path(categories: List[str], source_file: str, title: str) -> List[str]:
    """
    Map categories to target knowledge file paths.
    Returns list of target file paths.
    """
    target_files = []

    # Category to directory mapping
    category_dir_map = {
        'batch-nablarch': 'features/processing',
        'rest': 'features/processing',
        'http-messaging': 'features/processing',
        'handler': 'features/handlers',
        'library': 'features/libraries',
        'adaptor': 'features/adapters',
        'tool': 'features/tools',
        'setup': 'features/setup',
        'archetype': 'features/setup',
        'configuration': 'features/setup',
        'dev-guide-pattern': 'guides/patterns',
        'dev-guide-anti': 'guides/anti-patterns',
        'dev-guide-project': 'guides/project-setup',
        'dev-guide-other': 'guides/other',
        'check-published-api': 'checks/published-api',
        'check-deprecated': 'checks/deprecated',
        'check-security': 'checks/security',
        'about': 'about',
        'migration': 'about/migration'
    }

    # Specific target file mappings for well-known topics
    specific_mappings = {
        'batch-nablarch': 'features/processing/nablarch-batch.json',
        'rest': 'features/processing/rest-web-services.json',
        'http-messaging': 'features/processing/http-messaging.json'
    }

    # Determine target path for each category
    seen_targets = set()

    for category in categories:
        # Check for specific mapping first
        if category in specific_mappings:
            target = specific_mappings[category]
            if target not in seen_targets:
                target_files.append(target)
                seen_targets.add(target)
        # Then check for directory mapping
        elif category in category_dir_map:
            base_dir = category_dir_map[category]

            # For handlers and libraries, try to generate specific filename
            if category in ['handler', 'library', 'adaptor', 'tool']:
                # Extract meaningful filename from source path or title
                source_path = Path(source_file)
                if source_path.stem != 'index':
                    filename_base = slugify(source_path.stem)
                else:
                    # Use parent directory name if file is index.rst
                    filename_base = slugify(source_path.parent.name)

                # Limit filename length
                if len(filename_base) > 50:
                    filename_base = filename_base[:50]

                target = f"{base_dir}/{filename_base}.json"
            else:
                # For other categories, use category-based naming
                filename_base = slugify(category)
                target = f"{base_dir}/{filename_base}.json"

            if target not in seen_targets:
                target_files.append(target)
                seen_targets.add(target)

    return target_files

def map_targets(categorized: Dict, version: str) -> Dict:
    """Map all in-scope files to target knowledge files."""
    mappings = categorized['mappings']
    results = []

    for entry in mappings:
        if entry['in_scope']:
            # Assign target files based on categories
            target_files = map_category_to_target_path(
                entry['categories'],
                entry['source_file'],
                entry['title']
            )
            entry['target_files'] = target_files
        else:
            # Out of scope files have no target files
            entry['target_files'] = []

        results.append(entry)

    return {
        'version': version,
        'statistics': categorized['statistics'],
        'mappings': results
    }

def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    work_dir = script_dir.parent

    # Process V6
    print("Processing V6 mapping...")
    categorized_v6_file = work_dir / 'categorized-v6.json'
    categorized_v6 = load_json(categorized_v6_file)

    mapping_v6 = map_targets(categorized_v6, '6')

    output_v6 = work_dir / 'mapping-v6.json'
    with open(output_v6, 'w', encoding='utf-8') as f:
        json.dump(mapping_v6, f, indent=2, ensure_ascii=False)

    print(f"Wrote {output_v6}")
    print(f"  Total entries: {mapping_v6['statistics']['total']}")
    print(f"  In scope with targets: {mapping_v6['statistics']['in_scope']}")
    print(f"  Out of scope: {mapping_v6['statistics']['out_of_scope']}")

    # Process V5
    print("\nProcessing V5 mapping...")
    categorized_v5_file = work_dir / 'categorized-v5.json'
    categorized_v5 = load_json(categorized_v5_file)

    mapping_v5 = map_targets(categorized_v5, '5')

    output_v5 = work_dir / 'mapping-v5.json'
    with open(output_v5, 'w', encoding='utf-8') as f:
        json.dump(mapping_v5, f, indent=2, ensure_ascii=False)

    print(f"Wrote {output_v5}")
    print(f"  Total entries: {mapping_v5['statistics']['total']}")
    print(f"  In scope with targets: {mapping_v5['statistics']['in_scope']}")
    print(f"  Out of scope: {mapping_v5['statistics']['out_of_scope']}")

    print("\nTarget mapping complete!")

if __name__ == '__main__':
    main()

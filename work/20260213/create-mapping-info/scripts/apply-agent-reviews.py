#!/usr/bin/env python3
"""
Apply agent review recommendations to mapping files.
"""

import json
from pathlib import Path

def load_json(file_path):
    """Load JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(file_path, data):
    """Save JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def apply_reviews(mapping, reviews, version):
    """Apply review recommendations to mapping."""
    changes = 0

    # Create file_path to entry mapping
    mapping_dict = {entry['source_file']: entry for entry in mapping['mappings']}

    for review in reviews:
        file_path = review['file_path']
        recommended = review['recommended_categories']

        if file_path not in mapping_dict:
            print(f"  Warning: {file_path} not found in mapping")
            continue

        entry = mapping_dict[file_path]

        # Replace categories with recommended
        if entry['categories'] != recommended:
            old_cats = entry['categories'].copy()
            entry['categories'] = recommended
            changes += 1

            # Show what changed
            added = set(recommended) - set(old_cats)
            if added:
                print(f"  [{version}] {Path(file_path).name}: +{added}")

    return changes

def main():
    script_dir = Path(__file__).parent
    work_dir = script_dir.parent

    # Load categorized files (these are used by map-targets.py)
    mapping_v6 = load_json(work_dir / 'categorized-v6.json')
    mapping_v5 = load_json(work_dir / 'categorized-v5.json')

    v6_changes = 0
    v5_changes = 0

    # Apply V6 library reviews
    print("Applying V6 library reviews...")
    v6_lib = load_json(work_dir / 'library-categorization-review.json')
    v6_changes += apply_reviews(mapping_v6, v6_lib, 'V6-LIB')

    # Apply V6 handler reviews
    print("\nApplying V6 handler reviews...")
    v6_handler = load_json(work_dir / 'handler-categorization-review.json')
    v6_changes += apply_reviews(mapping_v6, v6_handler, 'V6-HANDLER')

    # Apply V6 dev-guide reviews (manually for batch pattern files)
    print("\nApplying V6 dev-guide reviews...")
    batch_pattern_files = [
        'Nablarchバッチ処理パターン.md',
        'Nablarch_batch_processing_pattern.md'
    ]
    for entry in mapping_v6['mappings']:
        if any(f in entry['source_file'] for f in batch_pattern_files):
            if 'batch-nablarch' not in entry['categories']:
                entry['categories'].append('batch-nablarch')
                v6_changes += 1
                print(f"  [V6-DEVGUIDE] {Path(entry['source_file']).name}: +{{'batch-nablarch'}}")

    # Apply V5 handler reviews
    print("\nApplying V5 handler reviews...")
    v5_handler = load_json(work_dir / 'handler-categorization-review-v5.json')
    v5_changes += apply_reviews(mapping_v5, v5_handler, 'V5-HANDLER')

    # For V5 libraries, use V6 library reviews (same structure per agent)
    print("\nApplying V5 library reviews (using V6 structure)...")
    # Replace v6 paths with v5 paths in reviews
    v5_lib_reviews = []
    for review in v6_lib:
        v5_review = review.copy()
        v5_review['file_path'] = review['file_path'].replace('/v6/', '/v5/')
        v5_lib_reviews.append(v5_review)
    v5_changes += apply_reviews(mapping_v5, v5_lib_reviews, 'V5-LIB')

    # Save updated categorized files
    save_json(work_dir / 'categorized-v6.json', mapping_v6)
    print(f"\n✓ Updated categorized-v6.json ({v6_changes} changes)")

    save_json(work_dir / 'categorized-v5.json', mapping_v5)
    print(f"✓ Updated categorized-v5.json ({v5_changes} changes)")

    print(f"\n✓ Total changes: {v6_changes + v5_changes}")

if __name__ == '__main__':
    main()

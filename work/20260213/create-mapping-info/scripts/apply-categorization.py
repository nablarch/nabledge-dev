#!/usr/bin/env python3
"""
Apply categorization rules to source files.

Reads:
- sources-vX.json: Source files with metadata
- path-rules.json: Pattern matching rules
- categories-vX.json: Category definitions

Outputs:
- categorized-vX.json: Source files with categories and in_scope determination
"""

import json
import sys
from pathlib import Path
from fnmatch import fnmatch
from typing import Dict, List, Set

def load_json(file_path: Path) -> Dict:
    """Load JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def match_pattern(file_path: str, pattern: str) -> bool:
    """Check if file path matches glob pattern."""
    return fnmatch(file_path, pattern)

def match_exclusion(file_path: str, exclusions: List[Dict]) -> tuple:
    """
    Check if file matches any exclusion pattern.
    Returns (is_excluded, reason) tuple.
    """
    for rule in exclusions:
        pattern = rule['pattern']
        reason = rule['reason']
        except_pattern = rule.get('except')

        # Check if file matches exclusion pattern
        if match_pattern(file_path, pattern):
            # Check if file matches exception pattern
            if except_pattern and match_pattern(file_path, except_pattern):
                continue
            return (True, reason)

    return (False, None)

def match_inclusions(file_path: str, inclusions: List[Dict]) -> Set[str]:
    """
    Check if file matches any inclusion pattern.
    Returns set of matching categories.
    """
    categories = set()

    for rule in inclusions:
        pattern = rule['pattern']
        rule_categories = rule['categories']

        if match_pattern(file_path, pattern):
            categories.update(rule_categories)

    return categories

def match_dev_guide_patterns(file_path: str, filename: str, patterns: List[Dict]) -> Set[str]:
    """
    Match development guide filename patterns.
    Returns set of matching categories.
    """
    categories = set()

    for rule in patterns:
        pattern = rule['pattern']
        rule_categories = rule['categories']

        # Match against full path or just filename
        if match_pattern(file_path, pattern) or match_pattern(filename, pattern):
            categories.update(rule_categories)

    return categories

def categorize_sources(sources: List[Dict], path_rules: Dict, version: str) -> List[Dict]:
    """Apply categorization rules to all sources."""
    results = []
    stats = {
        'total': 0,
        'in_scope': 0,
        'out_of_scope': 0,
        'needs_review': 0
    }

    exclusions = path_rules['priority_1_exclusions']
    inclusions = path_rules['priority_2_inclusions']
    dev_guide_patterns = path_rules.get('dev_guide_filename_patterns', [])
    archetype_patterns = path_rules.get('archetype_patterns', [])

    for idx, source in enumerate(sources):
        file_path = source['source_file']
        filename = Path(file_path).name
        file_type = source['file_type']

        # Generate unique ID
        entry_id = f"v{version}-{idx+1:04d}"

        # Step 1: Check exclusions (priority 1)
        is_excluded, exclusion_reason = match_exclusion(file_path, exclusions)

        if is_excluded:
            # File is out of scope
            result = {
                'id': entry_id,
                'source_file': file_path,
                'title': source['title'],
                'categories': [],
                'in_scope': False,
                'reason_for_exclusion': exclusion_reason,
                'target_files': []
            }
            stats['out_of_scope'] += 1
        else:
            # Step 2: Check inclusions (priority 2)
            categories = match_inclusions(file_path, inclusions)

            # Step 3: Special handling for MD files (dev guide patterns)
            if file_type == 'md':
                dev_categories = match_dev_guide_patterns(file_path, filename, dev_guide_patterns)
                if dev_categories:
                    categories.update(dev_categories)

            # Step 4: Special handling for archetype files
            if 'archetype' in file_type:
                archetype_categories = match_inclusions(file_path, archetype_patterns)
                if archetype_categories:
                    categories.update(archetype_categories)

            # Determine in_scope status
            if categories:
                result = {
                    'id': entry_id,
                    'source_file': file_path,
                    'title': source['title'],
                    'categories': sorted(list(categories)),
                    'in_scope': True,
                    'reason_for_exclusion': None,
                    'target_files': []  # Will be filled by map-targets.py
                }
                stats['in_scope'] += 1
            else:
                # No categories matched - needs manual review
                result = {
                    'id': entry_id,
                    'source_file': file_path,
                    'title': source['title'],
                    'categories': ['NEEDS_REVIEW'],
                    'in_scope': None,  # Undetermined
                    'reason_for_exclusion': 'No matching pattern found - requires manual review',
                    'target_files': []
                }
                stats['needs_review'] += 1

        results.append(result)
        stats['total'] += 1

    return results, stats

def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    work_dir = script_dir.parent

    # Load path rules
    path_rules_file = script_dir / 'path-rules.json'
    print(f"Loading path rules from {path_rules_file}")
    path_rules = load_json(path_rules_file)

    # Process V6
    print("\nProcessing V6 sources...")
    sources_v6_file = work_dir / 'sources-v6.json'
    sources_v6 = load_json(sources_v6_file)

    categorized_v6, stats_v6 = categorize_sources(
        sources_v6['sources'],
        path_rules,
        '6'
    )

    output_v6 = work_dir / 'categorized-v6.json'
    with open(output_v6, 'w', encoding='utf-8') as f:
        json.dump({
            'version': '6',
            'statistics': stats_v6,
            'mappings': categorized_v6
        }, f, indent=2, ensure_ascii=False)

    print(f"Wrote {output_v6}")
    print(f"  Total: {stats_v6['total']}")
    print(f"  In scope: {stats_v6['in_scope']}")
    print(f"  Out of scope: {stats_v6['out_of_scope']}")
    print(f"  Needs review: {stats_v6['needs_review']}")

    # Process V5
    print("\nProcessing V5 sources...")
    sources_v5_file = work_dir / 'sources-v5.json'
    sources_v5 = load_json(sources_v5_file)

    categorized_v5, stats_v5 = categorize_sources(
        sources_v5['sources'],
        path_rules,
        '5'
    )

    output_v5 = work_dir / 'categorized-v5.json'
    with open(output_v5, 'w', encoding='utf-8') as f:
        json.dump({
            'version': '5',
            'statistics': stats_v5,
            'mappings': categorized_v5
        }, f, indent=2, ensure_ascii=False)

    print(f"Wrote {output_v5}")
    print(f"  Total: {stats_v5['total']}")
    print(f"  In scope: {stats_v5['in_scope']}")
    print(f"  Out of scope: {stats_v5['out_of_scope']}")
    print(f"  Needs review: {stats_v5['needs_review']}")

    print("\nCategorization complete!")

if __name__ == '__main__':
    main()

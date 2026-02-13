#!/usr/bin/env python3
"""
Deduplicate ja/en files, keeping only ja versions.

Reads:
- sources-vX.json: Source files with metadata

Outputs:
- sources-vX-dedup.json: Deduplicated sources (ja only when ja/en pair exists)
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

def load_json(file_path: Path) -> Dict:
    """Load JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def deduplicate_ja_en(sources: List[Dict]) -> tuple:
    """
    Deduplicate ja/en files, keeping only ja versions.
    Returns (deduplicated_sources, removed_en_files)
    """
    # Create a map of normalized paths to sources
    # Normalized path: replace /ja/ and /en/ with /XX/
    normalized_map = {}

    for source in sources:
        file_path = source['source_file']

        # Normalize path
        normalized = file_path.replace('/ja/', '/XX/').replace('/en/', '/XX/')

        if normalized not in normalized_map:
            normalized_map[normalized] = []

        normalized_map[normalized].append(source)

    # Filter: keep ja version if exists, otherwise keep en version
    deduplicated = []
    removed_en = []

    for normalized, files in normalized_map.items():
        if len(files) == 1:
            # No duplicate, keep as is
            deduplicated.append(files[0])
        else:
            # Multiple files (ja/en pair)
            # Prefer ja over en
            ja_files = [f for f in files if '/ja/' in f['source_file']]
            en_files = [f for f in files if '/en/' in f['source_file']]

            if ja_files:
                # Keep ja version
                deduplicated.append(ja_files[0])
                # Track removed en versions
                removed_en.extend(en_files)
            else:
                # No ja version, keep first file
                deduplicated.append(files[0])

    return deduplicated, removed_en

def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    work_dir = script_dir.parent

    # Process V6
    print("Deduplicating V6 sources (ja/en)...")
    sources_v6_file = work_dir / 'sources-v6.json'
    sources_v6 = load_json(sources_v6_file)

    dedup_v6, removed_v6 = deduplicate_ja_en(sources_v6['sources'])

    output_v6 = work_dir / 'sources-v6.json'
    with open(output_v6, 'w', encoding='utf-8') as f:
        json.dump({
            'version': '6',
            'total_files': len(dedup_v6),
            'sources': dedup_v6
        }, f, indent=2, ensure_ascii=False)

    print(f"  Original: {len(sources_v6['sources'])} files")
    print(f"  Deduplicated: {len(dedup_v6)} files")
    print(f"  Removed (en): {len(removed_v6)} files")
    print(f"Wrote {output_v6}")

    # Process V5
    print("\nDeduplicating V5 sources (ja/en)...")
    sources_v5_file = work_dir / 'sources-v5.json'
    sources_v5 = load_json(sources_v5_file)

    dedup_v5, removed_v5 = deduplicate_ja_en(sources_v5['sources'])

    output_v5 = work_dir / 'sources-v5.json'
    with open(output_v5, 'w', encoding='utf-8') as f:
        json.dump({
            'version': '5',
            'total_files': len(dedup_v5),
            'sources': dedup_v5
        }, f, indent=2, ensure_ascii=False)

    print(f"  Original: {len(sources_v5['sources'])} files")
    print(f"  Deduplicated: {len(dedup_v5)} files")
    print(f"  Removed (en): {len(removed_v5)} files")
    print(f"Wrote {output_v5}")

    print("\nDeduplication complete!")
    print("Run categorization, mapping, and validation scripts to update mappings.")

if __name__ == '__main__':
    main()

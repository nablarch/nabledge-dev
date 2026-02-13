#!/usr/bin/env python3
"""
Scan official documentation sources and extract metadata.

Outputs:
- sources-v6.json: All v6 source files with metadata
- sources-v5.json: All v5 source files with metadata
"""

import os
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

def extract_rst_title(file_path: str) -> Optional[str]:
    """Extract title from RST file by detecting ==== underline pattern."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for i in range(len(lines) - 1):
            current_line = lines[i].strip()
            next_line = lines[i + 1].strip()

            # Check if next line is all === or --- (underline pattern)
            if len(next_line) >= 3 and (all(c == '=' for c in next_line) or all(c == '-' for c in next_line)):
                if current_line and len(current_line) <= len(next_line):
                    return current_line

        # Fallback: return first non-empty line
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('..'):
                return stripped

        return None
    except Exception as e:
        print(f"Warning: Failed to extract title from {file_path}: {e}", file=sys.stderr)
        return None

def extract_md_title(file_path: str) -> Optional[str]:
    """Extract title from MD file (first line starting with #)."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith('# '):
                    return stripped.lstrip('# ').strip()
        return None
    except Exception as e:
        print(f"Warning: Failed to extract title from {file_path}: {e}", file=sys.stderr)
        return None

def scan_rst_files(base_dir: str) -> List[Dict]:
    """Scan all RST files in directory tree."""
    results = []
    base_path = Path(base_dir)

    if not base_path.exists():
        print(f"Warning: Directory not found: {base_dir}", file=sys.stderr)
        return results

    for rst_file in base_path.rglob('*.rst'):
        rel_path = str(rst_file.relative_to(base_path.parent.parent.parent))
        title = extract_rst_title(str(rst_file))

        results.append({
            'source_file': rel_path,
            'title': title or rst_file.stem,
            'file_type': 'rst',
            'size': rst_file.stat().st_size
        })

    return results

def scan_md_files(base_dir: str) -> List[Dict]:
    """Scan all MD files in directory tree."""
    results = []
    base_path = Path(base_dir)

    if not base_path.exists():
        print(f"Warning: Directory not found: {base_dir}", file=sys.stderr)
        return results

    for md_file in base_path.rglob('*.md'):
        # Skip node_modules and hidden directories within the scanned tree
        # (not the parent path components)
        rel_parts = md_file.relative_to(base_path).parts
        if any(part.startswith('.') or part == 'node_modules' for part in rel_parts):
            continue

        rel_path = str(md_file.relative_to(base_path.parent.parent.parent))
        title = extract_md_title(str(md_file))

        results.append({
            'source_file': rel_path,
            'title': title or md_file.stem,
            'file_type': 'md',
            'size': md_file.stat().st_size
        })

    return results

def scan_archetype_projects(base_dir: str) -> List[Dict]:
    """Scan archetype projects (use pom.xml + README.md as representative files)."""
    results = []
    base_path = Path(base_dir)

    if not base_path.exists():
        print(f"Warning: Directory not found: {base_dir}", file=sys.stderr)
        return results

    # Find all archetype directories (contain pom.xml at root level)
    for pom_file in base_path.glob('*/pom.xml'):
        project_dir = pom_file.parent
        project_name = project_dir.name

        # Add pom.xml as representative file
        rel_path = str(pom_file.relative_to(base_path.parent.parent.parent))
        results.append({
            'source_file': rel_path,
            'title': f"{project_name} (pom.xml)",
            'file_type': 'archetype-pom',
            'size': pom_file.stat().st_size
        })

        # Add README.md if exists
        readme_file = project_dir / 'README.md'
        if readme_file.exists():
            rel_path = str(readme_file.relative_to(base_path.parent.parent.parent))
            title = extract_md_title(str(readme_file))
            results.append({
                'source_file': rel_path,
                'title': title or f"{project_name} (README)",
                'file_type': 'archetype-readme',
                'size': readme_file.stat().st_size
            })

    return results

def main():
    """Main entry point."""
    # Get repository root (3 levels up from scripts/)
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent.parent.parent

    print("Scanning V6 documentation sources...")
    v6_sources = []

    # V6: nablarch-document
    print("  - nablarch-document (RST files)")
    v6_sources.extend(scan_rst_files(str(repo_root / '.lw/nab-official/v6/nablarch-document')))

    # V6: nablarch-system-development-guide
    print("  - nablarch-system-development-guide (MD files)")
    v6_sources.extend(scan_md_files(str(repo_root / '.lw/nab-official/v6/nablarch-system-development-guide')))

    # V6: nablarch-single-module-archetype
    print("  - nablarch-single-module-archetype (archetype projects)")
    v6_sources.extend(scan_archetype_projects(str(repo_root / '.lw/nab-official/v6/nablarch-single-module-archetype')))

    print(f"Found {len(v6_sources)} V6 source files")

    print("\nScanning V5 documentation sources...")
    v5_sources = []

    # V5: nablarch-document
    print("  - nablarch-document (RST files)")
    v5_sources.extend(scan_rst_files(str(repo_root / '.lw/nab-official/v5/nablarch-document')))

    # V5: nablarch-single-module-archetype
    print("  - nablarch-single-module-archetype (archetype projects)")
    v5_sources.extend(scan_archetype_projects(str(repo_root / '.lw/nab-official/v5/nablarch-single-module-archetype')))

    # Note: V5 has no system-development-guide (use v6 guide for v5 knowledge)
    print("  - Note: V5 has no system-development-guide (v6 guide will be referenced)")

    print(f"Found {len(v5_sources)} V5 source files")

    # Write output files
    output_dir = script_dir.parent

    v6_output = output_dir / 'sources-v6.json'
    with open(v6_output, 'w', encoding='utf-8') as f:
        json.dump({
            'version': '6',
            'total_files': len(v6_sources),
            'sources': v6_sources
        }, f, indent=2, ensure_ascii=False)
    print(f"\nWrote {v6_output}")

    v5_output = output_dir / 'sources-v5.json'
    with open(v5_output, 'w', encoding='utf-8') as f:
        json.dump({
            'version': '5',
            'total_files': len(v5_sources),
            'sources': v5_sources
        }, f, indent=2, ensure_ascii=False)
    print(f"Wrote {v5_output}")

    print("\nScan complete!")
    print(f"  V6: {len(v6_sources)} files")
    print(f"  V5: {len(v5_sources)} files")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""One-time script: extract hints from KC cache and write tools/rbkc/hints/v6.json.

Usage:
    cd tools/rbkc
    python ../../.pr/00299/extract_hints.py [--version 6] [--dry-run]

This script is run ONCE to generate the persistent hints source file.
After generation, edit tools/rbkc/hints/v{version}.json directly.
Do NOT regenerate — doing so would overwrite manual edits.

Algorithm:
    Uses build_hints_index() from scripts/create/hints.py:
    - Step A: catalog Expected Sections (section_range.sections) → KC index mapping
      Maps KC-synthesized titles to RST h2 headings via the catalog.
    - Step B: content overlap fallback when catalog has no Expected Sections.
    - Normalizes file_id: replace _ with - (KC uses original filenames; RBKC uses hyphens).

    The resulting keys match RBKC JSON sections[].title exactly, enabling lookup_hints
    to find hints for each section during create/update.

Self-validation:
    - Reports file_ids where ALL sections have empty hints
    - Reports sections with empty hints
    - Summary: file_ids, sections, total hints count
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Run from tools/rbkc/ — add to sys.path so scripts package is importable
_RBKC_DIR = Path(__file__).parents[2] / "tools/rbkc"
sys.path.insert(0, str(_RBKC_DIR))

from scripts.create.hints import build_hints_index  # noqa: E402


def validate(hints: dict[str, dict[str, list[str]]]) -> list[str]:
    """Return warning messages. Empty list = clean."""
    warnings: list[str] = []
    files_no_hints = []
    sections_no_hints = []

    for file_id, section_map in sorted(hints.items()):
        total = sum(len(h) for h in section_map.values())
        if total == 0:
            files_no_hints.append(file_id)
        for title, h in section_map.items():
            if not h:
                sections_no_hints.append(f"{file_id} / {title!r}")

    if files_no_hints:
        n = len(files_no_hints)
        sample = files_no_hints[:5]
        suffix = "..." if n > 5 else ""
        warnings.append(f"Files with zero hints ({n}): {sample}{suffix}")
    if sections_no_hints:
        n = len(sections_no_hints)
        sample = sections_no_hints[:5]
        suffix = "..." if n > 5 else ""
        warnings.append(f"Sections with empty hints ({n}): {sample}{suffix}")

    return warnings


def main():
    parser = argparse.ArgumentParser(description="Extract KC hints to hints/v{version}.json")
    parser.add_argument("--version", default="6")
    parser.add_argument("--dry-run", action="store_true", help="Print summary without writing")
    args = parser.parse_args()

    repo_root = Path(__file__).parents[2]
    cache_dir = repo_root / "tools/knowledge-creator/.cache" / f"v{args.version}"
    catalog_path = cache_dir / "catalog.json"
    out_path = repo_root / "tools/rbkc/hints" / f"v{args.version}.json"

    print(f"Reading KC cache: {cache_dir}")
    print(f"Catalog: {catalog_path} ({'found' if catalog_path.exists() else 'NOT FOUND'})")

    hints = build_hints_index(cache_dir, catalog_path, repo_root)

    total_files = len(hints)
    total_sections = sum(len(sm) for sm in hints.values())
    total_hints = sum(len(h) for sm in hints.values() for h in sm.values())
    print(f"Extracted: {total_files} file_ids, {total_sections} sections, {total_hints} hints")

    warnings = validate(hints)
    for w in warnings:
        print(f"WARNING: {w}", file=sys.stderr)

    if args.dry_run:
        print("Dry run — not writing.")
        return

    payload = {"version": args.version, "hints": hints}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Written: {out_path}")
    if warnings:
        print(f"Completed with {len(warnings)} warning(s).")
    else:
        print("No warnings — hints look clean.")


if __name__ == "__main__":
    main()

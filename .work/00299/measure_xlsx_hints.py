#!/usr/bin/env python3
"""Measure xlsx-format hints volume across all 5 versions.

For each xlsx source file in catalog.json, count:
- number of cache index entries (sections)
- total hints aggregated across those sections

Output helps Phase 21-C (row-level sectioning for xlsx) scope the workload.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from classify_p4 import REPO_ROOT, load_catalog, load_cache_entries  # noqa: E402


def measure(version: str) -> dict:
    cache_dir = REPO_ROOT / "tools/knowledge-creator/.cache" / f"v{version}"
    catalog = load_catalog(cache_dir)
    cache_by_base = load_cache_entries(cache_dir)

    xlsx_bases: dict[str, str] = {}
    for e in catalog["files"]:
        if e.get("format") == "xlsx":
            xlsx_bases[e["base_name"]] = e["source_path"]

    per_file: list[dict] = []
    total_index = 0
    total_hints = 0
    for base, src in sorted(xlsx_bases.items()):
        n_idx = 0
        n_hints = 0
        for data in cache_by_base.get(base, []):
            for idx in data.get("index", []):
                n_idx += 1
                n_hints += len(idx.get("hints", []))
        per_file.append({"base": base, "source": src, "indexes": n_idx, "hints": n_hints})
        total_index += n_idx
        total_hints += n_hints

    return {
        "version": version,
        "xlsx_files": len(xlsx_bases),
        "total_indexes": total_index,
        "total_hints": total_hints,
        "per_file": per_file,
    }


def main():
    results = {}
    for v in ["6", "5", "1.4", "1.3", "1.2"]:
        r = measure(v)
        results[v] = r
        print(
            f"v{v}: files={r['xlsx_files']:3d}  indexes={r['total_indexes']:5d}  hints={r['total_hints']:5d}",
            file=sys.stderr,
        )
        for f in r["per_file"]:
            print(
                f"  {f['base']:<40s} idx={f['indexes']:4d} hints={f['hints']:5d}  {f['source']}",
                file=sys.stderr,
            )

    out = Path(".pr/00299/xlsx-hints-measurement.json")
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out}", file=sys.stderr)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Is R6 triggered mostly on h1-only sources? If so, R6 is the *correct*
resolution (single-heading page), not a design failure."""
from __future__ import annotations
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from generate_hints import (
    REPO_ROOT,
    load_catalog_grouped,
    load_cache_by_base,
    merge_cache_index,
    merge_section_maps,
    parse_source_headings,
    resolve_sid,
)


def analyze(version: str) -> dict:
    cache_dir = REPO_ROOT / "tools/knowledge-creator/.cache" / f"v{version}"
    _, catalog_by_base, source_by_base, format_by_base = load_catalog_grouped(cache_dir)
    cache_by_base = load_cache_by_base(cache_dir)

    h1_only_r6 = 0  # R6 triggered on source with only 1 heading (h1-only)
    multi_r6 = 0    # R6 triggered on multi-heading source (real concern)
    multi_examples: list[str] = []
    total_sid = 0

    for base in sorted(catalog_by_base):
        entries = catalog_by_base[base]
        fmt = format_by_base.get(base, "rst")
        if fmt == "xlsx":
            continue
        cache_entries = cache_by_base.get(base, [])
        cache_index = merge_cache_index(cache_entries)
        section_map = merge_section_maps(entries)
        source_path = REPO_ROOT / source_by_base[base]
        source_headings = parse_source_headings(source_path, fmt)

        h1_only_source = len(source_headings) == 1

        for idx in cache_index:
            sid = idx.get("id")
            if not sid:
                continue
            total_sid += 1
            try:
                _, rule = resolve_sid(
                    sid=sid,
                    catalog_section_map=section_map,
                    cache_title=idx.get("title") or "",
                    source_headings=source_headings,
                )
            except ValueError:
                continue
            if rule != "R6":
                continue
            if h1_only_source:
                h1_only_r6 += 1
            else:
                multi_r6 += 1
                if len(multi_examples) < 10:
                    multi_examples.append(
                        f"{base}/{sid}: cache={idx.get('title','')[:50]!r} "
                        f"src_heads={[h[1] for h in source_headings[:3]]}"
                    )
    total_r6 = h1_only_r6 + multi_r6
    return {
        "version": version,
        "total_sid": total_sid,
        "total_r6": total_r6,
        "r6_pct": round(total_r6 / total_sid * 100, 2) if total_sid else 0,
        "h1_only_r6": h1_only_r6,
        "multi_r6": multi_r6,
        "multi_pct": round(multi_r6 / total_sid * 100, 2) if total_sid else 0,
        "multi_examples": multi_examples,
    }


def main():
    print(f"{'ver':>5} | {'sids':>5} | {'R6':>4} | {'R6%':>5} | {'h1-only R6':>10} | {'multi R6':>8} | {'multi%':>6}")
    for v in ["6", "5", "1.4", "1.3", "1.2"]:
        r = analyze(v)
        print(
            f"{v:>5} | {r['total_sid']:>5} | {r['total_r6']:>4} | {r['r6_pct']:>5} | "
            f"{r['h1_only_r6']:>10} | {r['multi_r6']:>8} | {r['multi_pct']:>6}"
        )
        for e in r["multi_examples"][:5]:
            print(f"    {e}")


if __name__ == "__main__":
    main()

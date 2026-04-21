#!/usr/bin/env python3
"""Analyze which sids hit R6 — understand root cause of R6 ratio > 2%."""
from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from generate_hints import (
    REPO_ROOT,
    build_file_hints,
    load_catalog_grouped,
    load_cache_by_base,
    merge_cache_index,
    merge_section_maps,
    parse_source_headings,
    resolve_sid,
)


def analyze(version: str, limit: int = 30):
    cache_dir = REPO_ROOT / "tools/knowledge-creator/.cache" / f"v{version}"
    _, catalog_by_base, source_by_base, format_by_base = load_catalog_grouped(cache_dir)
    cache_by_base = load_cache_by_base(cache_dir)

    r6_items: list[dict] = []
    cat_mismatch_cnt = 0  # catalog heading non-empty but not in source
    r6_patterns: Counter = Counter()

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
        heading_set = {h[1] for h in source_headings}

        for idx in cache_index:
            sid = idx.get("id")
            cache_title = idx.get("title") or ""
            if not sid:
                continue
            try:
                _, rule = resolve_sid(
                    sid=sid,
                    catalog_section_map=section_map,
                    cache_title=cache_title,
                    source_headings=source_headings,
                )
            except ValueError:
                continue
            if rule != "R6":
                continue

            cat_heading = section_map.get(sid, "<<no-entry>>")
            # classify
            if cat_heading == "":
                # R2 should have caught this; only happens if sid had empty catalog AND source had no h1
                kind = "R2-empty-but-no-h1?"
            elif cat_heading == "<<no-entry>>":
                kind = "sid-not-in-catalog-and-title-not-in-source"
            elif cat_heading and cat_heading not in heading_set:
                kind = "catalog-heading-not-in-source"
                cat_mismatch_cnt += 1
            else:
                kind = "other"
            r6_patterns[kind] += 1

            r6_items.append(
                {
                    "base": base,
                    "sid": sid,
                    "cache_title": cache_title[:60],
                    "catalog_heading": cat_heading[:60],
                    "source_h1": source_headings[0][1] if source_headings else "",
                    "heading_sample": [h[1] for h in source_headings[:5]],
                    "kind": kind,
                }
            )

    print(f"=== v{version} ===", file=sys.stderr)
    print(f"Total R6: {len(r6_items)}", file=sys.stderr)
    for k, n in r6_patterns.most_common():
        print(f"  {k}: {n}", file=sys.stderr)

    print(f"\nFirst {limit} R6 items:", file=sys.stderr)
    for e in r6_items[:limit]:
        print(
            f"  [{e['kind']}] {e['base']}/{e['sid']} "
            f"cat={e['catalog_heading']!r} cache={e['cache_title']!r} "
            f"src_h1={e['source_h1']!r}",
            file=sys.stderr,
        )
    return r6_items


def main():
    for v in ["1.4", "1.3", "1.2"]:
        analyze(v, limit=15)
        print(file=sys.stderr)


if __name__ == "__main__":
    main()

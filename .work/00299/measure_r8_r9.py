#!/usr/bin/env python3
"""Measure R8 rescue rate (content n-gram match) and R9 fallback page sizes
for non-h1-only fabricated P4 sids.

R8 = cache.sections[sid] content vs source text under each heading.
We compare character 3-gram Jaccard overlap. Threshold 0.3 means the
overlap ratio |A∩B|/|A∪B| ≥ 0.3.

R9 = falls through to h1 → how big is the h1-scoped content?
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from classify_p4 import (  # noqa: E402
    REPO_ROOT,
    load_catalog,
    load_cache_entries,
    parse_rst_headings,
    parse_md_headings,
    normalize,
    strip_parens,
    try_split_dash,
)


def extract_section_bodies(path: Path, headings: list[tuple[int, str, int]]) -> dict[str, str]:
    """Return heading_title -> body text (content under that heading until next same-or-higher)."""
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except FileNotFoundError:
        return {}
    out: dict[str, str] = {}
    for i, (lvl, title, ln) in enumerate(headings):
        start = ln + 2  # skip heading line + underline
        end = len(lines)
        for j in range(i + 1, len(headings)):
            if headings[j][0] <= lvl:
                end = headings[j][2]
                break
        body = "\n".join(lines[start:end])
        out[title] = body
    return out


def clean_text(s: str) -> str:
    s = re.sub(r"```[\s\S]*?```", " ", s)
    s = re.sub(r"`[^`]*`", " ", s)
    s = re.sub(r"^\s*\.\.\s+\S+::.*$", " ", s, flags=re.MULTILINE)
    s = re.sub(r":[a-z]+:`[^`]*`", " ", s)
    s = re.sub(r"\s+", "", s)
    return s


def ngrams(s: str, n: int = 3) -> set[str]:
    return {s[i:i+n] for i in range(len(s) - n + 1)} if len(s) >= n else set()


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def measure_version(version: str, threshold: float = 0.3) -> dict:
    cache_dir = REPO_ROOT / "tools/knowledge-creator/.cache" / f"v{version}"
    catalog = load_catalog(cache_dir)
    cache_by_base = load_cache_entries(cache_dir)

    catalog_by_base: dict[str, list[dict]] = defaultdict(list)
    catalog_sids: dict[str, set[str]] = defaultdict(set)
    source_by_base: dict[str, str] = {}
    format_by_base: dict[str, str] = {}
    for e in catalog["files"]:
        base = e["base_name"]
        catalog_by_base[base].append(e)
        source_by_base[base] = e["source_path"]
        format_by_base[base] = e["format"]
        for sm in e.get("section_map", []):
            catalog_sids[base].add(sm["section_id"])

    headings_cache: dict[str, list[tuple[int, str, int]]] = {}
    bodies_cache: dict[str, dict[str, str]] = {}

    def get_headings(base: str):
        if base in headings_cache:
            return headings_cache[base]
        src = source_by_base.get(base)
        fmt = format_by_base.get(base, "rst")
        path = REPO_ROOT / src if src else None
        if not path or not path.exists():
            headings_cache[base] = []
            return []
        if fmt == "rst":
            headings_cache[base] = parse_rst_headings(path)
        elif fmt == "md":
            headings_cache[base] = parse_md_headings(path)
        else:
            headings_cache[base] = []
        return headings_cache[base]

    def get_bodies(base: str):
        if base in bodies_cache:
            return bodies_cache[base]
        src = source_by_base.get(base)
        path = REPO_ROOT / src if src else None
        if not path or not path.exists():
            bodies_cache[base] = {}
            return {}
        bodies_cache[base] = extract_section_bodies(path, get_headings(base))
        return bodies_cache[base]

    r8_rescued: list[dict] = []
    r9_fallback: list[dict] = []
    h1_sizes: list[int] = []

    for base, entries in cache_by_base.items():
        if base not in catalog_by_base:
            continue
        # Skip xlsx — handled separately by Phase 21-C row-level sectioning
        if format_by_base.get(base) == "xlsx":
            continue
        cat_sids = catalog_sids.get(base, set())
        for data in entries:
            for idx in data.get("index", []):
                sid = idx.get("id")
                title = idx.get("title", "")
                hints = idx.get("hints", [])
                if sid in cat_sids:
                    continue
                headings = get_headings(base)
                heading_titles = [h[1] for h in headings]
                heading_norms = {normalize(h): h for h in heading_titles}
                # exclude heading_match
                if title in heading_titles or normalize(title) in heading_norms:
                    continue
                # exclude dash
                parts = try_split_dash(title)
                if parts and any(p in heading_titles or normalize(p) in heading_norms for p in parts):
                    continue
                stripped = strip_parens(title)
                if stripped and stripped != title and (stripped in heading_titles or normalize(stripped) in heading_norms):
                    continue
                # This is fabricated.
                h1_only = len(headings) == 1 and headings[0][0] == 1
                sections_map = data.get("sections", {})
                cache_body = clean_text(sections_map.get(sid, ""))[:2000]
                cache_ng = ngrams(cache_body)

                bodies = get_bodies(base)
                best_title = None
                best_score = 0.0
                for ht, body in bodies.items():
                    src_ng = ngrams(clean_text(body)[:2000])
                    sc = jaccard(cache_ng, src_ng)
                    if sc > best_score:
                        best_score = sc
                        best_title = ht

                record = {
                    "base": base,
                    "sid": sid,
                    "title": title,
                    "hints_count": len(hints),
                    "h1_only": h1_only,
                    "best_title": best_title,
                    "best_score": round(best_score, 3),
                }
                if not h1_only and best_score >= threshold:
                    r8_rescued.append(record)
                else:
                    r9_fallback.append(record)
                    # compute h1 source size (chars)
                    try:
                        raw = (REPO_ROOT / source_by_base[base]).read_text(encoding="utf-8", errors="replace")
                        h1_sizes.append(len(raw))
                    except Exception:
                        pass

    # stats on r9 page sizes
    def pct(xs, p):
        if not xs:
            return 0
        xs2 = sorted(xs)
        k = int(len(xs2) * p / 100)
        return xs2[min(k, len(xs2) - 1)]

    return {
        "version": version,
        "r8_rescued_count": len(r8_rescued),
        "r8_rescued_hints": sum(e["hints_count"] for e in r8_rescued),
        "r9_fallback_count": len(r9_fallback),
        "r9_fallback_hints": sum(e["hints_count"] for e in r9_fallback),
        "r9_h1_size_median_chars": pct(h1_sizes, 50),
        "r9_h1_size_p90_chars": pct(h1_sizes, 90),
        "r9_h1_size_max_chars": max(h1_sizes) if h1_sizes else 0,
        "r8_score_distribution": {
            "<0.1": sum(1 for e in r8_rescued + r9_fallback if e["best_score"] < 0.1),
            "0.1-0.3": sum(1 for e in r8_rescued + r9_fallback if 0.1 <= e["best_score"] < 0.3),
            "0.3-0.5": sum(1 for e in r8_rescued + r9_fallback if 0.3 <= e["best_score"] < 0.5),
            ">=0.5": sum(1 for e in r8_rescued + r9_fallback if e["best_score"] >= 0.5),
        },
        "r9_samples": r9_fallback[:10],
    }


def main():
    results = {}
    for v in ["6", "5", "1.4", "1.3", "1.2"]:
        print(f"=== v{v} ===", file=sys.stderr)
        r = measure_version(v)
        results[v] = r
        print(
            f"v{v}: R8 rescued={r['r8_rescued_count']} (hints {r['r8_rescued_hints']})  "
            f"R9 fallback={r['r9_fallback_count']} (hints {r['r9_fallback_hints']})  "
            f"R9 h1-size: med={r['r9_h1_size_median_chars']} p90={r['r9_h1_size_p90_chars']} max={r['r9_h1_size_max_chars']}  "
            f"dist={r['r8_score_distribution']}"
        )
    Path(".pr/00299/r8-r9-measurement.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

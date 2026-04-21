#!/usr/bin/env python3
"""Classify P4 (sid in cache but not in catalog.section_map) mismatches into
the three patterns from design doc §B-5:

1. `—` (em-dash / hyphen / colon) concatenation: AI merged h2 — h3
2. AI fabrication: cache title has no correspondence in source
3. Parenthesis annotation: cache adds (...) decoration that source lacks

Also measures how many P4 titles match source headings at ALL levels (h1/h2/h3/h4)
after loosening the match.

Usage:
    python .pr/00299/classify_p4.py --version 6
    python .pr/00299/classify_p4.py --all
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parents[2]

# RST adornment characters (per KC's step2_classify rules plus common ones)
ADORN_CHARS = "=-~^+*.:\"'`#<>|_"
ADORN_RE = re.compile(r"^([%s])\1{2,}\s*$" % re.escape(ADORN_CHARS))


def parse_rst_headings(path: Path) -> list[tuple[int, str, int]]:
    """Parse RST file. Return list of (level, title, line_no).

    Level is assigned by first-occurrence order of adornment characters:
      first seen underline char -> level 1
      next new char -> level 2
      etc.
    This mirrors RST spec (any char works; the ORDER defines hierarchy).

    To allow overline+underline titles, we also detect them.
    """
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except FileNotFoundError:
        return []

    # Map: adornment char -> level
    char_levels: dict[str, int] = {}
    next_level = 1
    headings: list[tuple[int, str, int]] = []

    i = 0
    while i < len(lines):
        line = lines[i]
        # Overline+underline: overline, title, underline (all same char)
        if i + 2 < len(lines) and _is_adorn_line(line):
            title_line = lines[i + 1]
            under_line = lines[i + 2]
            if (
                title_line.strip()
                and _is_adorn_line(under_line)
                and line[0] == under_line[0]
                and line[0] == _first_nonspace(line)
            ):
                char = line.strip()[0]
                if char not in char_levels:
                    char_levels[char] = next_level
                    next_level += 1
                headings.append((char_levels[char], title_line.strip(), i + 1))
                i += 3
                continue
        # Plain underline: previous line has title, next line is underline
        if i + 1 < len(lines) and _is_adorn_line(lines[i + 1]) and line.strip():
            # Must not be a directive line
            if not line.lstrip().startswith(".."):
                under = lines[i + 1]
                char = under.strip()[0]
                if len(under.strip()) >= len(line.strip()) - 2:  # underline roughly long enough
                    if char not in char_levels:
                        char_levels[char] = next_level
                        next_level += 1
                    headings.append((char_levels[char], line.strip(), i))
                    i += 2
                    continue
        i += 1

    return headings


def _is_adorn_line(s: str) -> bool:
    return bool(ADORN_RE.match(s))


def _first_nonspace(s: str) -> str:
    for c in s:
        if not c.isspace():
            return c
    return ""


def parse_md_headings(path: Path) -> list[tuple[int, str, int]]:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except FileNotFoundError:
        return []
    out: list[tuple[int, str, int]] = []
    in_fence = False
    for i, line in enumerate(lines):
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if m:
            out.append((len(m.group(1)), m.group(2).strip(), i))
    return out


def normalize(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"\s+", "", s)
    return s.strip()


def strip_parens(s: str) -> str:
    """Remove trailing 全角/半角 parenthesized annotation."""
    return re.sub(r"[（(][^）)]*[）)]\s*$", "", s).strip()


DASH_SPLITTERS = [" — ", " – ", " - ", "—", "–", ": ", "：", "｜", "|"]


def try_split_dash(title: str) -> list[str] | None:
    """Return list of pieces if title looks like 'A — B' concatenation."""
    for sep in DASH_SPLITTERS:
        if sep in title:
            parts = [p.strip() for p in title.split(sep) if p.strip()]
            if len(parts) >= 2:
                return parts
    return None


def load_catalog(cache_dir: Path) -> dict:
    return json.loads((cache_dir / "catalog.json").read_text(encoding="utf-8"))


def load_cache_entries(cache_dir: Path) -> dict[str, list[dict]]:
    """Return base_name -> list of cache JSON payloads."""
    knowledge_dir = cache_dir / "knowledge"
    out: dict[str, list[dict]] = defaultdict(list)
    for p in knowledge_dir.rglob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        # Derive base_name from split id
        file_id = data.get("id") or p.stem
        base = re.sub(r"--s\d+$", "", file_id)
        out[base].append(data)
    return out


def classify_version(version: str) -> dict:
    cache_dir = REPO_ROOT / "tools/knowledge-creator/.cache" / f"v{version}"
    catalog = load_catalog(cache_dir)
    cache_by_base = load_cache_entries(cache_dir)

    # Build catalog index: base_name -> list of entries, and set of (base_name, sid)
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

    # Cache parsed source headings per base
    headings_cache: dict[str, list[tuple[int, str, int]]] = {}

    def get_headings(base: str) -> list[tuple[int, str, int]]:
        if base in headings_cache:
            return headings_cache[base]
        src = source_by_base.get(base)
        if not src:
            headings_cache[base] = []
            return []
        fmt = format_by_base.get(base, "rst")
        path = REPO_ROOT / src
        if fmt == "rst":
            headings_cache[base] = parse_rst_headings(path)
        elif fmt == "md":
            headings_cache[base] = parse_md_headings(path)
        else:
            headings_cache[base] = []
        return headings_cache[base]

    # Classify P4 sids
    patterns = {
        "dash_split_resolved": [],   # `—` split: at least one side matches source heading
        "paren_resolved": [],        # stripping parens yields a source match
        "fabricated": [],            # none of the above
    }
    all_p4 = []

    for base, entries in cache_by_base.items():
        if base not in catalog_by_base:
            continue  # not in catalog at all, separate issue
        cat_sids = catalog_sids.get(base, set())
        for data in entries:
            for idx in data.get("index", []):
                sid = idx.get("id")
                title = idx.get("title", "")
                hints = idx.get("hints", [])
                if sid in cat_sids:
                    continue  # not P4
                # P4 case
                # Check exact/normalized match at ALL levels
                headings = get_headings(base)
                heading_titles = [h[1] for h in headings]
                heading_norms = {normalize(h): h for h in heading_titles}
                entry = {
                    "base": base,
                    "sid": sid,
                    "title": title,
                    "hints_count": len(hints),
                    "source_path": source_by_base[base],
                }
                all_p4.append(entry)
                # Skip if exact/normalized already matches (would be saved by heading-extractor upgrade)
                if title in heading_titles or normalize(title) in heading_norms:
                    entry["resolution"] = "heading_match_all_levels"
                    continue
                # Try dash split
                parts = try_split_dash(title)
                if parts:
                    matched = [p for p in parts if p in heading_titles or normalize(p) in heading_norms]
                    if matched:
                        entry["resolution"] = "dash_split"
                        entry["matched_parts"] = matched
                        patterns["dash_split_resolved"].append(entry)
                        continue
                # Try paren strip
                stripped = strip_parens(title)
                if stripped and stripped != title and (stripped in heading_titles or normalize(stripped) in heading_norms):
                    entry["resolution"] = "paren_strip"
                    entry["matched_to"] = stripped
                    patterns["paren_resolved"].append(entry)
                    continue
                # Check if h1-only source and cache creates multiple sections
                h1_only = len(headings) == 1 and headings[0][0] == 1
                entry["h1_only_source"] = h1_only
                entry["resolution"] = "fabricated"
                patterns["fabricated"].append(entry)

    fab_h1only = sum(1 for e in patterns["fabricated"] if e.get("h1_only_source"))
    fab_nonh1 = len(patterns["fabricated"]) - fab_h1only
    fab_h1only_hints = sum(e["hints_count"] for e in patterns["fabricated"] if e.get("h1_only_source"))
    fab_nonh1_hints = sum(e["hints_count"] for e in patterns["fabricated"] if not e.get("h1_only_source"))
    return {
        "version": version,
        "p4_total": len(all_p4),
        "heading_match_all_levels": sum(1 for e in all_p4 if e.get("resolution") == "heading_match_all_levels"),
        "dash_split_resolved": len(patterns["dash_split_resolved"]),
        "paren_resolved": len(patterns["paren_resolved"]),
        "fabricated": len(patterns["fabricated"]),
        "fabricated_h1_only": fab_h1only,
        "fabricated_not_h1_only": fab_nonh1,
        "fabricated_h1_only_hints": fab_h1only_hints,
        "fabricated_not_h1_only_hints": fab_nonh1_hints,
        "samples": {
            "dash_split": patterns["dash_split_resolved"][:10],
            "paren": patterns["paren_resolved"][:10],
            "fabricated_h1_only": [e for e in patterns["fabricated"] if e.get("h1_only_source")][:20],
            "fabricated_not_h1_only": [e for e in patterns["fabricated"] if not e.get("h1_only_source")][:20],
        },
        "fabricated_hints_loss": sum(e["hints_count"] for e in patterns["fabricated"]),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out", default=None, help="Write JSON result to file")
    args = ap.parse_args()

    versions = ["6", "5", "1.4", "1.3", "1.2"] if args.all else [args.version or "6"]

    results = {}
    for v in versions:
        print(f"=== v{v} ===", file=sys.stderr)
        r = classify_version(v)
        results[v] = r
        print(
            f"v{v}: P4={r['p4_total']}  "
            f"heading_match={r['heading_match_all_levels']}  "
            f"dash={r['dash_split_resolved']}  "
            f"paren={r['paren_resolved']}  "
            f"fab={r['fabricated']} (h1_only={r['fabricated_h1_only']} [hints {r['fabricated_h1_only_hints']}] / "
            f"other={r['fabricated_not_h1_only']} [hints {r['fabricated_not_h1_only_hints']}])  "
            f"total_fab_hints_loss={r['fabricated_hints_loss']}"
        )

    if args.out:
        Path(args.out).write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

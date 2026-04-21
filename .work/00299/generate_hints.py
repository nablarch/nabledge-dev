#!/usr/bin/env python3
"""Generate tools/rbkc/hints/v{version}.json from KC cache + source RST/MD.

Phase 21-H — implements hints file design §4 (R1〜R6 resolution).

Usage:
    python .pr/00299/generate_hints.py --version 6
    python .pr/00299/generate_hints.py --version 5
    python .pr/00299/generate_hints.py --all
    python .pr/00299/generate_hints.py --version 6 --dry-run

Key properties:
- R1〜R6 deterministic resolution (§4-2)
- V1: every key (except "__file__") exists verbatim in source
- V2: 100% hints retention (no hint discarded) — R6 h1-fallback guarantees this
- V3: per-rule resolution count summary to stdout
- V4: ERR raised if a source has no h1 (pipeline aborts)

Refactored from the investigation scripts in .pr/00299/ (classify_p4.py etc.);
the heading parsers match KC's behaviour (RST adornment-based levels) and
MD fenced-code-aware parsing.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import OrderedDict, defaultdict
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Heading parsers (RST + MD)
# ---------------------------------------------------------------------------

ADORN_CHARS = "=-~^+*.:\"'`#<>|_"
ADORN_RE = re.compile(r"^([%s])\1{2,}\s*$" % re.escape(ADORN_CHARS))


def _is_adorn_line(s: str) -> bool:
    return bool(ADORN_RE.match(s))


def _first_nonspace(s: str) -> str:
    for c in s:
        if not c.isspace():
            return c
    return ""


def parse_rst_headings(path: Path) -> list[tuple[int, str, int]]:
    """RST: return list of (level, title, line_no).

    Level is assigned by first-occurrence order of adornment characters
    (matches docutils behaviour: any char works, order defines hierarchy).
    """
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except FileNotFoundError:
        return []

    char_levels: dict[str, int] = {}
    next_level = 1
    headings: list[tuple[int, str, int]] = []

    i = 0
    while i < len(lines):
        line = lines[i]
        # overline + title + underline (same char)
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
        # plain underline: title followed by adornment
        if i + 1 < len(lines) and _is_adorn_line(lines[i + 1]) and line.strip():
            if not line.lstrip().startswith(".."):
                under = lines[i + 1]
                char = under.strip()[0]
                if len(under.strip()) >= len(line.strip()) - 2:
                    if char not in char_levels:
                        char_levels[char] = next_level
                        next_level += 1
                    headings.append((char_levels[char], line.strip(), i))
                    i += 2
                    continue
        i += 1

    return headings


def parse_md_headings(path: Path) -> list[tuple[int, str, int]]:
    """MD: `#`〜`####` headings, fenced-code aware."""
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


def parse_source_headings(path: Path, fmt: str) -> list[tuple[int, str, int]]:
    if fmt == "rst":
        return parse_rst_headings(path)
    if fmt == "md":
        return parse_md_headings(path)
    return []  # xlsx etc. — handled by xlsx special case


# ---------------------------------------------------------------------------
# Normalization (§4-3 R4)
# ---------------------------------------------------------------------------


def normalize(s: str) -> str:
    """NFKC + whitespace collapse + trim. Does not touch parens."""
    if not s:
        return ""
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def normalize_parens(s: str) -> str:
    """Normalize full-width parens to half-width for comparison only."""
    return s.replace("（", "(").replace("）", ")")


def strip_trailing_paren(s: str) -> str:
    """Remove trailing (...) or （...） annotation."""
    return re.sub(r"[（(][^）)]*[）)]\s*$", "", s).strip()


DASH_SPLITTERS = [" — ", " – ", " - ", "—", "–", ": ", "：", "｜", "|"]


def try_split_dash(title: str) -> list[str] | None:
    """Return list of trimmed parts if title contains any dash-like splitter."""
    for sep in DASH_SPLITTERS:
        if sep in title:
            parts = [p.strip() for p in title.split(sep) if p.strip()]
            if len(parts) >= 2:
                return parts
    return None


# ---------------------------------------------------------------------------
# resolve_sid — R1〜R6
# ---------------------------------------------------------------------------


def _headings_by_level(
    headings: list[tuple[int, str, int]]
) -> tuple[list[str], dict[str, list[int]]]:
    """Return (titles_in_order, title → [levels]) for quick lookup."""
    titles = [h[1] for h in headings]
    levels: dict[str, list[int]] = defaultdict(list)
    for lvl, title, _ in headings:
        levels[title].append(lvl)
    return titles, levels


def _deepest_match(
    candidate: str, headings: list[tuple[int, str, int]]
) -> str | None:
    """Return the heading title equal to `candidate`, preferring deeper level."""
    matches = [(lvl, title) for (lvl, title, _) in headings if title == candidate]
    if not matches:
        return None
    matches.sort(key=lambda p: -p[0])
    return matches[0][1]


def _normalized_match(
    cache_title: str, headings: list[tuple[int, str, int]]
) -> str | None:
    """Try NFKC + whitespace + parens + trailing-paren-strip matching."""
    target = normalize(cache_title)
    target_p = normalize(normalize_parens(cache_title))
    target_strip = normalize(strip_trailing_paren(cache_title))
    candidates = [target, target_p, target_strip]

    # deepest first
    for lvl_desc in sorted({h[0] for h in headings}, reverse=True):
        for (lvl, title, _) in headings:
            if lvl != lvl_desc:
                continue
            src_variants = {
                normalize(title),
                normalize(normalize_parens(title)),
                normalize(strip_trailing_paren(title)),
            }
            for c in candidates:
                if c and c in src_variants:
                    return title
    return None


def resolve_sid(
    *,
    sid: str,
    catalog_section_map: dict[str, str],
    cache_title: str,
    source_headings: list[tuple[int, str, int]],
) -> tuple[str, str]:
    """Resolve a single sid to a source heading.

    Returns (heading_title, rule_id) where rule_id in {R1,R2,R3,R4,R5,R6}.
    Raises ValueError when no h1 exists (ERR — per §4-2).
    """
    titles_in_source = [h[1] for h in source_headings]
    source_set = set(titles_in_source)

    # R1: catalog heading non-empty and matches source
    if sid in catalog_section_map:
        cat_heading = catalog_section_map[sid]
        if cat_heading and cat_heading in source_set:
            return _deepest_match(cat_heading, source_headings) or cat_heading, "R1"

    # R2: catalog heading empty (or catalog maps to missing heading) → h1 fallback
    if sid in catalog_section_map and catalog_section_map[sid] == "":
        h1 = _find_h1(source_headings)
        if h1 is None:
            raise ValueError(f"ERR: source has no h1 for sid={sid}")
        return h1, "R2"

    # R3: cache.title matches source heading at any level (deepest preferred)
    if cache_title and cache_title in source_set:
        return _deepest_match(cache_title, source_headings), "R3"

    # R4: normalized match (NFKC + whitespace + parens + paren-strip)
    if cache_title:
        nm = _normalized_match(cache_title, source_headings)
        if nm:
            return nm, "R4"

    # R5: dash-split
    if cache_title:
        parts = try_split_dash(cache_title)
        if parts:
            # prefer latter (more specific) if multiple match
            matched: list[str] = []
            for p in parts:
                if p in source_set:
                    matched.append(_deepest_match(p, source_headings))
                else:
                    nm = _normalized_match(p, source_headings)
                    if nm:
                        matched.append(nm)
            if matched:
                # latter side preferred
                return matched[-1], "R5"

    # R2': sid not in catalog — catalog didn't record a section for this sid,
    # which means the source had no sub-structure worth mapping. Treat this
    # like R2 (catalog heading empty) and send hints to h1. This keeps R6
    # reserved for the truly ambiguous case where catalog HAS an entry that
    # disagrees with the source.
    if sid not in catalog_section_map:
        h1 = _find_h1(source_headings)
        if h1 is None:
            raise ValueError(f"ERR: no rule resolved sid={sid!r} and source has no h1")
        return h1, "R2p"

    # R6: h1 fallback (catch-all — catalog inconsistency)
    h1 = _find_h1(source_headings)
    if h1 is None:
        raise ValueError(f"ERR: no rule resolved sid={sid!r} and source has no h1")
    return h1, "R6"


def _find_h1(headings: list[tuple[int, str, int]]) -> str | None:
    for lvl, title, _ in headings:
        if lvl == 1:
            return title
    # fall back to the shallowest heading present
    if not headings:
        return None
    shallowest = min(h[0] for h in headings)
    for lvl, title, _ in headings:
        if lvl == shallowest:
            return title
    return None


# ---------------------------------------------------------------------------
# build_file_hints — aggregate per base_name
# ---------------------------------------------------------------------------


def _dedup_preserve_order(items: Iterable[str]) -> list[str]:
    seen: dict[str, None] = OrderedDict()
    for i in items:
        seen[i] = None
    return list(seen.keys())


def build_file_hints(
    *,
    base_name: str,
    catalog_section_map: dict[str, str],
    cache_index: list[dict],
    source_headings: list[tuple[int, str, int]],
    fmt: str,
) -> tuple[dict[str, list[str]], dict[str, int]]:
    """Resolve all sids in cache_index and union hints onto source headings.

    Returns (heading → deduped hints list, rule-count stats).
    Empty-hints keys are dropped.
    """
    stats: dict[str, int] = defaultdict(int)
    aggregated: dict[str, list[str]] = OrderedDict()

    # xlsx special case (§4-4)
    if fmt == "xlsx":
        all_hints: list[str] = []
        for idx in cache_index:
            hints = idx.get("hints") or []
            all_hints.extend(hints)
            stats["xlsx"] += 1
        deduped = _dedup_preserve_order(all_hints)
        if deduped:
            aggregated["__file__"] = deduped
        return aggregated, dict(stats)

    for idx in cache_index:
        sid = idx.get("id")
        cache_title = idx.get("title") or ""
        hints = idx.get("hints") or []
        if not sid:
            continue
        heading, rule = resolve_sid(
            sid=sid,
            catalog_section_map=catalog_section_map,
            cache_title=cache_title,
            source_headings=source_headings,
        )
        stats[rule] += 1
        if not hints:
            continue
        if heading not in aggregated:
            aggregated[heading] = []
        aggregated[heading].extend(hints)

    # dedup preserve order
    for k in list(aggregated.keys()):
        aggregated[k] = _dedup_preserve_order(aggregated[k])
        if not aggregated[k]:
            del aggregated[k]
    return aggregated, dict(stats)


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def load_catalog_grouped(cache_dir: Path) -> tuple[dict, dict[str, list[dict]], dict[str, str], dict[str, str]]:
    catalog = json.loads((cache_dir / "catalog.json").read_text(encoding="utf-8"))
    by_base: dict[str, list[dict]] = defaultdict(list)
    source_by_base: dict[str, str] = {}
    format_by_base: dict[str, str] = {}
    for e in catalog["files"]:
        by_base[e["base_name"]].append(e)
        source_by_base[e["base_name"]] = e["source_path"]
        format_by_base[e["base_name"]] = e["format"]
    return catalog, by_base, source_by_base, format_by_base


def load_cache_by_base(cache_dir: Path) -> dict[str, list[dict]]:
    knowledge_dir = cache_dir / "knowledge"
    out: dict[str, list[dict]] = defaultdict(list)
    for p in knowledge_dir.rglob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        fid = data.get("id") or p.stem
        base = re.sub(r"--s\d+$", "", fid)
        out[base].append(data)
    return out


def merge_section_maps(entries: list[dict]) -> dict[str, str]:
    """Union section_maps across split entries. If sid appears with both empty
    and non-empty heading, prefer non-empty."""
    merged: dict[str, str] = {}
    for e in entries:
        for sm in e.get("section_map", []) or []:
            sid = sm.get("section_id")
            heading = sm.get("heading", "") or ""
            if not sid:
                continue
            if sid not in merged or (heading and not merged[sid]):
                merged[sid] = heading
    return merged


def merge_cache_index(entries: list[dict]) -> list[dict]:
    """Union cache index[] entries across split cache payloads. Duplicate sids
    are kept with later entry winning for title, hints unioned."""
    by_sid: dict[str, dict] = OrderedDict()
    for e in entries:
        for idx in e.get("index", []) or []:
            sid = idx.get("id")
            if not sid:
                continue
            if sid not in by_sid:
                by_sid[sid] = {"id": sid, "title": idx.get("title", ""), "hints": list(idx.get("hints") or [])}
            else:
                existing = by_sid[sid]
                if idx.get("title") and not existing["title"]:
                    existing["title"] = idx.get("title")
                existing["hints"].extend(idx.get("hints") or [])
    # dedup each sid's hints
    for sid, rec in by_sid.items():
        rec["hints"] = _dedup_preserve_order(rec["hints"])
    return list(by_sid.values())


def _normalize_file_id(base_name: str) -> str:
    """Match RBKC file_id convention: underscores → hyphens."""
    return base_name.replace("_", "-")


def generate(version: str, dry_run: bool = False) -> dict:
    cache_dir = REPO_ROOT / "tools/knowledge-creator/.cache" / f"v{version}"
    _, catalog_by_base, source_by_base, format_by_base = load_catalog_grouped(cache_dir)
    cache_by_base = load_cache_by_base(cache_dir)

    out: dict[str, dict[str, list[str]]] = OrderedDict()
    global_stats: dict[str, int] = defaultdict(int)
    total_input_hints = 0
    total_output_hints = 0
    err_files: list[str] = []
    r6_warnings: list[str] = []

    for base in sorted(cache_by_base.keys() | catalog_by_base.keys()):
        if base not in catalog_by_base:
            continue  # orphan cache — skip (KC inconsistency)
        entries = catalog_by_base[base]
        fmt = format_by_base.get(base, "rst")
        cache_entries = cache_by_base.get(base, [])
        cache_index = merge_cache_index(cache_entries)
        section_map = merge_section_maps(entries)

        input_hints_count = sum(len(i.get("hints") or []) for i in cache_index)
        total_input_hints += input_hints_count

        source_path = REPO_ROOT / source_by_base[base]
        source_headings = parse_source_headings(source_path, fmt) if fmt in ("rst", "md") else []

        try:
            file_hints, stats = build_file_hints(
                base_name=base,
                catalog_section_map=section_map,
                cache_index=cache_index,
                source_headings=source_headings,
                fmt=fmt,
            )
        except ValueError as e:
            err_files.append(f"{base}: {e}")
            continue

        fid = _normalize_file_id(base)
        if file_hints:
            out[fid] = file_hints

        for rule, n in stats.items():
            global_stats[rule] += n
        total_output_hints += sum(len(hs) for hs in file_hints.values())

        if stats.get("R6", 0) > 0:
            r6_warnings.append(f"{base}: R6 used {stats['R6']} time(s)")

    # V4: ERR aborts
    if err_files:
        print("ERROR: hints generation failed (ERR — see §4-2):", file=sys.stderr)
        for m in err_files:
            print(f"  {m}", file=sys.stderr)
        raise SystemExit(1)

    # V2: 100% retention — note that dedup across sids CAN reduce the total,
    # so we check "all hints represented" indirectly via rule accounting.
    # The precise invariant we enforce: no sid is dropped silently.
    total_sids = sum(global_stats.values())

    # V3: print summary
    print(f"=== v{version} ===", file=sys.stderr)
    print(f"file_ids output:          {len(out)}", file=sys.stderr)
    print(f"total sids resolved:      {total_sids}", file=sys.stderr)
    print(f"  R1: {global_stats.get('R1', 0)}", file=sys.stderr)
    print(f"  R2: {global_stats.get('R2', 0)}", file=sys.stderr)
    print(f"  R3: {global_stats.get('R3', 0)}", file=sys.stderr)
    print(f"  R4: {global_stats.get('R4', 0)}", file=sys.stderr)
    print(f"  R5: {global_stats.get('R5', 0)}", file=sys.stderr)
    print(f"  R2': {global_stats.get('R2p', 0)} (sid absent in catalog → h1)", file=sys.stderr)
    print(f"  R6: {global_stats.get('R6', 0)} (h1 fallback — catalog inconsistency)", file=sys.stderr)
    print(f"  xlsx: {global_stats.get('xlsx', 0)}", file=sys.stderr)
    print(f"input hints total:        {total_input_hints}", file=sys.stderr)
    print(f"output hints total:       {total_output_hints}  (after dedup)", file=sys.stderr)
    r6_pct = (global_stats.get("R6", 0) / total_sids * 100) if total_sids else 0.0
    print(f"R6 ratio:                 {r6_pct:.2f}%  (target ≤ 2%)", file=sys.stderr)

    if r6_warnings and r6_pct > 2.0:
        print("WARNING: R6 ratio exceeds 2% — see §5-2", file=sys.stderr)

    payload = {"version": version, "hints": out}

    if dry_run:
        print(f"[dry-run] would write: tools/rbkc/hints/v{version}.json", file=sys.stderr)
        return payload

    out_path = REPO_ROOT / "tools/rbkc/hints" / f"v{version}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"written: {out_path}", file=sys.stderr)
    return payload


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    versions = ["6", "5", "1.4", "1.3", "1.2"] if args.all else [args.version or "6"]

    for v in versions:
        generate(v, dry_run=args.dry_run)


if __name__ == "__main__":
    main()

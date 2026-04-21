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
                if len(under.strip()) >= len(line.strip()):
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
    # drop empties so a normalized-to-empty candidate can't match arbitrarily
    candidates = [c for c in (target, target_p, target_strip) if c]
    if not candidates:
        return None

    # deepest first
    for lvl_desc in sorted({h[0] for h in headings}, reverse=True):
        for (lvl, title, _) in headings:
            if lvl != lvl_desc:
                continue
            src_variants = {
                v for v in (
                    normalize(title),
                    normalize(normalize_parens(title)),
                    normalize(strip_trailing_paren(title)),
                ) if v
            }
            for c in candidates:
                if c in src_variants:
                    return title
    return None


def resolve_sid(
    *,
    sid: str,
    catalog_section_map: dict[str, str],
    cache_title: str,
    source_headings: list[tuple[int, str, int]],
    catalog_ever_empty: set[str] | None = None,
) -> tuple[str, str]:
    """Resolve a single sid to a source heading.

    Returns (heading_title, rule_id) where rule_id in {R1,R2,R3,R4,R5,R2p,R6}.
    Raises ValueError when no h1 exists (ERR — per §4-2).

    catalog_ever_empty: sids for which any catalog entry had empty heading.
        When provided and sid is in it, R2 fires (h1 fallback) even if another
        split entry supplied a non-empty heading that disagrees with source.
    """
    titles_in_source = [h[1] for h in source_headings]
    source_set = set(titles_in_source)
    ever_empty = catalog_ever_empty or set()

    # R1: catalog heading non-empty and matches source
    if sid in catalog_section_map:
        cat_heading = catalog_section_map[sid]
        if cat_heading and cat_heading in source_set:
            # _deepest_match cannot fail here because cat_heading is in source_set
            return _deepest_match(cat_heading, source_headings), "R1"

    # R2: catalog heading empty (or was empty in any split entry) → h1 fallback
    if sid in catalog_section_map and (
        catalog_section_map[sid] == "" or sid in ever_empty
    ):
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
    """Return the first level=1 heading title, or None. No shallow fallback —
    spec §4-2 ERR requires a true h1; silently accepting h2 would hide V4
    violations."""
    for lvl, title, _ in headings:
        if lvl == 1:
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
    catalog_ever_empty: set[str] | None = None,
    unmapped_log: list[dict] | None = None,
) -> tuple[list[dict], dict[str, int]]:
    """Resolve all sids in cache_index and union hints onto source headings.

    Returns (list of {"title": ..., "hints": [...]} in source order, rule-count stats).
    Empty-hints entries are dropped.

    Output is an ARRAY (not dict) so same-named headings at different positions
    in the source are preserved as distinct entries (e.g., BeanUtil has two
    different "使用方法" sections under different h2 parents).

    V1: every emitted title (except "__file__") exists verbatim in source.
    Array order follows source heading order; xlsx uses a single "__file__" entry.
    """
    stats: dict[str, int] = defaultdict(int)

    # xlsx special case (§4-4)
    if fmt == "xlsx":
        all_hints: list[str] = []
        for idx in cache_index:
            hints = idx.get("hints") or []
            all_hints.extend(hints)
            stats["xlsx"] += 1
        deduped = _dedup_preserve_order(all_hints)
        if deduped:
            return [{"title": "__file__", "hints": deduped}], dict(stats)
        return [], dict(stats)

    # Map source heading title → list of (line_no, slot_index) so we can
    # distribute hints to the correct occurrence for duplicate titles.
    # Strategy: for each title, maintain an index; each resolved sid that
    # matches a title fills that title's next unresolved slot in source order.
    # For R2/R2p/R6 (h1 fallback), always goes to the h1 slot (first
    # occurrence of the h1 title).

    # Build ordered slots [{title, hints, line_no}]
    slots: list[dict] = []
    for lvl, title, line_no in source_headings:
        slots.append({"title": title, "hints": [], "_line": line_no, "_lvl": lvl})

    # For duplicate-title resolution: map title → list of slot indices in source order
    title_to_slots: dict[str, list[int]] = defaultdict(list)
    for i, s in enumerate(slots):
        title_to_slots[s["title"]].append(i)
    title_cursor: dict[str, int] = defaultdict(int)

    h1_slot_idx = next(
        (i for i, s in enumerate(slots) if s["_lvl"] == 1), None
    )

    def allocate_slot(title: str, is_h1_fallback: bool) -> tuple[int | None, bool]:
        """Pick the next slot for this title.

        Returns (slot_index, overflowed_to_h1). When N sids resolve to a title
        that appears M times in source (N > M), the (N-M+1)th sid onward
        overflow — we reroute them to h1 instead of wrapping (which would
        silently merge distinct subsections' hints into the first slot).
        The overflow is reclassified as R6 by the caller.
        """
        if is_h1_fallback:
            return h1_slot_idx, False
        idxs = title_to_slots.get(title)
        if not idxs:
            return None, False
        cur = title_cursor[title]
        if cur >= len(idxs):
            # overflow → h1 (reclassify as R6 — catalog/source cardinality mismatch)
            return h1_slot_idx, True
        slot = idxs[cur]
        title_cursor[title] = cur + 1
        return slot, False

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
            catalog_ever_empty=catalog_ever_empty,
        )
        if not hints:
            stats[rule] += 1
            continue
        is_h1_fallback = rule in ("R2", "R2p", "R6")
        slot_idx, overflowed = allocate_slot(heading, is_h1_fallback)
        if slot_idx is None:
            # Either resolve_sid returned a title not in source (V1 bug) or
            # overflow tried to fall back to h1 but source has no h1 (V4 bug).
            raise ValueError(
                f"ERR: allocator failed — heading {heading!r} for base "
                f"{base_name!r} has no slot (V1 or V4 violation)"
            )
        # Reclassify duplicate-title overflow as R6 for audit accuracy
        effective_rule = "R6" if overflowed else rule
        stats[effective_rule] += 1
        slots[slot_idx]["hints"].extend(hints)

        # Record sids that needed h1 fallback (R2/R2p/R6/overflow) for audit
        if unmapped_log is not None and effective_rule in ("R2", "R2p", "R6"):
            unmapped_log.append({
                "base": base_name,
                "sid": sid,
                "cache_title": cache_title,
                "catalog_heading": catalog_section_map.get(sid, "<absent>"),
                "rule": effective_rule,
                "overflow": overflowed,
                "resolved_to": slots[slot_idx]["title"],
                "hints_count": len(hints),
            })

    # Drop empty slots, dedup hints, strip internal fields
    out: list[dict] = []
    for s in slots:
        deduped = _dedup_preserve_order(s["hints"])
        if deduped:
            out.append({"title": s["title"], "hints": deduped})

    # V1 post-check: every emitted title must exist in source
    source_title_set = {t for _, t, _ in source_headings}
    for entry in out:
        if entry["title"] == "__file__":
            continue
        if entry["title"] not in source_title_set:
            raise ValueError(
                f"ERR: V1 violation — title {entry['title']!r} for base "
                f"{base_name!r} not in source headings"
            )

    # V2 per-base retention: every input hint (dedup'd) must appear in output
    input_hints_set = set()
    for idx in cache_index:
        input_hints_set.update(idx.get("hints") or [])
    output_hints_set = set()
    for entry in out:
        output_hints_set.update(entry["hints"])
    missing = input_hints_set - output_hints_set
    if missing:
        raise ValueError(
            f"ERR: V2 violation — {len(missing)} hint(s) dropped for base "
            f"{base_name!r}: {sorted(missing)[:5]!r}"
        )
    return out, dict(stats)


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def load_catalog_grouped(
    cache_dir: Path,
) -> tuple[dict, dict[str, list[dict]], dict[str, str], dict[str, str], dict[str, str]]:
    """Load catalog and index by base_name.

    Returns (catalog, by_base, source_by_base, format_by_base, id_to_base).
    id_to_base maps catalog entry id (e.g. "biz-samples-01--s1") → base_name.
    """
    catalog = json.loads((cache_dir / "catalog.json").read_text(encoding="utf-8"))
    by_base: dict[str, list[dict]] = defaultdict(list)
    source_by_base: dict[str, str] = {}
    format_by_base: dict[str, str] = {}
    id_to_base: dict[str, str] = {}
    for e in catalog["files"]:
        by_base[e["base_name"]].append(e)
        source_by_base[e["base_name"]] = e["source_path"]
        format_by_base[e["base_name"]] = e["format"]
        if e.get("id"):
            id_to_base[e["id"]] = e["base_name"]
    return catalog, by_base, source_by_base, format_by_base, id_to_base


def load_cache_by_base(
    cache_dir: Path, id_to_base: dict[str, str]
) -> dict[str, list[dict]]:
    """Group knowledge cache by catalog's base_name.

    Caller must provide a map from knowledge id (e.g. "biz-samples-01--s1")
    to catalog base_name (e.g. "about-nablarch-01"). Knowledge files whose
    id has no catalog entry are grouped under a synthetic base of the id
    with "--s\\d+$" stripped, so they surface as orphan ERR.
    """
    knowledge_dir = cache_dir / "knowledge"
    out: dict[str, list[dict]] = defaultdict(list)
    for p in knowledge_dir.rglob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        fid = data.get("id") or p.stem
        base = id_to_base.get(fid) or re.sub(r"--s\d+$", "", fid)
        out[base].append(data)
    return out


def merge_section_maps(entries: list[dict]) -> tuple[dict[str, str], set[str]]:
    """Union section_maps across split entries.

    Returns (merged heading map, set of sids that had empty heading in ANY entry).

    If a sid appears with both empty and non-empty heading across split
    entries, the non-empty one wins in `merged` — but we also record the
    sid in `ever_empty` so R2 can still fire when the non-empty heading is
    not in source (preserves R2's intent: "catalog didn't know the heading").
    """
    merged: dict[str, str] = {}
    ever_empty: set[str] = set()
    for e in entries:
        for sm in e.get("section_map", []) or []:
            sid = sm.get("section_id")
            heading = sm.get("heading", "") or ""
            if not sid:
                continue
            if not heading:
                ever_empty.add(sid)
            if sid not in merged or (heading and not merged[sid]):
                merged[sid] = heading
    return merged, ever_empty


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
    _, catalog_by_base, source_by_base, format_by_base, id_to_base = load_catalog_grouped(cache_dir)
    cache_by_base = load_cache_by_base(cache_dir, id_to_base)

    out: dict[str, list[dict]] = OrderedDict()
    global_stats: dict[str, int] = defaultdict(int)
    total_input_hints = 0
    total_output_hints = 0
    err_files: list[str] = []

    orphan_caches: list[str] = []
    # Per-sid log for sids that could not be mapped to a source-faithful slot
    # (R6 catalog-inconsistency + overflow-to-h1). These deserve inspection
    # so humans can decide whether to fix KC catalog or accept the fallback.
    unmapped_log: list[dict] = []

    for base in sorted(cache_by_base.keys() | catalog_by_base.keys()):
        if base not in catalog_by_base:
            # Orphan cache — KC inconsistency. V2 says no hints are lost, so
            # drop-with-silence is unacceptable. Count these for ERR aggregation.
            cache_entries = cache_by_base.get(base, [])
            orphan_hints = sum(
                len(i.get("hints") or [])
                for e in cache_entries
                for i in (e.get("index") or [])
            )
            if orphan_hints:
                orphan_caches.append(f"{base}: {orphan_hints} orphan hint(s)")
            continue
        entries = catalog_by_base[base]
        fmt = format_by_base.get(base, "rst")
        cache_entries = cache_by_base.get(base, [])
        cache_index = merge_cache_index(cache_entries)
        section_map, ever_empty = merge_section_maps(entries)

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
                catalog_ever_empty=ever_empty,
                unmapped_log=unmapped_log,
            )
        except ValueError as e:
            err_files.append(f"{base}: {e}")
            continue

        fid = _normalize_file_id(base)
        if file_hints:
            out[fid] = file_hints

        for rule, n in stats.items():
            global_stats[rule] += n
        total_output_hints += sum(len(e["hints"]) for e in file_hints)

    # V4: ERR aborts (orphan caches with hints are also fatal — V2)
    if err_files or orphan_caches:
        print("ERROR: hints generation failed:", file=sys.stderr)
        for m in err_files:
            print(f"  [V1/V4] {m}", file=sys.stderr)
        for m in orphan_caches:
            print(f"  [V2 orphan] {m}", file=sys.stderr)
        raise SystemExit(1)

    # V2: 100% retention — note that dedup across sids CAN reduce the total,
    # so we check "all hints represented" indirectly via rule accounting.
    # The precise invariant we enforce: no sid is dropped silently.
    total_sids = sum(global_stats.values())
    non_xlsx_sids = total_sids - global_stats.get("xlsx", 0)

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
    payload = {"version": version, "hints": out}

    # Unmapped log — sids that could not be mapped to a source-faithful slot
    # (R2 / R2' / R6 / overflow-to-h1 cases). Written alongside the hints file
    # so humans can audit whether KC catalog or source should be fixed.
    unmapped_payload = {
        "version": version,
        "summary": {
            "R2": global_stats.get("R2", 0),
            "R2p": global_stats.get("R2p", 0),
            "R6": global_stats.get("R6", 0),
            "non_xlsx_sids": non_xlsx_sids,
        },
        "entries": unmapped_log,
    }

    if dry_run:
        print(f"[dry-run] would write: tools/rbkc/hints/v{version}.json", file=sys.stderr)
        print(f"[dry-run] would write: .pr/00299/unmapped-v{version}.json ({len(unmapped_log)} entries)", file=sys.stderr)
        return payload

    out_path = REPO_ROOT / "tools/rbkc/hints" / f"v{version}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"written: {out_path}", file=sys.stderr)

    log_path = REPO_ROOT / ".pr/00299" / f"unmapped-v{version}.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        json.dumps(unmapped_payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"written: {log_path} ({len(unmapped_log)} unmapped sid(s))", file=sys.stderr)
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

#!/usr/bin/env python3
"""Section-level TF keyword extraction for index-llm.md enrichment.

Reads the v{version} knowledge base and emits, per section, the list of
Japanese keywords to attach to that section's line in `index-llm.md`.

Pipeline (see `tools/benchmark/docs/index-enrichment.md`):

  1. tokenize each section body (Japanese 4+ char patterns, dedup per span)
  2. drop tokens that are in the manual stoplist
  3. drop tokens that are substrings of the page title or section title
  4. rank surviving tokens by TF, pick:
        - primary:  tf >= TF_THRESHOLD, top TOP_N
        - fallback: if primary empty, tf >= FALLBACK_TF AND df <= FALLBACK_DF_MAX,
                    top FALLBACK_TOP_N (only if primary produced nothing)
  5. ties broken alphabetically for determinism

Default params are the ones FROZEN in `.work/00307/index-params-decision.md`:
  TF_THRESHOLD=2, TOP_N=5, FALLBACK_TF=1, FALLBACK_DF_MAX=20, FALLBACK_TOP_N=3.

Output: JSON object keyed by "page_id|section_id" → ordered list of keyword
strings. Paths and section ids match what `build_index.py` reads.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from collections import Counter
from typing import Iterator

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PATTERN_KATAKANA = re.compile(r'[゠-ヿー]{4,}')
PATTERN_KANJI = re.compile(r'[一-鿿]{4,}')
PATTERN_MIXED = re.compile(r'[一-鿿゠-ヿー]{4,}')

# Java standard class names the question-side extractor (bench/term_extract.py)
# uses to drop ASCII identifiers. Kept here so the list lives with the rest of
# the identifier extraction knowledge; nothing in this module consumes it.
JAVA_STOPLIST = {
    "ArrayList", "HashMap", "HashSet", "TreeMap", "TreeSet", "LinkedList",
    "LinkedHashMap", "LinkedHashSet", "ConcurrentHashMap",
    "IOException", "RuntimeException", "NullPointerException",
    "IllegalArgumentException", "IllegalStateException",
    "UnsupportedOperationException",
    "FunctionalInterface", "SafeVarargs",
    "InputStream", "OutputStream", "BufferedReader", "BufferedWriter",
    "FileReader", "FileWriter", "PrintWriter",
    "LocalDate", "LocalTime", "LocalDateTime", "OffsetDateTime",
    "ZonedDateTime", "DateTimeFormatter",
    "StringBuilder", "StringBuffer",
}

# Frozen defaults — see .work/00307/index-params-decision.md.
DEFAULT_TF_THRESHOLD = 2
DEFAULT_TOP_N = 5
DEFAULT_FALLBACK_TF = 1
DEFAULT_FALLBACK_DF_MAX = 20
DEFAULT_FALLBACK_TOP_N = 3


def tokenize_ja_deduped(text: str) -> list[str]:
    """Tokenize Japanese 4+ char terms without double-counting a span.

    A pure-katakana or pure-kanji run is matched by both its specific pattern
    and the MIXED pattern. For TF computation we want a single occurrence per
    span, so we collect all matches with their spans and drop any whose span
    is already covered by a different-term match at the same start position.

    True compounds like `トランザクション管理` still emit both the atomic
    `トランザクション` (offset 0, len 8) and the compound
    `トランザクション管理` (offset 0, len 10) — different lengths, both kept.
    A pure katakana `トランザクション` run emits (KATAKANA, offset 0, len 8)
    and (MIXED, offset 0, len 8) with the same (offset, length, term): second
    one is dropped.
    """
    if not text:
        return []
    seen_spans: set[tuple[int, int, str]] = set()
    matches: list[tuple[int, int, str]] = []
    for pat in (PATTERN_KATAKANA, PATTERN_KANJI, PATTERN_MIXED):
        for m in pat.finditer(text):
            key = (m.start(), m.end(), m.group(0))
            if key in seen_spans:
                continue
            seen_spans.add(key)
            matches.append(key)
    # Sort by start position (preserve document order) for deterministic output.
    matches.sort(key=lambda x: (x[0], x[1]))
    return [t for _, _, t in matches]


def iter_sections(knowledge_dir: str) -> Iterator[dict]:
    """Yield section records with everything needed for filtering and ranking.

    Each record is:
        {"page_id", "page_title", "section_id", "section_title", "body"}
    Pages with `no_knowledge_content: true` and files missing id/title are
    skipped. Section titles come from the `index` array when available; if a
    section is missing from `index`, we fall back to a dict-stored title.
    """
    for fp in sorted(glob.glob(f"{knowledge_dir}/**/*.json", recursive=True)):
        try:
            with open(fp, encoding="utf-8") as fh:
                d = json.load(fh)
        except (json.JSONDecodeError, OSError) as e:
            print(f"WARN: skip {fp}: {e}", file=sys.stderr)
            continue
        if not isinstance(d, dict) or "id" not in d or "title" not in d:
            continue
        if d.get("no_knowledge_content") is True:
            continue
        page_id = d["id"]
        page_title = d["title"]
        index_titles: dict[str, str] = {}
        for entry in d.get("index") or []:
            if isinstance(entry, dict) and entry.get("id"):
                index_titles[entry["id"]] = entry.get("title") or ""
        secs = d.get("sections") or {}
        if not isinstance(secs, dict):
            continue
        for sid, s in sorted(secs.items()):
            if isinstance(s, str):
                body = s
                stitle = index_titles.get(sid, "")
            elif isinstance(s, dict):
                raw_body = s.get("body")
                body = raw_body if isinstance(raw_body, str) else ""
                stitle = index_titles.get(sid) or s.get("title") or ""
            else:
                body = ""
                stitle = index_titles.get(sid, "")
            yield {
                "page_id": page_id,
                "page_title": page_title,
                "section_id": sid,
                "section_title": stitle,
                "body": body,
            }


def _passes_filters(term: str, page_title: str, section_title: str,
                    stoplist: set[str]) -> bool:
    if term in stoplist:
        return False
    if term in page_title:
        return False
    if term in section_title:
        return False
    return True


def compute_candidates(
    sections: list[dict],
    stoplist: set[str],
) -> tuple[dict[str, Counter], Counter]:
    """Build per-section TF counters and a global df counter over
    post-filter candidate terms.

    df counts distinct sections in which the term survived the filters. A
    term filtered out of a given section (stoplist / title overlap) does not
    contribute to df for that section.
    """
    per_sec: dict[str, Counter] = {}
    df: Counter = Counter()
    for rec in sections:
        key = f"{rec['page_id']}|{rec['section_id']}"
        tokens = tokenize_ja_deduped(rec["body"])
        kept = [
            t for t in tokens
            if _passes_filters(t, rec["page_title"], rec["section_title"],
                                stoplist)
        ]
        tf = Counter(kept)
        per_sec[key] = tf
        for term in tf.keys():
            df[term] += 1
    return per_sec, df


def select_keywords(
    tf: Counter,
    df: Counter,
    *,
    tf_threshold: int = DEFAULT_TF_THRESHOLD,
    top_n: int = DEFAULT_TOP_N,
    fallback_tf: int = DEFAULT_FALLBACK_TF,
    fallback_df_max: int = DEFAULT_FALLBACK_DF_MAX,
    fallback_top_n: int = DEFAULT_FALLBACK_TOP_N,
) -> list[str]:
    """Primary path: tf >= tf_threshold, top `top_n` by (tf desc, term asc).

    Fallback (only when primary yields zero): tf >= fallback_tf
    AND df <= fallback_df_max, top `fallback_top_n`.
    """
    primary = [(t, c) for t, c in tf.items() if c >= tf_threshold]
    primary.sort(key=lambda x: (-x[1], x[0]))
    if primary:
        return [t for t, _ in primary[:top_n]]

    fallback = [
        (t, c) for t, c in tf.items()
        if c >= fallback_tf and df.get(t, 0) <= fallback_df_max
    ]
    fallback.sort(key=lambda x: (-x[1], x[0]))
    return [t for t, _ in fallback[:fallback_top_n]]


def build_keyword_map(
    sections: list[dict],
    stoplist: set[str],
    *,
    tf_threshold: int = DEFAULT_TF_THRESHOLD,
    top_n: int = DEFAULT_TOP_N,
    fallback_tf: int = DEFAULT_FALLBACK_TF,
    fallback_df_max: int = DEFAULT_FALLBACK_DF_MAX,
    fallback_top_n: int = DEFAULT_FALLBACK_TOP_N,
) -> dict[str, list[str]]:
    per_sec, df = compute_candidates(sections, stoplist)
    return {
        key: select_keywords(
            tf, df,
            tf_threshold=tf_threshold, top_n=top_n,
            fallback_tf=fallback_tf, fallback_df_max=fallback_df_max,
            fallback_top_n=fallback_top_n,
        )
        for key, tf in per_sec.items()
    }


def load_stoplist(path: str) -> set[str]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"stoplist must be a JSON array: {path}")
    return {str(t) for t in data}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", required=True)
    ap.add_argument("--stoplist", required=True,
                    help="Path to JSON array of Japanese stoplist terms")
    ap.add_argument("--out", required=True,
                    help="Output path for index-keywords-ja JSON")
    ap.add_argument("--tf-threshold", type=int, default=DEFAULT_TF_THRESHOLD)
    ap.add_argument("--top-n", type=int, default=DEFAULT_TOP_N)
    ap.add_argument("--fallback-tf", type=int, default=DEFAULT_FALLBACK_TF)
    ap.add_argument("--fallback-df-max", type=int, default=DEFAULT_FALLBACK_DF_MAX)
    ap.add_argument("--fallback-top-n", type=int, default=DEFAULT_FALLBACK_TOP_N)
    args = ap.parse_args()

    knowledge_dir = f"{REPO}/.claude/skills/nabledge-{args.version}/knowledge"
    if not os.path.isdir(knowledge_dir):
        print(f"ERROR: knowledge dir not found: {knowledge_dir}", file=sys.stderr)
        return 1
    stoplist = load_stoplist(args.stoplist)
    sections = list(iter_sections(knowledge_dir))
    keyword_map = build_keyword_map(
        sections, stoplist,
        tf_threshold=args.tf_threshold, top_n=args.top_n,
        fallback_tf=args.fallback_tf, fallback_df_max=args.fallback_df_max,
        fallback_top_n=args.fallback_top_n,
    )

    payload = {
        "meta": {
            "version": args.version,
            "sections": len(keyword_map),
            "stoplist_size": len(stoplist),
            "params": {
                "tf_threshold": args.tf_threshold,
                "top_n": args.top_n,
                "fallback_tf": args.fallback_tf,
                "fallback_df_max": args.fallback_df_max,
                "fallback_top_n": args.fallback_top_n,
            },
        },
        "keywords": keyword_map,
    }
    out_dir = os.path.dirname(args.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")

    n_primary = sum(1 for v in keyword_map.values() if v)
    n_empty = sum(1 for v in keyword_map.values() if not v)
    total_placements = sum(len(v) for v in keyword_map.values())
    print(
        f"Wrote {args.out} — {len(keyword_map)} sections "
        f"({n_primary} with keywords, {n_empty} empty, "
        f"{total_placements} total placements)",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Compute Japanese term section_df for stoplist judgment (#307).

Walks all knowledge sections, tokenizes bodies with the Japanese-only
patterns (katakana/kanji/mixed, 4+ chars), and emits a ranking JSON used as
input for 3-agent parallel human judgment that produces the final
`data/index-stoplist-ja-v6.json`.

Output shape (sorted by section_df desc):

  {
    "version": "6",
    "total_sections": 4821,
    "terms": [
      {"term": "バージョンアップ", "pattern": "katakana",
       "section_df": 312, "df_ratio": 0.0647,
       "sample_section_ids": ["a|s1", ...]  # up to 5, deterministic}
    ]
  }

Snippets are not embedded — judges can grep the knowledge dir directly.
Embedding snippets triples the file size for marginal judgment gain.

TODO: unify the tokenizer patterns with classify_terms.py / term_extract.py
when Step 2 rewrites classify_terms.py for section-level TF.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from collections import defaultdict
from typing import Iterator

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Japanese-only patterns, 4+ chars. ASCII identifiers are handled by the
# term_queries path, not this module.
PATTERN_KATAKANA = re.compile(r'[゠-ヿー]{4,}')
PATTERN_KANJI = re.compile(r'[一-鿿]{4,}')
PATTERN_MIXED = re.compile(r'[一-鿿゠-ヿー]{4,}')

SAMPLE_CAP = 5


def tokenize_ja(text: str) -> list[str]:
    """Extract Japanese terms (katakana / kanji / mixed, 4+ chars).

    The three patterns are applied in sequence, so a pure-katakana or pure-kanji
    term is emitted twice (once by its specific pattern, once by MIXED). This is
    intentional: MIXED greedily captures compounds like "トランザクション管理"
    that atomic patterns miss. `compute_section_df` dedups per section so
    section_df is unaffected; other callers consuming raw tf must dedup.
    """
    if not text:
        return []
    tokens: list[str] = []
    for pat in (PATTERN_KATAKANA, PATTERN_KANJI, PATTERN_MIXED):
        for m in pat.finditer(text):
            tokens.append(m.group(0))
    return tokens


def classify_pattern(term: str) -> str:
    """Label the term's dominant script. Mixed is checked last."""
    if PATTERN_KATAKANA.fullmatch(term):
        return "katakana"
    if PATTERN_KANJI.fullmatch(term):
        return "kanji"
    return "mixed"


def iter_sections(knowledge_dir: str) -> Iterator[tuple[str, str, str]]:
    """Yield (page_id, section_id, body) for every section in the corpus.

    - Skips pages with no_knowledge_content=True
    - Skips sections whose body is not a string (missing/null body → "")
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
        secs = d.get("sections") or {}
        if not isinstance(secs, dict):
            continue
        page_id = d["id"]
        for sid, s in sorted(secs.items()):
            if isinstance(s, str):
                body = s
            elif isinstance(s, dict):
                body = s.get("body") or ""
            else:
                body = ""
            yield page_id, sid, body


def compute_section_df(
    sections: list[tuple[str, str, str]],
) -> dict[str, dict]:
    """Compute section_df per Japanese term.

    Returns a dict mapping term → {section_df, df_ratio, sample_section_ids, pattern}.

    A term counts once per section even if it appears multiple times.
    sample_section_ids are the first SAMPLE_CAP section keys ("page|sid")
    sorted alphabetically — deterministic and stable across runs.
    """
    total = max(len(sections), 1)
    term_sections: dict[str, set[str]] = defaultdict(set)
    for page_id, sid, body in sections:
        key = f"{page_id}|{sid}"
        seen: set[str] = set()
        for tok in tokenize_ja(body):
            if tok in seen:
                continue
            seen.add(tok)
            term_sections[tok].add(key)

    result: dict[str, dict] = {}
    for term, keys in term_sections.items():
        sorted_keys = sorted(keys)
        result[term] = {
            "section_df": len(keys),
            "df_ratio": round(len(keys) / total, 4),
            "sample_section_ids": sorted_keys[:SAMPLE_CAP],
            "pattern": classify_pattern(term),
        }
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", required=True)
    ap.add_argument("--out", default=None,
                    help="Output path (default: /tmp/section-df-ja-v{version}.json)")
    args = ap.parse_args()

    knowledge_dir = f"{REPO}/.claude/skills/nabledge-{args.version}/knowledge"
    sections = list(iter_sections(knowledge_dir))
    df = compute_section_df(sections)

    sorted_terms = sorted(df.items(), key=lambda x: (-x[1]["section_df"], x[0]))
    payload = {
        "version": args.version,
        "total_sections": len(sections),
        "terms": [
            {"term": t, **info} for t, info in sorted_terms
        ],
    }

    out = args.out or f"/tmp/section-df-ja-v{args.version}.json"
    out_dir = os.path.dirname(out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(
        f"Wrote {out} — {len(df)} terms across {len(sections)} sections",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

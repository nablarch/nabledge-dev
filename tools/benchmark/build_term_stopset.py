#!/usr/bin/env python3
"""Compute the df_pct stopset for term_extract.

A term is added to the stopset when it appears in more than
THRESHOLD fraction of pages. Such terms are too broad to grep —
including them explodes the candidate count without improving recall.

Output:
  tools/benchmark/data/term_stopset-v{version}.json  (sorted JSON array)
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)

from tools.benchmark.bench.term_extract import PATTERNS  # noqa: E402


def page_bodies(knowledge_dir: str) -> list[str]:
    bodies: list[str] = []
    for fp in sorted(glob.glob(f"{knowledge_dir}/**/*.json", recursive=True)):
        try:
            d = json.load(open(fp))
        except Exception:
            continue
        if not isinstance(d, dict) or "id" not in d or "title" not in d:
            continue
        if d.get("no_knowledge_content") is True:
            continue
        parts = []
        secs = d.get("sections") or {}
        if isinstance(secs, dict):
            for _sid, s in secs.items():
                if isinstance(s, str):
                    parts.append(s)
                elif isinstance(s, dict):
                    parts.append(s.get("title") or "")
                    parts.append(s.get("body") or "")
        bodies.append("\n".join(parts))
    return bodies


def compute_stopset(bodies: list[str], threshold: float) -> list[str]:
    df: Counter[str] = Counter()
    for body in bodies:
        seen: set[str] = set()
        for name, pat in PATTERNS:
            for m in pat.finditer(body):
                term = "@" + m.group(1) if name == "annotation" else m.group(0)
                seen.add(term)
        for t in seen:
            df[t] += 1
    n = max(len(bodies), 1)
    return sorted(t for t, c in df.items() if (c / n) > threshold)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", required=True)
    ap.add_argument("--threshold", type=float, default=0.20,
                    help="df ratio above which a term is considered too broad")
    ap.add_argument("--out", default=None,
                    help="Output path (default: tools/benchmark/data/term_stopset-v{version}.json)")
    args = ap.parse_args()

    knowledge_dir = f"{REPO}/.claude/skills/nabledge-{args.version}/knowledge"
    bodies = page_bodies(knowledge_dir)
    stopset = compute_stopset(bodies, args.threshold)

    out = args.out or f"{REPO}/tools/benchmark/data/term_stopset-v{args.version}.json"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(stopset, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"Wrote {out} — {len(stopset)} terms (pages={len(bodies)}, threshold={args.threshold})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

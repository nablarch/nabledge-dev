#!/usr/bin/env python3
"""Score existing Stage 2/3 results with reference-answer-based grading.

Reuses `ai1_result.json` from an existing results directory to rebuild
the filter candidates deterministically (via facet_filter), then scores
each scenario against its reference answer citations.

Usage:
  python3 score_stage2.py --results .results/20260422-143411-stage3-sonnet
  python3 score_stage2.py --results .results/... --scenario review-01
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.benchmark.filter.facet_filter import (  # noqa: E402
    filter_with_fallback,
    load_index,
)
from tools.benchmark.grading.reference_answer import (  # noqa: E402
    extract_citations,
    score_stage2,
)

BENCH_DIR = Path(__file__).resolve().parent
INDEX_TOON_PATH = (
    REPO_ROOT / ".claude" / "skills" / "nabledge-6" / "knowledge" / "index.toon"
)
ANSWERS_DIR = BENCH_DIR / "scenarios" / "qa-v6-answers"


def rebuild_candidates(facets: dict, index_rows: list) -> tuple[list[str], str]:
    """Return (candidate_paths, fallback_used) mirroring run.py Stage 2 logic."""
    want_type = facets.get("type") or []
    want_cat = facets.get("category") or []
    coverage = facets.get("coverage")
    if coverage == "out_of_scope" and not want_type and not want_cat:
        return [], "out_of_scope-shortcircuit"
    outcome = filter_with_fallback(index_rows, want_type, want_cat)
    return [r.path for r in outcome.rows], outcome.fallback_used


def score_one(scen_dir: Path, index_rows: list) -> dict:
    scenario_id = scen_dir.name
    ai1 = json.loads((scen_dir / "ai1_result.json").read_text(encoding="utf-8"))
    facets = ai1.get("extracted_facets") or {}
    candidate_paths, fallback = rebuild_candidates(facets, index_rows)

    answer_path = ANSWERS_DIR / f"{scenario_id}.md"
    if not answer_path.exists():
        return {
            "id": scenario_id,
            "error": f"reference answer missing: {answer_path.name}",
        }
    citations = extract_citations(answer_path.read_text(encoding="utf-8"))
    result = score_stage2(citations, set(candidate_paths))
    return {
        "id": scenario_id,
        "facets": facets,
        "fallback": fallback,
        "candidate_count": len(candidate_paths),
        **result,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True,
                    help="results directory (e.g. .results/...-stage3-sonnet)")
    ap.add_argument("--scenario", help="single scenario id")
    ap.add_argument("--out", help="output JSON (default: <results>/stage2_script.json)")
    args = ap.parse_args()

    results_dir = Path(args.results)
    if not results_dir.exists():
        print(f"results dir not found: {results_dir}", file=sys.stderr)
        return 2

    index_rows = load_index(INDEX_TOON_PATH)

    scen_dirs = sorted(d for d in results_dir.iterdir() if d.is_dir())
    if args.scenario:
        scen_dirs = [d for d in scen_dirs if d.name == args.scenario]
        if not scen_dirs:
            print(f"scenario not found: {args.scenario}", file=sys.stderr)
            return 2

    rows: list[dict] = []
    for scen_dir in scen_dirs:
        row = score_one(scen_dir, index_rows)
        rows.append(row)
        if "error" in row:
            print(f"{row['id']:<12} ERROR: {row['error']}", file=sys.stderr)
            continue
        print(
            f"{row['id']:<12} level={row['level']} "
            f"ratio={row['ratio']:.2f} ({row['covered']}/{row['total']}) "
            f"candidates={row['candidate_count']} fallback={row['fallback']} "
            f"missing={row['missing_paths'] or '—'}"
        )

    ok = [r for r in rows if "error" not in r]
    dist = {str(lv): sum(1 for r in ok if r["level"] == lv) for lv in [0, 1, 2, 3]}
    summary = {
        "total": len(rows),
        "errors": len(rows) - len(ok),
        "level_distribution": dist,
        "pass_rate_level_3": (
            sum(1 for r in ok if r["level"] == 3) / len(ok) if ok else 0
        ),
        "pass_rate_level_ge_2": (
            sum(1 for r in ok if r["level"] >= 2) / len(ok) if ok else 0
        ),
        "rows": rows,
    }
    out_path = Path(args.out) if args.out else results_dir / "stage2_script.json"
    out_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        f"\nsummary: {dist} | level=3: {summary['pass_rate_level_3']:.0%} "
        f"| level≥2: {summary['pass_rate_level_ge_2']:.0%}",
        file=sys.stderr,
    )
    print(f"wrote: {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

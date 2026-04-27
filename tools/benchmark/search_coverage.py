#!/usr/bin/env python3
"""Phase 1 coverage report: did search retrieve the sections the model answer cites?

Reads a search-only results dir and compares each scenario's merged_selections
against two targets:

1. expected_sections declared in qa-v6.json (file-level expected retrieval)
2. citations in the reference model answer qa-v6-answers/{id}.md (actual
   section-level ground truth the answer depends on)

Outputs coverage.json and a terminal summary.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


CITATION_RE = re.compile(r"([a-zA-Z0-9_\-./]+\.json)[:#]([a-zA-Z0-9_\-]+)")


def _norm_expected(expected: list[str], path_to_id: dict[str, str]) -> set[tuple[str, str]]:
    """expected_sections values look like `<path>|sid` or `<file_id>|sid`.
    Normalize to (file_id, sid) pairs so they can be compared with selections.
    """
    out: set[tuple[str, str]] = set()
    for s in expected or []:
        if "|" not in s:
            continue
        left, sid = s.split("|", 1)
        if left.endswith(".json"):
            fid = path_to_id.get(left)
            if not fid:
                continue
        else:
            fid = left
        out.add((fid, sid))
    return out


def _norm_ref_citations(md: str, path_to_id: dict[str, str]) -> set[tuple[str, str]]:
    out: set[tuple[str, str]] = set()
    for m in CITATION_RE.finditer(md):
        path, sid = m.group(1), m.group(2)
        fid = path_to_id.get(path)
        if fid:
            out.add((fid, sid))
    return out


def _norm_merged(selectors: list[str]) -> set[tuple[str, str]]:
    out: set[tuple[str, str]] = set()
    for s in selectors or []:
        if "|" in s:
            fid, sid = s.split("|", 1)
            out.add((fid, sid))
    return out


def load_path_to_id(index_script_path: Path) -> dict[str, str]:
    data = json.loads(index_script_path.read_text(encoding="utf-8"))
    return {v["path"]: fid for fid, v in data.items() if "path" in v}


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    bench_dir = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser()
    ap.add_argument("results_dir", type=Path)
    ap.add_argument("--version", default="6",
                    help="nabledge skill version (6, 5, 1.4, 1.3, 1.2)")
    ap.add_argument("--scenarios", type=Path, default=None,
                    help="scenarios JSON (default: scenarios/qa-v{version}.json)")
    ap.add_argument("--answers", type=Path, default=None,
                    help="answers dir (default: scenarios/qa-v{version}-answers)")
    ap.add_argument("--index", type=Path, default=None,
                    help="index-script.json path (default: skills/nabledge-{version}/knowledge/)")
    args = ap.parse_args()

    if args.scenarios is None:
        args.scenarios = bench_dir / "scenarios" / f"qa-v{args.version}.json"
    if args.answers is None:
        args.answers = bench_dir / "scenarios" / f"qa-v{args.version}-answers"
    if args.index is None:
        args.index = repo_root / ".claude" / "skills" / f"nabledge-{args.version}" / "knowledge" / "index-script.json"

    path_to_id = load_path_to_id(args.index)
    scenarios = json.loads(args.scenarios.read_text(encoding="utf-8"))

    rows: list[dict] = []
    for sc in scenarios:
        sid = sc["id"]
        scen_dir = args.results_dir / sid
        search_path = scen_dir / "search.json"
        if not search_path.exists():
            continue
        search = json.loads(search_path.read_text(encoding="utf-8"))
        merged_selectors = set(search.get("steps", {}).get("merged_selections")
                               or search.get("steps", {}).get("raw_selections") or [])
        merged = _norm_merged(list(merged_selectors))

        expected = _norm_expected(sc.get("expected_sections") or [], path_to_id)
        ref_md = (args.answers / f"{sid}.md").read_text(encoding="utf-8")
        ref_cites = _norm_ref_citations(ref_md, path_to_id)

        expected_hit = expected & merged
        expected_miss = expected - merged
        ref_hit = ref_cites & merged
        ref_miss = ref_cites - merged

        row = {
            "id": sid,
            "merged_count": len(merged),
            "expected_total": len(expected),
            "expected_hit": len(expected_hit),
            "expected_coverage": round(len(expected_hit) / len(expected), 2) if expected else None,
            "expected_missing": sorted(f"{f}|{s}" for f, s in expected_miss),
            "ref_total": len(ref_cites),
            "ref_hit": len(ref_hit),
            "ref_coverage": round(len(ref_hit) / len(ref_cites), 2) if ref_cites else None,
            "ref_missing": sorted(f"{f}|{s}" for f, s in ref_miss),
            "term_queries": search.get("steps", {}).get("term_queries") or [],
            "term_hit_count": len(search.get("steps", {}).get("term_hits") or []),
        }
        rows.append(row)

    # Summary
    n = len(rows)
    exp_full = sum(1 for r in rows if r["expected_total"] and r["expected_hit"] == r["expected_total"])
    ref_full = sum(1 for r in rows if r["ref_total"] and r["ref_hit"] == r["ref_total"])

    summary = {
        "total": n,
        "expected_full_coverage_count": exp_full,
        "expected_full_coverage_pct": round(exp_full / n, 2) if n else 0,
        "ref_full_coverage_count": ref_full,
        "ref_full_coverage_pct": round(ref_full / n, 2) if n else 0,
    }

    out = args.results_dir / "coverage.json"
    out.write_text(json.dumps({"summary": summary, "rows": rows}, ensure_ascii=False, indent=2),
                   encoding="utf-8")

    # Print terminal summary
    print(f"\n=== coverage ({n} scenarios) ===", file=sys.stderr)
    print(f"expected_sections 完全 hit: {exp_full}/{n} ({summary['expected_full_coverage_pct']*100:.0f}%)",
          file=sys.stderr)
    print(f"ref citations 完全 hit:    {ref_full}/{n} ({summary['ref_full_coverage_pct']*100:.0f}%)",
          file=sys.stderr)
    print(f"\nper-scenario (id | merged | exp_cov | ref_cov | ref_miss):", file=sys.stderr)
    for r in rows:
        exc = f"{r['expected_hit']}/{r['expected_total']}" if r["expected_total"] else "-"
        rec = f"{r['ref_hit']}/{r['ref_total']}" if r["ref_total"] else "-"
        miss = ",".join(r["ref_missing"][:3]) + ("..." if len(r["ref_missing"]) > 3 else "")
        print(f"  {r['id']:<12} {r['merged_count']:>2}  exp={exc}  ref={rec}  miss: {miss}",
              file=sys.stderr)
    print(f"\nwrote: {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

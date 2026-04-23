#!/usr/bin/env python3
"""Benchmark runner for the nabledge-6 search flows.

Commands:
  python3 run.py --variant {ids|current} [--scenario X] [--limit N] [--model sonnet]
      Run the full scenario set (or a subset) through one flow. Writes per-scenario
      artifacts under .results/{ts}-{variant}-{model}/.
  python3 run.py --rejudge --results-dir .results/...
      Re-score an existing run using the current judge prompt.

Parallel runs are not supported — see .claude/rules/benchmark.md.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Callable

# Allow running as a script: `python3 tools/benchmark/run.py`.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tools.benchmark.bench import io, judge, search_current, search_ids
from tools.benchmark.bench.types import JudgeResult, Scenario, SearchResult, Variant


def run_variant(
    *, variant: Variant, scenarios: list[Scenario], model: str, out_dir: Path
) -> None:
    search_fn = _dispatch(variant)
    ids_map = search_ids.load_id_to_path() if variant == "ids" else {}
    print(f"variant={variant} model={model} scenarios={len(scenarios)} out={out_dir}",
          file=sys.stderr)
    summary_rows: list[dict] = []
    for i, sc in enumerate(scenarios, 1):
        scen = io.scen_dir(out_dir, sc.id)
        print(f"[{i}/{len(scenarios)}] {sc.id} ...", file=sys.stderr, flush=True)
        search: SearchResult = search_fn(
            question=sc.question, model=model, scen_dir=scen, **({"id_to_path": ids_map} if variant == "ids" else {}),
        )
        io.write_search(scen, search)
        jr = judge.run(scenario=sc, search=search, model=model, scen_dir=scen)
        io.write_judge(scen, jr)
        _print_row(sc.id, search, jr)
        summary_rows.append(_summary_row(sc.id, search, jr))
    _write_run_meta(out_dir, variant=variant, model=model, scenarios=[s.id for s in scenarios])
    _write_summary(out_dir, summary_rows)


def rejudge(*, results_dir: Path, model: str, scenarios: list[Scenario]) -> None:
    print(f"rejudge model={model} results_dir={results_dir}", file=sys.stderr)
    summary_rows: list[dict] = []
    for i, sc in enumerate(scenarios, 1):
        scen = results_dir / sc.id
        if not scen.is_dir():
            print(f"[{i}/{len(scenarios)}] {sc.id} — SKIP (no dir)", file=sys.stderr)
            continue
        try:
            search = io.read_search(scen)
        except FileNotFoundError:
            print(f"[{i}/{len(scenarios)}] {sc.id} — SKIP (no search.json)", file=sys.stderr)
            continue
        print(f"[{i}/{len(scenarios)}] {sc.id} ...", file=sys.stderr, flush=True)
        # Keep stream/ subdir isolated per rejudge call.
        (scen / "stream").mkdir(exist_ok=True)
        jr = judge.run(scenario=sc, search=search, model=model, scen_dir=scen)
        io.write_judge(scen, jr)
        _print_row(sc.id, search, jr)
        summary_rows.append(_summary_row(sc.id, search, jr))
    _write_summary(results_dir, summary_rows)


# --- internals ----------------------------------------------------------------


def _dispatch(variant: Variant) -> Callable[..., SearchResult]:
    if variant == "ids":
        return search_ids.run
    if variant == "current":
        return search_current.run
    raise ValueError(f"unknown variant: {variant}")


def _print_row(sid: str, search: SearchResult, jr: JudgeResult) -> None:
    level = jr.verdict.level if jr.verdict else None
    total_cost = search.cost_usd + jr.cost_usd
    total_wall = search.duration_s + jr.duration_s
    print(
        f"  -> level={level} cited={len(search.cited)} "
        f"cost=${total_cost:.4f} wall={total_wall:.1f}s",
        file=sys.stderr,
    )


def _summary_row(sid: str, search: SearchResult, jr: JudgeResult) -> dict:
    return {
        "id": sid,
        "level": jr.verdict.level if jr.verdict else None,
        "cited_count": len(search.cited),
        "search_cost_usd": round(search.cost_usd, 6),
        "judge_cost_usd": round(jr.cost_usd, 6),
        "search_s": round(search.duration_s, 2),
        "judge_s": round(jr.duration_s, 2),
        "error": search.error or jr.error or "",
    }


def _write_run_meta(out_dir: Path, *, variant: str, model: str, scenarios: list[str]) -> None:
    (out_dir / "run.json").write_text(
        json.dumps({
            "variant": variant,
            "model": model,
            "started_at": datetime.now().isoformat(timespec="seconds"),
            "scenarios": scenarios,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _write_summary(out_dir: Path, rows: list[dict]) -> None:
    csv_path = out_dir / "summary.csv"
    fields = ["id", "level", "cited_count",
              "search_cost_usd", "judge_cost_usd", "search_s", "judge_s", "error"]
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})

    levels = [r["level"] for r in rows if r.get("level") is not None]
    summary = {
        "total": len(rows),
        "scored": len(levels),
        "errors": sum(1 for r in rows if r.get("error")),
        "mean_level": sum(levels) / len(levels) if levels else None,
        "level_distribution": {str(lv): levels.count(lv) for lv in [0, 1, 2, 3]},
        "total_cost_usd": round(sum(
            (r.get("search_cost_usd") or 0) + (r.get("judge_cost_usd") or 0)
            for r in rows
        ), 4),
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"summary: mean_level={summary['mean_level']} "
          f"dist={summary['level_distribution']} cost=${summary['total_cost_usd']}",
          file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", choices=["ids", "current"],
                    help="search flow variant (required unless --rejudge)")
    ap.add_argument("--rejudge", action="store_true",
                    help="re-score an existing results dir using the current judge prompt")
    ap.add_argument("--results-dir",
                    help="(rejudge) path to .results/{ts}-... to re-score")
    ap.add_argument("--scenario", help="run only this scenario id")
    ap.add_argument("--limit", type=int, help="run only the first N scenarios")
    ap.add_argument("--scenarios-file", default=str(io.SCENARIOS_PATH),
                    help=f"scenarios JSON path (default: {io.SCENARIOS_PATH})")
    ap.add_argument("--model", default="sonnet",
                    help="claude model id or alias (sonnet, haiku, opus, or exact id)")
    ap.add_argument("--out", help="output directory (default: .results/{ts}-{variant}-{model})")
    args = ap.parse_args()

    scenarios = io.load_scenarios(Path(args.scenarios_file))
    if args.scenario:
        scenarios = [s for s in scenarios if s.id == args.scenario]
        if not scenarios:
            print(f"scenario not found: {args.scenario}", file=sys.stderr)
            return 2
    if args.limit:
        scenarios = scenarios[: args.limit]

    if args.rejudge:
        if not args.results_dir:
            print("--results-dir is required with --rejudge", file=sys.stderr)
            return 2
        rd = Path(args.results_dir)
        if not rd.is_dir():
            print(f"results dir not found: {rd}", file=sys.stderr)
            return 2
        rejudge(results_dir=rd, model=args.model, scenarios=scenarios)
        return 0

    if not args.variant:
        print("--variant is required (ids|current) unless --rejudge", file=sys.stderr)
        return 2

    out_dir = Path(args.out) if args.out else io.new_results_dir(args.variant, args.model)
    run_variant(variant=args.variant, scenarios=scenarios, model=args.model, out_dir=out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())

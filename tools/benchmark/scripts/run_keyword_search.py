"""Keyword-search benchmark runner: executes keyword-search.sh for each scenario.

Runs keyword-search.sh directly and evaluates recall against scenario expectations.

Output per scenario:
  {output-dir}/{scenario-id}/search.json     — keyword-search.sh raw output
  {output-dir}/{scenario-id}/evaluation.json — recall evaluation (must/acceptable found status)
  {output-dir}/{scenario-id}/metrics.json    — performance metrics (duration)
  {output-dir}/summary.json                  — run summary with context
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

_RESULTS_BASE = Path(__file__).parent.parent / "results"


def default_output_dir() -> Path:
    """Return a timestamped output directory under tools/benchmark/results/."""
    return _RESULTS_BASE / datetime.now().strftime("%Y%m%d-%H%M%S")


def _extract_section_ids(search_result: list) -> set[str]:
    """Extract flat set of section_id strings from keyword-search.sh JSON output."""
    ids = set()
    for cat in search_result:
        for page in cat.get("pages", []):
            for sec in page.get("sections", []):
                ids.add(sec["section_id"])
    return ids


def evaluate_keyword_search(scenario: dict, returned_section_ids: set[str]) -> dict:
    """Evaluate keyword-search results against scenario expectations.

    Returns dict with must/acceptable found status and recall score.
    Recall = found must sections / total must sections (1.0 when no must sections).
    """
    must_facts = scenario["then"].get("must", [])
    acceptable = scenario["then"].get("acceptable", [])

    must_results = [
        {"section": mf["section"], "fact": mf.get("fact", ""), "found": mf["section"] in returned_section_ids}
        for mf in must_facts
    ]
    acceptable_results = [
        {"section": a["section"], "found": a["section"] in returned_section_ids}
        for a in acceptable
    ]

    if must_facts:
        recall = sum(1 for m in must_results if m["found"]) / len(must_facts)
    else:
        recall = 1.0

    return {
        "scenario_id": scenario["id"],
        "must": must_results,
        "acceptable": acceptable_results,
        "scores": {"recall": recall},
    }


def run_keyword_search_scenario(scenario: dict, skill_dir: str | Path) -> dict:
    """Run a single keyword-search scenario.

    Calls keyword-search.sh with the keywords from scenario["when"]["input"]
    and evaluates the results against scenario["then"].

    Returns:
        Dict with scenario_id, search, evaluation, metrics.

    Raises:
        RuntimeError: If keyword-search.sh exits with non-zero return code.
    """
    skill_dir = Path(skill_dir)
    keywords_input = scenario["when"]["input"]
    keywords = keywords_input if isinstance(keywords_input, list) else [keywords_input]

    t0 = time.monotonic()
    proc = subprocess.run(
        ["bash", "scripts/keyword-search.sh", *keywords],
        capture_output=True,
        text=True,
        cwd=str(skill_dir),
    )
    duration_ms = int((time.monotonic() - t0) * 1000)

    if proc.returncode != 0:
        raise RuntimeError(
            f"keyword-search.sh exited with code {proc.returncode}: {proc.stderr[:500]}"
        )

    search_result = json.loads(proc.stdout)
    returned_ids = _extract_section_ids(search_result)
    evaluation = evaluate_keyword_search(scenario, returned_ids)

    return {
        "scenario_id": scenario["id"],
        "search": search_result,
        "evaluation": evaluation,
        "metrics": {"duration_ms": duration_ms},
    }


def save_keyword_search_results(output_dir: str | Path, scenario_id: str, data: dict) -> None:
    """Save keyword-search scenario results."""
    scenario_dir = Path(output_dir) / scenario_id
    scenario_dir.mkdir(parents=True, exist_ok=True)

    (scenario_dir / "search.json").write_text(
        json.dumps(data["search"], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (scenario_dir / "evaluation.json").write_text(
        json.dumps(data["evaluation"], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (scenario_dir / "metrics.json").write_text(
        json.dumps(data["metrics"], ensure_ascii=False, indent=2), encoding="utf-8"
    )


def run_keyword_search_all(
    scenarios_path: str,
    skill_dir: str | Path,
    output_dir: str | Path | None = None,
    scenario_ids: list[str] | None = None,
) -> dict:
    """Run all keyword-search scenarios and save results.

    Args:
        scenarios_path: Path to scenarios JSON file.
        skill_dir: Path to the skill directory.
        output_dir: Directory to save results (default: tools/benchmark/results/YYYYMMDD-HHMMSS/).
        scenario_ids: Optional list of scenario IDs to run (runs all if None).

    Returns:
        Summary dict with total_scenarios, skill_dir, scenarios_file, executed_at, and per-scenario info.
    """
    skill_dir = Path(skill_dir)
    executed_at = datetime.now().isoformat()

    with open(scenarios_path, encoding="utf-8") as f:
        data = json.load(f)

    out = Path(output_dir) if output_dir else default_output_dir()
    out.mkdir(parents=True, exist_ok=True)

    scenario_summaries = []
    for scenario in data["scenarios"]:
        sid = scenario["id"]
        if scenario_ids and sid not in scenario_ids:
            continue

        print(f"Running {sid}...", file=sys.stderr)
        try:
            result = run_keyword_search_scenario(scenario, skill_dir)
            save_keyword_search_results(str(out), sid, result)

            recall = result["evaluation"]["scores"]["recall"]
            scenario_summaries.append({
                "id": sid,
                "sections_returned": len(_extract_section_ids(result["search"])),
                "recall": recall,
            })
        except Exception as exc:
            exc_type = type(exc).__name__
            print(f"  ERROR {sid}: {exc_type}: {exc}", file=sys.stderr)
            error_dir = out / sid
            error_dir.mkdir(parents=True, exist_ok=True)
            (error_dir / "error.json").write_text(
                json.dumps({"error": str(exc), "exception_type": exc_type}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            scenario_summaries.append({"id": sid, "status": "error", "error": str(exc)})

    summary = {
        "total_scenarios": len(scenario_summaries),
        "skill_dir": str(skill_dir),
        "scenarios_file": str(scenarios_path),
        "executed_at": executed_at,
        "scenarios": scenario_summaries,
    }

    (out / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return summary


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Run keyword-search benchmark: direct keyword-search.sh evaluation"
    )
    parser.add_argument("--scenarios", required=True, help="Path to scenarios JSON")
    parser.add_argument("--skill-dir", required=True, help="Path to skill directory")
    parser.add_argument("--scenario-ids", help="Comma-separated scenario IDs to run")
    args = parser.parse_args()

    scenario_ids = args.scenario_ids.split(",") if args.scenario_ids else None
    output_dir = default_output_dir()
    print(f"Output dir: {output_dir}", file=sys.stderr)

    summary = run_keyword_search_all(
        args.scenarios,
        args.skill_dir,
        output_dir=str(output_dir),
        scenario_ids=scenario_ids,
    )

    print(f"\nCompleted: {summary['total_scenarios']} scenarios", file=sys.stderr)
    for s in summary["scenarios"]:
        if s.get("status") == "error":
            print(f"  {s['id']}: ERROR — {s.get('error', '')}", file=sys.stderr)
        else:
            print(f"  {s['id']}: {s['sections_returned']} sections, recall={s['recall']:.2f}", file=sys.stderr)


if __name__ == "__main__":
    main()

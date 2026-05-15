"""Simulate verification for QA scenarios.

Takes existing answers (from answer simulation output) and runs verify.md
to assess verification quality. Measures PASS/FAIL rates and claim
extraction accuracy.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from tools.benchmark.scripts.evaluate import call_llm
from tools.benchmark.scripts.simulate_answer_verify import (
    VERIFY_JSON_SCHEMA,
    build_verify_prompt,
    load_scenario_sections,
    parse_verify_response,
)


def aggregate_metrics(metrics_list: list[dict]) -> dict:
    total_duration = sum(m.get("duration_ms", 0) for m in metrics_list)
    total_cost = sum(m.get("total_cost_usd", 0.0) for m in metrics_list)
    total_in = sum(m.get("usage", {}).get("input_tokens", 0) for m in metrics_list)
    total_out = sum(m.get("usage", {}).get("output_tokens", 0) for m in metrics_list)
    return {
        "duration_ms": total_duration,
        "total_cost_usd": total_cost,
        "total_tokens": total_in + total_out,
        "call_count": len(metrics_list),
    }


def simulate_scenario(
    scenario: dict,
    knowledge_dir: str | Path,
    answer_text: str,
    llm_fn=None,
) -> dict:
    if llm_fn is None:
        def llm_fn(prompt, schema):
            return call_llm(prompt, schema)

    must = scenario["then"].get("must", [])
    acceptable = scenario["then"].get("acceptable", [])

    sections_content, section_refs = load_scenario_sections(knowledge_dir, must, acceptable)

    verify_prompt = build_verify_prompt(answer_text, sections_content)
    verify_response = llm_fn(verify_prompt, VERIFY_JSON_SCHEMA)
    verify_result = parse_verify_response(verify_response["result"])
    verify_metrics = verify_response.get("metrics", {})

    return {
        "scenario_id": scenario["id"],
        "sections_input": section_refs,
        "verify": verify_result,
        "metrics": aggregate_metrics([verify_metrics]),
    }


def simulate_all(
    scenarios_path: str,
    knowledge_dir: str,
    answers_dir: str,
    output_dir: str,
    scenario_ids: list[str] | None = None,
    llm_fn=None,
) -> dict:
    with open(scenarios_path, encoding="utf-8") as f:
        data = json.load(f)

    answers_path = Path(answers_dir)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    results = []
    for scenario in data["scenarios"]:
        sid = scenario["id"]
        if scenario_ids and sid not in scenario_ids:
            continue

        answer_file = answers_path / sid / "answer.md"
        if not answer_file.exists():
            print(f"Skipping {sid}: no answer.md found", file=sys.stderr)
            continue

        answer_text = answer_file.read_text(encoding="utf-8")
        print(f"Simulating {sid}...", file=sys.stderr)

        result = simulate_scenario(scenario, knowledge_dir, answer_text, llm_fn=llm_fn)

        scenario_dir = out_path / sid
        scenario_dir.mkdir(parents=True, exist_ok=True)

        (scenario_dir / "verify.json").write_text(
            json.dumps(result["verify"], ensure_ascii=False, indent=2), encoding="utf-8"
        )
        if result.get("metrics"):
            (scenario_dir / "metrics.json").write_text(
                json.dumps(result["metrics"], ensure_ascii=False, indent=2), encoding="utf-8"
            )
        results.append(result)

    verify_pass = sum(1 for r in results if r["verify"]["result"] == "PASS")
    verify_fail = sum(1 for r in results if r["verify"]["result"] == "FAIL")

    scenarios_with_metrics = [r for r in results if r.get("metrics")]
    if scenarios_with_metrics:
        total_duration = sum(r["metrics"]["duration_ms"] for r in scenarios_with_metrics)
        total_cost = sum(r["metrics"]["total_cost_usd"] for r in scenarios_with_metrics)
        n = len(scenarios_with_metrics)
        agg_metrics = {
            "total_duration_ms": total_duration,
            "total_cost_usd": round(total_cost, 6),
            "avg_duration_ms": round(total_duration / n),
            "avg_cost_usd": round(total_cost / n, 6),
        }
    else:
        agg_metrics = {}

    per_scenario = [
        {
            "id": r["scenario_id"],
            "verify_result": r["verify"]["result"],
            "claims_count": len(r["verify"]["claims"]),
            "issues_count": len(r["verify"]["issues"]),
            "metrics": r.get("metrics", {}),
        }
        for r in results
    ]

    summary = {
        "total_scenarios": len(results),
        "verify_pass": verify_pass,
        "verify_fail": verify_fail,
        "metrics": agg_metrics,
        "per_scenario": per_scenario,
    }

    (out_path / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return summary


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Simulate verification on existing answers"
    )
    parser.add_argument("--scenarios", required=True, help="Path to scenarios JSON")
    parser.add_argument("--knowledge-dir", required=True, help="Path to knowledge directory")
    parser.add_argument("--answers-dir", required=True, help="Path to answers directory (from answer simulation)")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    parser.add_argument("--scenario-ids", help="Comma-separated scenario IDs to run")
    args = parser.parse_args()

    scenario_ids = args.scenario_ids.split(",") if args.scenario_ids else None

    summary = simulate_all(
        args.scenarios,
        args.knowledge_dir,
        args.answers_dir,
        args.output_dir,
        scenario_ids=scenario_ids,
    )

    total = summary["total_scenarios"]
    print(f"\nResults: {summary['verify_pass']}/{total} PASS, {summary['verify_fail']}/{total} FAIL", file=sys.stderr)
    for s in summary["per_scenario"]:
        print(
            f"  {s['id']}: {s['verify_result']} — {s['claims_count']} claims, {s['issues_count']} issues",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()

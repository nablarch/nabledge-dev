"""Page-selection-only benchmark runner for gate-1 experiments.

Runs semantic-search Steps 1–2c only (page candidate selection).
Does NOT execute section reading or answer generation.

Output per scenario per trial:
  {output-dir}/trial-{N}/{scenario-id}/workflow_details.json  — step3.selected_pages
  {output-dir}/trial-{N}/{scenario-id}/metrics.json
  {output-dir}/trial-{N}/{scenario-id}/trace.json
  {output-dir}/summary.json                                   — aggregated results

Usage:
  python3 -m tools.benchmark.scripts.run_page_selection \
    --scenarios tools/benchmark/scenarios/qa.json \
    --skill-dir .tmp/experiment-20 \
    --scenario-ids qa-05 \
    --trials 10
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

_RESULTS_BASE = Path(__file__).parent.parent / "results"
_PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "page-selection-only-prompt.md"
WORKFLOW_FILE = "workflows/semantic-search.md"
TIMEOUT = 240

_WORKFLOW_DETAILS_START = "<<<WORKFLOW_DETAILS_JSON>>>"
_WORKFLOW_DETAILS_END = "<<<END_WORKFLOW_DETAILS>>>"


def _build_question(scenario: dict) -> str:
    question = scenario["when"]["input"]
    hearing_answer = scenario["when"].get("hearing_answer")
    if hearing_answer is None:
        return question
    parts = [question]
    if hearing_answer.get("processing_type"):
        parts.append(f"（処理方式: {hearing_answer['processing_type']}）")
    if hearing_answer.get("purpose"):
        parts.append(f"（目的: {hearing_answer['purpose']}）")
    return "".join(parts)


def _build_prompt(scenario: dict, workflow_content: str) -> str:
    template = _PROMPT_FILE.read_text(encoding="utf-8")
    question = _build_question(scenario)
    return template.replace("{workflow}", workflow_content).replace("{question}", question)


def _parse_response(response_text: str) -> dict:
    idx = response_text.find(_WORKFLOW_DETAILS_START)
    if idx == -1:
        raise ValueError("<<<WORKFLOW_DETAILS_JSON>>> marker not found")

    details_section = response_text[idx + len(_WORKFLOW_DETAILS_START):]
    end_idx = details_section.find(_WORKFLOW_DETAILS_END)
    if end_idx != -1:
        details_section = details_section[:end_idx]

    fence_start = details_section.find("```json")
    fence_end = details_section.find("```", fence_start + 3) if fence_start != -1 else -1
    if fence_start == -1 or fence_end == -1:
        json_raw = details_section.strip()
    else:
        json_raw = details_section[fence_start + len("```json"):fence_end].strip()

    return json.loads(json_raw)


def _extract_metrics(claude_output: dict) -> dict:
    usage = claude_output.get("usage", {})
    cost_usd = claude_output.get("cost_usd", 0.0)
    return {
        "total_cost_usd": cost_usd,
        "usage": {
            "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
            "cache_read_input_tokens": usage.get("cache_read_input_tokens", 0),
            "cache_creation_input_tokens": usage.get("cache_creation_input_tokens", 0),
        },
    }


def run_one(scenario: dict, skill_dir: Path, trial: int, output_dir: Path) -> dict:
    workflow_content = (skill_dir / WORKFLOW_FILE).read_text(encoding="utf-8")
    prompt = _build_prompt(scenario, workflow_content)

    trial_dir = output_dir / f"trial-{trial:02d}" / scenario["id"]
    trial_dir.mkdir(parents=True, exist_ok=True)

    proc = subprocess.run(
        [
            "claude", "-p",
            "--model", "sonnet",
            "--output-format", "json",
            "--no-session-persistence",
            "--allowedTools", "Read",
        ],
        input=prompt,
        capture_output=True,
        text=True,
        cwd=str(skill_dir),
        timeout=TIMEOUT,
    )

    if proc.returncode != 0:
        error_msg = f"claude exited {proc.returncode}: {proc.stderr[:500]}"
        (trial_dir / "error.txt").write_text(error_msg)
        return {"trial": trial, "scenario_id": scenario["id"], "status": "error", "error": error_msg}

    claude_output = json.loads(proc.stdout)
    result_text = claude_output.get("result", "")

    try:
        details = _parse_response(result_text)
    except (ValueError, json.JSONDecodeError) as exc:
        error_msg = str(exc)
        (trial_dir / "error.txt").write_text(f"{error_msg}\n\nRaw:\n{result_text[:2000]}")
        (trial_dir / "trace.json").write_text(json.dumps(claude_output, ensure_ascii=False, indent=2))
        return {"trial": trial, "scenario_id": scenario["id"], "status": "error", "error": error_msg}

    metrics = _extract_metrics(claude_output)

    (trial_dir / "workflow_details.json").write_text(json.dumps(details, ensure_ascii=False, indent=2))
    (trial_dir / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2))
    (trial_dir / "trace.json").write_text(json.dumps(claude_output, ensure_ascii=False, indent=2))

    selected_pages = details.get("step3", {}).get("selected_pages", [])
    page_paths = [p["path"] for p in selected_pages]

    return {
        "trial": trial,
        "scenario_id": scenario["id"],
        "status": "ok",
        "selected_pages": page_paths,
        "total_pages": len(page_paths),
        "cost_usd": metrics["total_cost_usd"],
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run page-selection-only experiment")
    parser.add_argument("--scenarios", required=True)
    parser.add_argument("--skill-dir", required=True)
    parser.add_argument("--scenario-ids", required=True, help="Comma-separated scenario IDs")
    parser.add_argument("--trials", type=int, default=10)
    parser.add_argument("--output-dir", help="Output directory (default: timestamped under results/)")
    args = parser.parse_args()

    scenarios_path = Path(args.scenarios)
    skill_dir = Path(args.skill_dir)
    scenario_ids = [s.strip() for s in args.scenario_ids.split(",")]

    all_scenarios = json.loads(scenarios_path.read_text())["scenarios"]
    target_scenarios = [s for s in all_scenarios if s["id"] in scenario_ids]
    if not target_scenarios:
        print(f"No scenarios matched: {scenario_ids}", file=sys.stderr)
        sys.exit(1)

    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = _RESULTS_BASE / datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Output dir: {output_dir}", file=sys.stderr)
    print(f"Skill dir: {skill_dir}", file=sys.stderr)
    print(f"Scenarios: {scenario_ids}", file=sys.stderr)
    print(f"Trials: {args.trials}", file=sys.stderr)

    results = []
    for trial in range(1, args.trials + 1):
        for scenario in target_scenarios:
            print(f"  trial {trial:02d} / {scenario['id']} ...", file=sys.stderr, flush=True)
            result = run_one(scenario, skill_dir, trial, output_dir)
            results.append(result)
            status = result.get("status", "?")
            if status == "ok":
                pages = result["selected_pages"]
                print(f"    → {len(pages)} pages | cost ${result['cost_usd']:.4f}", file=sys.stderr)
            else:
                print(f"    → ERROR: {result.get('error','')[:80]}", file=sys.stderr)

    summary = {
        "executed_at": datetime.now().isoformat(),
        "skill_dir": str(skill_dir),
        "scenarios": scenario_ids,
        "trials": args.trials,
        "results": results,
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"\nDone. Summary: {output_dir}/summary.json", file=sys.stderr)


if __name__ == "__main__":
    main()

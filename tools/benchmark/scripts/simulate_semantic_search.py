"""Simulate semantic search: test section selection accuracy against qa.json scenarios.

For each scenario, feeds question + index.md to Claude and compares
selected sections against must-sections.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from generate_index import generate_index

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

POINTER_JSON_SCHEMA = json.dumps({
    "type": "object",
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "file": {"type": "string"},
                    "section_id": {"type": "string"},
                    "relevance": {"type": "string", "enum": ["high", "partial"]},
                },
                "required": ["file", "section_id", "relevance"],
            },
        },
    },
    "required": ["results"],
})


def build_prompt(index_md: str, question: str, hearing_answer: str | None) -> str:
    template = (PROMPTS_DIR / "semantic-search.md").read_text(encoding="utf-8")
    if hearing_answer:
        hearing_block = f"\n## ヒアリング回答\n{hearing_answer}"
    else:
        hearing_block = ""
    return (
        template
        .replace("{index_md}", index_md)
        .replace("{question}", question)
        .replace("{hearing_block}", hearing_block)
    )


def call_llm(prompt: str, model: str = "sonnet") -> dict:
    result = subprocess.run(
        [
            "claude", "-p",
            "--bare",
            "--model", model,
            "--output-format", "json",
            "--json-schema", POINTER_JSON_SCHEMA,
            "--no-session-persistence",
            prompt,
        ],
        capture_output=True,
        text=True,
        timeout=180,
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude CLI failed: {result.stderr}")
    data = json.loads(result.stdout)
    return json.loads(data["result"])


def extract_must_sections(scenario: dict) -> list[str]:
    """Extract must-section refs as 'file:section_id' from scenario."""
    refs = []
    for m in scenario["then"].get("must", []):
        refs.append(m["section"])
    return refs


def extract_acceptable_sections(scenario: dict) -> list[str]:
    refs = []
    for a in scenario["then"].get("acceptable", []):
        refs.append(a["section"])
    return refs


def results_to_refs(results: list[dict]) -> set[str]:
    """Convert pointer JSON results to set of 'file:section_id' refs."""
    return {f"{r['file']}:{r['section_id']}" for r in results}


def evaluate_selection(
    selected: set[str],
    must_sections: list[str],
    acceptable_sections: list[str],
) -> dict:
    must_hit = [s for s in must_sections if s in selected]
    must_miss = [s for s in must_sections if s not in selected]
    acceptable_hit = [s for s in acceptable_sections if s in selected]

    recall = len(must_hit) / len(must_sections) if must_sections else 1.0

    return {
        "must_total": len(must_sections),
        "must_hit": must_hit,
        "must_miss": must_miss,
        "acceptable_hit": acceptable_hit,
        "recall": recall,
        "selected_count": len(selected),
    }


def run_simulation(
    scenarios_path: str,
    knowledge_dir: str,
    output_dir: str,
    model: str = "sonnet",
    llm_fn=None,
) -> list[dict]:
    if llm_fn is None:
        def llm_fn(prompt: str) -> dict:
            return call_llm(prompt, model)

    index_md = generate_index(knowledge_dir)

    with open(scenarios_path, encoding="utf-8") as f:
        data = json.load(f)

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    results = []
    for scenario in data["scenarios"]:
        sid = scenario["id"]
        question = scenario["when"]["input"]
        hearing_answer = scenario["when"].get("hearing_answer")

        prompt = build_prompt(index_md, question, hearing_answer)

        print(f"  {sid}: ", end="", flush=True, file=sys.stderr)
        start = time.time()
        try:
            response = llm_fn(prompt)
        except Exception as e:
            print(f"ERROR — {e}", file=sys.stderr)
            results.append({"scenario_id": sid, "error": str(e)})
            continue
        elapsed_ms = int((time.time() - start) * 1000)

        selected = results_to_refs(response.get("results", []))
        must_sections = extract_must_sections(scenario)
        acceptable_sections = extract_acceptable_sections(scenario)
        evaluation = evaluate_selection(selected, must_sections, acceptable_sections)

        status = "HIT" if evaluation["recall"] == 1.0 else "MISS"
        print(
            f"{status} recall={evaluation['recall']:.0%} "
            f"must={evaluation['must_total']} "
            f"selected={evaluation['selected_count']} "
            f"{elapsed_ms}ms",
            file=sys.stderr,
        )

        entry = {
            "scenario_id": sid,
            "question": question,
            "hearing_answer": hearing_answer,
            "response": response,
            "evaluation": evaluation,
            "elapsed_ms": elapsed_ms,
        }
        results.append(entry)

        scenario_out = out_path / f"{sid}.json"
        scenario_out.write_text(
            json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    return results


def print_summary(results: list[dict]) -> None:
    total = len(results)
    errors = sum(1 for r in results if "error" in r)
    evaluated = [r for r in results if "error" not in r]

    if not evaluated:
        print("No scenarios evaluated.", file=sys.stderr)
        return

    perfect = sum(1 for r in evaluated if r["evaluation"]["recall"] == 1.0)
    total_must = sum(r["evaluation"]["must_total"] for r in evaluated)
    total_hit = sum(len(r["evaluation"]["must_hit"]) for r in evaluated)
    avg_recall = total_hit / total_must if total_must else 0
    avg_selected = sum(r["evaluation"]["selected_count"] for r in evaluated) / len(evaluated)
    avg_elapsed = sum(r["elapsed_ms"] for r in evaluated) / len(evaluated)

    print(f"\n{'='*60}", file=sys.stderr)
    print(f"Semantic Search Simulation Summary", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)
    print(f"Scenarios:       {total} total, {errors} errors", file=sys.stderr)
    print(f"Perfect recall:  {perfect}/{len(evaluated)} ({perfect/len(evaluated):.0%})", file=sys.stderr)
    print(f"Section recall:  {total_hit}/{total_must} ({avg_recall:.0%})", file=sys.stderr)
    print(f"Avg selected:    {avg_selected:.1f} sections", file=sys.stderr)
    print(f"Avg latency:     {avg_elapsed:.0f}ms", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    misses = [r for r in evaluated if r["evaluation"]["recall"] < 1.0]
    if misses:
        print(f"\nMissed scenarios:", file=sys.stderr)
        for r in misses:
            ev = r["evaluation"]
            print(f"  {r['scenario_id']}: recall={ev['recall']:.0%} miss={ev['must_miss']}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Simulate semantic search")
    parser.add_argument("--scenarios", required=True, help="Path to qa.json")
    parser.add_argument("--knowledge-dir", required=True, help="Path to knowledge directory")
    parser.add_argument("--output-dir", required=True, help="Output directory for results")
    parser.add_argument("--model", default="sonnet", help="Model (default: sonnet)")
    args = parser.parse_args()

    print(f"Running semantic search simulation...", file=sys.stderr)
    print(f"  Scenarios: {args.scenarios}", file=sys.stderr)
    print(f"  Knowledge: {args.knowledge_dir}", file=sys.stderr)
    print(f"  Model:     {args.model}", file=sys.stderr)

    results = run_simulation(
        args.scenarios,
        args.knowledge_dir,
        args.output_dir,
        args.model,
    )

    print_summary(results)

    summary_path = Path(args.output_dir) / "summary.json"
    summary_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nResults saved to {args.output_dir}/", file=sys.stderr)


if __name__ == "__main__":
    main()

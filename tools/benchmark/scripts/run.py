"""Benchmark runner: semantic search + answer generation for QA scenarios.

Executes the semantic search pipeline (Stage 1 + Stage 2) and answer generation
(Stage 3) for each scenario, saving results in evaluate.py-compatible format.

Output per scenario:
  {output-dir}/{scenario-id}/hearing.json   — hearing behavior
  {output-dir}/{scenario-id}/search.json    — search results (section IDs)
  {output-dir}/{scenario-id}/answer.md      — generated answer text
  {output-dir}/{scenario-id}/metrics.json   — performance metrics
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from tools.benchmark.scripts.evaluate import call_llm
from tools.benchmark.scripts.simulate_semantic_search import (
    STAGE1_JSON_SCHEMA,
    STAGE2_JSON_SCHEMA,
    build_stage1_prompt,
    build_stage2_prompt,
    format_files_content,
    format_hearing_answer,
    parse_stage1_response,
    parse_stage2_response,
)

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

ANSWER_JSON_SCHEMA = json.dumps({
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
    },
    "required": ["answer"],
})


def build_answer_prompt(question: str, hearing_answer: dict | None, sections_content: str) -> str:
    """Build the answer generation prompt from template."""
    template = (PROMPTS_DIR / "answer-generation.md").read_text(encoding="utf-8")
    ha = format_hearing_answer(hearing_answer)
    return (
        template
        .replace("{question}", question)
        .replace("{hearing_answer}", ha)
        .replace("{sections_content}", sections_content)
    )


def format_sections_for_answer(
    knowledge_dir: str | Path,
    results: list[dict],
    max_sections: int = 10,
) -> str:
    """Load and format selected sections for the answer generation prompt."""
    knowledge_dir = Path(knowledge_dir)
    parts = []
    count = 0
    for r in results:
        if count >= max_sections:
            break
        file_path = knowledge_dir / r["file"]
        if not file_path.exists():
            print(f"WARNING: file not found: {file_path}", file=sys.stderr)
            continue
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
        section_id = r["section_id"]
        section = None
        for s in data.get("sections", []):
            if s["id"] == section_id:
                section = s
                break
        if section is None:
            print(f"WARNING: section {section_id} not found in {r['file']}", file=sys.stderr)
            continue
        ref = f"{r['file']}:{section_id}"
        title = section.get("title", "")
        content = section.get("content", "")
        parts.append(f"=== {ref} — {title} ===\n{content}\n=== END ===")
        count += 1
    return "\n\n".join(parts)


def parse_answer_response(response: dict) -> str:
    """Parse and validate answer generation response."""
    if "answer" not in response:
        raise ValueError("Response missing 'answer' key")
    return response["answer"]


def aggregate_all_metrics(stage1: dict, stage2: dict, answer: dict) -> dict:
    """Combine metrics from all three stages."""
    def _get(d: dict, key: str, default=0):
        return d.get(key, default)

    def _usage(d: dict) -> tuple[int, int]:
        u = d.get("usage", {})
        return u.get("input_tokens", 0), u.get("output_tokens", 0)

    s1_in, s1_out = _usage(stage1)
    s2_in, s2_out = _usage(stage2)
    a_in, a_out = _usage(answer)

    return {
        "duration_ms": _get(stage1, "duration_ms") + _get(stage2, "duration_ms") + _get(answer, "duration_ms"),
        "total_cost_usd": _get(stage1, "total_cost_usd", 0.0) + _get(stage2, "total_cost_usd", 0.0) + _get(answer, "total_cost_usd", 0.0),
        "total_tokens": s1_in + s1_out + s2_in + s2_out + a_in + a_out,
        "stages": {
            "stage1": {
                "duration_ms": _get(stage1, "duration_ms"),
                "input_tokens": s1_in,
                "output_tokens": s1_out,
            },
            "stage2": {
                "duration_ms": _get(stage2, "duration_ms"),
                "input_tokens": s2_in,
                "output_tokens": s2_out,
            },
            "answer": {
                "duration_ms": _get(answer, "duration_ms"),
                "input_tokens": a_in,
                "output_tokens": a_out,
            },
        },
    }


def save_scenario_results(output_dir: str | Path, scenario_id: str, data: dict) -> None:
    """Save scenario results to files in evaluate.py-compatible format."""
    scenario_dir = Path(output_dir) / scenario_id
    scenario_dir.mkdir(parents=True, exist_ok=True)

    (scenario_dir / "hearing.json").write_text(
        json.dumps(data["hearing"], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (scenario_dir / "search.json").write_text(
        json.dumps(data["search"], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (scenario_dir / "answer.md").write_text(data["answer"], encoding="utf-8")
    (scenario_dir / "metrics.json").write_text(
        json.dumps(data["metrics"], ensure_ascii=False, indent=2), encoding="utf-8"
    )


def run_scenario(
    scenario: dict,
    index_content: str,
    knowledge_dir: str | Path,
    llm_fn=None,
    model: str = "sonnet",
) -> dict:
    """Run a single scenario through the full pipeline.

    Returns dict with: scenario_id, hearing, search, answer, metrics.
    """
    if llm_fn is None:
        def llm_fn(prompt, schema, model=model):
            return call_llm(prompt, schema, model)

    question = scenario["when"]["input"]
    hearing_answer = scenario["when"].get("hearing_answer")

    # Stage 1: page selection
    s1_prompt = build_stage1_prompt(question, hearing_answer, index_content)
    s1_response = llm_fn(s1_prompt, STAGE1_JSON_SCHEMA)
    s1_files = parse_stage1_response(s1_response["result"])
    s1_metrics = s1_response.get("metrics", {})

    # Stage 2: section selection
    file_paths = [f["path"] for f in s1_files]
    files_content = format_files_content(knowledge_dir, file_paths)
    s2_prompt = build_stage2_prompt(question, hearing_answer, files_content)
    s2_response = llm_fn(s2_prompt, STAGE2_JSON_SCHEMA)
    s2_results = parse_stage2_response(s2_response["result"])
    s2_metrics = s2_response.get("metrics", {})

    # Stage 3: answer generation
    sections_content = format_sections_for_answer(knowledge_dir, s2_results)
    a_prompt = build_answer_prompt(question, hearing_answer, sections_content)
    a_response = llm_fn(a_prompt, ANSWER_JSON_SCHEMA)
    answer_text = parse_answer_response(a_response["result"])
    a_metrics = a_response.get("metrics", {})

    # Build hearing info
    if hearing_answer:
        hearing = {"status": "provided"}
        if hearing_answer.get("processing_type"):
            hearing["processing_type"] = hearing_answer["processing_type"]
        if hearing_answer.get("goal"):
            hearing["goal"] = hearing_answer["goal"]
    else:
        hearing = {"status": "skipped"}

    # Build search info
    section_ids = [f"{r['file']}:{r['section_id']}" for r in s2_results]
    search = {"section_ids": section_ids}

    metrics = aggregate_all_metrics(s1_metrics, s2_metrics, a_metrics)

    return {
        "scenario_id": scenario["id"],
        "hearing": hearing,
        "search": search,
        "answer": answer_text,
        "metrics": metrics,
    }


def run_all(
    scenarios_path: str,
    knowledge_dir: str,
    output_dir: str,
    index_path: str | None = None,
    model: str = "sonnet",
    scenario_ids: list[str] | None = None,
) -> dict:
    """Run all scenarios and save results."""
    with open(scenarios_path, encoding="utf-8") as f:
        data = json.load(f)

    if index_path:
        index_content = Path(index_path).read_text(encoding="utf-8")
    else:
        from tools.benchmark.scripts.generate_index import generate_index
        index_content = generate_index(knowledge_dir)

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    results = []
    for scenario in data["scenarios"]:
        sid = scenario["id"]
        if scenario_ids and sid not in scenario_ids:
            continue

        print(f"Running {sid}...", file=sys.stderr)
        result = run_scenario(scenario, index_content, knowledge_dir, model=model)
        save_scenario_results(output_dir, sid, result)
        results.append(result)

    total = len(results)
    summary = {
        "total_scenarios": total,
        "scenarios": [
            {"id": r["scenario_id"], "search_sections": len(r["search"]["section_ids"])}
            for r in results
        ],
    }

    (out / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return summary


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run QA benchmark: semantic search + answer generation")
    parser.add_argument("--scenarios", required=True, help="Path to scenarios JSON")
    parser.add_argument("--knowledge-dir", required=True, help="Path to knowledge directory")
    parser.add_argument("--index", help="Path to index.md (default: generate from knowledge-dir)")
    parser.add_argument("--output-dir", required=True, help="Output directory for results")
    parser.add_argument("--model", default="sonnet", help="LLM model (default: sonnet)")
    parser.add_argument("--scenario-ids", help="Comma-separated scenario IDs to run")
    args = parser.parse_args()

    scenario_ids = args.scenario_ids.split(",") if args.scenario_ids else None

    summary = run_all(
        args.scenarios,
        args.knowledge_dir,
        args.output_dir,
        index_path=args.index,
        model=args.model,
        scenario_ids=scenario_ids,
    )

    print(f"\nCompleted: {summary['total_scenarios']} scenarios", file=sys.stderr)
    for s in summary["scenarios"]:
        print(f"  {s['id']}: {s['search_sections']} sections found", file=sys.stderr)


if __name__ == "__main__":
    main()

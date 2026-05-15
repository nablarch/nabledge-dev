"""Simulate hearing (clarification) step against QA scenarios.

Runs classification (skip/ask) and extraction for each scenario,
then compares results with expected_hearing and hearing_answer ground truth.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from tools.benchmark.scripts.evaluate import call_llm

PROMPTS_DIR = Path(__file__).parent.parent / "components" / "prompts"

SLUG_TO_DISPLAY_NAME = {
    "web-application": "ウェブアプリケーション",
    "restful-web-service": "RESTfulウェブサービス",
    "nablarch-batch": "Nablarchバッチ",
    "db-messaging": "テーブルをキューとして使ったメッセージング",
    "http-messaging": "HTTPメッセージング",
    "jakarta-batch": "Jakartaバッチ",
    "mom-messaging": "MOMメッセージング",
}

CLASSIFY_JSON_SCHEMA = json.dumps({
    "type": "object",
    "properties": {
        "classification": {
            "type": "string",
            "enum": ["skip", "ask"],
        },
        "hearing_answer": {
            "type": ["object", "null"],
            "properties": {
                "processing_type": {"type": ["string", "null"]},
                "goal": {"type": "string"},
            },
            "required": ["processing_type", "goal"],
        },
        "trace": {
            "type": "object",
            "properties": {
                "reason": {"type": "string"},
                "matched_keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["reason", "matched_keywords"],
        },
    },
    "required": ["classification", "hearing_answer", "trace"],
})

EXTRACT_JSON_SCHEMA = json.dumps({
    "type": "object",
    "properties": {
        "hearing_answer": {
            "type": "object",
            "properties": {
                "processing_type": {"type": ["string", "null"]},
                "goal": {"type": "string"},
            },
            "required": ["processing_type", "goal"],
        },
        "trace": {
            "type": "object",
            "properties": {
                "user_intent": {"type": "string"},
                "goal_derivation": {"type": "string"},
            },
            "required": ["user_intent", "goal_derivation"],
        },
    },
    "required": ["hearing_answer", "trace"],
})


def extract_processing_types(index_content: str) -> list[str]:
    """Extract processing type category names from index.md H2 headings.

    Extracts the subcategory part from headings like '## processing-pattern/web-application'.
    """
    types = []
    for line in index_content.splitlines():
        if line.startswith("## processing-pattern/"):
            slug = line[len("## processing-pattern/"):].strip()
            types.append(SLUG_TO_DISPLAY_NAME.get(slug, slug))
    return types


def format_processing_types(types: list[str]) -> str:
    """Format processing types list for prompt injection."""
    if not types:
        return "（なし）"
    return "\n".join(f"- {t}" for t in types)


def build_classify_prompt(question: str, processing_types: str) -> str:
    template = (PROMPTS_DIR / "hearing-classify.md").read_text(encoding="utf-8")
    return (
        template
        .replace("{question}", question)
        .replace("{processing_types}", processing_types)
    )


def build_extract_prompt(question: str, user_response: str) -> str:
    template = (PROMPTS_DIR / "hearing-extract.md").read_text(encoding="utf-8")
    return (
        template
        .replace("{question}", question)
        .replace("{user_response}", user_response)
    )


def expected_classification(expected_hearing: str) -> str:
    """Map expected_hearing to expected classification."""
    if expected_hearing == "should_skip":
        return "skip"
    return "ask"


def compare_classification(actual: str, expected_hearing: str) -> dict:
    """Compare actual classification with expected.

    Returns PASS/FAIL based on the evaluation matrix:
    - should_skip → skip: PASS
    - should_skip → ask: PASS (unnecessary but harmless)
    - must_ask → ask: PASS
    - must_ask → skip: FAIL
    - nice_to_ask → ask: PASS
    - nice_to_ask → skip: PASS (room for improvement)
    """
    if expected_hearing == "must_ask" and actual == "skip":
        return {"result": "FAIL", "reason": "must_ask classified as skip"}
    if expected_hearing == "should_skip" and actual == "ask":
        return {"result": "PASS", "note": "unnecessary hearing (harmless)"}
    if expected_hearing == "nice_to_ask" and actual == "skip":
        return {"result": "PASS", "note": "nice_to_ask skipped (room for improvement)"}
    return {"result": "PASS"}


def compare_processing_type(actual: str | None, expected: str | None) -> dict:
    """Compare actual processing_type with ground truth."""
    if actual == expected:
        return {"result": "MATCH"}
    return {"result": "MISMATCH", "actual": actual, "expected": expected}


def _aggregate_metrics(classify_metrics: dict, extract_metrics: dict) -> dict:
    """Aggregate metrics from classify and extract stages."""
    if not classify_metrics and not extract_metrics:
        return {}
    total_duration = classify_metrics.get("duration_ms", 0) + extract_metrics.get("duration_ms", 0)
    total_cost = classify_metrics.get("total_cost_usd", 0.0) + extract_metrics.get("total_cost_usd", 0.0)
    c_usage = classify_metrics.get("usage", {})
    e_usage = extract_metrics.get("usage", {})
    total_in = c_usage.get("input_tokens", 0) + e_usage.get("input_tokens", 0)
    total_out = c_usage.get("output_tokens", 0) + e_usage.get("output_tokens", 0)
    return {
        "total_duration_ms": total_duration,
        "total_cost_usd": round(total_cost, 6),
        "total_input_tokens": total_in,
        "total_output_tokens": total_out,
    }


def simulate_scenario(
    scenario: dict,
    processing_types: str,
    llm_fn=None,
    model: str = "sonnet",
) -> dict:
    if llm_fn is None:
        def llm_fn(prompt, schema, model=model):
            return call_llm(prompt, schema, model)

    scenario_id = scenario["id"]
    question = scenario["when"]["input"]
    expected_hearing = scenario["when"].get("expected_hearing", "should_skip")
    ground_truth_ha = scenario["when"].get("hearing_answer")
    ground_truth_pt = ground_truth_ha.get("processing_type") if ground_truth_ha else None

    classify_prompt = build_classify_prompt(question, processing_types)
    classify_response = llm_fn(classify_prompt, CLASSIFY_JSON_SCHEMA)
    classify_result = classify_response["result"]
    classify_metrics = classify_response.get("metrics", {})

    actual_classification = classify_result["classification"]
    classification_comparison = compare_classification(actual_classification, expected_hearing)

    extract_result = None
    extract_metrics = {}

    if actual_classification == "skip":
        actual_ha = classify_result.get("hearing_answer")
    elif ground_truth_ha:
        user_response = ground_truth_pt or ""
        extract_prompt = build_extract_prompt(question, user_response)
        extract_response = llm_fn(extract_prompt, EXTRACT_JSON_SCHEMA)
        extract_result = extract_response["result"]
        extract_metrics = extract_response.get("metrics", {})
        actual_ha = extract_result.get("hearing_answer")
    else:
        print(
            f"  WARNING: {scenario_id} classified as ask but no ground_truth hearing_answer",
            file=sys.stderr,
        )
        actual_ha = None

    actual_pt = actual_ha.get("processing_type") if actual_ha else None
    pt_comparison = compare_processing_type(actual_pt, ground_truth_pt)

    return {
        "scenario_id": scenario_id,
        "expected_hearing": expected_hearing,
        "classify": {
            "classification": actual_classification,
            "hearing_answer": classify_result.get("hearing_answer"),
            "trace": classify_result.get("trace"),
            "metrics": classify_metrics,
        },
        "extract": {
            "hearing_answer": extract_result.get("hearing_answer") if extract_result else None,
            "trace": extract_result.get("trace") if extract_result else None,
            "metrics": extract_metrics,
        } if extract_result else None,
        "comparison": {
            "classification": classification_comparison,
            "processing_type": pt_comparison,
        },
        "final_hearing_answer": actual_ha,
        "metrics": _aggregate_metrics(classify_metrics, extract_metrics),
    }


def simulate_all(
    scenarios_path: str,
    index_content: str,
    output_dir: str,
    model: str = "sonnet",
    scenario_ids: list[str] | None = None,
) -> dict:
    with open(scenarios_path, encoding="utf-8") as f:
        data = json.load(f)

    processing_types_list = extract_processing_types(index_content)
    processing_types = format_processing_types(processing_types_list)

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    results = []
    for scenario in data["scenarios"]:
        sid = scenario["id"]
        if scenario_ids and sid not in scenario_ids:
            continue

        print(f"Simulating hearing {sid}...", file=sys.stderr)
        result = simulate_scenario(scenario, processing_types, model=model)

        scenario_dir = out_path / sid
        scenario_dir.mkdir(parents=True, exist_ok=True)
        (scenario_dir / "hearing.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        results.append(result)

    classification_pass = sum(
        1 for r in results if r["comparison"]["classification"]["result"] == "PASS"
    )
    pt_match = sum(
        1 for r in results if r["comparison"]["processing_type"]["result"] == "MATCH"
    )
    total = len(results)

    scenarios_with_metrics = [r for r in results if r.get("metrics")]
    if scenarios_with_metrics:
        total_duration = sum(r["metrics"]["total_duration_ms"] for r in scenarios_with_metrics)
        total_cost = sum(r["metrics"]["total_cost_usd"] for r in scenarios_with_metrics)
        total_in = sum(r["metrics"]["total_input_tokens"] for r in scenarios_with_metrics)
        total_out = sum(r["metrics"]["total_output_tokens"] for r in scenarios_with_metrics)
        n = len(scenarios_with_metrics)
        aggregate_metrics = {
            "total_duration_ms": total_duration,
            "total_cost_usd": round(total_cost, 6),
            "total_input_tokens": total_in,
            "total_output_tokens": total_out,
            "avg_duration_ms": round(total_duration / n),
            "avg_cost_usd": round(total_cost / n, 6),
        }
    else:
        aggregate_metrics = {}

    summary = {
        "total_scenarios": total,
        "classification_pass": classification_pass,
        "classification_rate": classification_pass / total if total > 0 else 0.0,
        "processing_type_match": pt_match,
        "processing_type_rate": pt_match / total if total > 0 else 0.0,
        "metrics": aggregate_metrics,
        "per_scenario": [
            {
                "id": r["scenario_id"],
                "expected_hearing": r["expected_hearing"],
                "actual_classification": r["classify"]["classification"],
                "classification_result": r["comparison"]["classification"]["result"],
                "pt_result": r["comparison"]["processing_type"]["result"],
                "final_hearing_answer": r["final_hearing_answer"],
            }
            for r in results
        ],
    }

    (out_path / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return summary


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Simulate hearing classification")
    parser.add_argument("--scenarios", required=True, help="Path to scenarios JSON")
    parser.add_argument("--index", required=True, help="Path to index.md")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    parser.add_argument("--model", default="sonnet", help="LLM model (default: sonnet)")
    parser.add_argument("--scenario-ids", help="Comma-separated scenario IDs to run")
    args = parser.parse_args()

    index_content = Path(args.index).read_text(encoding="utf-8")
    scenario_ids = args.scenario_ids.split(",") if args.scenario_ids else None

    summary = simulate_all(
        args.scenarios,
        index_content,
        args.output_dir,
        model=args.model,
        scenario_ids=scenario_ids,
    )

    total = summary["total_scenarios"]
    cls_pass = summary["classification_pass"]
    pt_match = summary["processing_type_match"]
    print(
        f"\nResults: classification {cls_pass}/{total} PASS "
        f"({summary['classification_rate']:.1%}), "
        f"processing_type {pt_match}/{total} MATCH "
        f"({summary['processing_type_rate']:.1%})",
        file=sys.stderr,
    )
    for s in summary["per_scenario"]:
        cls_status = s["classification_result"]
        pt_status = s["pt_result"]
        print(f"  {s['id']}: cls={cls_status} pt={pt_status}", file=sys.stderr)


if __name__ == "__main__":
    main()

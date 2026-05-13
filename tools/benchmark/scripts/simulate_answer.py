"""Simulate answer generation for QA scenarios.

Takes scenario must+acceptable sections as "perfect search" input,
generates answers, and evaluates quality using C-claim and hallucination
judges. Isolates answer quality from search and verify quality.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from tools.benchmark.scripts.evaluate import (
    CLAIM_JSON_SCHEMA,
    HALLUCINATION_JSON_SCHEMA,
    build_claim_prompt,
    build_hallucination_prompt,
    calculate_accuracy_score,
    calculate_hallucination_score,
    call_llm,
    load_section_content,
    parse_claim_response,
    parse_hallucination_response,
)
from tools.benchmark.scripts.simulate_answer_verify import (
    ANSWER_JSON_SCHEMA,
    build_answer_prompt,
    load_scenario_sections,
    parse_answer_response,
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


def evaluate_answer(
    answer: str,
    must_facts: list[dict],
    acceptable_sections: list[dict],
    knowledge_dir: str | Path,
    llm_fn=None,
    section_loader=None,
) -> dict:
    if llm_fn is None:
        llm_fn = call_llm
    if section_loader is None:
        section_loader = load_section_content

    eval_metrics = []
    claim_verdicts = []

    for mf in must_facts:
        section_content = section_loader(knowledge_dir, mf["section"])
        prompt = build_claim_prompt(mf["fact"], answer, section_content)
        response = llm_fn(prompt, CLAIM_JSON_SCHEMA)
        parsed = parse_claim_response(response["result"])
        parsed["fact"] = mf["fact"]
        claim_verdicts.append(parsed)
        eval_metrics.append(response.get("metrics", {}))

    all_refs = [m["section"] for m in must_facts] + [a["section"] for a in acceptable_sections]
    sections_parts = []
    for ref in all_refs:
        try:
            content = section_loader(knowledge_dir, ref)
            sections_parts.append(content)
        except (FileNotFoundError, ValueError):
            pass
    sections_text = "\n\n---\n\n".join(sections_parts) if sections_parts else ""

    h_prompt = build_hallucination_prompt(answer, sections_text)
    h_response = llm_fn(h_prompt, HALLUCINATION_JSON_SCHEMA)
    hallucination = parse_hallucination_response(h_response["result"])
    eval_metrics.append(h_response.get("metrics", {}))

    accuracy = calculate_accuracy_score(claim_verdicts)
    h_score = calculate_hallucination_score(hallucination)

    return {
        "claim_verdicts": claim_verdicts,
        "hallucination": hallucination,
        "scores": {"accuracy": accuracy, "hallucination": h_score},
        "eval_metrics": eval_metrics,
    }


def simulate_scenario(
    scenario: dict,
    knowledge_dir: str | Path,
    llm_fn=None,
    model: str = "sonnet",
) -> dict:
    if llm_fn is None:
        def llm_fn(prompt, schema, model=model):
            return call_llm(prompt, schema, model)

    question = scenario["when"]["input"]
    hearing_answer = scenario["when"].get("hearing_answer")
    must = scenario["then"].get("must", [])
    acceptable = scenario["then"].get("acceptable", [])

    sections_content, section_refs = load_scenario_sections(knowledge_dir, must, acceptable)

    answer_prompt = build_answer_prompt(question, hearing_answer, sections_content)
    answer_response = llm_fn(answer_prompt, ANSWER_JSON_SCHEMA)
    answer_text = parse_answer_response(answer_response["result"])
    answer_metrics = answer_response.get("metrics", {})

    evaluation = evaluate_answer(
        answer_text, must, acceptable, knowledge_dir, llm_fn=llm_fn,
    )

    all_metrics = [answer_metrics] + evaluation["eval_metrics"]
    metrics = aggregate_metrics(all_metrics)

    return {
        "scenario_id": scenario["id"],
        "sections_input": section_refs,
        "answer": answer_text,
        "claim_verdicts": evaluation["claim_verdicts"],
        "hallucination": evaluation["hallucination"],
        "scores": evaluation["scores"],
        "metrics": metrics,
    }


def simulate_all(
    scenarios_path: str,
    knowledge_dir: str,
    output_dir: str,
    model: str = "sonnet",
    scenario_ids: list[str] | None = None,
    llm_fn=None,
) -> dict:
    with open(scenarios_path, encoding="utf-8") as f:
        data = json.load(f)

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    results = []
    for scenario in data["scenarios"]:
        sid = scenario["id"]
        if scenario_ids and sid not in scenario_ids:
            continue

        print(f"Simulating {sid}...", file=sys.stderr)

        if llm_fn is not None:
            result = simulate_scenario(scenario, knowledge_dir, llm_fn=llm_fn)
        else:
            result = simulate_scenario(scenario, knowledge_dir, model=model)

        scenario_dir = out_path / sid
        scenario_dir.mkdir(parents=True, exist_ok=True)

        (scenario_dir / "answer.md").write_text(result["answer"], encoding="utf-8")
        eval_data = {
            "claim_verdicts": result["claim_verdicts"],
            "hallucination": result["hallucination"],
            "scores": result["scores"],
        }
        (scenario_dir / "evaluation.json").write_text(
            json.dumps(eval_data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        if result.get("metrics"):
            (scenario_dir / "metrics.json").write_text(
                json.dumps(result["metrics"], ensure_ascii=False, indent=2), encoding="utf-8"
            )
        results.append(result)

    accuracies = [r["scores"]["accuracy"] for r in results if r["scores"]["accuracy"] is not None]
    h_scores = [r["scores"]["hallucination"] for r in results if r["scores"]["hallucination"] is not None]

    pass_count = sum(
        1 for r in results
        if r["scores"]["accuracy"] is not None
        and r["scores"]["accuracy"] == 1.0
        and r["scores"]["hallucination"] == 1
    )

    total = len(results)
    scores = {
        "mean_accuracy": sum(accuracies) / len(accuracies) if accuracies else None,
        "hallucination_pass_rate": sum(h_scores) / len(h_scores) if h_scores else None,
        "pass_count": pass_count,
        "pass_rate": pass_count / total if total > 0 else None,
    }

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

    per_scenario = []
    for r in results:
        must_present = sum(
            1 for cv in r["claim_verdicts"] if cv["verdict"] == "PRESENT"
        )
        per_scenario.append({
            "id": r["scenario_id"],
            "accuracy": r["scores"]["accuracy"],
            "hallucination": r["hallucination"]["verdict"],
            "must_total": len(r["claim_verdicts"]),
            "must_present": must_present,
            "metrics": r.get("metrics", {}),
        })

    summary = {
        "total_scenarios": total,
        "scores": scores,
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
        description="Simulate answer generation with evaluation"
    )
    parser.add_argument("--scenarios", required=True, help="Path to scenarios JSON")
    parser.add_argument("--knowledge-dir", required=True, help="Path to knowledge directory")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    parser.add_argument("--model", default="sonnet", help="LLM model (default: sonnet)")
    parser.add_argument("--scenario-ids", help="Comma-separated scenario IDs to run")
    args = parser.parse_args()

    scenario_ids = args.scenario_ids.split(",") if args.scenario_ids else None

    summary = simulate_all(
        args.scenarios,
        args.knowledge_dir,
        args.output_dir,
        model=args.model,
        scenario_ids=scenario_ids,
    )

    total = summary["total_scenarios"]
    scores = summary["scores"]
    acc_str = f"{scores['mean_accuracy']:.1%}" if scores["mean_accuracy"] is not None else "N/A"
    hall_str = f"{scores['hallucination_pass_rate']:.1%}" if scores["hallucination_pass_rate"] is not None else "N/A"
    print(f"\nResults: {scores['pass_count']}/{total} PASS", file=sys.stderr)
    print(f"  Accuracy: {acc_str}", file=sys.stderr)
    print(f"  Hallucination pass: {hall_str}", file=sys.stderr)
    for s in summary["per_scenario"]:
        status = "PASS" if s["accuracy"] == 1.0 and s["hallucination"] == "PASS" else "FAIL"
        s_acc = f"{s['accuracy']:.0%}" if s["accuracy"] is not None else "N/A"
        print(
            f"  {s['id']}: {status} — acc={s_acc} hall={s['hallucination']} ({s['must_present']}/{s['must_total']})",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()

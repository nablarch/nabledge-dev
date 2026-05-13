"""Simulate answer generation + verification for QA scenarios.

Takes scenario must+acceptable sections as "perfect search" input,
generates answers, verifies them for hallucinations, and retries on FAIL.
Isolates answer+verify quality from search quality.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from tools.benchmark.scripts.evaluate import call_llm, parse_section_ref
from tools.benchmark.scripts.simulate_semantic_search import format_hearing_answer

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

ANSWER_JSON_SCHEMA = json.dumps({
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "trace": {
            "type": "object",
            "properties": {
                "user_intent": {"type": "string"},
                "sections": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "section": {"type": "string"},
                            "used": {"type": "boolean"},
                            "extracted": {"type": "string"},
                            "mapped_to": {"type": "string"},
                            "reason": {"type": "string"},
                        },
                        "required": ["section", "used"],
                    },
                },
            },
            "required": ["user_intent", "sections"],
        },
    },
    "required": ["answer", "trace"],
})

VERIFY_JSON_SCHEMA = json.dumps({
    "type": "object",
    "properties": {
        "result": {"type": "string", "enum": ["PASS", "FAIL"]},
        "claims": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "claim": {"type": "string"},
                    "supported": {"type": "boolean"},
                    "evidence": {"type": "string"},
                },
                "required": ["claim", "supported", "evidence"],
            },
        },
        "issues": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "claim": {"type": "string"},
                    "quote": {"type": "string"},
                },
                "required": ["claim", "quote"],
            },
        },
    },
    "required": ["result", "claims", "issues"],
})


def format_section_content(
    rel_path: str,
    section_id: str,
    page_title: str,
    section_title: str,
    content: str,
) -> str:
    return (
        f"=== {rel_path} : {section_id} ===\n"
        f"# {page_title} > {section_title}\n"
        f"{content}\n"
        f"=== END ==="
    )


def load_scenario_sections(
    knowledge_dir: str | Path,
    must_sections: list[dict],
    acceptable_sections: list[dict],
) -> tuple[str, list[str]]:
    knowledge_dir = Path(knowledge_dir)
    parts = []
    refs = []

    all_sections = [(m["section"], "must") for m in must_sections] + [
        (a["section"], "acceptable") for a in acceptable_sections
    ]

    for section_ref, _ in all_sections:
        file_path, section_id = parse_section_ref(section_ref)
        full_path = knowledge_dir / file_path
        if not full_path.exists():
            print(f"WARNING: file not found: {full_path}", file=sys.stderr)
            continue
        with open(full_path, encoding="utf-8") as f:
            data = json.load(f)

        section = None
        for s in data.get("sections", []):
            if s["id"] == section_id:
                section = s
                break
        if section is None:
            print(f"WARNING: section {section_id} not found in {file_path}", file=sys.stderr)
            continue

        parts.append(format_section_content(
            file_path, section_id,
            data.get("title", ""),
            section.get("title", ""),
            section.get("content", ""),
        ))
        refs.append(section_ref)

    return "\n\n".join(parts), refs


def build_answer_prompt(question: str, hearing_answer: dict | None, sections_content: str) -> str:
    template = (PROMPTS_DIR / "answer.md").read_text(encoding="utf-8")
    ha = format_hearing_answer(hearing_answer)
    return (
        template
        .replace("{question}", question)
        .replace("{hearing_answer}", ha)
        .replace("{sections_content}", sections_content)
    )


def build_answer_retry_prompt(base_prompt: str, issues: list[dict]) -> str:
    if not issues:
        return base_prompt
    exclusion_lines = [f"- {issue['claim']}" for issue in issues]
    exclusion_text = "\n".join(exclusion_lines)
    return (
        f"{base_prompt}\n\n"
        f"## 除外指示\n\n"
        f"以下の主張は知識セクションに裏付けがないため含めないこと:\n{exclusion_text}"
    )


def build_verify_prompt(answer: str, sections_content: str) -> str:
    template = (PROMPTS_DIR / "verify.md").read_text(encoding="utf-8")
    return (
        template
        .replace("{answer}", answer)
        .replace("{sections_content}", sections_content)
    )


def parse_answer_response(response: dict) -> str:
    if "answer" not in response:
        raise ValueError("Response missing 'answer' key")
    return response["answer"]


def parse_verify_response(response: dict) -> dict:
    result = response.get("result")
    if result not in ("PASS", "FAIL"):
        raise ValueError(f"Invalid or missing 'result': {result!r}")
    claims = response.get("claims")
    if claims is None:
        raise ValueError("Response missing 'claims' key")
    if not isinstance(claims, list):
        raise ValueError(f"'claims' must be a list, got {type(claims).__name__!r}")
    issues = response.get("issues")
    if issues is None:
        raise ValueError("Response missing 'issues' key")
    if not isinstance(issues, list):
        raise ValueError(f"'issues' must be a list, got {type(issues).__name__!r}")
    return {"result": result, "claims": claims, "issues": issues}


def aggregate_metrics(
    answer_metrics: dict,
    verify_metrics: dict,
    retry_metrics: dict | None = None,
) -> dict:
    def _get(d: dict, key: str, default=0):
        return d.get(key, default)

    def _usage(d: dict) -> tuple[int, int]:
        u = d.get("usage", {})
        return u.get("input_tokens", 0), u.get("output_tokens", 0)

    a_in, a_out = _usage(answer_metrics)
    v_in, v_out = _usage(verify_metrics)

    total_duration = _get(answer_metrics, "duration_ms") + _get(verify_metrics, "duration_ms")
    total_cost = _get(answer_metrics, "total_cost_usd", 0.0) + _get(verify_metrics, "total_cost_usd", 0.0)
    total_tokens = a_in + a_out + v_in + v_out

    stages = {
        "answer": {
            "duration_ms": _get(answer_metrics, "duration_ms"),
            "input_tokens": a_in,
            "output_tokens": a_out,
        },
        "verify": {
            "duration_ms": _get(verify_metrics, "duration_ms"),
            "input_tokens": v_in,
            "output_tokens": v_out,
        },
    }

    if retry_metrics is not None:
        r_in, r_out = _usage(retry_metrics)
        total_duration += _get(retry_metrics, "duration_ms")
        total_cost += _get(retry_metrics, "total_cost_usd", 0.0)
        total_tokens += r_in + r_out
        stages["retry"] = {
            "duration_ms": _get(retry_metrics, "duration_ms"),
            "input_tokens": r_in,
            "output_tokens": r_out,
        }

    return {
        "duration_ms": total_duration,
        "total_cost_usd": total_cost,
        "total_tokens": total_tokens,
        "stages": stages,
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
    trace = answer_response["result"].get("trace")
    answer_metrics = answer_response.get("metrics", {})

    verify_prompt = build_verify_prompt(answer_text, sections_content)
    verify_response = llm_fn(verify_prompt, VERIFY_JSON_SCHEMA)
    verify_result = parse_verify_response(verify_response["result"])
    verify_metrics = verify_response.get("metrics", {})

    retry_answer = None
    retry_metrics_data = None

    if verify_result["result"] == "FAIL" and verify_result["issues"]:
        retry_prompt = build_answer_retry_prompt(answer_prompt, verify_result["issues"])
        retry_response = llm_fn(retry_prompt, ANSWER_JSON_SCHEMA)
        retry_answer = parse_answer_response(retry_response["result"])
        retry_metrics_data = retry_response.get("metrics", {})

    metrics = aggregate_metrics(answer_metrics, verify_metrics, retry_metrics_data)

    return {
        "scenario_id": scenario["id"],
        "sections_input": section_refs,
        "answer": answer_text,
        "trace": trace,
        "verify": verify_result,
        "retry_answer": retry_answer,
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
        if result.get("trace"):
            (scenario_dir / "trace.json").write_text(
                json.dumps(result["trace"], ensure_ascii=False, indent=2), encoding="utf-8"
            )
        (scenario_dir / "verify.json").write_text(
            json.dumps(result["verify"], ensure_ascii=False, indent=2), encoding="utf-8"
        )
        if result["retry_answer"] is not None:
            (scenario_dir / "retry_answer.md").write_text(
                result["retry_answer"], encoding="utf-8"
            )
        if result.get("metrics"):
            (scenario_dir / "metrics.json").write_text(
                json.dumps(result["metrics"], ensure_ascii=False, indent=2), encoding="utf-8"
            )
        results.append(result)

    verify_pass = sum(1 for r in results if r["verify"]["result"] == "PASS")
    verify_fail = sum(1 for r in results if r["verify"]["result"] == "FAIL")
    retry_count = sum(1 for r in results if r["retry_answer"] is not None)

    summary = {
        "total_scenarios": len(results),
        "verify_pass": verify_pass,
        "verify_fail": verify_fail,
        "retry_count": retry_count,
        "per_scenario": [
            {
                "id": r["scenario_id"],
                "verify_result": r["verify"]["result"],
                "claims_count": len(r["verify"]["claims"]),
                "issues_count": len(r["verify"]["issues"]),
                "retried": r["retry_answer"] is not None,
                "metrics": r.get("metrics", {}),
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

    parser = argparse.ArgumentParser(
        description="Simulate answer generation + verification"
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

    print(f"\nResults: {summary['verify_pass']}/{summary['total_scenarios']} PASS", file=sys.stderr)
    for s in summary["per_scenario"]:
        status = "PASS" if s["verify_result"] == "PASS" else "FAIL"
        retry = " (retried)" if s["retried"] else ""
        print(f"  {s['id']}: {status}{retry} — {s['claims_count']} claims", file=sys.stderr)


if __name__ == "__main__":
    main()

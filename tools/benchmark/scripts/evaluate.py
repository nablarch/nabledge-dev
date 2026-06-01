"""Benchmark evaluation logic: DeepEval RAG metrics scoring."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def parse_section_ref(ref: str) -> tuple[str, str]:
    """Parse 'path/to/file.json:sN' into (file_path, section_id)."""
    last_colon = ref.rfind(":")
    return ref[:last_colon], ref[last_colon + 1:]


def load_section_content(knowledge_dir: str, section_ref: str) -> str:
    """Load section content from a knowledge JSON file."""
    file_path, section_id = parse_section_ref(section_ref)
    full_path = Path(knowledge_dir) / file_path
    with open(full_path, encoding="utf-8") as f:
        data = json.load(f)
    for section in data["sections"]:
        if section["id"] == section_id:
            return section["content"]
    raise ValueError(f"Section {section_id} not found in {file_path}")


def load_page_content(knowledge_dir: str, file_path: str) -> str:
    """Load all sections from a knowledge JSON file, joined with separators."""
    full_path = Path(knowledge_dir) / file_path
    with open(full_path, encoding="utf-8") as f:
        data = json.load(f)
    parts = [s["content"] for s in data.get("sections", [])]
    return "\n\n---\n\n".join(parts)


def load_runner_output(run_dir: str, scenario_id: str) -> dict:
    """Load runner output files for a scenario."""
    scenario_dir = Path(run_dir) / scenario_id
    if not scenario_dir.is_dir():
        raise FileNotFoundError(f"Scenario directory not found: {scenario_dir}")
    answer_path = scenario_dir / "answer.md"
    workflow_details_path = scenario_dir / "workflow_details.json"
    metrics_path = scenario_dir / "metrics.json"
    result = {
        "answer": answer_path.read_text(encoding="utf-8") if answer_path.exists() else "",
    }
    for key, path in [("workflow_details", workflow_details_path), ("metrics", metrics_path)]:
        if path.exists():
            with open(path, encoding="utf-8") as f:
                result[key] = json.load(f)
        else:
            result[key] = {}
    return result


def extract_json_from_result(text: str) -> str:
    """Extract JSON from a result that may be wrapped in markdown code fences."""
    stripped = text.strip()
    lines = stripped.split("\n")
    fence_start = None
    for i, line in enumerate(lines):
        if line.strip().startswith("```"):
            fence_start = i
            break
    if fence_start is not None:
        fence_end = len(lines)
        for i in range(len(lines) - 1, fence_start, -1):
            if lines[i].strip() == "```":
                fence_end = i
                break
        stripped = "\n".join(lines[fence_start + 1:fence_end]).strip()
    obj_start = stripped.find("{")
    if obj_start >= 0:
        decoder = json.JSONDecoder()
        try:
            _, end = decoder.raw_decode(stripped, obj_start)
            return stripped[obj_start:end].strip()
        except json.JSONDecodeError:
            pass
    return stripped


def call_llm(prompt: str, json_schema: str, model: str = "sonnet") -> dict:
    """Call Claude CLI for LLM judgment.

    json_schema is appended to the prompt as output format instructions.
    The model is expected to return valid JSON matching the schema.

    Returns dict with "result" (parsed JSON) and "metrics" keys.
    """
    full_prompt = (
        f"{prompt}\n\n"
        f"## 出力形式（厳守）\n"
        f"以下のJSON Schemaに従ったJSONのみを出力してください。"
        f"コードフェンス・説明文・その他のテキストは一切不要です。\n"
        f"```\n{json_schema}\n```"
    )
    result = subprocess.run(
        [
            "claude", "-p",
            "--model", model,
            "--output-format", "json",
            "--no-session-persistence",
        ],
        input=full_prompt,
        capture_output=True,
        text=True,
        cwd="/tmp",
        timeout=300,
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude CLI failed: {result.stderr}")
    data = json.loads(result.stdout)
    parsed_result = json.loads(extract_json_from_result(data["result"]))
    usage = data.get("usage", {})
    input_tokens = (
        usage.get("input_tokens", 0)
        + usage.get("cache_creation_input_tokens", 0)
        + usage.get("cache_read_input_tokens", 0)
    )
    metrics = {
        "duration_ms": data.get("duration_ms", 0),
        "duration_api_ms": data.get("duration_api_ms", 0),
        "total_cost_usd": data.get("total_cost_usd", 0.0),
        "usage": {
            "input_tokens": input_tokens,
            "output_tokens": usage.get("output_tokens", 0),
        },
    }
    return {"result": parsed_result, "metrics": metrics}


def evaluate_scenario(
    scenario: dict,
    runner_output: dict,
    knowledge_dir: str,
    section_loader=None,
    deepeval_model=None,
) -> dict:
    """Evaluate a single scenario using DeepEval RAG metrics. Returns evaluation dict."""
    if section_loader is None:
        section_loader = load_section_content

    scenario_id = scenario["id"]

    tc = build_deepeval_test_case(scenario, runner_output, knowledge_dir, section_loader)
    scores = compute_deepeval_metrics(tc, model=deepeval_model)

    return {
        "scenario_id": scenario_id,
        "description": scenario.get("given", {}).get("description", ""),
        "input": scenario.get("when", {}).get("input", ""),
        "scores": scores,
        "diagnostics": {
            "search_sections": (
                runner_output.get("diagnostics", {}).get("search_sections", [])
                or [
                    f"{s['file']}:{s['section_id']}"
                    for s in (
                        runner_output.get("workflow_details", {})
                        .get("step3", {})
                        .get("selected_sections", [])
                    )
                    if s.get("file") and s.get("section_id")
                ]
            ),
        },
        "metrics": runner_output.get("metrics", {}),
    }


def evaluate_all(
    run_dir: str,
    scenarios_path: str,
    knowledge_dir: str,
) -> list[dict]:
    """Evaluate all scenarios in a run directory."""
    with open(scenarios_path, encoding="utf-8") as f:
        data = json.load(f)

    results = []
    for scenario in data["scenarios"]:
        sid = scenario["id"]
        try:
            runner_output = load_runner_output(run_dir, sid)
        except FileNotFoundError:
            continue
        evaluation = evaluate_scenario(scenario, runner_output, knowledge_dir)
        out_path = Path(run_dir) / sid / "evaluation.json"
        out_path.write_text(json.dumps(evaluation, ensure_ascii=False, indent=2), encoding="utf-8")
        results.append(evaluation)
    return results


def build_deepeval_test_case(
    scenario: dict,
    runner_output: dict,
    knowledge_dir: str,
    section_loader=None,
):
    """Build a DeepEval LLMTestCase from scenario and runner output.

    Mapping:
    - input: scenario["when"]["input"]
    - actual_output: runner_output["answer"]
    - expected_output: must.facts joined with newline
    - retrieval_context: section content for each ref in diagnostics.search_sections
    """
    from deepeval.test_case import LLMTestCase

    if section_loader is None:
        section_loader = load_section_content

    input_text = scenario.get("when", {}).get("input", "")
    actual_output = runner_output.get("answer", "")

    must_facts = scenario.get("then", {}).get("must", [])
    expected_output = "\n".join(mf["fact"] for mf in must_facts if mf.get("fact"))

    # Support two runner output formats:
    # 1. evaluation.json (post-evaluate): diagnostics.search_sections as "path/to/file.json:sN"
    # 2. run_qa output (pre-evaluate): workflow_details.step3.selected_sections as [{file, section_id}]
    search_section_refs: list[str] = []
    diag_sections = runner_output.get("diagnostics", {}).get("search_sections", [])
    if diag_sections:
        search_section_refs = diag_sections
    else:
        wf_sections = (
            runner_output.get("workflow_details", {})
            .get("step3", {})
            .get("selected_sections", [])
        )
        for s in wf_sections:
            file_path = s.get("file", "")
            section_id = s.get("section_id", "")
            if file_path and section_id:
                search_section_refs.append(f"{file_path}:{section_id}")

    seen_refs: set[str] = set()
    retrieval_context = []
    for ref in search_section_refs:
        if ref in seen_refs:
            continue
        seen_refs.add(ref)
        try:
            content = section_loader(knowledge_dir, ref)
            retrieval_context.append(content)
        except (FileNotFoundError, ValueError):
            pass

    return LLMTestCase(
        input=input_text,
        actual_output=actual_output,
        expected_output=expected_output,
        retrieval_context=retrieval_context,
    )


def _run_deepeval_metric(metric, test_case) -> dict:
    """Run a single DeepEval metric synchronously and return score + reason."""
    import asyncio
    asyncio.run(metric.a_measure(test_case))
    return {"score": metric.score, "reason": getattr(metric, "reason", "") or ""}


def compute_deepeval_metrics(test_case, model=None) -> dict:
    """Compute 3 DeepEval metrics: answer_correctness, answer_relevancy, faithfulness.

    Returns dict with float scores (0-1), or None per metric on failure.
    Uses AmazonBedrockModel with AWS_CA_BUNDLE for SSL if model is not provided.
    """
    from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric, GEval
    from deepeval.test_case import LLMTestCaseParams

    # aiobotocore (used by AmazonBedrockModel async calls) reads AWS_CA_BUNDLE for SSL verification.
    # Fall back to SSL_CERT_FILE when AWS_CA_BUNDLE is not set to avoid SSL errors in corp envs.
    if not os.environ.get("AWS_CA_BUNDLE") and os.environ.get("SSL_CERT_FILE"):
        os.environ["AWS_CA_BUNDLE"] = os.environ["SSL_CERT_FILE"]

    if model is None:
        from deepeval.models import AmazonBedrockModel
        model = AmazonBedrockModel(
            model=os.environ.get("BEDROCK_MODEL_ID", "jp.anthropic.claude-sonnet-4-6"),
            region=os.environ.get("AWS_REGION", "ap-northeast-1"),
        )

    metrics_config = [
        (
            "answer_correctness",
            lambda: GEval(
                name="AnswerCorrectness",
                criteria="The actual output covers all expected facts listed in expected_output.",
                evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
                model=model,
                async_mode=True,
            ),
        ),
        (
            "answer_relevancy",
            lambda: AnswerRelevancyMetric(model=model, async_mode=True),
        ),
        (
            "faithfulness",
            lambda: FaithfulnessMetric(model=model, async_mode=True),
        ),
    ]

    results = {}
    for key, metric_factory in metrics_config:
        try:
            metric = metric_factory()
            outcome = _run_deepeval_metric(metric, test_case)
            results[key] = {"score": float(outcome["score"]), "reason": outcome["reason"]}
        except Exception:
            results[key] = None
    return results


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate benchmark run results")
    parser.add_argument("--run-dir", required=True, help="Path to benchmark run directory")
    parser.add_argument("--scenarios", required=True, help="Path to scenarios JSON file")
    parser.add_argument("--knowledge-dir", required=True, help="Path to knowledge directory")
    args = parser.parse_args()

    results = evaluate_all(args.run_dir, args.scenarios, args.knowledge_dir)
    print(f"Evaluated {len(results)} scenarios", file=sys.stderr)


if __name__ == "__main__":
    main()

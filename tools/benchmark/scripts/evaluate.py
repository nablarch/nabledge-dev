"""Benchmark evaluation logic: C-claim judgment, hallucination detection, scoring."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

VALID_CLAIM_VERDICTS = {"PRESENT", "ABSENT", "UNCERTAIN"}
VALID_HALLUCINATION_VERDICTS = {"PASS", "FAIL", "UNCERTAIN"}

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

CLAIM_JSON_SCHEMA = json.dumps({
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": ["PRESENT", "ABSENT", "UNCERTAIN"]},
        "reason": {"type": "string"},
    },
    "required": ["verdict", "reason"],
})

HALLUCINATION_JSON_SCHEMA = json.dumps({
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": ["PASS", "FAIL", "UNCERTAIN"]},
        "claims": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "claim": {"type": "string"},
                    "supported": {"type": "boolean"},
                },
                "required": ["claim", "supported"],
            },
        },
        "reason": {"type": "string"},
    },
    "required": ["verdict", "claims", "reason"],
})


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


def calculate_accuracy_score(verdicts: list[dict]) -> float | None:
    """Calculate accuracy score: PRESENT count / total. Returns None if no verdicts or any UNCERTAIN.

    Design spec: UNCERTAIN-containing scenarios are excluded from aggregation (score=None).
    Returning None signals the caller to treat this scenario as unconfirmed.
    """
    if not verdicts:
        return None
    if any(v["verdict"] == "UNCERTAIN" for v in verdicts):
        return None
    present = sum(1 for v in verdicts if v["verdict"] == "PRESENT")
    return present / len(verdicts)


def calculate_hallucination_score(verdict: dict) -> int | None:
    """Calculate hallucination score: 1 for PASS, 0 for FAIL, None for UNCERTAIN."""
    v = verdict["verdict"]
    if v == "PASS":
        return 1
    if v == "FAIL":
        return 0
    return None


def determine_human_review_items(
    claim_verdicts: list[dict], hallucination_verdict: dict
) -> list[str]:
    """Determine items needing human review."""
    items = []
    for i, cv in enumerate(claim_verdicts):
        if cv["verdict"] in ("UNCERTAIN", "ABSENT"):
            items.append(f"claim[{i}]: {cv['verdict']} — {cv['fact']}")
    hv = hallucination_verdict["verdict"]
    if hv in ("FAIL", "UNCERTAIN"):
        items.append(f"hallucination: {hv} — {hallucination_verdict['reason']}")
    return items


def build_claim_prompt(fact: str, answer: str, section_content: str) -> str:
    """Build the C-claim judgment prompt."""
    template = (PROMPTS_DIR / "c-claim-judge.md").read_text(encoding="utf-8")
    return (
        template
        .replace("{fact}", fact)
        .replace("{answer}", answer)
        .replace("{section_content}", section_content)
    )


def build_hallucination_prompt(answer: str, sections_content: str) -> str:
    """Build the hallucination judgment prompt."""
    template = (PROMPTS_DIR / "hallucination-judge.md").read_text(encoding="utf-8")
    return (
        template
        .replace("{answer}", answer)
        .replace("{sections}", sections_content)
    )


def parse_claim_response(response: dict) -> dict:
    """Parse and validate a C-claim LLM response."""
    verdict = response.get("verdict")
    if verdict not in VALID_CLAIM_VERDICTS:
        raise ValueError(f"Invalid claim verdict: {verdict!r}")
    return {"verdict": verdict, "reason": response.get("reason", "")}


def parse_hallucination_response(response: dict) -> dict:
    """Parse and validate a hallucination LLM response."""
    verdict = response.get("verdict")
    if verdict not in VALID_HALLUCINATION_VERDICTS:
        raise ValueError(f"Invalid hallucination verdict: {verdict!r}")
    return {
        "verdict": verdict,
        "claims": response.get("claims", []),
        "reason": response.get("reason", ""),
    }


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
    llm_fn=None,
    section_loader=None,
    page_loader=None,
) -> dict:
    """Evaluate a single scenario. Returns evaluation dict."""
    if llm_fn is None:
        llm_fn = call_llm
    if section_loader is None:
        section_loader = load_section_content
    if page_loader is None:
        page_loader = load_page_content

    scenario_id = scenario["id"]
    answer = runner_output["answer"]
    must_facts = scenario["then"].get("must", [])
    acceptable = scenario["then"].get("acceptable", [])

    claim_verdicts = []
    for mf in must_facts:
        # out-of-scope scenarios have no section reference — use empty string
        section_ref = mf.get("section")
        section_content = section_loader(knowledge_dir, section_ref) if section_ref else ""
        prompt = build_claim_prompt(mf["fact"], answer, section_content)
        response = llm_fn(prompt, CLAIM_JSON_SCHEMA)
        parsed = parse_claim_response(response["result"])
        parsed["fact"] = mf["fact"]
        claim_verdicts.append(parsed)

    # Build sections_text for hallucination judge:
    # - must/acceptable refs: individual section content (for claim grounding)
    # - search results: full page content (all sections of each retrieved file),
    #   because the LLM sees the full file during Stage 2 section selection
    must_acceptable_refs = (
        [m["section"] for m in must_facts if m.get("section")]
        + [a["section"] for a in acceptable if a.get("section")]
    )
    seen_refs: set[str] = set()
    sections_content_parts = []
    for ref in must_acceptable_refs:
        if ref in seen_refs:
            continue
        seen_refs.add(ref)
        try:
            content = section_loader(knowledge_dir, ref)
            sections_content_parts.append(content)
        except (FileNotFoundError, ValueError):
            pass

    seen_files: set[str] = set()
    selected_pages = (
        runner_output.get("workflow_details", {})
        .get("step3", {})
        .get("selected_pages", [])
    )
    for page in selected_pages:
        file_path = page.get("path", "")
        if not file_path or file_path in seen_files:
            continue
        seen_files.add(file_path)
        try:
            content = page_loader(knowledge_dir, file_path)
            sections_content_parts.append(content)
        except (FileNotFoundError, ValueError):
            pass

    sections_text = "\n\n---\n\n".join(sections_content_parts) if sections_content_parts else ""

    h_prompt = build_hallucination_prompt(answer, sections_text)
    h_response = llm_fn(h_prompt, HALLUCINATION_JSON_SCHEMA)
    hallucination = parse_hallucination_response(h_response["result"])

    accuracy = calculate_accuracy_score(claim_verdicts)
    h_score = calculate_hallucination_score(hallucination)

    review_items = determine_human_review_items(claim_verdicts, hallucination)

    return {
        "scenario_id": scenario_id,
        "description": scenario.get("given", {}).get("description", ""),
        "input": scenario.get("when", {}).get("input", ""),
        "claim_verdicts": claim_verdicts,
        "hallucination": hallucination,
        "scores": {
            "accuracy": accuracy,
            "hallucination": h_score,
        },
        "needs_human_review": len(review_items) > 0,
        "human_review_items": review_items,
        "diagnostics": {
            "selected_pages": selected_pages,
            "selected_sections": (
                runner_output.get("workflow_details", {})
                .get("step3", {})
                .get("selected_sections", [])
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

    def llm_fn(prompt, schema):
        return call_llm(prompt, schema)

    results = []
    for scenario in data["scenarios"]:
        sid = scenario["id"]
        try:
            runner_output = load_runner_output(run_dir, sid)
        except FileNotFoundError:
            continue
        evaluation = evaluate_scenario(scenario, runner_output, knowledge_dir, llm_fn)
        out_path = Path(run_dir) / sid / "evaluation.json"
        out_path.write_text(json.dumps(evaluation, ensure_ascii=False, indent=2), encoding="utf-8")
        results.append(evaluation)
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

"""QA benchmark runner: executes qa.md skill workflow end-to-end via claude -p.

Runs the qa.md workflow for each scenario, capturing diagnostic markers from
the response to extract hearing, search, and answer information.

Output per scenario:
  {output-dir}/{scenario-id}/workflow_details.json — step3/step4/step8 details (pages, sections, answer sections)
  {output-dir}/{scenario-id}/answer.md             — generated answer text
  {output-dir}/{scenario-id}/metrics.json          — performance metrics
  {output-dir}/{scenario-id}/trace.json            — full claude -p JSON output (for QA review)
  {output-dir}/{scenario-id}/evaluation.json       — evaluation results
  {output-dir}/summary.json                        — run summary with context
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

_RESULTS_BASE = Path(__file__).parent.parent / "results"


def default_output_dir() -> Path:
    """Return a timestamped output directory under tools/benchmark/results/."""
    return _RESULTS_BASE / datetime.now().strftime("%Y%m%d-%H%M%S")

from tools.benchmark.scripts.evaluate import evaluate_scenario

WORKFLOW_FILE = "workflows/qa.md"
QA_PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "e2e-prompt.md"
TIMEOUT = 360

class MarkerError(ValueError):
    """Raised when a required benchmark marker is missing from the response.

    Carries the full claude output and raw response text so callers can save
    them for diagnosis.
    """

    def __init__(self, message: str, raw_response: str = "", claude_output: dict | None = None) -> None:
        super().__init__(message)
        self.raw_response = raw_response
        self.claude_output = claude_output



def _build_question(scenario: dict) -> str:
    """Build the question text, appending hearing_answer context when present."""
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


def build_qa_prompt(scenario: dict, workflow_content: str, prompt_template: str | None = None) -> str:
    """Build the E2E prompt from e2e-prompt.md template."""
    if prompt_template is None:
        prompt_template = QA_PROMPT_FILE.read_text(encoding="utf-8")
    question = _build_question(scenario)
    return prompt_template.replace("{workflow}", workflow_content).replace("{question}", question)


_QA_ANSWER_HEADING = "### Answer"
_QA_WORKFLOW_DETAILS_START = "<<<WORKFLOW_DETAILS_JSON>>>"
_QA_WORKFLOW_DETAILS_END = "<<<END_WORKFLOW_DETAILS>>>"


def parse_qa_response(response_text: str) -> dict:
    """Parse e2e-prompt.md formatted response.

    Expected format:
      ### Answer
      <answer text>

      <<<WORKFLOW_DETAILS_JSON>>>
      ```json
      {...}
      ```
      <<<END_WORKFLOW_DETAILS>>>

    The answer is extracted from between '### Answer' and '<<<WORKFLOW_DETAILS_JSON>>>'.
    If '### Answer' is absent (legacy format), all text before '<<<WORKFLOW_DETAILS_JSON>>>'
    is used as the answer.

    Raises ValueError if '<<<WORKFLOW_DETAILS_JSON>>>' or the JSON block is missing.
    """
    idx = response_text.find(_QA_WORKFLOW_DETAILS_START)
    if idx == -1:
        raise ValueError("<<<WORKFLOW_DETAILS_JSON>>> marker not found in response")

    before_workflow = response_text[:idx]

    answer_idx = before_workflow.find(_QA_ANSWER_HEADING)
    if answer_idx != -1:
        answer = before_workflow[answer_idx + len(_QA_ANSWER_HEADING):].strip()
    else:
        answer = before_workflow.strip()

    details_section = response_text[idx + len(_QA_WORKFLOW_DETAILS_START):]

    # Extract JSON: between start marker and end marker (if present), else use fence
    end_idx = details_section.find(_QA_WORKFLOW_DETAILS_END)
    if end_idx != -1:
        details_section = details_section[:end_idx]

    fence_start = details_section.find("```json")
    fence_end = details_section.find("```", fence_start + 3) if fence_start != -1 else -1
    if fence_start == -1 or fence_end == -1:
        json_raw = details_section.strip()
    else:
        json_raw = details_section[fence_start + len("```json"):fence_end].strip()

    try:
        workflow_details = json.loads(json_raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in workflow details: {e}") from e

    return {
        "answer": answer,
        "workflow_details": workflow_details,
    }


def _extract_metrics(claude_output: dict) -> dict:
    """Extract performance metrics from claude -p JSON output."""
    usage = claude_output.get("usage", {})
    return {
        "duration_ms": claude_output.get("duration_ms", 0),
        "duration_api_ms": claude_output.get("duration_api_ms", 0),
        "num_turns": claude_output.get("num_turns", 0),
        "total_cost_usd": claude_output.get("total_cost_usd", 0.0),
        "usage": {
            "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
            "cache_read_input_tokens": usage.get("cache_read_input_tokens", 0),
            "cache_creation_input_tokens": usage.get("cache_creation_input_tokens", 0),
        },
        "model_usage": claude_output.get("modelUsage", {}),
    }


def save_qa_results(output_dir: str | Path, scenario_id: str, data: dict) -> None:
    """Save E2E scenario results."""
    scenario_dir = Path(output_dir) / scenario_id
    scenario_dir.mkdir(parents=True, exist_ok=True)

    (scenario_dir / "workflow_details.json").write_text(
        json.dumps(data["workflow_details"], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (scenario_dir / "answer.md").write_text(data["answer"], encoding="utf-8")
    (scenario_dir / "metrics.json").write_text(
        json.dumps(data["metrics"], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (scenario_dir / "trace.json").write_text(
        json.dumps(data["trace"], ensure_ascii=False, indent=2), encoding="utf-8"
    )


def run_qa_scenario(
    scenario: dict,
    skill_dir: str | Path,
) -> dict:
    """Run a single scenario through the skill workflow end-to-end.

    Injects hearing_answer context when scenario["when"]["hearing_answer"] is not None.

    Returns:
        Dict with scenario_id, hearing, search, answer, metrics, trace.

    Raises:
        RuntimeError: If claude subprocess exits with non-zero return code.
        ValueError: If response is missing required benchmark markers.
    """
    skill_dir = Path(skill_dir)
    workflow_content = (skill_dir / WORKFLOW_FILE).read_text(encoding="utf-8")
    prompt = build_qa_prompt(scenario, workflow_content)

    proc = subprocess.run(
        [
            "claude", "-p",
            "--model", "sonnet",
            "--output-format", "json",
            "--no-session-persistence",
            "--allowedTools", "Bash(bash scripts/keyword-search.sh *) Bash(bash scripts/bm25-search.sh *) Bash(bash scripts/read-sections.sh *) Read",
        ],
        input=prompt,
        capture_output=True,
        text=True,
        cwd=str(skill_dir),
        timeout=TIMEOUT,
    )

    if proc.returncode != 0:
        raise RuntimeError(
            f"claude exited with code {proc.returncode}: {proc.stderr[:500]}"
        )

    claude_output = json.loads(proc.stdout)
    result_text = claude_output.get("result", "")

    try:
        parsed = parse_qa_response(result_text)
    except ValueError as exc:
        raise MarkerError(str(exc), raw_response=result_text, claude_output=claude_output) from exc
    metrics = _extract_metrics(claude_output)

    return {
        "scenario_id": scenario["id"],
        "workflow_details": parsed["workflow_details"],
        "answer": parsed["answer"],
        "metrics": metrics,
        "trace": claude_output,
    }


def run_qa_all(
    scenarios_path: str,
    skill_dir: str | Path,
    output_dir: str | Path | None = None,
    scenario_ids: list[str] | None = None,
) -> dict:
    """Run all scenarios end-to-end and save results.

    Args:
        scenarios_path: Path to scenarios JSON file.
        skill_dir: Path to the skill directory.
        output_dir: Directory to save results (default: tools/benchmark/results/YYYYMMDD-HHMMSS/).
        scenario_ids: Optional list of scenario IDs to run (runs all if None).

    Returns:
        Summary dict with total_scenarios, skill_dir, scenarios_file, executed_at, and per-scenario info.
    """
    skill_dir = Path(skill_dir)
    knowledge_dir = str(skill_dir / "knowledge")
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
            result = run_qa_scenario(scenario, skill_dir)
            save_qa_results(str(out), sid, result)

            evaluation = evaluate_scenario(scenario, result, knowledge_dir)
            (out / sid / "evaluation.json").write_text(
                json.dumps(evaluation, ensure_ascii=False, indent=2), encoding="utf-8"
            )

            wd = result["workflow_details"]
            sections_used = (
                wd.get("step5", {}).get("sections_used")
                or wd.get("step2", {}).get("bm25_sections")
                or wd.get("step4", {}).get("selected_sections")
                or []
            )
            scenario_summaries.append({
                "id": result["scenario_id"],
                "search_sections": len(sections_used),
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
            if isinstance(exc, MarkerError):
                if exc.claude_output is not None:
                    (error_dir / "trace.json").write_text(
                        json.dumps(exc.claude_output, ensure_ascii=False, indent=2), encoding="utf-8"
                    )
                if exc.raw_response:
                    (error_dir / "raw_response.txt").write_text(exc.raw_response, encoding="utf-8")
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
        description="Run QA benchmark: qa.md skill workflow end-to-end"
    )
    parser.add_argument("--scenarios", required=True, help="Path to scenarios JSON")
    parser.add_argument("--skill-dir", required=True, help="Path to skill directory")
    parser.add_argument("--scenario-ids", help="Comma-separated scenario IDs to run")
    args = parser.parse_args()

    scenario_ids = args.scenario_ids.split(",") if args.scenario_ids else None
    output_dir = default_output_dir()
    print(f"Output dir: {output_dir}", file=sys.stderr)

    summary = run_qa_all(
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
            sections = s["search_sections"]
            print(f"  {s['id']}: {sections} sections selected", file=sys.stderr)


if __name__ == "__main__":
    main()

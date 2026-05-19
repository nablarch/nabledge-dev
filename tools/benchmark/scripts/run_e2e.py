"""E2E benchmark runner: executes skill workflow end-to-end via claude -p.

Runs the qa.md workflow for each scenario, capturing diagnostic markers from
the response to extract hearing, search, and answer information.

Output per scenario:
  {output-dir}/{scenario-id}/hearing.json    — hearing behavior (skipped or asked)
  {output-dir}/{scenario-id}/search.json     — search results (section IDs)
  {output-dir}/{scenario-id}/answer.md       — generated answer text
  {output-dir}/{scenario-id}/metrics.json    — performance metrics
  {output-dir}/{scenario-id}/trace.json      — full claude -p JSON output (for QA review)
  {output-dir}/{scenario-id}/evaluation.json — evaluation results
  {output-dir}/summary.json                  — run summary with context
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


MARKER_HEARING_START = "<<<BENCHMARK_HEARING>>>"
MARKER_HEARING_END = "<<<END_BENCHMARK_HEARING>>>"
MARKER_SEARCH_START = "<<<BENCHMARK_SEARCH>>>"
MARKER_SEARCH_END = "<<<END_BENCHMARK_SEARCH>>>"
MARKER_ANSWER_START = "<<<BENCHMARK_ANSWER>>>"
MARKER_ANSWER_END = "<<<END_BENCHMARK_ANSWER>>>"


def _extract_between_markers(text: str, start_marker: str, end_marker: str) -> str:
    """Extract text between start and end markers. Raises ValueError if not found."""
    start_idx = text.find(start_marker)
    if start_idx == -1:
        raise ValueError(f"Marker not found in response: {start_marker}")
    end_idx = text.find(end_marker, start_idx)
    if end_idx == -1:
        raise ValueError(f"End marker not found in response: {end_marker}")
    return text[start_idx + len(start_marker):end_idx].strip()


def build_e2e_prompt(scenario: dict, workflow_content: str) -> str:
    """Build the E2E prompt that instructs the model to follow qa.md.

    Injects hearing_answer context when scenario["when"]["hearing_answer"] is not None.
    """
    question = scenario["when"]["input"]
    hearing_answer = scenario["when"].get("hearing_answer")

    if hearing_answer is not None:
        hearing_section = (
            f"\n## コンテキスト（ヒアリング結果）\n"
            f"処理方式: {hearing_answer.get('processing_type', '')}\n"
            f"目的: {hearing_answer.get('goal', '')}\n\n"
            f"ヒアリング結果が提供されている場合、ワークフローのヒアリングステップはスキップして検索から開始してください。\n"
        )
    else:
        hearing_section = ""

    return f"""以下のワークフロー（qa.md）に従って質問に回答してください。

## ワークフロー
{workflow_content}

## 質問
{question}
{hearing_section}
## 出力要件

回答を出力した後、以下のマーカー形式でベンチマーク診断情報を出力してください。全マーカーの出力は必須です。

{MARKER_HEARING_START}
{{"status": "skipped" または "asked", "questions": ["質問1", "質問2"]}}
{MARKER_HEARING_END}

{MARKER_SEARCH_START}
{{"section_ids": ["path/to/file.json:s1", "path/to/file.json:s3"]}}
{MARKER_SEARCH_END}

{MARKER_ANSWER_START}
回答テキスト全文をここに出力
{MARKER_ANSWER_END}
"""


def parse_e2e_response(response_text: str) -> dict:
    """Parse structured benchmark markers from the workflow response.

    Raises ValueError if any required marker is missing.
    """
    hearing_raw = _extract_between_markers(
        response_text, MARKER_HEARING_START, MARKER_HEARING_END
    )
    search_raw = _extract_between_markers(
        response_text, MARKER_SEARCH_START, MARKER_SEARCH_END
    )
    answer_text = _extract_between_markers(
        response_text, MARKER_ANSWER_START, MARKER_ANSWER_END
    )

    try:
        hearing = json.loads(hearing_raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in BENCHMARK_HEARING: {e}") from e

    try:
        search = json.loads(search_raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in BENCHMARK_SEARCH: {e}") from e

    return {
        "hearing": hearing,
        "search": search,
        "answer": answer_text,
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


def save_e2e_results(output_dir: str | Path, scenario_id: str, data: dict) -> None:
    """Save E2E scenario results."""
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
    (scenario_dir / "trace.json").write_text(
        json.dumps(data["trace"], ensure_ascii=False, indent=2), encoding="utf-8"
    )


def run_e2e_scenario(
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
    prompt = build_e2e_prompt(scenario, workflow_content)

    proc = subprocess.run(
        [
            "claude", "-p",
            "--model", "sonnet",
            "--output-format", "json",
            "--no-session-persistence",
            "--allowedTools", "Bash(keyword-search.sh *) Bash(read-sections.sh *) Read",
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
        parsed = parse_e2e_response(result_text)
    except ValueError as exc:
        raise MarkerError(str(exc), raw_response=result_text, claude_output=claude_output) from exc
    metrics = _extract_metrics(claude_output)

    return {
        "scenario_id": scenario["id"],
        "hearing": parsed["hearing"],
        "search": parsed["search"],
        "answer": parsed["answer"],
        "metrics": metrics,
        "trace": claude_output,
    }


def run_e2e_all(
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
            result = run_e2e_scenario(scenario, skill_dir)
            save_e2e_results(str(out), sid, result)

            evaluation = evaluate_scenario(scenario, result, knowledge_dir)
            (out / sid / "evaluation.json").write_text(
                json.dumps(evaluation, ensure_ascii=False, indent=2), encoding="utf-8"
            )

            scenario_summaries.append({
                "id": result["scenario_id"],
                "search_sections": len(result["search"]["section_ids"]),
                "hearing_status": result["hearing"].get("status", "unknown"),
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
        description="Run E2E QA benchmark: skill workflow end-to-end"
    )
    parser.add_argument("--scenarios", required=True, help="Path to scenarios JSON")
    parser.add_argument("--skill-dir", required=True, help="Path to skill directory")
    parser.add_argument("--scenario-ids", help="Comma-separated scenario IDs to run")
    args = parser.parse_args()

    scenario_ids = args.scenario_ids.split(",") if args.scenario_ids else None
    output_dir = default_output_dir()
    print(f"Output dir: {output_dir}", file=sys.stderr)

    summary = run_e2e_all(
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
            hearing = s["hearing_status"]
            print(f"  {s['id']}: {sections} sections found, hearing={hearing}", file=sys.stderr)


if __name__ == "__main__":
    main()

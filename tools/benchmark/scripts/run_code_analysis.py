"""Code analysis benchmark runner: executes code-analysis.md skill workflow end-to-end via claude -p.

Runs the code-analysis.md workflow for each scenario, capturing diagnostic markers from
the response to extract step1/step2 details and the generated documentation.

Output per scenario:
  {output-dir}/{scenario-id}/answer.md             — generated documentation text
  {output-dir}/{scenario-id}/code_analysis_details.json — step1/step2 details (files, dependencies, sections)
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

WORKFLOW_FILE = "workflows/code-analysis.md"
TEMPLATE_FILE = "workflows/code-analysis/template.md"
TEMPLATE_GUIDE_FILE = "workflows/code-analysis/template-guide.md"
CODE_ANALYSIS_E2E_PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "code-analysis-e2e-prompt.md"
TIMEOUT = 600


class MarkerError(ValueError):
    """Raised when a required benchmark marker is missing from the response.

    Carries the full claude output and raw response text so callers can save
    them for diagnosis.
    """

    def __init__(self, message: str, raw_response: str = "", claude_output: dict | None = None) -> None:
        super().__init__(message)
        self.raw_response = raw_response
        self.claude_output = claude_output


def build_code_analysis_prompt(
    scenario: dict,
    workflow_content: str,
    template_content: str,
    template_guide_content: str,
    prompt_template: str | None = None,
) -> str:
    """Build the E2E prompt from code-analysis-e2e-prompt.md template.

    Fills {workflow}, {template}, {template_guide}, and {target_class}
    from the scenario's when.input field.
    """
    if prompt_template is None:
        prompt_template = CODE_ANALYSIS_E2E_PROMPT_FILE.read_text(encoding="utf-8")
    target_class = scenario["when"]["input"]
    return (
        prompt_template
        .replace("{workflow}", workflow_content)
        .replace("{template}", template_content)
        .replace("{template_guide}", template_guide_content)
        .replace("{target_class}", target_class)
    )


_CA_ANSWER_HEADING = "### Answer"
_CA_DETAILS_START = "<<<CODE_ANALYSIS_DETAILS_JSON>>>"
_CA_DETAILS_END = "<<<END_CODE_ANALYSIS_DETAILS>>>"


def parse_code_analysis_response(response_text: str) -> dict:
    """Parse code-analysis-e2e-prompt.md formatted response.

    Expected format:
      ### Answer
      <complete documentation>

      <<<CODE_ANALYSIS_DETAILS_JSON>>>
      ```json
      {...}
      ```
      <<<END_CODE_ANALYSIS_DETAILS>>>

    The answer is extracted from between '### Answer' and '<<<CODE_ANALYSIS_DETAILS_JSON>>>'.

    Returns dict with keys 'answer' and 'code_analysis_details'.

    Raises MarkerError if '<<<CODE_ANALYSIS_DETAILS_JSON>>>' or the JSON block is missing.
    """
    idx = response_text.find(_CA_DETAILS_START)
    if idx == -1:
        raise MarkerError("<<<CODE_ANALYSIS_DETAILS_JSON>>> marker not found in response")

    before_details = response_text[:idx]

    answer_idx = before_details.find(_CA_ANSWER_HEADING)
    if answer_idx != -1:
        answer = before_details[answer_idx + len(_CA_ANSWER_HEADING):].strip()
    else:
        answer = before_details.strip()

    details_section = response_text[idx + len(_CA_DETAILS_START):]

    # Extract JSON: between start marker and end marker (if present), else use fence
    end_idx = details_section.find(_CA_DETAILS_END)
    if end_idx != -1:
        details_section = details_section[:end_idx]

    fence_start = details_section.find("```json")
    fence_end = details_section.find("```", fence_start + 3) if fence_start != -1 else -1
    if fence_start == -1 or fence_end == -1:
        json_raw = details_section.strip()
    else:
        json_raw = details_section[fence_start + len("```json"):fence_end].strip()

    try:
        code_analysis_details = json.loads(json_raw)
    except json.JSONDecodeError as e:
        raise MarkerError(f"Invalid JSON in code analysis details: {e}") from e

    return {
        "answer": answer,
        "code_analysis_details": code_analysis_details,
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


def save_code_analysis_results(output_dir: str | Path, scenario_id: str, data: dict) -> None:
    """Save code analysis scenario results.

    Creates {output_dir}/{scenario_id}/ and writes:
      answer.md, code_analysis_details.json, metrics.json, trace.json
    """
    scenario_dir = Path(output_dir) / scenario_id
    scenario_dir.mkdir(parents=True, exist_ok=True)

    (scenario_dir / "answer.md").write_text(data["answer"], encoding="utf-8")
    (scenario_dir / "code_analysis_details.json").write_text(
        json.dumps(data["code_analysis_details"], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (scenario_dir / "metrics.json").write_text(
        json.dumps(data["metrics"], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (scenario_dir / "trace.json").write_text(
        json.dumps(data["trace"], ensure_ascii=False, indent=2), encoding="utf-8"
    )


def run_code_analysis_scenario(
    scenario: dict,
    skill_dir: str | Path,
    project_dir: str | Path | None = None,
) -> dict:
    """Run a single code-analysis scenario through the skill workflow end-to-end.

    Args:
        scenario: Scenario dict with id, given, when, then fields.
        skill_dir: Path to the skill directory (contains workflows/, scripts/).
        project_dir: Root directory to run claude from so find-file.sh can locate
                     Java source files. Defaults to parent of skill_dir.

    Returns:
        Dict with scenario_id, code_analysis_details, answer, metrics, trace.

    Raises:
        RuntimeError: If claude subprocess exits with non-zero return code.
        MarkerError: If response is missing required benchmark markers.
    """
    skill_dir = Path(skill_dir)
    if project_dir is None:
        project_dir = skill_dir.parent
    project_dir = Path(project_dir)

    workflow_content = (skill_dir / WORKFLOW_FILE).read_text(encoding="utf-8")
    template_content = (skill_dir / TEMPLATE_FILE).read_text(encoding="utf-8")
    template_guide_content = (skill_dir / TEMPLATE_GUIDE_FILE).read_text(encoding="utf-8")
    prompt = build_code_analysis_prompt(scenario, workflow_content, template_content, template_guide_content)

    # Determine the cwd for the claude invocation.
    # When project_subdir is set, narrow the search root to that subdir so
    # find-file.sh does not pick up the wrong file when the same class name
    # exists in multiple sub-projects (e.g. ProjectAction in both
    # nablarch-example-rest and nablarch-example-web).
    project_subdir = scenario["when"].get("project_subdir")
    if project_subdir:
        cwd = str(project_dir / project_subdir)
        # Scripts are specified relative to cwd in the default case, but when
        # cwd is a sub-directory the relative path ".claude/skills/..." would
        # not resolve.  Use the absolute path derived from skill_dir instead.
        scripts_dir = str(skill_dir.resolve() / "scripts")
        allowed_tools = (
            f"Bash(bash {scripts_dir}/find-file.sh *) "
            f"Bash(bash {scripts_dir}/read-file.sh *) "
            f"Bash(bash {scripts_dir}/keyword-search.sh *) "
            f"Bash(bash {scripts_dir}/read-sections.sh *) "
            "Read"
        )
    else:
        cwd = str(project_dir)
        allowed_tools = (
            "Bash(bash .claude/skills/nabledge-6/scripts/find-file.sh *) "
            "Bash(bash .claude/skills/nabledge-6/scripts/read-file.sh *) "
            "Bash(bash .claude/skills/nabledge-6/scripts/keyword-search.sh *) "
            "Bash(bash .claude/skills/nabledge-6/scripts/read-sections.sh *) "
            "Read"
        )

    proc = subprocess.run(
        [
            "claude", "-p",
            "--model", "sonnet",
            "--output-format", "json",
            "--no-session-persistence",
            "--allowedTools",
            allowed_tools,
        ],
        input=prompt,
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=TIMEOUT,
    )

    if proc.returncode != 0:
        raise RuntimeError(
            f"claude exited with code {proc.returncode}: {proc.stderr[:500]}"
        )

    claude_output = json.loads(proc.stdout)
    result_text = claude_output.get("result", "")

    try:
        parsed = parse_code_analysis_response(result_text)
    except MarkerError as exc:
        # Attach claude_output so callers can save trace and raw_response for diagnosis
        raise MarkerError(str(exc), raw_response=result_text, claude_output=claude_output) from exc

    metrics = _extract_metrics(claude_output)

    return {
        "scenario_id": scenario["id"],
        "code_analysis_details": parsed["code_analysis_details"],
        "answer": parsed["answer"],
        "metrics": metrics,
        "trace": claude_output,
    }


def run_code_analysis_all(
    scenarios_path: str,
    skill_dir: str | Path,
    project_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
    scenario_ids: list[str] | None = None,
) -> dict:
    """Run all code-analysis scenarios end-to-end and save results.

    Args:
        scenarios_path: Path to scenarios JSON file.
        skill_dir: Path to the skill directory.
        project_dir: Root directory for claude invocation. Defaults to parent of skill_dir.
        output_dir: Directory to save results (default: tools/benchmark/results/YYYYMMDD-HHMMSS/).
        scenario_ids: Optional list of scenario IDs to run (runs all if None).

    Returns:
        Summary dict with total_scenarios, skill_dir, scenarios_file, executed_at, and per-scenario info.
    """
    skill_dir = Path(skill_dir)
    if project_dir is None:
        project_dir = skill_dir.parent
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
            result = run_code_analysis_scenario(scenario, skill_dir, project_dir)
            save_code_analysis_results(str(out), sid, result)

            # evaluate_scenario expects retrieval_context from knowledge sections,
            # but code-analysis derives facts from source code, not knowledge JSON.
            # Pass knowledge_dir=None and use empty retrieval_context via a patched call.
            _runner_output_with_empty_sections = {
                **result,
                "workflow_details": {
                    "step3": {"selected_sections": []},
                },
            }
            evaluation = evaluate_scenario(
                scenario,
                _runner_output_with_empty_sections,
                knowledge_dir=str(skill_dir / "knowledge"),
                section_loader=lambda _kdir, _ref: "",
            )
            (out / sid / "evaluation.json").write_text(
                json.dumps(evaluation, ensure_ascii=False, indent=2), encoding="utf-8"
            )

            scenario_summaries.append({
                "id": result["scenario_id"],
                "status": "ok",
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
        "project_dir": str(project_dir),
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
        description="Run code-analysis benchmark: code-analysis.md skill workflow end-to-end"
    )
    parser.add_argument("--scenarios", required=True, help="Path to scenarios JSON")
    parser.add_argument("--skill-dir", required=True, help="Path to skill directory")
    parser.add_argument(
        "--project-dir",
        help="Root directory to run claude from (default: parent of skill-dir)",
    )
    parser.add_argument("--scenario-ids", help="Comma-separated scenario IDs to run")
    parser.add_argument("--output-dir", help="Directory to save results (default: results/YYYYMMDD-HHMMSS/)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Load scenarios and print them, then exit 0 without running claude",
    )
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir)
    project_dir = Path(args.project_dir) if args.project_dir else skill_dir.parent

    # Validate scenarios file exists and is loadable
    with open(args.scenarios, encoding="utf-8") as f:
        scenarios_data = json.load(f)

    if args.dry_run:
        print(f"Scenarios file: {args.scenarios}", file=sys.stderr)
        print(f"Skill dir: {skill_dir}", file=sys.stderr)
        print(f"Project dir: {project_dir}", file=sys.stderr)
        print(f"Scenarios ({len(scenarios_data['scenarios'])}):", file=sys.stderr)
        for s in scenarios_data["scenarios"]:
            print(f"  {s['id']}: {s['when']['input']}", file=sys.stderr)
        sys.exit(0)

    scenario_ids = args.scenario_ids.split(",") if args.scenario_ids else None
    output_dir = Path(args.output_dir) if args.output_dir else default_output_dir()
    print(f"Output dir: {output_dir}", file=sys.stderr)

    summary = run_code_analysis_all(
        args.scenarios,
        skill_dir,
        project_dir=project_dir,
        output_dir=str(output_dir),
        scenario_ids=scenario_ids,
    )

    print(f"\nCompleted: {summary['total_scenarios']} scenarios", file=sys.stderr)
    for s in summary["scenarios"]:
        if s.get("status") == "error":
            print(f"  {s['id']}: ERROR — {s.get('error', '')}", file=sys.stderr)
        else:
            print(f"  {s['id']}: OK", file=sys.stderr)


if __name__ == "__main__":
    main()

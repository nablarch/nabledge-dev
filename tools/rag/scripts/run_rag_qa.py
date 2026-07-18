"""RAG QA runner: retrieves top-k sections via Qdrant and answers using LLM.

Produces the same output structure as tools/benchmark/scripts/run_qa.py:
  {output-dir}/{scenario-id}/workflow_details.json
  {output-dir}/{scenario-id}/answer.md
  {output-dir}/{scenario-id}/metrics.json
  {output-dir}/{scenario-id}/evaluation.json
  {output-dir}/summary.json

Usage:
    python3 -m tools.rag.scripts.run_rag_qa \
        --scenarios tools/benchmark/scenarios/qa.json \
        --knowledge-dir .claude/skills/nabledge-6/knowledge \
        --scenario-ids pre-01
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from tools.rag.scripts.query import (
    QueryResult,
    query as rag_query,
    DEFAULT_EMBED_MODEL_ID,
    DEFAULT_TOP_K,
    QDRANT_HOST,
    QDRANT_PORT,
)
from tools.benchmark.scripts.evaluate import evaluate_scenario

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_RESULTS_BASE = Path(__file__).parent.parent.parent / "benchmark" / "results"
_TIMEOUT = 360  # seconds for LLM call

# Mapping from hearing_answer.processing_type (Japanese display name) to Qdrant slug
_PROCESSING_TYPE_MAP: dict[str, str] = {
    "Nablarchバッチ": "nablarch-batch",
    "ウェブアプリケーション": "web-application",
    "RESTfulウェブサービス": "restful-web-service",
    "Jakartaバッチ": "jakarta-batch",
    "テーブルをキューとして使ったメッセージング": "db-messaging",
    "HTTPメッセージング": "http-messaging",
    "MOMメッセージング": "mom-messaging",
}

# RAG prompt: passes retrieved sections as context, outputs in e2e-prompt.md format
_RAG_PROMPT_TEMPLATE = """\
以下のナレッジセクションを参考に、質問に回答してください。

## 参照セクション

{context}

## 回答の形式（厳守）

以下の形式で出力してください。コードフェンス・説明文は形式通りに出力し、マーカー行は一字一句変更しないこと。

### Answer
（日本語で回答してください。回答には参照したセクションの情報を具体的に含めること。）

<<<WORKFLOW_DETAILS_JSON>>>
```json
{workflow_details_template}
```
<<<END_WORKFLOW_DETAILS>>>

## 質問

{question}
"""

# ---------------------------------------------------------------------------
# Processing-type helper
# ---------------------------------------------------------------------------

def resolve_processing_type_slug(hearing_answer: dict | None) -> str | None:
    """Map hearing_answer.processing_type (Japanese) to Qdrant slug.

    Args:
        hearing_answer: The scenario's hearing_answer dict, or None.

    Returns:
        Slug string (e.g. "nablarch-batch") or None if not mappable.
    """
    if hearing_answer is None:
        return None
    pt = hearing_answer.get("processing_type", "")
    return _PROCESSING_TYPE_MAP.get(pt)


# ---------------------------------------------------------------------------
# Prompt building
# ---------------------------------------------------------------------------

def build_rag_prompt(
    question: str,
    results: list[QueryResult],
    knowledge_dir: Path,
) -> str:
    """Build the RAG prompt from retrieved sections.

    Loads each section's content from the knowledge directory and injects it
    as context. The prompt outputs in the same e2e-prompt.md format.

    Args:
        question: The user question.
        results: Top-k QueryResult objects from Qdrant.
        knowledge_dir: Path to the knowledge root directory.

    Returns:
        Prompt string ready to be sent to the LLM.
    """
    context_parts: list[str] = []
    for r in results:
        file_full_path = knowledge_dir / r.file_path
        section_content = ""
        try:
            page_data = json.loads(file_full_path.read_text(encoding="utf-8"))
            for sec in page_data.get("sections", []):
                if sec.get("id") == r.section_id:
                    section_content = sec.get("content", "")
                    break
        except (OSError, json.JSONDecodeError):
            section_content = f"(content unavailable: {r.file_path})"

        context_parts.append(
            f"### {r.section_ref}\n"
            f"**{r.title}**\n\n"
            f"{section_content}"
        )

    context = "\n\n---\n\n".join(context_parts)

    # Build the workflow_details template that the LLM must fill in
    selected_sections_template = [
        {
            "file": r.file_path,
            "section_id": r.section_id,
            "relevance": "high",
            "reason": "RAG top-k result",
        }
        for r in results
    ]
    read_sections_template = [r.section_ref for r in results]

    workflow_details_template = json.dumps(
        {
            "step3": {
                "selected_sections": selected_sections_template,
            },
            "step4": {
                "read_sections": read_sections_template,
            },
            "step8": {
                "answer_sections": {
                    "used": [],
                    "unused": [],
                }
            },
        },
        ensure_ascii=False,
        indent=2,
    )

    return _RAG_PROMPT_TEMPLATE.format(
        context=context,
        workflow_details_template=workflow_details_template,
        question=question,
    )


# ---------------------------------------------------------------------------
# LLM call
# ---------------------------------------------------------------------------

def call_llm(prompt: str) -> dict:
    """Call claude CLI with the RAG prompt.

    Args:
        prompt: The full prompt to send.

    Returns:
        Parsed claude -p JSON output dict.

    Raises:
        RuntimeError: If claude exits with non-zero code.
    """
    try:
        proc = subprocess.run(
            [
                "claude", "-p",
                "--model", "sonnet",
                "--output-format", "json",
                "--no-session-persistence",
            ],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=_TIMEOUT,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            f"claude timed out after {_TIMEOUT}s"
        ) from exc
    if proc.returncode != 0:
        raise RuntimeError(
            f"claude exited with code {proc.returncode}: {proc.stderr[:500]}"
        )
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"claude output is not valid JSON: {proc.stdout[:200]!r}"
        ) from exc


# ---------------------------------------------------------------------------
# Response parsing (reuses run_qa.py's format)
# ---------------------------------------------------------------------------

_ANSWER_HEADING = "### Answer"
_WORKFLOW_DETAILS_START = "<<<WORKFLOW_DETAILS_JSON>>>"
_WORKFLOW_DETAILS_END = "<<<END_WORKFLOW_DETAILS>>>"


def parse_rag_response(response_text: str, fallback_results: list[QueryResult]) -> dict:
    """Parse the LLM response that follows the e2e-prompt.md output format.

    Falls back to the RAG-retrieved sections if the LLM omits the JSON block
    or returns malformed JSON.

    Args:
        response_text: Raw text from claude result field.
        fallback_results: QueryResult list used as fallback workflow_details.

    Returns:
        Dict with "answer" (str) and "workflow_details" (dict) keys.
    """
    idx = response_text.find(_WORKFLOW_DETAILS_START)
    if idx == -1:
        # Fallback: use full response as answer, build workflow_details from RAG results
        return {
            "answer": response_text.strip(),
            "workflow_details": _build_fallback_workflow_details(fallback_results),
        }

    before_workflow = response_text[:idx]
    answer_idx = before_workflow.find(_ANSWER_HEADING)
    if answer_idx != -1:
        answer = before_workflow[answer_idx + len(_ANSWER_HEADING):].strip()
    else:
        answer = before_workflow.strip()

    details_section = response_text[idx + len(_WORKFLOW_DETAILS_START):]
    end_idx = details_section.find(_WORKFLOW_DETAILS_END)
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
    except json.JSONDecodeError:
        workflow_details = _build_fallback_workflow_details(fallback_results)

    return {"answer": answer, "workflow_details": workflow_details}


def _build_fallback_workflow_details(results: list[QueryResult]) -> dict:
    """Build workflow_details from RAG results when LLM output is unavailable."""
    return {
        "step3": {
            "selected_sections": [r.as_selected_section() for r in results],
        },
        "step4": {
            "read_sections": [r.section_ref for r in results],
        },
        "step8": {
            "answer_sections": {"used": [], "unused": []},
        },
    }


# ---------------------------------------------------------------------------
# Metrics extraction
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Output directory
# ---------------------------------------------------------------------------

def default_output_dir(k: int, has_filter: bool) -> Path:
    """Return a timestamped RAG output directory."""
    filter_suffix = "filter" if has_filter else "nofilter"
    label = datetime.now().strftime(f"%Y%m%d-%H%M-rag-k{k}-{filter_suffix}")
    return _RESULTS_BASE / label


# ---------------------------------------------------------------------------
# Save results
# ---------------------------------------------------------------------------

def save_rag_results(output_dir: Path, scenario_id: str, data: dict) -> None:
    """Save RAG scenario results in run_qa.py-compatible format."""
    scenario_dir = output_dir / scenario_id
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


# ---------------------------------------------------------------------------
# Single scenario
# ---------------------------------------------------------------------------

def run_rag_scenario(
    scenario: dict,
    knowledge_dir: Path,
    k: int = DEFAULT_TOP_K,
    model_id: str = DEFAULT_EMBED_MODEL_ID,
    use_filter: bool = True,
    qdrant_host: str = QDRANT_HOST,
    qdrant_port: int = QDRANT_PORT,
    verify_ssl: bool = True,
) -> dict:
    """Run a single scenario through the RAG pipeline.

    Args:
        scenario: Scenario dict (from qa.json).
        knowledge_dir: Path to knowledge root directory.
        k: Number of top-k sections to retrieve.
        model_id: Bedrock Cohere Embed model ID.
        use_filter: Whether to apply processing_type metadata filter.
        qdrant_host: Qdrant host.
        qdrant_port: Qdrant port.
        verify_ssl: Whether to verify SSL certificates.

    Returns:
        Dict with scenario_id, workflow_details, answer, metrics, trace.
    """
    from qdrant_client import QdrantClient  # noqa: PLC0415

    question_base = scenario["when"]["input"]
    hearing_answer = scenario["when"].get("hearing_answer")

    # Append hearing context to question (same as run_qa.py)
    question_parts = [question_base]
    if hearing_answer:
        if hearing_answer.get("processing_type"):
            question_parts.append(f"（処理方式: {hearing_answer['processing_type']}）")
        if hearing_answer.get("purpose"):
            question_parts.append(f"（目的: {hearing_answer['purpose']}）")
    question = "".join(question_parts)

    # Resolve processing type slug for Qdrant filter
    processing_type_slug = resolve_processing_type_slug(hearing_answer) if use_filter else None

    # Retrieve top-k sections via RAG query
    client = QdrantClient(host=qdrant_host, port=qdrant_port)
    results = rag_query(
        question,
        k=k,
        processing_type=processing_type_slug,
        model_id=model_id,
        qdrant_client=client,
        knowledge_dir=knowledge_dir,
        verify_ssl=verify_ssl,
    )

    # Build prompt
    prompt = build_rag_prompt(question, results, knowledge_dir)

    # Call LLM
    claude_output = call_llm(prompt)
    result_text = claude_output.get("result", "")

    # Parse response
    parsed = parse_rag_response(result_text, results)
    metrics = _extract_metrics(claude_output)

    return {
        "scenario_id": scenario["id"],
        "workflow_details": parsed["workflow_details"],
        "answer": parsed["answer"],
        "metrics": metrics,
        "trace": claude_output,
    }


# ---------------------------------------------------------------------------
# Run all scenarios
# ---------------------------------------------------------------------------

def run_rag_all(
    scenarios_path: str | Path,
    knowledge_dir: str | Path,
    output_dir: Path | None = None,
    scenario_ids: list[str] | None = None,
    k: int = DEFAULT_TOP_K,
    model_id: str = DEFAULT_EMBED_MODEL_ID,
    use_filter: bool = True,
    qdrant_host: str = QDRANT_HOST,
    qdrant_port: int = QDRANT_PORT,
    verify_ssl: bool = True,
) -> dict:
    """Run all (or selected) scenarios through the RAG pipeline.

    Args:
        scenarios_path: Path to scenarios JSON.
        knowledge_dir: Path to knowledge root.
        output_dir: Override output directory (default: auto-timestamped).
        scenario_ids: Limit to these IDs (None = run all).
        k: Top-k for retrieval.
        model_id: Bedrock Cohere Embed model ID.
        use_filter: Whether to apply processing_type metadata filter.
        qdrant_host: Qdrant host.
        qdrant_port: Qdrant port.
        verify_ssl: Whether to verify SSL certificates.

    Returns:
        Summary dict.
    """
    knowledge_dir = Path(knowledge_dir)
    executed_at = datetime.now().isoformat()

    with open(scenarios_path, encoding="utf-8") as f:
        data = json.load(f)

    out = output_dir or default_output_dir(k=k, has_filter=use_filter)
    out.mkdir(parents=True, exist_ok=True)

    scenario_summaries: list[dict] = []
    for scenario in data["scenarios"]:
        sid = scenario["id"]
        if scenario_ids and sid not in scenario_ids:
            continue

        print(f"Running {sid}...", file=sys.stderr)
        try:
            result = run_rag_scenario(
                scenario,
                knowledge_dir=knowledge_dir,
                k=k,
                model_id=model_id,
                use_filter=use_filter,
                qdrant_host=qdrant_host,
                qdrant_port=qdrant_port,
                verify_ssl=verify_ssl,
            )
            save_rag_results(out, sid, result)

            evaluation = evaluate_scenario(scenario, result, str(knowledge_dir))
            (out / sid / "evaluation.json").write_text(
                json.dumps(evaluation, ensure_ascii=False, indent=2), encoding="utf-8"
            )

            selected = result["workflow_details"].get("step3", {}).get("selected_sections", [])
            scenario_summaries.append({
                "id": result["scenario_id"],
                "search_sections": len(selected),
            })
            print(f"  {sid}: {len(selected)} sections retrieved", file=sys.stderr)

        except Exception as exc:
            exc_type = type(exc).__name__
            print(f"  ERROR {sid}: {exc_type}: {exc}", file=sys.stderr)
            error_dir = out / sid
            error_dir.mkdir(parents=True, exist_ok=True)
            (error_dir / "error.json").write_text(
                json.dumps({"error": str(exc), "exception_type": exc_type}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            scenario_summaries.append({"id": sid, "status": "error", "error": str(exc)})

    summary = {
        "total_scenarios": len(scenario_summaries),
        "knowledge_dir": str(knowledge_dir),
        "scenarios_file": str(scenarios_path),
        "executed_at": executed_at,
        "k": k,
        "use_filter": use_filter,
        "scenarios": scenario_summaries,
    }

    (out / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="RAG QA runner: top-k retrieval + LLM answer generation"
    )
    parser.add_argument(
        "--scenarios",
        default="tools/benchmark/scenarios/qa.json",
        help="Path to scenarios JSON (default: tools/benchmark/scenarios/qa.json)",
    )
    parser.add_argument(
        "--knowledge-dir",
        default=".claude/skills/nabledge-6/knowledge",
        help="Path to knowledge directory",
    )
    parser.add_argument(
        "--scenario-ids",
        default=None,
        help="Comma-separated scenario IDs to run (default: all)",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_EMBED_MODEL_ID,
        help=f"Cohere Embed model ID (default: {DEFAULT_EMBED_MODEL_ID})",
    )
    parser.add_argument(
        "--k",
        type=int,
        default=DEFAULT_TOP_K,
        help=f"Top-k results to retrieve (default: {DEFAULT_TOP_K})",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Override output directory",
    )
    parser.add_argument(
        "--no-filter",
        action="store_true",
        default=False,
        help="Disable metadata filtering (ablation mode)",
    )
    parser.add_argument(
        "--qdrant-host",
        default=QDRANT_HOST,
        help=f"Qdrant host (default: {QDRANT_HOST})",
    )
    parser.add_argument(
        "--qdrant-port",
        type=int,
        default=QDRANT_PORT,
        help=f"Qdrant port (default: {QDRANT_PORT})",
    )
    parser.add_argument(
        "--no-verify-ssl",
        action="store_true",
        default=False,
        help="Disable SSL certificate verification",
    )
    args = parser.parse_args()

    scenario_ids = args.scenario_ids.split(",") if args.scenario_ids else None
    output_dir = Path(args.output_dir) if args.output_dir else None

    print(f"RAG QA runner: k={args.k}, filter={not args.no_filter}", file=sys.stderr)

    summary = run_rag_all(
        scenarios_path=args.scenarios,
        knowledge_dir=args.knowledge_dir,
        output_dir=output_dir,
        scenario_ids=scenario_ids,
        k=args.k,
        model_id=args.model,
        use_filter=not args.no_filter,
        qdrant_host=args.qdrant_host,
        qdrant_port=args.qdrant_port,
        verify_ssl=not args.no_verify_ssl,
    )

    print(f"\nCompleted: {summary['total_scenarios']} scenarios", file=sys.stderr)
    for s in summary["scenarios"]:
        if s.get("status") == "error":
            print(f"  {s['id']}: ERROR — {s.get('error', '')}", file=sys.stderr)
        else:
            print(f"  {s['id']}: {s['search_sections']} sections retrieved", file=sys.stderr)


if __name__ == "__main__":
    main()

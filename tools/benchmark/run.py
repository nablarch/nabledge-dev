#!/usr/bin/env python3
"""
Benchmark runner for nabledge-6 faceted search flow.

Stages:
  --stage 1   AI-1 facet extraction only (tool-less), script-judged via
              per-axis Jaccard against scenario.expected_facets.
  --stage 2   [planned] stage 1 + mechanical type×category filter,
              LLM-judged in an isolated sub-agent.
  --stage 3   [planned] stage 1-2 + AI-2 section select + final answer,
              LLM-judged in an isolated sub-agent.

Results land under tools/benchmark/.results/{ts}-stage{N}-{model}/ with
one sub-directory per scenario. Every claude -p invocation is captured as
raw stream-json so we can audit turns / tool use / errors after the fact.

Usage:
  python3 run.py --stage 1 --scenarios-file scenarios/qa-v6-sample5.json --model sonnet
  python3 run.py --stage 1 --scenarios-file scenarios/qa-v6-sample5.json --model haiku --scenario review-01
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from tools.benchmark.filter.facet_filter import (  # noqa: E402
    IndexRow,
    filter_with_fallback,
    load_index,
)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BENCH_DIR = Path(__file__).resolve().parent
SCENARIOS_PATH_DEFAULT = BENCH_DIR / "scenarios" / "qa-v6-sample5.json"

PROMPT_STAGE1_FACET = BENCH_DIR / "prompts" / "stage1_facet.md"
PROMPT_JUDGE_STAGE2 = BENCH_DIR / "prompts" / "judge_stage2.md"
PROMPT_STAGE3_SELECT = BENCH_DIR / "prompts" / "stage3_section_select.md"
PROMPT_STAGE3_ANSWER = BENCH_DIR / "prompts" / "stage3_answer.md"
PROMPT_JUDGE_STAGE3 = BENCH_DIR / "prompts" / "judge_stage3.md"

KNOWLEDGE_ROOT = REPO_ROOT / ".claude" / "skills" / "nabledge-6" / "knowledge"
INDEX_TOON_PATH = KNOWLEDGE_ROOT / "index.toon"

TYPE_ENUM = [
    "about", "check", "component", "development-tools",
    "guide", "processing-pattern", "releases", "setup",
]
CATEGORY_ENUM = [
    "about-nablarch", "adapters", "biz-samples", "blank-project",
    "cloud-native", "configuration", "db-messaging", "handlers",
    "http-messaging", "jakarta-batch", "java-static-analysis",
    "libraries", "migration", "mom-messaging", "nablarch-batch",
    "nablarch-patterns", "release-notes", "releases",
    "restful-web-service", "security-check", "setting-guide",
    "testing-framework", "toolbox", "web-application",
]
COVERAGE_ENUM = ["in_scope", "uncertain", "out_of_scope"]

SCHEMA_JUDGE_STAGE2 = {
    "type": "object",
    "required": ["level", "reason"],
    "additionalProperties": False,
    "properties": {
        "level": {"type": "integer", "enum": [0, 1, 2, 3]},
        "reason": {"type": "string", "maxLength": 300},
    },
}

SCHEMA_STAGE3_SELECT = {
    "type": "object",
    "required": ["selections"],
    "additionalProperties": False,
    "properties": {
        "selections": {
            "type": "array",
            "maxItems": 10,
            "items": {"type": "string", "pattern": r"^[^:]+\.json:[a-zA-Z0-9_-]+$"},
        },
    },
}

SCHEMA_STAGE3_ANSWER = {
    "type": "object",
    "required": ["answer", "cited"],
    "additionalProperties": False,
    "properties": {
        "answer": {"type": "string", "maxLength": 4000},
        "cited": {
            "type": "array",
            "items": {"type": "string", "pattern": r"^[^:]+\.json:[a-zA-Z0-9_-]+$"},
        },
    },
}

SCHEMA_JUDGE_STAGE3 = {
    "type": "object",
    "required": ["level", "reason"],
    "additionalProperties": False,
    "properties": {
        "level": {"type": "integer", "enum": [0, 1, 2, 3]},
        "reason": {"type": "string", "maxLength": 300},
    },
}

SCHEMA_STAGE1_FACET = {
    "type": "object",
    "required": ["type", "category", "coverage"],
    "additionalProperties": False,
    "properties": {
        "type": {
            "type": "array", "maxItems": 3, "uniqueItems": True,
            "items": {"enum": TYPE_ENUM},
        },
        "category": {
            "type": "array", "maxItems": 4, "uniqueItems": True,
            "items": {"enum": CATEGORY_ENUM},
        },
        "coverage": {"enum": COVERAGE_ENUM},
    },
}


def load_scenarios(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def invoke_claude_stream(
    prompt: str,
    schema: dict,
    max_turns: int,
    model: str,
    log_path: Path,
    allowed_tools: list[str] | None = None,
    timeout_s: int = 300,
) -> tuple[dict | None, dict, float, str]:
    """Run `claude -p --output-format stream-json` and persist every event.

    Returns (structured_output, final_envelope, wall_s, error).
    The full NDJSON stream is written to log_path regardless of outcome.
    """
    cmd = [
        "claude",
        "-p",
        "--model", model,
        "--output-format", "stream-json",
        "--include-partial-messages",
        "--verbose",
        "--max-turns", str(max_turns),
        "--json-schema", json.dumps(schema),
        "--permission-mode", "bypassPermissions",
    ]
    if allowed_tools is None:
        pass
    elif allowed_tools:
        cmd += ["--tools", ",".join(allowed_tools)]
    else:
        cmd += ["--tools", ""]

    t0 = time.time()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        proc = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=timeout_s,
        )
    except subprocess.TimeoutExpired as e:
        log_path.write_text(
            (e.stdout or "") + "\n---TIMEOUT---\n" + (e.stderr or ""),
            encoding="utf-8",
        )
        return None, {}, time.time() - t0, f"timeout after {timeout_s}s"
    wall_s = time.time() - t0

    log_path.write_text(proc.stdout or "", encoding="utf-8")
    if proc.stderr:
        log_path.with_suffix(log_path.suffix + ".stderr").write_text(
            proc.stderr, encoding="utf-8"
        )

    # Stream-json NDJSON: last "result" event carries usage/cost/structured_output.
    # As a fallback, also pick up StructuredOutput tool_use inputs that the
    # assistant emitted during the run — useful when max-turns is hit after
    # the structured output was already provided.
    final_envelope: dict = {}
    structured: dict | None = None
    tool_use_structured: dict | None = None
    for line in (proc.stdout or "").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            evt = json.loads(line)
        except json.JSONDecodeError:
            continue
        if evt.get("type") == "result":
            final_envelope = evt
            structured = evt.get("structured_output") or structured
        elif evt.get("type") == "assistant":
            msg = evt.get("message", {})
            for block in msg.get("content", []) or []:
                if (
                    block.get("type") == "tool_use"
                    and block.get("name") == "StructuredOutput"
                ):
                    inp = block.get("input")
                    if isinstance(inp, dict) and inp:
                        tool_use_structured = inp
    if structured is None and tool_use_structured is not None:
        structured = tool_use_structured

    # Recover from error_max_turns when structured output was already captured.
    if proc.returncode != 0 and structured is None:
        return None, final_envelope, wall_s, (
            f"claude exited {proc.returncode}: {(proc.stderr or '')[-500:]}"
        )

    if not final_envelope:
        return structured, {}, wall_s, "no result event in stream"

    return structured, final_envelope, wall_s, ""


def jaccard(a: list[str], b: list[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def score_stage1_facet(extracted: dict, expected: dict) -> dict:
    """Per-axis Jaccard + coverage exact match."""
    ex_type = extracted.get("type", []) or []
    ex_cat = extracted.get("category", []) or []
    ex_cov = extracted.get("coverage")
    want_type = expected.get("type", []) or []
    want_cat = expected.get("category", []) or []
    want_cov = expected.get("coverage")

    j_type = jaccard(ex_type, want_type)
    j_cat = jaccard(ex_cat, want_cat)
    cov_match = ex_cov == want_cov

    return {
        "extracted": {"type": ex_type, "category": ex_cat, "coverage": ex_cov},
        "expected": {"type": want_type, "category": want_cat, "coverage": want_cov},
        "jaccard_type": j_type,
        "jaccard_category": j_cat,
        "coverage_match": cov_match,
        "overall": (j_type + j_cat + (1.0 if cov_match else 0.0)) / 3.0,
    }


def run_stage1_facet(scenario: dict, model: str, scen_dir: Path) -> dict:
    question = scenario["expected_question"]
    prompt = PROMPT_STAGE1_FACET.read_text(encoding="utf-8").replace(
        "{{question}}", question
    )
    (scen_dir / "ai1_prompt.md").write_text(prompt, encoding="utf-8")

    structured, envelope, wall_s, err = invoke_claude_stream(
        prompt=prompt,
        schema=SCHEMA_STAGE1_FACET,
        max_turns=2,
        model=model,
        allowed_tools=[],
        timeout_s=180,
        log_path=scen_dir / "ai1_facet_extract.stream-json",
    )

    result = {
        "id": scenario["id"],
        "stage": 1,
        "model": model,
        "question": question,
        "expected_facets": scenario.get("expected_facets"),
        "wall_s": wall_s,
        "duration_ms": envelope.get("duration_ms"),
        "num_turns": envelope.get("num_turns"),
        "total_cost_usd": envelope.get("total_cost_usd"),
        "is_error": envelope.get("is_error"),
    }
    if err:
        result["error"] = err
    else:
        result["extracted_facets"] = structured
        if scenario.get("expected_facets") and structured:
            result["score"] = score_stage1_facet(
                structured, scenario["expected_facets"]
            )
    (scen_dir / "ai1_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return result


def format_candidate_list(rows: list[IndexRow], max_rows: int = 200) -> str:
    """Format filter result as a markdown-friendly `title — path` list."""
    head = rows[:max_rows]
    return "\n".join(f"- {r.title} — {r.path}" for r in head)


def format_candidate_list_with_sections(
    rows: list[IndexRow], max_rows: int = 200
) -> str:
    """For Stage 3 AI-2: title — path, then indented section id/title list.

    Reads each candidate's knowledge JSON to emit its index. Skips files
    that cannot be read (reports as missing) rather than aborting.
    """
    lines: list[str] = []
    for row in rows[:max_rows]:
        lines.append(f"- {row.title} — {row.path}")
        kf = KNOWLEDGE_ROOT / row.path
        try:
            data = json.loads(kf.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            lines.append("    (sections unavailable)")
            continue
        for sec in data.get("index", []) or []:
            sid = sec.get("id")
            stitle = sec.get("title")
            if sid and stitle:
                lines.append(f"    - {sid}: {stitle}")
    return "\n".join(lines)


def read_selected_sections(
    selectors: list[str], max_selectors: int = 10
) -> tuple[str, list[dict]]:
    """Load the text of each `path:section_id` selector from knowledge/.

    Returns a (formatted_text, records) pair. `records` is the per-selector
    outcome for logging. Invalid selectors are marked but do not abort.
    """
    chunks: list[str] = []
    records: list[dict] = []
    for sel in selectors[:max_selectors]:
        if ":" not in sel:
            records.append({"selector": sel, "status": "malformed"})
            continue
        path, section_id = sel.split(":", 1)
        kf = KNOWLEDGE_ROOT / path
        try:
            data = json.loads(kf.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            records.append({"selector": sel, "status": "file-missing"})
            continue
        sections = data.get("sections") or {}
        text = sections.get(section_id)
        title = next(
            (s["title"] for s in data.get("index", []) or [] if s.get("id") == section_id),
            None,
        )
        if text is None:
            records.append(
                {"selector": sel, "status": "section-missing", "title": title}
            )
            continue
        chunks.append(f"=== {sel} — {title or ''} ===\n{text}\n=== END ===")
        records.append(
            {
                "selector": sel,
                "status": "ok",
                "title": title,
                "chars": len(text),
            }
        )
    return "\n\n".join(chunks), records


def run_stage2(
    scenario: dict, model: str, scen_dir: Path, index_rows: list[IndexRow]
) -> dict:
    """Stage 1 facet + mechanical filter + Stage 2 LLM judge."""
    # 1. Run Stage 1 (facet extraction) — reuse run_stage1_facet output.
    stage1 = run_stage1_facet(scenario, model, scen_dir)
    if stage1.get("error"):
        return {**stage1, "stage": 2, "filter": None, "judge": None}

    facets = stage1.get("extracted_facets") or {}
    want_type = facets.get("type", []) or []
    want_cat = facets.get("category", []) or []
    coverage = facets.get("coverage")

    # 2. Mechanical filter.
    if coverage == "out_of_scope" and not want_type and not want_cat:
        outcome_rows: list[IndexRow] = []
        fallback_used = "out_of_scope-shortcircuit"
    else:
        outcome = filter_with_fallback(index_rows, want_type, want_cat)
        outcome_rows = outcome.rows
        fallback_used = outcome.fallback_used

    filter_record = {
        "want_type": want_type,
        "want_category": want_cat,
        "coverage": coverage,
        "fallback_used": fallback_used,
        "candidate_count": len(outcome_rows),
        "candidates": [
            {"title": r.title, "type": r.type, "category": r.category, "path": r.path}
            for r in outcome_rows
        ],
    }
    (scen_dir / "filter_result.json").write_text(
        json.dumps(filter_record, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 3. Judge.
    if not outcome_rows:
        judge = {"level": 0, "reason": "filter returned no candidates"}
        judge_envelope: dict = {}
        judge_wall = 0.0
        judge_err = ""
    else:
        candidate_list = format_candidate_list(outcome_rows)
        judge_prompt = (
            PROMPT_JUDGE_STAGE2.read_text(encoding="utf-8")
            .replace("{{question}}", scenario["expected_question"])
            .replace("{{candidate_list}}", candidate_list)
        )
        (scen_dir / "judge_stage2_prompt.md").write_text(
            judge_prompt, encoding="utf-8"
        )
        judge, judge_envelope, judge_wall, judge_err = invoke_claude_stream(
            prompt=judge_prompt,
            schema=SCHEMA_JUDGE_STAGE2,
            max_turns=2,
            model=model,
            allowed_tools=[],
            timeout_s=180,
            log_path=scen_dir / "judge_stage2.stream-json",
        )

    judge_record = {
        "level": (judge or {}).get("level") if judge else None,
        "reason": (judge or {}).get("reason") if judge else None,
        "wall_s": judge_wall,
        "total_cost_usd": judge_envelope.get("total_cost_usd"),
        "error": judge_err or None,
    }
    (scen_dir / "judge_stage2_result.json").write_text(
        json.dumps(judge_record, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    total_cost = (stage1.get("total_cost_usd") or 0.0) + (
        judge_envelope.get("total_cost_usd") or 0.0
    )
    total_wall = (stage1.get("wall_s") or 0.0) + judge_wall

    return {
        "id": scenario["id"],
        "stage": 2,
        "model": model,
        "question": scenario["expected_question"],
        "stage1": {
            "extracted_facets": stage1.get("extracted_facets"),
            "score": stage1.get("score"),
            "cost_usd": stage1.get("total_cost_usd"),
            "wall_s": stage1.get("wall_s"),
        },
        "filter": {
            "fallback_used": fallback_used,
            "candidate_count": len(outcome_rows),
        },
        "judge": judge_record,
        "total_cost_usd": total_cost,
        "wall_s": total_wall,
    }


def run_stage3(
    scenario: dict, model: str, scen_dir: Path, index_rows: list[IndexRow]
) -> dict:
    """Stage 1 facet + filter + AI-2 section select + read + AI-3 answer + judge."""
    # Reuse Stage 2 pipeline up to filter.
    stage1 = run_stage1_facet(scenario, model, scen_dir)
    if stage1.get("error"):
        return {**stage1, "stage": 3}

    facets = stage1.get("extracted_facets") or {}
    want_type = facets.get("type", []) or []
    want_cat = facets.get("category", []) or []
    coverage = facets.get("coverage")

    if coverage == "out_of_scope" and not want_type and not want_cat:
        outcome_rows: list[IndexRow] = []
        fallback_used = "out_of_scope-shortcircuit"
    else:
        outcome = filter_with_fallback(index_rows, want_type, want_cat)
        outcome_rows = outcome.rows
        fallback_used = outcome.fallback_used

    filter_record = {
        "want_type": want_type,
        "want_category": want_cat,
        "coverage": coverage,
        "fallback_used": fallback_used,
        "candidate_count": len(outcome_rows),
    }
    (scen_dir / "filter_result.json").write_text(
        json.dumps(filter_record, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    question = scenario["expected_question"]

    # --- AI-2: section selection ---
    if not outcome_rows:
        selections: list[str] = []
        select_envelope: dict = {}
        select_wall = 0.0
        select_err = "no candidates"
    else:
        candidate_block = format_candidate_list_with_sections(outcome_rows)
        select_prompt = (
            PROMPT_STAGE3_SELECT.read_text(encoding="utf-8")
            .replace("{{question}}", question)
            .replace("{{candidate_list}}", candidate_block)
        )
        (scen_dir / "ai2_select_prompt.md").write_text(select_prompt, encoding="utf-8")
        select_out, select_envelope, select_wall, select_err = invoke_claude_stream(
            prompt=select_prompt,
            schema=SCHEMA_STAGE3_SELECT,
            max_turns=2,
            model=model,
            allowed_tools=[],
            timeout_s=300,
            log_path=scen_dir / "ai2_section_select.stream-json",
        )
        selections = (select_out or {}).get("selections", []) or []
    (scen_dir / "ai2_result.json").write_text(
        json.dumps(
            {
                "selections": selections,
                "wall_s": select_wall,
                "total_cost_usd": select_envelope.get("total_cost_usd"),
                "error": select_err or None,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    # --- Read sections ---
    sections_text, section_records = read_selected_sections(selections)
    (scen_dir / "sections_read.json").write_text(
        json.dumps(section_records, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # --- AI-3: answer ---
    if not sections_text:
        answer_struct: dict = {
            "answer": "（参照可能なセクションがありません。）",
            "cited": [],
        }
        answer_envelope: dict = {}
        answer_wall = 0.0
        answer_err = "no sections"
    else:
        answer_prompt = (
            PROMPT_STAGE3_ANSWER.read_text(encoding="utf-8")
            .replace("{{question}}", question)
            .replace("{{sections_text}}", sections_text)
        )
        (scen_dir / "ai3_answer_prompt.md").write_text(answer_prompt, encoding="utf-8")
        answer_struct, answer_envelope, answer_wall, answer_err = invoke_claude_stream(
            prompt=answer_prompt,
            schema=SCHEMA_STAGE3_ANSWER,
            max_turns=2,
            model=model,
            allowed_tools=[],
            timeout_s=300,
            log_path=scen_dir / "ai3_answer.stream-json",
        )
        answer_struct = answer_struct or {"answer": "", "cited": []}
    (scen_dir / "final_answer.md").write_text(
        answer_struct.get("answer") or "", encoding="utf-8"
    )
    (scen_dir / "ai3_result.json").write_text(
        json.dumps(
            {
                "answer": answer_struct.get("answer"),
                "cited": answer_struct.get("cited"),
                "wall_s": answer_wall,
                "total_cost_usd": answer_envelope.get("total_cost_usd"),
                "error": answer_err or None,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    # --- Judge ---
    if not answer_struct.get("answer"):
        judge: dict | None = {"level": 0, "reason": "no answer produced"}
        judge_envelope: dict = {}
        judge_wall = 0.0
        judge_err = ""
    else:
        judge_prompt = (
            PROMPT_JUDGE_STAGE3.read_text(encoding="utf-8")
            .replace("{{question}}", question)
            .replace("{{answer}}", answer_struct.get("answer") or "")
            .replace(
                "{{cited}}",
                "\n".join(f"- {c}" for c in (answer_struct.get("cited") or [])),
            )
        )
        (scen_dir / "judge_stage3_prompt.md").write_text(
            judge_prompt, encoding="utf-8"
        )
        judge, judge_envelope, judge_wall, judge_err = invoke_claude_stream(
            prompt=judge_prompt,
            schema=SCHEMA_JUDGE_STAGE3,
            max_turns=2,
            model=model,
            allowed_tools=[],
            timeout_s=180,
            log_path=scen_dir / "judge_stage3.stream-json",
        )

    judge_record = {
        "level": (judge or {}).get("level") if judge else None,
        "reason": (judge or {}).get("reason") if judge else None,
        "wall_s": judge_wall,
        "total_cost_usd": judge_envelope.get("total_cost_usd"),
        "error": judge_err or None,
    }
    (scen_dir / "judge_stage3_result.json").write_text(
        json.dumps(judge_record, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    total_cost = sum(
        v or 0.0
        for v in [
            stage1.get("total_cost_usd"),
            select_envelope.get("total_cost_usd"),
            answer_envelope.get("total_cost_usd"),
            judge_envelope.get("total_cost_usd"),
        ]
    )
    total_wall = (stage1.get("wall_s") or 0.0) + select_wall + answer_wall + judge_wall

    return {
        "id": scenario["id"],
        "stage": 3,
        "model": model,
        "question": question,
        "stage1": {
            "extracted_facets": stage1.get("extracted_facets"),
            "cost_usd": stage1.get("total_cost_usd"),
            "wall_s": stage1.get("wall_s"),
        },
        "filter": {
            "fallback_used": fallback_used,
            "candidate_count": len(outcome_rows),
        },
        "select": {
            "selections": selections,
            "cost_usd": select_envelope.get("total_cost_usd"),
            "wall_s": select_wall,
            "error": select_err or None,
        },
        "sections_read": {
            "ok": sum(1 for r in section_records if r.get("status") == "ok"),
            "total": len(section_records),
        },
        "answer": {
            "cited": answer_struct.get("cited"),
            "cost_usd": answer_envelope.get("total_cost_usd"),
            "wall_s": answer_wall,
            "error": answer_err or None,
        },
        "judge": judge_record,
        "total_cost_usd": total_cost,
        "wall_s": total_wall,
    }


def summarize(results: list[dict]) -> dict:
    def stat(values: list) -> dict:
        vs = [v for v in values if v is not None]
        if not vs:
            return {"count": 0}
        vs_sorted = sorted(vs)
        n = len(vs_sorted)
        median = (
            vs_sorted[n // 2]
            if n % 2 == 1
            else (vs_sorted[n // 2 - 1] + vs_sorted[n // 2]) / 2
        )
        return {
            "count": n,
            "mean": sum(vs) / n,
            "median": median,
            "min": min(vs),
            "max": max(vs),
        }

    ok = [r for r in results if not r.get("error")]
    summary = {
        "total": len(results),
        "errors": len(results) - len(ok),
        "wall_s": stat([r.get("wall_s") for r in ok]),
        "cost_usd": stat([r.get("total_cost_usd") for r in ok]),
        "turns": stat([r.get("num_turns") for r in ok]),
    }
    with_score = [r for r in ok if "score" in r]
    if with_score:
        summary["jaccard_type"] = stat(
            [r["score"]["jaccard_type"] for r in with_score]
        )
        summary["jaccard_category"] = stat(
            [r["score"]["jaccard_category"] for r in with_score]
        )
        summary["coverage_match_rate"] = sum(
            1 for r in with_score if r["score"]["coverage_match"]
        ) / len(with_score)
        summary["overall"] = stat([r["score"]["overall"] for r in with_score])
    with_judge = [r for r in ok if r.get("judge", {}).get("level") is not None]
    if with_judge:
        levels = [r["judge"]["level"] for r in with_judge]
        summary["judge_level"] = stat(levels)
        summary["judge_level_distribution"] = {
            str(lv): levels.count(lv) for lv in [0, 1, 2, 3]
        }
        summary["candidate_count"] = stat(
            [r["filter"]["candidate_count"] for r in with_judge if r.get("filter")]
        )
    return summary


def write_markdown_summary(
    stage: int, summary: dict, results: list[dict], out_path: Path
) -> None:
    lines = [f"# Stage {stage} — {summary.get('total')} scenarios", ""]
    if "overall" in summary:
        lines += [
            f"- mean Jaccard(type):     {summary['jaccard_type']['mean']:.3f}",
            f"- mean Jaccard(category): {summary['jaccard_category']['mean']:.3f}",
            f"- coverage match rate:    {summary['coverage_match_rate']:.2%}",
            f"- mean overall score:     {summary['overall']['mean']:.3f}",
        ]
    if "judge_level" in summary:
        lines += [
            f"- mean judge level:       {summary['judge_level']['mean']:.2f}",
            f"- judge distribution:     {summary['judge_level_distribution']}",
            f"- mean candidate count:   {summary['candidate_count']['mean']:.1f}",
        ]
    lines += [
        f"- mean cost (USD):        {summary['cost_usd'].get('mean', 0):.4f}",
        f"- mean wall (s):          {summary['wall_s'].get('mean', 0):.1f}",
        "",
    ]
    if stage == 3:
        lines += [
            "| id | facets | filter | picks | judge | reason | cost | wall |",
            "|----|--------|--------|-------|-------|--------|------|------|",
        ]
        for r in results:
            if r.get("error"):
                lines.append(
                    f"| {r['id']} | ERROR | - | - | - | {r['error']} | - | "
                    f"{r.get('wall_s', 0):.1f} |"
                )
                continue
            s1 = r.get("stage1", {})
            f_ = r.get("filter", {}) or {}
            sel_ = r.get("select", {}) or {}
            j_ = r.get("judge", {}) or {}
            facets = s1.get("extracted_facets") or {}
            reason = (j_.get("reason") or "").replace("|", "\\|").replace("\n", " ")
            if len(reason) > 80:
                reason = reason[:77] + "..."
            lines.append(
                "| {id} | {t}/{c} | {n} ({fb}) | {p} | {lv} | {rs} | "
                "{cost:.4f} | {w:.1f} |".format(
                    id=r["id"],
                    t=",".join(facets.get("type", []) or ["∅"]),
                    c=",".join(facets.get("category", []) or ["∅"]),
                    n=f_.get("candidate_count", 0),
                    fb=f_.get("fallback_used", "?"),
                    p=len(sel_.get("selections") or []),
                    lv=j_.get("level"),
                    rs=reason,
                    cost=r.get("total_cost_usd") or 0.0,
                    w=r.get("wall_s") or 0.0,
                )
            )
        out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return
    if stage == 2:
        lines += [
            "| id | facets (type / cat) | filter | judge | reason | cost | wall |",
            "|----|----------------------|--------|-------|--------|------|------|",
        ]
        for r in results:
            if r.get("error"):
                lines.append(
                    f"| {r['id']} | ERROR | - | - | {r['error']} | - | "
                    f"{r.get('wall_s', 0):.1f} |"
                )
                continue
            s1 = r.get("stage1", {})
            f_ = r.get("filter", {}) or {}
            j_ = r.get("judge", {}) or {}
            facets = s1.get("extracted_facets") or {}
            reason = (j_.get("reason") or "").replace("|", "\\|").replace("\n", " ")
            if len(reason) > 80:
                reason = reason[:77] + "..."
            lines.append(
                "| {id} | {t} / {c} | {n} ({fb}) | {lv} | {rs} | {cost:.4f} | {w:.1f} |".format(
                    id=r["id"],
                    t=",".join(facets.get("type", []) or ["∅"]),
                    c=",".join(facets.get("category", []) or ["∅"]),
                    n=f_.get("candidate_count", 0),
                    fb=f_.get("fallback_used", "?"),
                    lv=j_.get("level"),
                    rs=reason,
                    cost=r.get("total_cost_usd") or 0.0,
                    w=r.get("wall_s") or 0.0,
                )
            )
        out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return
    lines += [
        "| id | type (got → want) | cat (got → want) | cov | J(t) | J(c) | cost | wall |",
        "|----|-------------------|------------------|-----|------|------|------|------|",
    ]
    for r in results:
        if r.get("error"):
            lines.append(
                f"| {r['id']} | ERROR | - | - | - | - | - | {r.get('wall_s', 0):.1f} |"
            )
            continue
        s = r.get("score", {})
        got = s.get("extracted", {})
        want = s.get("expected", {})
        lines.append(
            "| {id} | {got_t} → {want_t} | {got_c} → {want_c} | "
            "{got_cov}{cov_flag}→{want_cov} | {jt:.2f} | {jc:.2f} | "
            "{cost:.4f} | {wall:.1f} |".format(
                id=r["id"],
                got_t=",".join(got.get("type", []) or ["∅"]),
                want_t=",".join(want.get("type", []) or ["∅"]),
                got_c=",".join(got.get("category", []) or ["∅"]),
                want_c=",".join(want.get("category", []) or ["∅"]),
                got_cov=got.get("coverage") or "∅",
                want_cov=want.get("coverage") or "∅",
                cov_flag=" ✅ " if s.get("coverage_match") else " ❌ ",
                jt=s.get("jaccard_type", 0.0),
                jc=s.get("jaccard_category", 0.0),
                cost=r.get("total_cost_usd") or 0.0,
                wall=r.get("wall_s") or 0.0,
            )
        )
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=int, choices=[1, 2, 3], required=True)
    ap.add_argument("--scenario", help="single scenario id")
    ap.add_argument("--limit", type=int, help="run only first N scenarios")
    ap.add_argument(
        "--scenarios-file",
        default=str(SCENARIOS_PATH_DEFAULT),
        help=f"scenarios JSON path (default: {SCENARIOS_PATH_DEFAULT})",
    )
    ap.add_argument("--model", default="sonnet",
                    help="claude model id or alias (sonnet, haiku, opus, or exact id)")
    ap.add_argument("--out", help="output directory (default: .results/{ts}-stage{N}-{model})")
    args = ap.parse_args()

    scenarios = load_scenarios(Path(args.scenarios_file))
    if args.scenario:
        scenarios = [s for s in scenarios if s["id"] == args.scenario]
        if not scenarios:
            print(f"scenario not found: {args.scenario}", file=sys.stderr)
            return 2
    if args.limit:
        scenarios = scenarios[: args.limit]

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    model_slug = args.model.replace("/", "_").replace(":", "_")
    default_out = BENCH_DIR / ".results" / f"{ts}-stage{args.stage}-{model_slug}"
    out_dir = Path(args.out) if args.out else default_out
    out_dir.mkdir(parents=True, exist_ok=True)
    results_path = out_dir / "results.jsonl"
    summary_path = out_dir / "summary.json"
    summary_md_path = out_dir / "summary.md"

    print(
        f"stage={args.stage} model={args.model} scenarios={len(scenarios)} out={out_dir}",
        file=sys.stderr,
    )

    index_rows = load_index(INDEX_TOON_PATH) if args.stage >= 2 else []

    results: list[dict] = []
    with results_path.open("w", encoding="utf-8") as f:
        for i, sc in enumerate(scenarios, 1):
            print(f"[{i}/{len(scenarios)}] {sc['id']} ...", file=sys.stderr, flush=True)
            scen_dir = out_dir / sc["id"]
            scen_dir.mkdir(parents=True, exist_ok=True)
            if args.stage == 1:
                r = run_stage1_facet(sc, args.model, scen_dir)
            elif args.stage == 2:
                r = run_stage2(sc, args.model, scen_dir, index_rows)
            else:
                r = run_stage3(sc, args.model, scen_dir, index_rows)
            results.append(r)
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            f.flush()
            if r.get("error"):
                print(f"  -> ERROR: {r['error']}", file=sys.stderr)
            elif args.stage == 1:
                s = r.get("score", {})
                print(
                    f"  -> turns={r.get('num_turns')} cost=${r.get('total_cost_usd')} "
                    f"wall={r.get('wall_s'):.1f}s "
                    f"J(type)={s.get('jaccard_type', 0):.2f} "
                    f"J(cat)={s.get('jaccard_category', 0):.2f} "
                    f"cov={'✓' if s.get('coverage_match') else '✗'}",
                    file=sys.stderr,
                )
            else:
                f_ = r.get("filter", {}) or {}
                j_ = r.get("judge", {}) or {}
                print(
                    f"  -> candidates={f_.get('candidate_count')} "
                    f"fallback={f_.get('fallback_used')} "
                    f"judge={j_.get('level')} "
                    f"cost=${r.get('total_cost_usd'):.4f} "
                    f"wall={r.get('wall_s'):.1f}s",
                    file=sys.stderr,
                )

    summary = summarize(results)
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_markdown_summary(args.stage, summary, results, summary_md_path)
    print(f"done. results: {results_path}", file=sys.stderr)
    print(f"       summary: {summary_path}", file=sys.stderr)
    print(f"       summary: {summary_md_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

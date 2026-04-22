#!/usr/bin/env python3
"""
Benchmark runner for nabledge-6 search flow.

Runs scenarios against one of three measurement stages:

  --stage 1   AI keyword extraction only (tool-less), script-judged against expected_keywords
  --stage 2   Stage 1 + keyword-search.sh, LLM-judged in an isolated sub-agent
  --stage 3   Full nabledge-6 skill, LLM-judged in an isolated sub-agent

Results land under .results/{YYYYMMDD-HHMMSS}-stage{N}-{flow}/.

Usage:
  python run.py --stage 1 --flow current --limit 3
  python run.py --stage 2 --flow new --scenario review-01
  python run.py --stage 3 --flow current
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BENCH_DIR = Path(__file__).resolve().parent
SCENARIOS_PATH_DEFAULT = BENCH_DIR / "scenarios" / "qa-v6.json"

PROMPT_STAGE1 = BENCH_DIR / "prompts" / "stage1_extract.md"
PROMPT_STAGE2_CURRENT = BENCH_DIR / "prompts" / "stage2_search_current.md"
PROMPT_STAGE2_NEW = BENCH_DIR / "prompts" / "stage2_search_new.md"
PROMPT_STAGE3_CURRENT = BENCH_DIR / "prompts" / "stage3_full_current.md"
PROMPT_STAGE3_NEW = BENCH_DIR / "prompts" / "stage3_full_new.md"
PROMPT_JUDGE_STAGE2 = BENCH_DIR / "prompts" / "judge_stage2.md"
PROMPT_JUDGE_STAGE3 = BENCH_DIR / "prompts" / "judge_stage3.md"

SCHEMA_STAGE1 = {
    "type": "object",
    "properties": {
        "keywords": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["keywords"],
}

SCHEMA_STAGE2 = {
    "type": "object",
    "properties": {
        "keywords": {"type": "array", "items": {"type": "string"}},
        "hits": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "file": {"type": "string"},
                    "section_id": {"type": "string"},
                },
                "required": ["file", "section_id"],
            },
        },
    },
    "required": ["keywords", "hits"],
}

SCHEMA_STAGE3 = {
    "type": "object",
    "properties": {
        "keywords": {"type": "array", "items": {"type": "string"}},
        "matched_sections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "file": {"type": "string"},
                    "section_id": {"type": "string"},
                },
                "required": ["file", "section_id"],
            },
        },
        "answer": {"type": "string"},
    },
    "required": ["keywords", "matched_sections", "answer"],
}

SCHEMA_JUDGE = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": ["pass", "partial", "fail"]},
        "score": {"type": "number"},
        "reasoning": {"type": "string"},
    },
    "required": ["verdict", "score", "reasoning"],
}


def load_scenarios(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def invoke_claude(
    prompt: str,
    schema: dict,
    max_turns: int,
    model: str,
    allowed_tools: list[str] | None = None,
    timeout_s: int = 600,
) -> tuple[dict | None, dict, float, str]:
    """Run claude -p and return (structured_output, envelope, wall_s, error).

    envelope is the raw JSON from claude -p (cost/turns/duration_ms/etc).
    error is a short human-readable string if something went wrong, else "".
    """
    # Variadic flags like --allowedTools / --disallowedTools greedily consume
    # subsequent positional args, so we feed the prompt via stdin.
    cmd = [
        "claude",
        "-p",
        "--model", model,
        "--output-format", "json",
        "--max-turns", str(max_turns),
        "--json-schema", json.dumps(schema),
        "--permission-mode", "bypassPermissions",
    ]
    if allowed_tools is None:
        pass  # default: all tools allowed
    elif allowed_tools:
        cmd += ["--tools", ",".join(allowed_tools)]
    else:
        cmd += ["--tools", ""]  # empty string -> disable all tools

    t0 = time.time()
    try:
        proc = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=timeout_s,
        )
    except subprocess.TimeoutExpired:
        return None, {}, time.time() - t0, f"timeout after {timeout_s}s"
    wall_s = time.time() - t0

    if proc.returncode != 0:
        return None, {}, wall_s, f"claude exited {proc.returncode}: {proc.stderr[-500:]}"

    try:
        envelope = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        return None, {}, wall_s, f"json decode: {e}"

    structured = envelope.get("structured_output")
    return structured, envelope, wall_s, ""


def score_stage1(extracted: list[str], expected: list[str]) -> dict:
    """Script-based scoring: recall/precision against expected_keywords."""
    ex = [k.strip().lower() for k in extracted if k.strip()]
    want = [k.strip().lower() for k in expected if k.strip()]
    matched = [k for k in want if any(k in e or e in k for e in ex)]
    recall = len(matched) / len(want) if want else 0.0
    precision = len(matched) / len(ex) if ex else 0.0
    return {
        "extracted_count": len(ex),
        "expected_count": len(want),
        "matched": matched,
        "missed": [k for k in want if k not in matched],
        "recall": recall,
        "precision": precision,
    }


def run_stage1(scenario: dict, model: str) -> dict:
    question = scenario["expected_question"]
    prompt = PROMPT_STAGE1.read_text(encoding="utf-8").replace("{{question}}", question)

    structured, envelope, wall_s, err = invoke_claude(
        prompt=prompt,
        schema=SCHEMA_STAGE1,
        max_turns=2,
        model=model,
        allowed_tools=[],
        timeout_s=120,
    )

    result = {
        "id": scenario["id"],
        "stage": 1,
        "question": question,
        "expected_keywords": scenario.get("expected_keywords", []),
        "wall_s": wall_s,
        "duration_ms": envelope.get("duration_ms"),
        "num_turns": envelope.get("num_turns"),
        "total_cost_usd": envelope.get("total_cost_usd"),
        "is_error": envelope.get("is_error"),
    }
    if err:
        result["error"] = err
        return result
    keywords = (structured or {}).get("keywords", [])
    result["keywords"] = keywords
    result["score"] = score_stage1(keywords, scenario.get("expected_keywords", []))
    return result


def summarize(results: list[dict]) -> dict:
    def stat(values: list[float]) -> dict:
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
    if ok and "score" in ok[0]:
        summary["recall"] = stat([r["score"]["recall"] for r in ok])
        summary["precision"] = stat([r["score"]["precision"] for r in ok])
    return summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=int, choices=[1, 2, 3], required=True)
    ap.add_argument(
        "--flow",
        choices=["current", "new"],
        default="current",
        help="search flow variant (relevant for stage 2/3 only)",
    )
    ap.add_argument("--scenario", help="single scenario id")
    ap.add_argument("--limit", type=int, help="run only first N scenarios")
    ap.add_argument(
        "--scenarios-file",
        default=str(SCENARIOS_PATH_DEFAULT),
        help=f"scenarios JSON path (default: {SCENARIOS_PATH_DEFAULT})",
    )
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--out", help="output directory (default: .results/{ts}-stage{N}-{flow})")
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
    default_out = BENCH_DIR / ".results" / f"{ts}-stage{args.stage}-{args.flow}"
    out_dir = Path(args.out) if args.out else default_out
    out_dir.mkdir(parents=True, exist_ok=True)
    results_path = out_dir / "results.jsonl"
    summary_path = out_dir / "summary.json"

    print(
        f"stage={args.stage} flow={args.flow} scenarios={len(scenarios)} out={out_dir}",
        file=sys.stderr,
    )

    results: list[dict] = []
    with results_path.open("w", encoding="utf-8") as f:
        for i, sc in enumerate(scenarios, 1):
            print(f"[{i}/{len(scenarios)}] {sc['id']} ...", file=sys.stderr, flush=True)
            if args.stage == 1:
                r = run_stage1(sc, args.model)
            else:
                print(
                    f"stage {args.stage} not implemented yet",
                    file=sys.stderr,
                )
                return 3
            results.append(r)
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            f.flush()
            if r.get("error"):
                print(f"  -> ERROR: {r['error']}", file=sys.stderr)
            else:
                score = r.get("score", {})
                print(
                    f"  -> turns={r.get('num_turns')} cost=${r.get('total_cost_usd')} "
                    f"wall={r.get('wall_s'):.1f}s recall={score.get('recall'):.2f} "
                    f"missed={score.get('missed')}",
                    file=sys.stderr,
                )

    summary = summarize(results)
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"done. results: {results_path}", file=sys.stderr)
    print(f"       summary: {summary_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

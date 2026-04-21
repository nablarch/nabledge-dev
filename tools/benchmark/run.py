#!/usr/bin/env python3
"""
Benchmark runner for nabledge-6 search flow.

Runs N QA scenarios against a chosen flow (current / new), captures answer +
metrics, and writes results under .results/{YYYYMMDD-HHMMSS}/.

The baseline/ directory is a git-tracked snapshot of a specific run, copied
manually from .results/ when we want to commit it.

Usage:
  python run.py --flow current --limit 1
  python run.py --flow new --limit 1
  python run.py --flow current                      # all 30
  python run.py --flow current --scenario review-01 # single scenario by id
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
SCENARIOS_PATH = BENCH_DIR / "scenarios" / "qa-v6.json"
PROMPT_CURRENT = BENCH_DIR / "prompts" / "search_current.md"
PROMPT_NEW = BENCH_DIR / "prompts" / "search_new.md"

# Structured output schema. answer+keywords+matched_sections only — everything
# else (cost, duration, turns) comes from claude -p's own JSON envelope.
OUTPUT_SCHEMA = {
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
                    "relevance": {"type": "string", "enum": ["high", "partial"]},
                },
                "required": ["file", "section_id", "relevance"],
            },
        },
        "answer": {"type": "string"},
    },
    "required": ["keywords", "matched_sections", "answer"],
}


def load_scenarios() -> list[dict]:
    return json.loads(SCENARIOS_PATH.read_text(encoding="utf-8"))


def build_prompt(flow: str, question: str) -> str:
    prompt_file = PROMPT_CURRENT if flow == "current" else PROMPT_NEW
    return prompt_file.read_text(encoding="utf-8").replace("{{question}}", question)


def run_scenario(scenario: dict, flow: str, max_turns: int, model: str) -> dict:
    question = scenario["expected_question"]
    prompt = build_prompt(flow, question)

    # Tools required: just Bash (the skill scripts). No Edit/Write.
    # allowedTools restricts to Bash only.
    cmd = [
        "claude",
        "-p",
        "--model", model,
        "--output-format", "json",
        "--max-turns", str(max_turns),
        "--json-schema", json.dumps(OUTPUT_SCHEMA),
        "--allowedTools", "Bash",
        "--permission-mode", "bypassPermissions",
        prompt,
    ]

    t0 = time.time()
    proc = subprocess.run(
        cmd, capture_output=True, text=True, cwd=REPO_ROOT, timeout=600
    )
    wall_s = time.time() - t0

    if proc.returncode != 0:
        return {
            "id": scenario["id"],
            "flow": flow,
            "error": f"claude exited {proc.returncode}",
            "stderr": proc.stderr[-2000:],
            "wall_s": wall_s,
        }

    try:
        envelope = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        return {
            "id": scenario["id"],
            "flow": flow,
            "error": f"json decode: {e}",
            "stdout_tail": proc.stdout[-2000:],
            "wall_s": wall_s,
        }

    structured = envelope.get("structured_output") or {}
    return {
        "id": scenario["id"],
        "flow": flow,
        "question": question,
        "expected_sections": scenario.get("expected_sections", []),
        "expected_keywords": scenario.get("expected_keywords", []),
        "keywords": structured.get("keywords", []),
        "matched_sections": structured.get("matched_sections", []),
        "answer": structured.get("answer", ""),
        "duration_ms": envelope.get("duration_ms"),
        "num_turns": envelope.get("num_turns"),
        "total_cost_usd": envelope.get("total_cost_usd"),
        "is_error": envelope.get("is_error"),
        "stop_reason": envelope.get("stop_reason"),
        "terminal_reason": envelope.get("terminal_reason"),
        "wall_s": wall_s,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--flow", choices=["current", "new"], required=True)
    ap.add_argument("--scenario", help="single scenario id")
    ap.add_argument("--limit", type=int, help="run only first N scenarios")
    ap.add_argument("--max-turns", type=int, default=30)
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--out", help="output directory (default: .results/{ts})")
    args = ap.parse_args()

    scenarios = load_scenarios()
    if args.scenario:
        scenarios = [s for s in scenarios if s["id"] == args.scenario]
        if not scenarios:
            print(f"scenario not found: {args.scenario}", file=sys.stderr)
            return 2
    if args.limit:
        scenarios = scenarios[: args.limit]

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = Path(args.out) if args.out else BENCH_DIR / ".results" / ts
    out_dir.mkdir(parents=True, exist_ok=True)
    results_path = out_dir / "results.jsonl"

    print(f"flow={args.flow} scenarios={len(scenarios)} out={out_dir}", file=sys.stderr)

    with results_path.open("w", encoding="utf-8") as f:
        for i, sc in enumerate(scenarios, 1):
            print(f"[{i}/{len(scenarios)}] {sc['id']} ...", file=sys.stderr, flush=True)
            r = run_scenario(sc, args.flow, args.max_turns, args.model)
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            f.flush()
            print(
                f"  -> turns={r.get('num_turns')} cost={r.get('total_cost_usd')} wall={r.get('wall_s'):.1f}s err={r.get('error') or r.get('is_error')}",
                file=sys.stderr,
            )

    print(f"done. results: {results_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Simulate 2-stage semantic search against QA scenarios.

Runs Stage 1 (page selection from index.md) and Stage 2 (section selection
from knowledge JSONs) for each scenario, then compares results with must sections.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from tools.benchmark.scripts.evaluate import call_llm, parse_section_ref

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

STAGE1_JSON_SCHEMA = json.dumps({
    "type": "object",
    "properties": {
        "files": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "reason": {"type": "string"},
                },
                "required": ["path", "reason"],
            },
        },
    },
    "required": ["files"],
})

STAGE2_JSON_SCHEMA = json.dumps({
    "type": "object",
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "file": {"type": "string"},
                    "section_id": {"type": "string"},
                    "relevance": {
                        "type": "string",
                        "enum": ["high", "partial"],
                    },
                },
                "required": ["file", "section_id", "relevance"],
            },
        },
    },
    "required": ["results"],
})


def build_stage1_prompt(question: str, hearing_answer: str | None, index_content: str) -> str:
    template = (PROMPTS_DIR / "semantic-search-stage1.md").read_text(encoding="utf-8")
    ha = hearing_answer if hearing_answer else "なし"
    return (
        template
        .replace("{question}", question)
        .replace("{hearing_answer}", ha)
        .replace("{index_content}", index_content)
    )


def build_stage2_prompt(question: str, hearing_answer: str | None, files_content: str) -> str:
    template = (PROMPTS_DIR / "semantic-search-stage2.md").read_text(encoding="utf-8")
    ha = hearing_answer if hearing_answer else "なし"
    return (
        template
        .replace("{question}", question)
        .replace("{hearing_answer}", ha)
        .replace("{files_content}", files_content)
    )


def format_file_content(rel_path: str, knowledge_data: dict) -> str:
    lines = [f"## {rel_path}", f"タイトル: {knowledge_data.get('title', '')}"]
    for section in knowledge_data.get("sections", []):
        sid = section["id"]
        title = section["title"]
        content = section.get("content", "")
        lines.append(f"\n### {sid}: {title}\n")
        if content:
            lines.append(content)
    return "\n".join(lines)


def format_files_content(knowledge_dir: str | Path, file_paths: list[str]) -> str:
    knowledge_dir = Path(knowledge_dir)
    parts = []
    for rel_path in file_paths:
        full_path = knowledge_dir / rel_path
        if not full_path.exists():
            print(f"WARNING: file not found: {full_path}", file=sys.stderr)
            continue
        with open(full_path, encoding="utf-8") as f:
            data = json.load(f)
        parts.append(format_file_content(rel_path, data))
    return "\n\n".join(parts)


def parse_stage1_response(response: dict) -> list[dict]:
    if "files" not in response:
        raise ValueError("Response missing 'files' key")
    if not isinstance(response["files"], list):
        raise ValueError(f"'files' must be a list, got {type(response['files']).__name__!r}")
    return response["files"][:5]


def parse_stage2_response(response: dict) -> list[dict]:
    if "results" not in response:
        raise ValueError("Response missing 'results' key")
    if not isinstance(response["results"], list):
        raise ValueError(f"'results' must be a list, got {type(response['results']).__name__!r}")
    for r in response["results"]:
        if r.get("relevance") not in ("high", "partial"):
            raise ValueError(f"Invalid relevance: {r.get('relevance')!r}")
    return response["results"][:10]


def compare_results(
    results: list[dict],
    must_sections: list[dict],
    acceptable_sections: list[dict],
) -> dict:
    result_set = {(r["file"], r["section_id"]) for r in results}
    result_files = {r["file"] for r in results}

    must_hits = []
    must_misses = []
    must_file_hit = 0
    must_file_miss = 0
    seen_files = set()

    for must in must_sections:
        file_path, section_id = parse_section_ref(must["section"])
        if (file_path, section_id) in result_set:
            must_hits.append(must["section"])
        else:
            must_misses.append(must["section"])

        if file_path not in seen_files:
            seen_files.add(file_path)
            if file_path in result_files:
                must_file_hit += 1
            else:
                must_file_miss += 1

    acceptable_hits = []
    for acc in acceptable_sections:
        file_path, section_id = parse_section_ref(acc["section"])
        if (file_path, section_id) in result_set:
            acceptable_hits.append(acc["section"])

    total_must = len(must_sections)
    return {
        "must_total": total_must,
        "must_hit": len(must_hits),
        "must_miss": len(must_misses),
        "must_hits": must_hits,
        "must_misses": must_misses,
        "must_file_hit": must_file_hit,
        "must_file_miss": must_file_miss,
        "acceptable_hits": acceptable_hits,
        "hit_rate": len(must_hits) / total_must if total_must > 0 else 1.0,
    }


def simulate_scenario(
    scenario: dict,
    index_content: str,
    knowledge_dir: str | Path,
    llm_fn=None,
    model: str = "sonnet",
) -> dict:
    if llm_fn is None:
        def llm_fn(prompt, schema, model=model):
            return call_llm(prompt, schema, model)

    scenario_id = scenario["id"]
    question = scenario["when"]["input"]
    hearing_answer = scenario["when"].get("hearing_answer")
    must = scenario["then"].get("must", [])
    acceptable = scenario["then"].get("acceptable", [])

    stage1_prompt = build_stage1_prompt(question, hearing_answer, index_content)
    stage1_raw = llm_fn(stage1_prompt, STAGE1_JSON_SCHEMA)
    stage1_files = parse_stage1_response(stage1_raw)

    file_paths = [f["path"] for f in stage1_files]
    files_content = format_files_content(knowledge_dir, file_paths)

    stage2_prompt = build_stage2_prompt(question, hearing_answer, files_content)
    stage2_raw = llm_fn(stage2_prompt, STAGE2_JSON_SCHEMA)
    stage2_results = parse_stage2_response(stage2_raw)

    comparison = compare_results(stage2_results, must, acceptable)

    return {
        "scenario_id": scenario_id,
        "stage1": {"files": stage1_files},
        "stage2": {"results": stage2_results},
        "comparison": comparison,
    }


def simulate_all(
    scenarios_path: str,
    knowledge_dir: str,
    index_content: str,
    output_dir: str,
    model: str = "sonnet",
    scenario_ids: list[str] | None = None,
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
        result = simulate_scenario(scenario, index_content, knowledge_dir, model=model)

        scenario_dir = out_path / sid
        scenario_dir.mkdir(parents=True, exist_ok=True)
        (scenario_dir / "stage1.json").write_text(
            json.dumps(result["stage1"], ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (scenario_dir / "stage2.json").write_text(
            json.dumps(result["stage2"], ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (scenario_dir / "comparison.json").write_text(
            json.dumps(result["comparison"], ensure_ascii=False, indent=2), encoding="utf-8"
        )
        results.append(result)

    total_must = sum(r["comparison"]["must_total"] for r in results)
    total_hit = sum(r["comparison"]["must_hit"] for r in results)
    summary = {
        "total_scenarios": len(results),
        "total_must": total_must,
        "total_hit": total_hit,
        "total_miss": total_must - total_hit,
        "overall_hit_rate": total_hit / total_must if total_must > 0 else 1.0,
        "per_scenario": [
            {
                "id": r["scenario_id"],
                "must_hit": r["comparison"]["must_hit"],
                "must_miss": r["comparison"]["must_miss"],
                "hit_rate": r["comparison"]["hit_rate"],
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

    parser = argparse.ArgumentParser(description="Simulate 2-stage semantic search")
    parser.add_argument("--scenarios", required=True, help="Path to scenarios JSON")
    parser.add_argument("--knowledge-dir", required=True, help="Path to knowledge directory")
    parser.add_argument("--index", help="Path to index.md (default: generate from knowledge-dir)")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    parser.add_argument("--model", default="sonnet", help="LLM model (default: sonnet)")
    parser.add_argument("--scenario-ids", help="Comma-separated scenario IDs to run")
    args = parser.parse_args()

    if args.index:
        index_content = Path(args.index).read_text(encoding="utf-8")
    else:
        from tools.benchmark.scripts.generate_index import generate_index
        index_content = generate_index(args.knowledge_dir)

    scenario_ids = args.scenario_ids.split(",") if args.scenario_ids else None

    summary = simulate_all(
        args.scenarios,
        args.knowledge_dir,
        index_content,
        args.output_dir,
        model=args.model,
        scenario_ids=scenario_ids,
    )

    hit_rate = summary["overall_hit_rate"]
    print(f"\nResults: {summary['total_hit']}/{summary['total_must']} must sections hit ({hit_rate:.1%})", file=sys.stderr)
    for s in summary["per_scenario"]:
        status = "OK" if s["must_miss"] == 0 else "MISS"
        print(f"  {s['id']}: {status} ({s['must_hit']}/{s['must_hit'] + s['must_miss']})", file=sys.stderr)


if __name__ == "__main__":
    main()

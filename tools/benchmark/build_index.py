#!/usr/bin/env python3
"""Build two indexes for the benchmark AI-1 redesign.

Inputs
------
.claude/skills/nabledge-{version}/knowledge/**/*.json

Outputs
-------
knowledge/index-llm.md      — human/LLM readable: [id] title + "  sid:section_title / ..."
knowledge/index-script.json — compact JSON: {id: {path, sections: [sid,...]}}
"""
from __future__ import annotations
import argparse
import glob
import json
import os
import sys


REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def collect(knowledge_dir: str) -> list[dict]:
    entries = []
    for fp in sorted(glob.glob(f"{knowledge_dir}/**/*.json", recursive=True)):
        try:
            d = json.load(open(fp))
        except Exception:
            continue
        if not isinstance(d, dict) or "id" not in d or "title" not in d:
            continue
        if d.get("no_knowledge_content") is True:
            continue
        rel = os.path.relpath(fp, knowledge_dir)
        sections = [
            {"id": s.get("id", ""), "title": s.get("title", "")}
            for s in d.get("index", [])
            if isinstance(s, dict) and s.get("id")
        ]
        entries.append({
            "id": d["id"],
            "title": d["title"],
            "path": rel,
            "sections": sections,
        })
    return entries


def build_llm_index(entries: list[dict], version: str) -> str:
    lines = [
        f"# Nabledge-{version} LLM Index",
        "",
        f"{len(entries)} files / "
        f"{sum(len(e['sections']) for e in entries)} sections",
        "",
        "Format: `[file_id] page_title` followed by `  sid:section_title / ...`",
        "Return `file_id` or `file_id|sid` that best matches the question.",
        "",
    ]
    for e in entries:
        lines.append(f"[{e['id']}] {e['title']}")
        if e["sections"]:
            lines.append(
                "  "
                + " / ".join(f"{s['id']}:{s['title']}" for s in e["sections"])
            )
    return "\n".join(lines) + "\n"


def build_script_index(entries: list[dict]) -> str:
    obj = {
        e["id"]: {
            "path": e["path"],
            "sections": [s["id"] for s in e["sections"]],
        }
        for e in entries
    }
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", required=True)
    args = ap.parse_args()

    knowledge_dir = f"{REPO}/.claude/skills/nabledge-{args.version}/knowledge"
    if not os.path.isdir(knowledge_dir):
        print(f"ERROR: knowledge dir not found: {knowledge_dir}", file=sys.stderr)
        return 1

    entries = collect(knowledge_dir)
    llm_md = build_llm_index(entries, args.version)
    script_json = build_script_index(entries)

    llm_path = f"{knowledge_dir}/index-llm.md"
    script_path = f"{knowledge_dir}/index-script.json"
    with open(llm_path, "w") as f:
        f.write(llm_md)
    with open(script_path, "w") as f:
        f.write(script_json)

    print(f"Wrote: {llm_path} ({len(llm_md):,} chars)")
    print(f"Wrote: {script_path} ({len(script_json):,} chars)")
    print(f"Entries: {len(entries)} files, "
          f"{sum(len(e['sections']) for e in entries)} sections")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

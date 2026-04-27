#!/usr/bin/env python3
"""Build the two indexes consumed by the benchmark AI-1 search variant.

Inputs
------
- .claude/skills/nabledge-{version}/knowledge/**/*.json
- --keywords <path>  JSON written by classify_terms.py; shape:
      {"keywords": {"<page_id>|<section_id>": ["kw1", "kw2", ...]}}
  When --keywords is omitted, sections render without trailing keywords.

Outputs
-------
- knowledge/index-llm.md     human/LLM readable — AI-1 reads this:
    [id] title
      sid:section_title [— keyword / keyword / ...]
      ...
- knowledge/index-script.json  compact JSON: {id: {path, sections: [sid,...]}}

Each section's keywords come from the `keywords` map keyed by
`"<page_id>|<section_id>"`. Keywords are rendered in the order they appear in
the map (classify_terms.py emits them in TF-desc / alphabetic-tie order).
"""
from __future__ import annotations
import argparse
import glob
import json
import os
import sys


REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_keyword_map(path: str | None) -> dict[str, list[str]]:
    if not path:
        return {}
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    kw = data.get("keywords") if isinstance(data, dict) else None
    if not isinstance(kw, dict):
        raise ValueError(
            f"keywords file must be a JSON object with a 'keywords' map: {path}"
        )
    out: dict[str, list[str]] = {}
    for key, terms in kw.items():
        if not isinstance(terms, list):
            continue
        out[str(key)] = [str(t) for t in terms]
    return out


def collect(knowledge_dir: str, keyword_map: dict[str, list[str]]) -> list[dict]:
    """Collect page entries with each section's keywords attached.

    Sections are ordered by their appearance in the page's `index` array.
    """
    entries = []
    for fp in sorted(glob.glob(f"{knowledge_dir}/**/*.json", recursive=True)):
        try:
            with open(fp, encoding="utf-8") as fh:
                d = json.load(fh)
        except (json.JSONDecodeError, OSError) as e:
            print(f"WARN: skip {fp}: {e}", file=sys.stderr)
            continue
        if not isinstance(d, dict) or "id" not in d or "title" not in d:
            continue
        if d.get("no_knowledge_content") is True:
            continue
        rel = os.path.relpath(fp, knowledge_dir)
        page_id = d["id"]

        sections = []
        for s in d.get("index", []):
            if not isinstance(s, dict) or not s.get("id"):
                continue
            sid = s["id"]
            stitle = s.get("title", "")
            key = f"{page_id}|{sid}"
            sections.append({
                "id": sid,
                "title": stitle,
                "keywords": list(keyword_map.get(key, [])),
            })

        entries.append({
            "id": page_id,
            "title": d["title"],
            "path": rel,
            "sections": sections,
        })
    return entries


def build_llm_index(entries: list[dict], version: str) -> str:
    n_sections = sum(len(e["sections"]) for e in entries)
    lines = [
        f"# Nabledge-{version} LLM Index",
        "",
        f"{len(entries)} files / {n_sections} sections",
        "",
        "Format: `[file_id] page_title  (relative_path)` followed by one line",
        "per section: `  sid:section_title` optionally ending with",
        "` — keyword / keyword / ...` when keywords are available from the body.",
        "The relative_path is resolved against the knowledge root",
        f"(`.claude/skills/nabledge-{version}/knowledge/`) and can be passed to",
        "the Read tool when the caller needs to inspect a section's body.",
        "",
    ]
    for e in entries:
        lines.append(f"[{e['id']}] {e['title']}  ({e['path']})")
        for s in e["sections"]:
            line = f"  {s['id']}:{s['title']}"
            if s["keywords"]:
                line += " — " + " / ".join(s["keywords"])
            lines.append(line)
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
    ap.add_argument("--keywords", default=None,
                    help="Path to index-keywords-ja JSON (from classify_terms.py)")
    args = ap.parse_args()

    knowledge_dir = f"{REPO}/.claude/skills/nabledge-{args.version}/knowledge"
    if not os.path.isdir(knowledge_dir):
        print(f"ERROR: knowledge dir not found: {knowledge_dir}", file=sys.stderr)
        return 1

    keyword_map = load_keyword_map(args.keywords)
    entries = collect(knowledge_dir, keyword_map)
    llm_md = build_llm_index(entries, args.version)
    script_json = build_script_index(entries)

    llm_path = f"{knowledge_dir}/index-llm.md"
    script_path = f"{knowledge_dir}/index-script.json"
    with open(llm_path, "w", encoding="utf-8") as f:
        f.write(llm_md)
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_json)

    print(f"Wrote: {llm_path} ({len(llm_md):,} chars)")
    print(f"Wrote: {script_path} ({len(script_json):,} chars)")
    n_sections = sum(len(e['sections']) for e in entries)
    print(f"Entries: {len(entries)} files, {n_sections} sections")

    if keyword_map:
        n_placed = sum(len(s['keywords']) for e in entries for s in e['sections'])
        print(f"Keyword placements: {n_placed} "
              f"(keyword map entries: {len(keyword_map)})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

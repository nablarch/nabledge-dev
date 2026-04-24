#!/usr/bin/env python3
"""Build two indexes for the benchmark AI-1 redesign.

Inputs
------
.claude/skills/nabledge-{version}/knowledge/**/*.json

Outputs
-------
knowledge/index-llm.md      — human/LLM readable:
    [id] title
      sid:section_title [— keyword / keyword / ...]
      ...
knowledge/index-script.json — compact JSON: {id: {path, sections: [sid,...]}}

Keywords come from MANUAL_ALLOWLIST_JA (see manual-allowlist-ja-*.json).
Each allowlist term is placed after every section whose body contains
the term. Terms not found in any section body trigger a warning (see
docs/index-enrichment.md).
"""
from __future__ import annotations
import argparse
import glob
import json
import os
import sys


REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_allowlist(path: str | None) -> list[str]:
    if not path:
        return []
    with open(path) as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"allowlist must be a JSON array: {path}")
    return [str(t) for t in data]


def collect(knowledge_dir: str, allowlist: list[str]) -> tuple[list[dict], dict]:
    """Collect page entries. Each section dict carries its matched keywords.

    Returns (entries, stats) where stats includes terms-not-found.
    """
    entries = []
    found_terms: set[str] = set()

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

        # Map sid -> body for keyword matching
        sections_raw = d.get("sections") or {}
        sid_to_body: dict[str, str] = {}
        if isinstance(sections_raw, dict):
            for sid, body in sections_raw.items():
                if isinstance(body, str):
                    sid_to_body[sid] = body
                elif isinstance(body, dict):
                    sid_to_body[sid] = body.get("body") or ""

        # Section titles (from `index` array, preserving order)
        sections = []
        for s in d.get("index", []):
            if not isinstance(s, dict) or not s.get("id"):
                continue
            sid = s["id"]
            stitle = s.get("title", "")
            body = sid_to_body.get(sid, "")
            # Match keywords: term appears in body, but not in title/section_title
            matched = []
            for term in allowlist:
                if term in body and term not in d["title"] and term not in stitle:
                    matched.append(term)
                    found_terms.add(term)
            sections.append({"id": sid, "title": stitle, "keywords": matched})

        entries.append({
            "id": d["id"],
            "title": d["title"],
            "path": rel,
            "sections": sections,
        })

    not_found = [t for t in allowlist if t not in found_terms]
    return entries, {"terms_not_found": not_found}


def build_llm_index(entries: list[dict], version: str) -> str:
    n_sections = sum(len(e["sections"]) for e in entries)
    lines = [
        f"# Nabledge-{version} LLM Index",
        "",
        f"{len(entries)} files / {n_sections} sections",
        "",
        "Format: `[file_id] page_title` followed by one line per section:",
        "`  sid:section_title` optionally ending with ` — keyword / keyword / ...`",
        "when keywords are available from the page body.",
        "Return `file_id|sid` that best matches the question. Match the user query",
        "against the title, section titles, and keywords.",
        "",
    ]
    for e in entries:
        lines.append(f"[{e['id']}] {e['title']}")
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
    ap.add_argument("--allowlist", default=None,
                    help="Path to JSON array of allowed keywords to attach to sections")
    ap.add_argument("--strict", action="store_true",
                    help="Exit non-zero if any allowlist term is not found in any body")
    args = ap.parse_args()

    knowledge_dir = f"{REPO}/.claude/skills/nabledge-{args.version}/knowledge"
    if not os.path.isdir(knowledge_dir):
        print(f"ERROR: knowledge dir not found: {knowledge_dir}", file=sys.stderr)
        return 1

    allowlist = load_allowlist(args.allowlist)
    entries, stats = collect(knowledge_dir, allowlist)
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

    if allowlist:
        n_placed = sum(len(s['keywords']) for e in entries for s in e['sections'])
        print(f"Keyword placements: {n_placed} (allowlist size: {len(allowlist)})")
        if stats['terms_not_found']:
            print(f"\nWARN: {len(stats['terms_not_found'])} allowlist terms were "
                  f"not found in any section body.", file=sys.stderr)
            for t in stats['terms_not_found']:
                print(f"  - {t}", file=sys.stderr)
            if args.strict:
                return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

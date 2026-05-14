#!/bin/bash
# Keyword search using terms.json inverted index.
#
# - Case-insensitive partial match (substring)
# - Multiple keywords: page-level AND, section-level OR
#   (page must have hits for ALL keywords; return all hit sections)
# - Minimum keyword length: 2
# - No result limit
#
# Arguments: keywords (one or more, each 2+ chars)
# Output: JSON — category > page > section hierarchy

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
KNOWLEDGE_DIR="$SKILL_DIR/knowledge"
TERMS_FILE="$KNOWLEDGE_DIR/terms.json"

if [ $# -eq 0 ]; then
  echo "Usage: $0 <keyword1> [keyword2] ..." >&2
  exit 1
fi

if [ ! -f "$TERMS_FILE" ]; then
  echo "Error: terms.json not found at $TERMS_FILE" >&2
  exit 1
fi

python3 - "$KNOWLEDGE_DIR" "$@" << 'PYEOF'
import sys
import json
from collections import defaultdict
from pathlib import Path

knowledge_dir = Path(sys.argv[1])
keywords = [kw for kw in sys.argv[2:] if len(kw) >= 2]

if not keywords:
    print(json.dumps([], ensure_ascii=False))
    sys.exit(0)

terms_path = knowledge_dir / "terms.json"
terms = json.loads(terms_path.read_text(encoding="utf-8"))

terms_lower = {k.lower(): k for k in terms}

def page_of(sec_id):
    return sec_id.rsplit(":", 1)[0]

per_kw_sections = []
for kw in keywords:
    matched = set()
    kw_lower = kw.lower()
    for term_key, original_key in terms_lower.items():
        if kw_lower in term_key:
            matched.update(terms[original_key])
    per_kw_sections.append(matched)

per_kw_pages = [set(page_of(s) for s in secs) for secs in per_kw_sections]
valid_pages = per_kw_pages[0]
for p in per_kw_pages[1:]:
    valid_pages &= p

if not valid_pages:
    print(json.dumps([], ensure_ascii=False))
    sys.exit(0)

all_hit_sections = set()
for secs in per_kw_sections:
    for s in secs:
        if page_of(s) in valid_pages:
            all_hit_sections.add(s)

file_cache = {}
results = []
for sec_id in sorted(all_hit_sections):
    parts = sec_id.rsplit(":", 1)
    if len(parts) != 2:
        continue
    rel_path, sid = parts
    json_path = knowledge_dir / rel_path
    if rel_path not in file_cache:
        try:
            file_cache[rel_path] = json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            continue
    data = file_cache[rel_path]
    if data.get("no_knowledge_content"):
        continue

    section_title = ""
    for sec in data.get("sections", []):
        if sec["id"] == sid:
            section_title = sec.get("title", "")
            break

    path_parts = rel_path.split("/")
    category = "/".join(path_parts[:2]) if len(path_parts) >= 3 else path_parts[0]

    results.append({
        "section_id": sec_id,
        "section_title": section_title,
        "page_title": data.get("title", ""),
        "page_path": rel_path,
        "category": category,
    })

cat_map = defaultdict(lambda: defaultdict(list))
for r in results:
    cat_map[r["category"]][(r["page_path"], r["page_title"])].append(r)

sorted_cats = sorted(cat_map.keys())

output = []
for cat in sorted_cats:
    pages = cat_map[cat]
    sorted_pages = sorted(pages.keys(), key=lambda p: (-len(pages[p]), p[1]))
    page_list = []
    for (page_path, page_title) in sorted_pages:
        secs = pages[(page_path, page_title)]
        sorted_secs = sorted(secs, key=lambda s: s["section_id"])
        section_list = [
            {"section_id": s["section_id"], "section_title": s["section_title"]}
            for s in sorted_secs
        ]
        page_list.append({"page_title": page_title, "sections": section_list})
    output.append({"category": cat, "pages": page_list})

print(json.dumps(output, ensure_ascii=False, indent=2))
PYEOF

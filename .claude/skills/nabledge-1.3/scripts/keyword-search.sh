#!/bin/bash
# Keyword search using terms.json inverted index.
#
# 3-stage matching per keyword:
#   1. Exact match in terms.json
#   2. Case-insensitive match
#   3. Partial match (substring, only if keyword > 5 chars)
#
# Arguments: keywords (one or more)
# Output: JSON — category > page > section hierarchy (top 30)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
KNOWLEDGE_DIR="$SKILL_DIR/knowledge"
TERMS_FILE="$KNOWLEDGE_DIR/terms.json"
MAX_RESULTS=30

if [ $# -eq 0 ]; then
  echo "Usage: $0 <keyword1> [keyword2] ..." >&2
  exit 1
fi

if [ ! -f "$TERMS_FILE" ]; then
  echo "Error: terms.json not found at $TERMS_FILE" >&2
  exit 1
fi

python3 - "$KNOWLEDGE_DIR" "$MAX_RESULTS" "$@" << 'PYEOF'
import sys
import json
from collections import defaultdict
from pathlib import Path

knowledge_dir = Path(sys.argv[1])
max_results = int(sys.argv[2])
keywords = sys.argv[3:]

terms_path = knowledge_dir / "terms.json"
terms = json.loads(terms_path.read_text(encoding="utf-8"))

terms_lower = {k.lower(): k for k in terms}

section_scores = defaultdict(int)

for kw in keywords:
    matched_sections = set()

    if kw in terms:
        matched_sections.update(terms[kw])
    elif kw.lower() in terms_lower:
        matched_sections.update(terms[terms_lower[kw.lower()]])
    elif len(kw) > 5:
        kw_lower = kw.lower()
        for term_key, original_key in terms_lower.items():
            if kw_lower in term_key:
                matched_sections.update(terms[original_key])

    for sec_id in matched_sections:
        section_scores[sec_id] += 1

if not section_scores:
    print(json.dumps([], ensure_ascii=False))
    sys.exit(0)

ranked = sorted(section_scores.items(), key=lambda x: (-x[1], x[0]))[:max_results]

file_cache = {}
results = []
for sec_id, score in ranked:
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
        "score": score,
    })

cat_map = defaultdict(lambda: defaultdict(list))
for r in results:
    cat_map[r["category"]][(r["page_path"], r["page_title"])].append(r)

cat_max = {cat: max(r["score"] for secs in pages.values() for r in secs)
           for cat, pages in cat_map.items()}

sorted_cats = sorted(cat_map.keys(), key=lambda c: (-cat_max[c], c))

output = []
for cat in sorted_cats:
    pages = cat_map[cat]
    sorted_pages = sorted(pages.keys(), key=lambda p: (-len(pages[p]), p[1]))
    page_list = []
    for (page_path, page_title) in sorted_pages:
        secs = pages[(page_path, page_title)]
        sorted_secs = sorted(secs, key=lambda s: (-s["score"], s["section_id"]))
        section_list = [
            {"section_id": s["section_id"], "section_title": s["section_title"]}
            for s in sorted_secs
        ]
        page_list.append({"page_title": page_title, "sections": section_list})
    output.append({"category": cat, "pages": page_list})

print(json.dumps(output, ensure_ascii=False, indent=2))
PYEOF

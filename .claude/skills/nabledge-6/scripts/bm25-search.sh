#!/bin/bash
# BM25 pre-search over nabledge-6 knowledge files.
#
# - Builds a bm25s index from all knowledge/*.json section titles+content on first run
# - Saves index to scripts/.bm25-index/; reloads on subsequent runs
# - Detects staleness by comparing index mtime to newest JSON mtime; rebuilds if stale
# - Returns top-20 sections by BM25 score
#
# Arguments: one or more search terms
# Output: JSON array to stdout — [{file, section_id, section_title, score}, ...]
#         Empty array [] if no hits or no arguments.
# Exit code: non-zero on error (missing bm25s, index build failure, etc.)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
KNOWLEDGE_DIR="${KNOWLEDGE_DIR:-$SKILL_DIR/knowledge}"
INDEX_DIR="$SCRIPT_DIR/.bm25-index"

if [ $# -eq 0 ]; then
  echo "[]"
  exit 0
fi

python3 - "$KNOWLEDGE_DIR" "$INDEX_DIR" "$@" << 'PYEOF'
import sys
import json
import os
import time
from pathlib import Path

knowledge_dir = Path(sys.argv[1])
index_dir = Path(sys.argv[2])
terms = sys.argv[3:]

if not terms:
    print(json.dumps([], ensure_ascii=False))
    sys.exit(0)

try:
    import bm25s
    import numpy as np
except ImportError as e:
    print(f"Error: {e}. Run: pip install bm25s", file=sys.stderr)
    sys.exit(1)

INDEX_FILE = index_dir / "index.bm25s"
META_FILE = index_dir / "meta.json"


# Token pattern: match sequences of word characters including CJK characters and underscores.
# \w+ covers ASCII identifiers; 　-鿿 covers CJK ideographs and common Japanese ranges.
# This is used as the token_pattern for bm25s.tokenize.
TOKEN_PATTERN = r'(?u)[\w　-鿿]+'


def get_newest_json_mtime(knowledge_dir: Path) -> float:
    """Return the mtime of the most recently modified JSON file."""
    mtimes = [p.stat().st_mtime for p in knowledge_dir.rglob("*.json")]
    return max(mtimes) if mtimes else 0.0


def load_sections(knowledge_dir: Path) -> tuple[list[dict], list[str]]:
    """Load all sections from knowledge JSON files. Returns (section_meta, corpus)."""
    section_meta = []
    corpus = []
    for json_path in sorted(knowledge_dir.rglob("*.json")):
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if data.get("no_knowledge_content"):
            continue
        rel_path = json_path.relative_to(knowledge_dir).as_posix()
        for sec in data.get("sections", []):
            sid = sec.get("id", "")
            if not sid:
                continue
            title = sec.get("title", "")
            content = sec.get("content", "")
            text = f"{title} {content}"
            section_meta.append({
                "file": rel_path,
                "section_id": sid,
                "section_title": title,
            })
            corpus.append(text)
    return section_meta, corpus


def build_index(knowledge_dir: Path, index_dir: Path) -> tuple[object, list[dict]]:
    """Build and save BM25 index. Returns (retriever, section_meta)."""
    section_meta, corpus = load_sections(knowledge_dir)
    if not corpus:
        raise RuntimeError("No sections found in knowledge directory")

    tokenized = bm25s.tokenize(corpus, token_pattern=TOKEN_PATTERN, stopwords=None, show_progress=False)
    retriever = bm25s.BM25()
    retriever.index(tokenized, show_progress=False)

    index_dir.mkdir(parents=True, exist_ok=True)
    retriever.save(str(INDEX_FILE))

    newest_mtime = get_newest_json_mtime(knowledge_dir)
    meta = {
        "section_meta": section_meta,
        "built_at": time.time(),
        "newest_json_mtime": newest_mtime,
        "count": len(section_meta),
    }
    META_FILE.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")

    return retriever, section_meta


def is_index_stale(knowledge_dir: Path) -> bool:
    """Return True if the index needs to be rebuilt."""
    if not INDEX_FILE.exists() or not META_FILE.exists():
        return True
    try:
        meta = json.loads(META_FILE.read_text(encoding="utf-8"))
        saved_mtime = meta.get("newest_json_mtime", 0)
        current_mtime = get_newest_json_mtime(knowledge_dir)
        return current_mtime > saved_mtime
    except Exception:
        return True


def load_index(index_dir: Path) -> tuple[object, list[dict]]:
    """Load saved BM25 index and metadata."""
    retriever = bm25s.BM25.load(str(INDEX_FILE), load_corpus=False)
    meta = json.loads(META_FILE.read_text(encoding="utf-8"))
    return retriever, meta["section_meta"]


# Build or reload index
if is_index_stale(knowledge_dir):
    retriever, section_meta = build_index(knowledge_dir, index_dir)
else:
    retriever, section_meta = load_index(index_dir)

if not section_meta:
    print(json.dumps([], ensure_ascii=False))
    sys.exit(0)

# Search
query = " ".join(terms)
tokenized_query = bm25s.tokenize([query], token_pattern=TOKEN_PATTERN, stopwords=None, show_progress=False)
top_k = min(20, len(section_meta))
results, scores = retriever.retrieve(tokenized_query, k=top_k, show_progress=False)

# results shape: (n_queries, k), scores shape: (n_queries, k)
output = []
for idx, score in zip(results[0], scores[0]):
    if score <= 0:
        continue
    meta = section_meta[int(idx)]
    output.append({
        "file": meta["file"],
        "section_id": meta["section_id"],
        "section_title": meta["section_title"],
        "score": round(float(score), 4),
    })

print(json.dumps(output, ensure_ascii=False, indent=2))
PYEOF

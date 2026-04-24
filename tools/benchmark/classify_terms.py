#!/usr/bin/env python3
"""Classify terms in the corpus for index-llm.md keyword selection.

Pipeline steps 1-3 (see .work/00307/tasks.md):
  1. Extract all tokens from 295 pages
  2. Compute TF-IDF globally
  3. Categorize each unique term into one of:
       - stop  (java)       Java-standard CamelCase names
       - allow (annotation) @Foo
       - allow (camel)      2-hump CamelCase (Nablarch class names)
       - allow (lowerCamel) camelCase (property/config keys)
       - allow (highScore)  max TF-IDF score across corpus >= threshold
       - pending            everything else — subject to step 4 agent judgment

The step 4 (agent judgment) consumes `pending.json`.
"""
from __future__ import annotations
import argparse
import glob
import json
import os
import re
import sys

from sklearn.feature_extraction.text import TfidfVectorizer

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 2-hump Java-standard CamelCase names we never want as keywords.
# Single-word types (String, Integer, BigDecimal) are already excluded by the
# 2-hump pattern itself.
JAVA_STOPLIST = {
    "ArrayList", "HashMap", "HashSet", "TreeMap", "TreeSet", "LinkedList",
    "LinkedHashMap", "LinkedHashSet", "ConcurrentHashMap",
    "IOException", "RuntimeException", "NullPointerException",
    "IllegalArgumentException", "IllegalStateException",
    "UnsupportedOperationException",
    "FunctionalInterface", "SafeVarargs",
    "InputStream", "OutputStream", "BufferedReader", "BufferedWriter",
    "FileReader", "FileWriter", "PrintWriter",
    "LocalDate", "LocalTime", "LocalDateTime", "OffsetDateTime",
    "ZonedDateTime", "DateTimeFormatter",
    "StringBuilder", "StringBuffer",
}

# Extraction patterns.
PATTERN_ANNOTATION = re.compile(r'@([A-Za-z_][A-Za-z0-9_]{1,40})')
PATTERN_CAMEL = re.compile(r'\b([A-Z][a-z]+(?:[A-Z][a-zA-Z0-9_]*)+)\b')
PATTERN_LOWER_CAMEL = re.compile(r'\b([a-z][a-z0-9]+[A-Z][A-Za-z0-9]+)\b')
PATTERN_KATAKANA = re.compile(r'[゠-ヿー]{4,}')
PATTERN_KANJI = re.compile(r'[一-鿿]{4,}')
PATTERN_MIXED = re.compile(r'[一-鿿゠-ヿー]{4,}')


def tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    for m in PATTERN_ANNOTATION.finditer(text):
        tokens.append('@' + m.group(1))
    for m in PATTERN_CAMEL.finditer(text):
        tokens.append(m.group(1))
    for m in PATTERN_LOWER_CAMEL.finditer(text):
        tokens.append(m.group(1))
    for pat in (PATTERN_KATAKANA, PATTERN_KANJI, PATTERN_MIXED):
        for m in pat.finditer(text):
            tokens.append(m.group(0))
    return tokens


def page_body(entry: dict) -> str:
    parts = []
    sections = entry.get("sections")
    if isinstance(sections, dict):
        for sid, s in sections.items():
            if isinstance(s, str):
                parts.append(s)
            elif isinstance(s, dict):
                parts.append(s.get("title") or "")
                parts.append(s.get("body") or "")
    return "\n".join(parts)


def collect_pages(knowledge_dir: str) -> list[dict]:
    pages = []
    for fp in sorted(glob.glob(f"{knowledge_dir}/**/*.json", recursive=True)):
        try:
            d = json.load(open(fp))
        except Exception:
            continue
        if not isinstance(d, dict) or "id" not in d or "title" not in d:
            continue
        if d.get("no_knowledge_content") is True:
            continue
        section_titles = [
            s.get("title", "")
            for s in (d.get("index") or [])
            if isinstance(s, dict) and s.get("title")
        ]
        pages.append({
            "id": d["id"],
            "title": d["title"],
            "section_titles": section_titles,
            "body": page_body(d),
        })
    return pages


def classify(pages: list[dict], score_threshold: float):
    token_lists = [tokenize(p["body"]) for p in pages]
    vec = TfidfVectorizer(
        analyzer=lambda toks: toks,
        lowercase=False,
        token_pattern=None,
    )
    matrix = vec.fit_transform(token_lists)
    features = vec.get_feature_names_out()

    # Per-term maximum TF-IDF score across the corpus
    col_max = matrix.max(axis=0).toarray().ravel()

    # Also record the top-3 pages by score for each term (for human review later)
    matrix_csc = matrix.tocsc()

    categories = {
        "stop_java": {},
        "stop_title_overlap": {},
        "allow_annotation": {},
        "allow_camel": {},
        "allow_lower_camel": {},
        "allow_high_score": {},
        "pending": {},
    }

    for i, term in enumerate(features):
        max_score = float(col_max[i])
        # top 3 pages by score for this term
        col = matrix_csc.getcol(i).tocoo()
        top_rows = sorted(
            zip(col.row, col.data), key=lambda x: -x[1]
        )[:3]
        top_pages = [
            {"id": pages[r]["id"], "title": pages[r]["title"],
             "score": round(float(s), 3)}
            for r, s in top_rows
        ]

        info = {"max_score": round(max_score, 4), "top_pages": top_pages}

        # Check if term is already visible in the top page's title or section titles.
        # If so, it adds no value to put it in the keyword slot — skip from judgment.
        title_overlap = False
        if top_rows:
            top_r = top_rows[0][0]
            top_page = pages[top_r]
            if term in top_page["title"]:
                title_overlap = True
            elif any(term in st for st in top_page["section_titles"]):
                title_overlap = True

        if term in JAVA_STOPLIST:
            categories["stop_java"][term] = info
        elif title_overlap:
            categories["stop_title_overlap"][term] = info
        elif term.startswith('@'):
            categories["allow_annotation"][term] = info
        elif re.match(r'^[a-z][a-z0-9]+[A-Z]', term):
            categories["allow_lower_camel"][term] = info
        elif re.match(r'^[A-Z][a-z]+[A-Z]', term):
            categories["allow_camel"][term] = info
        elif max_score >= score_threshold:
            categories["allow_high_score"][term] = info
        else:
            categories["pending"][term] = info

    return categories


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="6")
    ap.add_argument("--score-threshold", type=float, default=0.30,
                    help="Non-pattern terms auto-pass if max TF-IDF >= threshold")
    ap.add_argument("--show", choices=[
        "summary", "stop_java", "stop_title_overlap", "allow_annotation",
        "allow_camel", "allow_lower_camel", "allow_high_score", "pending",
    ], default="summary")
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--out", default=None,
                    help="Write classification JSON to this file")
    args = ap.parse_args()

    knowledge_dir = f"{REPO}/.claude/skills/nabledge-{args.version}/knowledge"
    pages = collect_pages(knowledge_dir)
    print(f"Collected {len(pages)} pages", file=sys.stderr)

    result = classify(pages, args.score_threshold)

    if args.out:
        with open(args.out, "w") as f:
            json.dump({
                "meta": {
                    "version": args.version,
                    "pages": len(pages),
                    "score_threshold": args.score_threshold,
                },
                "categories": {
                    k: {t: v for t, v in sorted(
                        d.items(), key=lambda x: -x[1]["max_score"])}
                    for k, d in result.items()
                },
            }, f, ensure_ascii=False, indent=2)
        print(f"Wrote {args.out}", file=sys.stderr)

    if args.show == "summary":
        print(f"\n== Classification summary (threshold={args.score_threshold}) ==")
        total = 0
        for cat in ["stop_java", "stop_title_overlap", "allow_annotation",
                     "allow_camel", "allow_lower_camel",
                     "allow_high_score", "pending"]:
            print(f"  {cat:22s} : {len(result[cat]):5d} terms")
            total += len(result[cat])
        print(f"  {'total':22s} : {total:5d} terms")
        return 0

    bucket = result[args.show]
    sorted_terms = sorted(bucket.items(), key=lambda x: -x[1]["max_score"])
    print(f"\n== {args.show} (showing top {args.limit} of {len(bucket)}) ==")
    for term, info in sorted_terms[:args.limit]:
        top1 = info["top_pages"][0]["id"] if info["top_pages"] else ""
        print(f"  {info['max_score']:.3f}  {term:40s}  (top: {top1})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""terms.json generator for RBKC.

Generates terms.json — a term-to-section-id inverted index used by
keyword-search.sh for exact/case-insensitive/partial matching.

Format:
    {term: [section_ids], ...}

where section_ids use full relative path format:
    "component/libraries/libraries-universal-dao.json:s1"

Term extraction rules:
    1. ASCII identifiers: [A-Za-z@][A-Za-z0-9_@]* with length >= 3
       (all-caps abbreviations >= 2 are also included: DB, IO, CORS)
    2. CJK: contiguous CJK/hiragana/katakana sequences of length >= 2
    3. Japanese section titles: full title + verb-suffix-removed form
    4. Property names: dot-separated identifiers (nablarch.core.validation)
    5. Compound keywords: hyphen-separated words (use-token)
    6. Stoplist: terms with section_df >= 7% are excluded

Public API:
    generate_terms(knowledge_dir, output_path) -> int
"""
from __future__ import annotations

import json
import re
from pathlib import Path

_ASCII_TERM = re.compile(r'[@A-Za-z][@A-Za-z0-9_]*')

_CJK_TERM = re.compile(
    r'[぀-ゟ'
    r'゠-ヿ'
    r'一-鿿'
    r'＀-￯'
    r']+'
)

_PROPERTY_NAME = re.compile(r'[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*){2,}')

_COMPOUND_HYPHEN = re.compile(r'[A-Za-z][A-Za-z0-9]*(?:-[A-Za-z][A-Za-z0-9]*)+')

_VERB_SUFFIXES = re.compile(
    r'(?:を使う|を行う|する|について|のやり方|の方法|の使い方|の設定|を設定する|を作成する|を実装する)$'
)

_HAS_CJK = re.compile(r'[぀-ゟ゠-ヿ一-鿿]')

_SECTION_DF_THRESHOLD = 0.07


def _extract_terms(text: str) -> set[str]:
    terms: set[str] = set()

    for m in _PROPERTY_NAME.finditer(text):
        terms.add(m.group())

    for m in _COMPOUND_HYPHEN.finditer(text):
        terms.add(m.group())

    for m in _ASCII_TERM.finditer(text):
        t = m.group()
        if len(t) >= 3:
            terms.add(t)
        elif len(t) >= 2 and t.isupper():
            terms.add(t)

    for m in _CJK_TERM.finditer(text):
        t = m.group()
        if len(t) >= 2:
            terms.add(t)

    return terms


def _extract_title_terms(title: str) -> set[str]:
    """Extract Japanese section title terms: full title + verb-suffix-removed."""
    terms: set[str] = set()
    if not _HAS_CJK.search(title):
        return terms

    stripped = title.strip()
    if not stripped:
        return terms

    terms.add(stripped)
    shortened = _VERB_SUFFIXES.sub('', stripped)
    if shortened != stripped and len(shortened) >= 2:
        terms.add(shortened)

    return terms


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def generate_terms(knowledge_dir: Path, output_path: Path) -> int:
    """Write terms.json to output_path by scanning all knowledge JSON files.

    Args:
        knowledge_dir: Root directory containing knowledge JSON files.
        output_path: Destination path for terms.json.

    Returns:
        Number of terms written after stoplist filtering.
    """
    term_to_sections: dict[str, set[str]] = {}
    total_sections = 0

    for json_path in sorted(knowledge_dir.rglob("*.json")):
        try:
            data = _load_json(json_path)
        except Exception:
            continue
        if data.get("no_knowledge_content") is True:
            continue
        rel_path = str(json_path.relative_to(knowledge_dir)).replace("\\", "/")
        for sec in data.get("sections", []):
            sec_id = f"{rel_path}:{sec['id']}"
            total_sections += 1
            text = f"{sec.get('title', '')} {sec.get('content', '')}"
            for term in _extract_terms(text):
                term_to_sections.setdefault(term, set()).add(sec_id)

            title = sec.get('title', '')
            for term in _extract_title_terms(title):
                term_to_sections.setdefault(term, set()).add(sec_id)

    if total_sections == 0:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("{}", encoding="utf-8")
        return 0

    result: dict[str, list[str]] = {}
    for term, section_ids in term_to_sections.items():
        section_df = len(section_ids) / total_sections
        if section_df < _SECTION_DF_THRESHOLD:
            result[term] = sorted(section_ids)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2),
        encoding="utf-8",
    )
    return len(result)

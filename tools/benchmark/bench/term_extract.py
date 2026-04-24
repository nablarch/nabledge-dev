"""Question-side term extraction for the ids search variant.

Mirrors the patterns used by `tools/benchmark/classify_terms.py` so the
grep-query side of the flow stays aligned with the index-enrichment side.

Patterns (4+ chars, 3-char words excluded on purpose):
  annotation    @Published, @UseToken
  camel         TransactionManagementHandler
  lower_camel   connectionFactory, concurrentNumber
  katakana      バリデーション
  kanji         暗号化処理
  mixed         暗号化処理, 悲観ロック (kanji+katakana composite)

Java standard class names are filtered out (JAVA_STOPLIST). A caller-supplied
stopset (terms with df_pct > 20% in the corpus) can be applied via
`filter_terms` to prevent candidate explosion in downstream grep.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from tools.benchmark.classify_terms import JAVA_STOPLIST

PATTERN_ANNOTATION = re.compile(r'@([A-Za-z_][A-Za-z0-9_]{1,40})')
PATTERN_CAMEL = re.compile(r'\b([A-Z][a-z]+(?:[A-Z][a-zA-Z0-9_]*)+)\b')
PATTERN_LOWER_CAMEL = re.compile(r'\b([a-z][a-z0-9]+[A-Z][A-Za-z0-9]+)\b')
PATTERN_KATAKANA = re.compile(r'[゠-ヿー]{4,}')
PATTERN_KANJI = re.compile(r'[一-鿿]{4,}')
PATTERN_MIXED = re.compile(r'[一-鿿゠-ヿー]{4,}')

PATTERNS: list[tuple[str, re.Pattern]] = [
    ("annotation", PATTERN_ANNOTATION),
    ("camel", PATTERN_CAMEL),
    ("lower_camel", PATTERN_LOWER_CAMEL),
    ("katakana", PATTERN_KATAKANA),
    ("kanji", PATTERN_KANJI),
    ("mixed", PATTERN_MIXED),
]


def extract_terms(text: str) -> list[str]:
    """Extract grep-worthy terms from a question.

    - Deduplicates while preserving first-occurrence order.
    - Annotation matches are returned with the leading `@`.
    - Terms in JAVA_STOPLIST are dropped.
    """
    seen: set[str] = set()
    out: list[str] = []
    for name, pat in PATTERNS:
        for m in pat.finditer(text):
            term = "@" + m.group(1) if name == "annotation" else m.group(0)
            if term in seen:
                continue
            if term in JAVA_STOPLIST:
                continue
            seen.add(term)
            out.append(term)
    return out


def filter_terms(terms: list[str], *, stopset: set[str]) -> list[str]:
    """Drop any term present in `stopset`. Preserves order."""
    if not stopset:
        return list(terms)
    return [t for t in terms if t not in stopset]


def load_stopset(path: Path | None) -> set[str]:
    """Load a stopset from a JSON array file. Missing file → empty set."""
    if path is None or not path.exists():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"stopset file must be a JSON array: {path}")
    return {str(t) for t in data}

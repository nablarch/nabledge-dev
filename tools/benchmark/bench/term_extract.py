"""Question-side term extraction for the ids search variant.

Extracts identifier-only terms from the question for the body-grep path.
Japanese concepts are handled by `index-llm.md` (section-level keywords),
not here — empirically they either miss due to orthographic drift or hit
generic noise (チェック/レコード/クライアント) that eats the per-term cap.

Patterns (4+ chars, ASCII only):
  annotation    @Published, @UseToken
  camel         TransactionManagementHandler
  lower_camel   connectionFactory, concurrentNumber

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

# Minimum term length. Per docs/index-enrichment.md: 3 chars or less are
# too generic (they produce noisy grep hits and can usually be recovered
# via the 4+ composite form).
MIN_TERM_LENGTH = 4

# Identifier-only patterns. Japanese concepts are covered by index-llm.md
# section-level keywords; including them here produces noisy grep hits.
PATTERNS: list[tuple[str, re.Pattern]] = [
    ("annotation", PATTERN_ANNOTATION),
    ("camel", PATTERN_CAMEL),
    ("lower_camel", PATTERN_LOWER_CAMEL),
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
            if len(term) < MIN_TERM_LENGTH:
                continue
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

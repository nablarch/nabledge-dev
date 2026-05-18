"""Terms generator for RBKC — builds terms.json for keyword search.

Scans knowledge JSON files and extracts technical terms from section titles
and content, then builds a term → [path:sN, ...] reverse index.

Term extraction rules (keyword-search-design.md):
1. Java class names (CamelCase, 2+ chars)
2. Method names (camelCase: lowercase start, contains uppercase)
3. Annotations (@Name)
4. Japanese technical terms from section titles (full + verb-stripped)
5. English abbreviations (ALL_CAPS 2+ chars)
6. Property names (dot-separated 3+ segments)
7. Compound keywords (hyphen-separated, each part 2+ chars)

Exclusions: common words, single chars, high-frequency terms (section_df >= 7%).

Public API:
    extract_terms(content, title) -> set[str]
    build_terms_map(knowledge_dir) -> dict[str, list[str]]
    generate_terms(knowledge_dir, output_path) -> None
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Common English stop words (lowercase)
# ---------------------------------------------------------------------------
_ENGLISH_STOPWORDS = frozenset([
    "the", "is", "for", "and", "or", "a", "an", "to", "in", "of",
    "be", "by", "as", "at", "on", "it", "if", "do", "so", "no",
    "up", "use", "get", "set", "new", "not", "but", "all", "any",
    "can", "has", "its", "was", "are", "that", "this", "with", "from",
    "have", "will", "when", "then", "than", "each", "into", "also",
    "more", "some", "been", "used", "null", "true", "false", "java",
    "void", "class", "return", "string", "int", "long", "object",
    "list", "map", "type", "name", "value", "data", "result",
])

# Verb patterns to strip from Japanese section titles
_JP_VERB_PATTERNS = re.compile(
    r"(を使う|を行う|を使用する|を実装する|について|のやり方|する|します|の方法|の使い方)$"
)

# Pattern matchers
_CAMEL_CLASS = re.compile(r'\b([A-Z][a-zA-Z0-9]{1,})\b')
_CAMEL_METHOD = re.compile(r'\b([a-z][a-z0-9]*[A-Z][a-zA-Z0-9]*)\b')
_ANNOTATION = re.compile(r'@([A-Z][a-zA-Z0-9]+)')
_ABBREVIATION = re.compile(r'\b([A-Z]{2,})\b')
_PROPERTY = re.compile(r'\b([a-z][a-z0-9]*(?:\.[a-z][a-zA-Z0-9]*){2,})\b')
_COMPOUND = re.compile(r'\b([a-z][a-z0-9]+-[a-z][a-z0-9]+(?:-[a-z][a-z0-9]+)*)\b')

# Contains Japanese characters
_HAS_JAPANESE = re.compile(r'[぀-鿿]')


def extract_terms(content: str, title: str) -> set[str]:
    """Extract technical terms from section content and title.

    Args:
        content: Section body text.
        title: Section title.

    Returns:
        Set of extracted term strings.
    """
    terms: set[str] = set()
    combined = content + " " + title

    # 1. Java class names (CamelCase)
    for m in _CAMEL_CLASS.finditer(combined):
        w = m.group(1)
        if w.lower() not in _ENGLISH_STOPWORDS and len(w) >= 2:
            terms.add(w)

    # 2. Method names (camelCase)
    for m in _CAMEL_METHOD.finditer(combined):
        w = m.group(1)
        if w.lower() not in _ENGLISH_STOPWORDS:
            terms.add(w)

    # 3. Annotations
    for m in _ANNOTATION.finditer(combined):
        terms.add(f"@{m.group(1)}")

    # 4. Japanese technical terms from title
    if title and _HAS_JAPANESE.search(title):
        terms.add(title)
        stripped = _JP_VERB_PATTERNS.sub("", title)
        if stripped and stripped != title:
            terms.add(stripped)

    # 5. English abbreviations (ALL_CAPS 2+)
    for m in _ABBREVIATION.finditer(combined):
        w = m.group(1)
        if len(w) >= 2:
            terms.add(w)

    # 6. Property names (3+ dot segments)
    for m in _PROPERTY.finditer(combined):
        terms.add(m.group(1))

    # 7. Compound keywords (hyphen-separated)
    for m in _COMPOUND.finditer(combined):
        terms.add(m.group(0))

    # Remove single-char terms
    terms = {t for t in terms if len(t) >= 2}

    return terms


def build_terms_map(knowledge_dir: Path) -> dict[str, list[str]]:
    """Build term→[path:sN] reverse index from knowledge JSON files.

    High-frequency terms (section_df >= 7%) are excluded from the output
    to avoid search noise. section_df = count(sections containing term) /
    total section count.

    Args:
        knowledge_dir: Root directory containing knowledge JSON files.

    Returns:
        Dict mapping term string to sorted list of "path:sN" references.
    """
    # First pass: collect all (term, ref) pairs and count total sections
    raw: dict[str, list[str]] = {}
    total_sections = 0

    for json_path in sorted(knowledge_dir.rglob("*.json")):
        if json_path.stem.startswith("index") or json_path.stem.startswith("terms"):
            continue
        rel = json_path.relative_to(knowledge_dir)
        if len(rel.parts) < 2:
            continue
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if data.get("no_knowledge_content") is True:
            continue

        rel_str = str(rel).replace("\\", "/")
        for sec in data.get("sections", []):
            sid = sec.get("id", "")
            if not sid:
                continue
            total_sections += 1
            ref = f"{rel_str}:{sid}"
            for term in extract_terms(sec.get("content", ""), sec.get("title", "")):
                raw.setdefault(term, [])
                if ref not in raw[term]:
                    raw[term].append(ref)

    if total_sections == 0:
        return {}

    # Second pass: remove high-frequency terms (section_df >= 7%)
    # Minimum threshold of 2 ensures single-section corpora are not over-filtered.
    threshold = max(2, math.ceil(total_sections * 0.07))
    result: dict[str, list[str]] = {}
    for term, refs in raw.items():
        if len(refs) < threshold:
            result[term] = sorted(refs)

    return result


def generate_terms(knowledge_dir: Path, output_path: Path) -> None:
    """Write ``terms.json`` to *output_path* from knowledge JSON files.

    Args:
        knowledge_dir: Root directory containing knowledge JSON files.
        output_path: Destination path for ``terms.json``.
    """
    terms_map = build_terms_map(knowledge_dir)
    sorted_map = dict(sorted(terms_map.items()))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(sorted_map, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

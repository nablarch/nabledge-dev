"""Knowledge file verifier for RBKC — Phase 11.

Checks that generated knowledge JSON files faithfully represent their
source documents and that coverage requirements are met.

Verification strategy (per-file):
    A. Section titles: source headings are present in JSON sections
    B. Token coverage: ≥70% of sampled source tokens appear in JSON content
    C. Internal links: relative links in JSON content resolve to real files
    D. External URLs: https?:// URLs in source text appear in JSON content

Verification strategy (global):
    F. index.toon coverage: all JSON entries exist (excl. no_knowledge_content)
    H. Docs (MD) coverage: every JSON has a corresponding MD file

Public API:
    check_titles(source_text, data, fmt) -> list[str]          # Check A
    check_content(source_text, data, fmt) -> list[str]         # Check B
    check_internal_links(data, json_path, knowledge_dir) -> list[str]  # Check C
    check_external_urls(source_text, data) -> list[str]        # Check D
    check_index_coverage(knowledge_dir, index_path) -> list[str]  # Check F
    check_docs_coverage(knowledge_dir, docs_dir) -> list[str]  # Check H

    verify_file(source_path, json_path, fmt, knowledge_dir=None) -> list[str]

    _extract_text_tokens(text) -> list[str]   # kept for backward compatibility
"""
from __future__ import annotations

import json
import re
from pathlib import Path


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_MIN_TOKEN_COVERAGE = 0.7
_MAX_SAMPLE = 100

# RST underline characters (from rst converter)
_UNDERLINE_CHARS = set("=-~^+#*_.:`!\"'")

# Synthetic preamble title used by RST converter
_PREAMBLE_TITLE = "概要"


# ---------------------------------------------------------------------------
# Token extraction (public — kept for backward compatibility)
# ---------------------------------------------------------------------------

def _extract_text_tokens(text: str) -> list[str]:
    """Extract significant (non-trivial) words from plain text.

    CJK/Kana: ≥2 chars; ASCII: ≥3 chars.
    Ranges start at U+4E00 (not U+3000) to exclude ideographic spaces/punctuation.
    """
    tokens = re.findall(
        r"[\u4e00-\u9fff\u3400-\u4dbf\u30a0-\u30ff\u3040-\u309f]{2,}|\w{3,}",
        text,
    )
    return list(dict.fromkeys(tokens))  # deduplicate, preserve order


# ---------------------------------------------------------------------------
# RST heading detection (independent implementation, mirrors rst converter)
# ---------------------------------------------------------------------------

def _is_underline(line: str) -> bool:
    """Return True if *line* is a valid RST underline (all same char, ≥3)."""
    s = line.rstrip("\n").rstrip()
    if len(s) < 3:
        return False
    c = s[0]
    if c not in _UNDERLINE_CHARS:
        return False
    return all(x == c for x in s)


def _detect_rst_heading_chars(lines: list[str]) -> list[str]:
    """Return RST heading underline chars in order of first appearance."""
    chars: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Overline style: underline / title / underline
        if (
            i + 2 < len(lines)
            and _is_underline(line)
            and lines[i + 1].strip()
            and not _is_underline(lines[i + 1])
            and _is_underline(lines[i + 2])
            and line.rstrip()[0] == lines[i + 2].rstrip()[0]
        ):
            c = line.rstrip()[0]
            if c not in chars:
                chars.append(c)
            i += 3
            continue
        # Underline-only style: title / underline
        if (
            i + 1 < len(lines)
            and line.strip()
            and not _is_underline(line)
            and _is_underline(lines[i + 1])
            # Exclude: this title line is itself preceded by an overline
            and not (i > 0 and _is_underline(lines[i - 1])
                     and lines[i - 1].rstrip()[0] == lines[i + 1].rstrip()[0])
        ):
            c = lines[i + 1].rstrip()[0]
            if c not in chars:
                chars.append(c)
            i += 2
            continue
        i += 1
    return chars


def _extract_rst_section_headings(source_text: str) -> list[str]:
    """Extract h2/h3 section heading texts from RST source.

    Returns a list of heading texts (not including h1 title).
    "概要" (preamble) is excluded — it is synthetic and has no source heading.
    """
    lines = source_text.splitlines()
    heading_chars = _detect_rst_heading_chars(lines)
    if not heading_chars:
        return []

    h1_char = heading_chars[0]
    section_chars = set(heading_chars[1:3]) if len(heading_chars) >= 2 else set()
    if not section_chars:
        return []

    headings: list[str] = []
    found_h1 = False
    i = 0
    while i < len(lines):
        line = lines[i]
        # Overline heading
        if (
            i + 2 < len(lines)
            and _is_underline(line)
            and lines[i + 1].strip()
            and not _is_underline(lines[i + 1])
            and _is_underline(lines[i + 2])
            and line.rstrip()[0] == lines[i + 2].rstrip()[0]
        ):
            c = line.rstrip()[0]
            text = lines[i + 1].strip()
            if c == h1_char and not found_h1:
                found_h1 = True
            elif c in section_chars:
                headings.append(text)
            i += 3
            continue
        # Underline-only heading
        if (
            i + 1 < len(lines)
            and line.strip()
            and not _is_underline(line)
            and _is_underline(lines[i + 1])
            and not (i > 0 and _is_underline(lines[i - 1])
                     and lines[i - 1].rstrip()[0] == lines[i + 1].rstrip()[0])
        ):
            c = lines[i + 1].rstrip()[0]
            if c in heading_chars:
                text = line.strip()
                if c == h1_char and not found_h1:
                    found_h1 = True
                elif c in section_chars:
                    headings.append(text)
                i += 2
                continue
        i += 1
    return headings


def _extract_md_section_headings(source_text: str) -> list[str]:
    """Extract ## and ### headings from Markdown source text."""
    headings = []
    for line in source_text.splitlines():
        m = re.match(r"^#{2,3}\s+(.+)", line.rstrip())
        if m:
            headings.append(m.group(1).strip())
    return headings


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _json_text(data: dict) -> str:
    """Concatenate all section titles and content from a knowledge JSON."""
    parts = []
    for sec in data.get("sections", []):
        if sec.get("title"):
            parts.append(sec["title"])
        if sec.get("content"):
            parts.append(sec["content"])
    return " ".join(parts)


def _json_section_titles(data: dict) -> set[str]:
    """Return the set of section titles in a knowledge JSON."""
    return {sec["title"] for sec in data.get("sections", []) if sec.get("title")}


# ---------------------------------------------------------------------------
# Check A: Section titles
# ---------------------------------------------------------------------------

def check_titles(source_text: str, data: dict, fmt: str) -> list[str]:
    """Check A: source headings are present in JSON sections.

    For RST: h2/h3 headings must all appear in JSON section titles.
    For MD: ## and ### headings must all appear in JSON section titles.
    For XLSX: skip (always passes).

    '概要' in JSON does not require a matching source heading (it is synthetic).

    Returns:
        List of issue strings. Empty = OK.
    """
    if fmt == "xlsx":
        return []

    if fmt == "rst":
        source_headings = _extract_rst_section_headings(source_text)
    elif fmt == "md":
        source_headings = _extract_md_section_headings(source_text)
    else:
        return []

    if not source_headings:
        return []

    json_titles = _json_section_titles(data)
    issues = []
    for heading in source_headings:
        if heading not in json_titles:
            issues.append(f"Source heading not found in JSON sections: {heading!r}")
    return issues


# ---------------------------------------------------------------------------
# Check B: Token coverage
# ---------------------------------------------------------------------------

def check_content(source_text: str, data: dict, fmt: str) -> list[str]:
    """Check B: source token coverage >= 70% in JSON content.

    Returns:
        List of issue strings. Empty = OK.
    """
    if not data.get("sections"):
        if data.get("no_knowledge_content"):
            return []
        return ["sections list is empty but no_knowledge_content is not set"]

    # For RST, strip directive lines before token extraction
    if fmt == "rst":
        source_clean = re.sub(r"^\.\.\s+\w+.*$", "", source_text, flags=re.MULTILINE)
    else:
        source_clean = source_text

    source_tokens = _extract_text_tokens(source_clean)

    # Sample tokens evenly across the source
    if len(source_tokens) > _MAX_SAMPLE:
        step = len(source_tokens) // _MAX_SAMPLE
        source_tokens = source_tokens[::step][:_MAX_SAMPLE]

    if not source_tokens:
        return []

    json_text = _json_text(data)
    found = sum(1 for t in source_tokens if t in json_text)
    coverage = found / len(source_tokens)

    if coverage < _MIN_TOKEN_COVERAGE:
        return [
            f"Token coverage too low: {found}/{len(source_tokens)} "
            f"({coverage:.0%} < {_MIN_TOKEN_COVERAGE:.0%}) — "
            f"JSON may be missing significant content from source"
        ]
    return []


# ---------------------------------------------------------------------------
# Check C: Internal links
# ---------------------------------------------------------------------------

# Markdown link pattern: [text](url)
_MD_LINK_RE = re.compile(r"\[(?:[^\]]*)\]\(([^)]+)\)")


def check_internal_links(
    data: dict,
    json_path: Path,
    knowledge_dir: Path,
) -> list[str]:
    """Check C: relative links in JSON content resolve to real files.

    Skips:
    - https?:// (external links)

    For assets/ links: resolves as knowledge_dir / url (i.e., knowledge/assets/xxx).

    Returns:
        List of issue strings. Empty = OK.
    """
    issues = []
    all_content = _json_text(data)

    for m in _MD_LINK_RE.finditer(all_content):
        url = m.group(1).strip()
        # Skip external links
        if re.match(r"https?://", url):
            continue
        # Resolve relative to knowledge_dir (assets/ is a subdir of knowledge_dir)
        target = (knowledge_dir / url).resolve()
        if not target.exists():
            issues.append(f"Internal link target not found: {url!r}")

    return issues


# ---------------------------------------------------------------------------
# Check D: External URLs
# ---------------------------------------------------------------------------

# Matches bare https?:// URLs and RST inline URL `text <URL>`_
_URL_RE = re.compile(r"https?://[^\s>\)\]\"'\x60]+")

# RST external hyperlink target definition: .. _Name: URL
# These are reference definitions only and their URLs are skipped
_RST_HYPERLINK_DEF_RE = re.compile(
    r"^\.\.\s+_[^:]+:\s+(https?://\S+)\s*$",
    re.MULTILINE,
)


def check_external_urls(source_text: str, data: dict) -> list[str]:
    """Check D: https?:// URLs in source text appear in JSON content.

    RST hyperlink target definitions (.. _Name: URL) that are not
    referenced inline are skipped.

    Returns:
        List of issue strings. Empty = OK.
    """
    # Collect URLs that appear ONLY as RST hyperlink definitions (not inline)
    definition_only_urls: set[str] = set()
    inline_re = re.compile(r"`[^`]+<(https?://[^>]+)>`_")

    # Gather all definition URLs
    def_urls = {m.group(1) for m in _RST_HYPERLINK_DEF_RE.finditer(source_text)}
    # Gather all inline URLs
    inline_urls = {m.group(1) for m in inline_re.finditer(source_text)}
    # Bare URLs not preceded by < (excluding inline URL tails)
    # A URL is definition-only if it appears in a def but NOT inline
    definition_only_urls = def_urls - inline_urls

    # Collect all URLs from source
    all_source_urls = set(_URL_RE.findall(source_text))

    # Remove definition-only URLs from check set
    urls_to_check = all_source_urls - definition_only_urls

    if not urls_to_check:
        return []

    json_text = _json_text(data)
    issues = []
    for url in sorted(urls_to_check):
        if url not in json_text:
            issues.append(f"External URL in source not found in JSON content: {url!r}")
    return issues


# ---------------------------------------------------------------------------
# Check F: index.toon coverage
# ---------------------------------------------------------------------------

def check_index_coverage(knowledge_dir: Path, index_path: Path) -> list[str]:
    """Check F: all JSON files have entries in index.toon.

    JSON files with no_knowledge_content=True are excluded.

    Returns:
        List of issue strings. Empty = OK.
    """
    if not index_path.exists():
        return [f"index.toon not found: {index_path}"]

    # Parse index.toon entries (last field of comma-separated line = relative path)
    indexed_paths: set[str] = set()
    index_text = index_path.read_text(encoding="utf-8")
    for line in index_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("files["):
            continue
        parts = [p.strip() for p in stripped.split(",")]
        if len(parts) >= 5:
            rel_path = parts[-1].strip()
            if rel_path.endswith(".json"):
                indexed_paths.add(rel_path)

    # Find all JSON files in knowledge_dir (excluding index.toon itself)
    issues = []
    for json_path in sorted(knowledge_dir.rglob("*.json")):
        rel = json_path.relative_to(knowledge_dir).as_posix()
        # Check if no_knowledge_content
        try:
            file_data = json.loads(json_path.read_text(encoding="utf-8"))
            if file_data.get("no_knowledge_content"):
                continue
        except Exception:
            pass
        if rel not in indexed_paths:
            issues.append(f"JSON file not in index.toon: {rel}")
    return issues


# ---------------------------------------------------------------------------
# Check H: Docs (MD) coverage
# ---------------------------------------------------------------------------

def check_docs_coverage(knowledge_dir: Path, docs_dir: Path) -> list[str]:
    """Check H: every JSON file has a corresponding MD file in docs_dir.

    Returns:
        List of issue strings. Empty = OK.
    """
    if not docs_dir.exists():
        return [f"docs directory not found: {docs_dir}"]

    issues = []
    for json_path in sorted(knowledge_dir.rglob("*.json")):
        rel = json_path.relative_to(knowledge_dir)
        md_path = docs_dir / rel.with_suffix(".md")
        if not md_path.exists():
            issues.append(f"Missing docs MD file: {rel.with_suffix('.md')}")
    return issues


# ---------------------------------------------------------------------------
# Check A/B/C/D for docs MD files (B2 fix)
# ---------------------------------------------------------------------------

def check_docs_md_titles(source_text: str, docs_md_text: str, fmt: str) -> list[str]:
    """Check A for docs MD: source headings present as ##/### in docs MD.

    For RST: h2/h3 headings must appear as ## or ### headings in docs MD.
    For MD: ## and ### headings must appear in docs MD.
    For XLSX: skip (always passes).

    Returns:
        List of issue strings. Empty = OK.
    """
    if fmt == "xlsx":
        return []

    if fmt == "rst":
        source_headings = _extract_rst_section_headings(source_text)
    elif fmt == "md":
        source_headings = _extract_md_section_headings(source_text)
    else:
        return []

    if not source_headings:
        return []

    # Extract ##/### headings from docs MD
    docs_md_headings: set[str] = set()
    for line in docs_md_text.splitlines():
        m = re.match(r"^#{2,3}\s+(.+)", line.rstrip())
        if m:
            docs_md_headings.add(m.group(1).strip())

    issues = []
    for heading in source_headings:
        if heading not in docs_md_headings:
            issues.append(f"Source heading not found in docs MD: {heading!r}")
    return issues


def check_docs_md_content(source_text: str, docs_md_text: str, fmt: str) -> list[str]:
    """Check B for docs MD: source token coverage >= 70% in docs MD text.

    Returns:
        List of issue strings. Empty = OK.
    """
    if fmt == "xlsx":
        return []

    if fmt == "rst":
        source_clean = re.sub(r"^\.\.\s+\w+.*$", "", source_text, flags=re.MULTILINE)
    else:
        source_clean = source_text

    source_tokens = _extract_text_tokens(source_clean)

    if len(source_tokens) > _MAX_SAMPLE:
        step = len(source_tokens) // _MAX_SAMPLE
        source_tokens = source_tokens[::step][:_MAX_SAMPLE]

    if not source_tokens:
        return []

    found = sum(1 for t in source_tokens if t in docs_md_text)
    coverage = found / len(source_tokens)

    if coverage < _MIN_TOKEN_COVERAGE:
        return [
            f"Token coverage too low: {found}/{len(source_tokens)} "
            f"({coverage:.0%} < {_MIN_TOKEN_COVERAGE:.0%}) — "
            f"docs MD may be missing significant content from source"
        ]
    return []


def check_docs_md_links(docs_md_text: str, docs_md_path: Path) -> list[str]:
    """Check C for docs MD: relative links resolve to real files (docs MD-relative).

    Skips https?:// links.

    Returns:
        List of issue strings. Empty = OK.
    """
    issues = []
    for m in _MD_LINK_RE.finditer(docs_md_text):
        url = m.group(1).strip()
        # Skip external links
        if re.match(r"https?://", url):
            continue
        # Resolve relative to the docs MD file's directory
        target = (docs_md_path.parent / url).resolve()
        if not target.exists():
            issues.append(f"Docs MD link target not found: {url!r}")
    return issues


def check_docs_md_urls(source_text: str, docs_md_text: str) -> list[str]:
    """Check D for docs MD: https?:// URLs in source text appear in docs MD.

    RST hyperlink target definitions (.. _Name: URL) that are not
    referenced inline are skipped (same logic as check_external_urls).

    Returns:
        List of issue strings. Empty = OK.
    """
    inline_re = re.compile(r"`[^`]+<(https?://[^>]+)>`_")
    def_urls = {m.group(1) for m in _RST_HYPERLINK_DEF_RE.finditer(source_text)}
    inline_urls = {m.group(1) for m in inline_re.finditer(source_text)}
    definition_only_urls = def_urls - inline_urls

    all_source_urls = set(_URL_RE.findall(source_text))
    urls_to_check = all_source_urls - definition_only_urls

    if not urls_to_check:
        return []

    issues = []
    for url in sorted(urls_to_check):
        if url not in docs_md_text:
            issues.append(f"External URL in source not found in docs MD: {url!r}")
    return issues


def verify_docs_md(source_path: Path, docs_md_path: Path, fmt: str) -> list[str]:
    """Verify a docs MD file against its source (checks A, B, C, D for docs MD).

    Args:
        source_path: Path to the original source file.
        docs_md_path: Path to the generated docs MD file.
        fmt: File format — 'rst', 'md', or 'xlsx'.

    Returns:
        List of issue strings. Empty list means the file passes verification.
    """
    if not source_path.exists():
        return [f"Source file not found: {source_path}"]
    if not docs_md_path.exists():
        return [f"docs MD not found: {docs_md_path}"]
    if fmt not in ("rst", "md", "xlsx"):
        return [f"Unknown format: {fmt}"]

    if fmt == "xlsx":
        return []

    source_text = source_path.read_text(encoding="utf-8", errors="replace")
    docs_md_text = docs_md_path.read_text(encoding="utf-8")
    issues = []

    # Check A: source headings present in docs MD
    issues.extend(check_docs_md_titles(source_text, docs_md_text, fmt))

    # Check B: token coverage in docs MD
    issues.extend(check_docs_md_content(source_text, docs_md_text, fmt))

    # Check C: relative links in docs MD resolve
    issues.extend(check_docs_md_links(docs_md_text, docs_md_path))

    # Check D: external URLs in source appear in docs MD
    issues.extend(check_docs_md_urls(source_text, docs_md_text))

    return issues


# ---------------------------------------------------------------------------
# Per-file verifier (public API)
# ---------------------------------------------------------------------------

def verify_file(
    source_path: Path,
    json_path: Path,
    fmt: str,
    knowledge_dir: Path | None = None,
) -> list[str]:
    """Verify a knowledge JSON file against its source (checks A, B, C, D).

    Args:
        source_path: Path to the original source file.
        json_path: Path to the generated knowledge JSON.
        fmt: File format — 'rst', 'md', or 'xlsx'.
        knowledge_dir: Root of knowledge directory (for internal link resolution).
                       If None, check C is skipped.

    Returns:
        List of issue strings. Empty list means the file passes verification.
    """
    if not source_path.exists():
        return [f"Source file not found: {source_path}"]
    if not json_path.exists():
        return [f"JSON file not found: {json_path}"]
    if fmt not in ("rst", "md", "xlsx"):
        return [f"Unknown format: {fmt}"]

    data = json.loads(json_path.read_text(encoding="utf-8"))

    if fmt == "xlsx":
        issues = []
        if not data.get("sections") and not data.get("no_knowledge_content"):
            issues.append("XLSX knowledge file has no sections")
        return issues

    source_text = source_path.read_text(encoding="utf-8", errors="replace")
    issues = []

    # Check A: section titles
    issues.extend(check_titles(source_text, data, fmt))

    # Check B: token coverage
    issues.extend(check_content(source_text, data, fmt))

    # Check C: internal links (only when knowledge_dir is provided)
    if knowledge_dir is not None:
        issues.extend(check_internal_links(data, json_path, knowledge_dir))

    # Check D: external URLs
    issues.extend(check_external_urls(source_text, data))

    return issues

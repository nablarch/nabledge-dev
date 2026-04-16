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

# Toctree directive names that introduce toctree entry blocks
_TOCTREE_DECL_RE = re.compile(r"^\.\.\s+toc(?:tree|list)::")

# URL pattern — URLs are checked by Check D, skip their tokens in content checks
_URL_STRIP_RE = re.compile(r"https?://\S+")
_PREAMBLE_TITLE = "概要"


# ---------------------------------------------------------------------------
# Phase 17-A: MD syntax stripping and RST line classification
# ---------------------------------------------------------------------------

# Inline role pattern: :role:`display<target>` or :role:`text`
# Handles both :role:`text` and :namespace:role:`text` (e.g. :java:extdoc:`...`)
_INLINE_ROLE_RE = re.compile(r":(?:[a-z][a-z_-]*:)+`([^`<]*?)(?:<[^>]*>)?`")


def strip_md_syntax(text: str) -> str:
    """Remove Markdown formatting syntax from text, preserving content tokens.

    Removes: ## headings, | table syntax, **bold**, `code`, [text](url) links,
    - bullet list markers, and other common MD syntax markers.

    Returns plain text suitable for token comparison.
    """
    lines = []
    for line in text.splitlines():
        # Remove ## heading markers
        stripped = re.sub(r"^#{1,6}\s+", "", line)
        # Remove table separator rows (|---|---|)
        stripped = re.sub(r"^[|\s-]+$", "", stripped) if re.match(r"^[\s|:-]+$", stripped) else stripped
        # Remove leading - for bullet lists (but preserve text after)
        stripped = re.sub(r"^\s*[-*+]\s+", " ", stripped)
        # Remove | table pipes (preserve cell content)
        stripped = stripped.replace("|", " ")
        # Remove ** bold/italic markers
        stripped = re.sub(r"\*{1,3}", "", stripped)
        # Remove [text](url) link syntax — keep link text
        stripped = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", stripped)
        # Remove `code` backtick markers
        stripped = stripped.replace("`", "")
        lines.append(stripped)
    return "\n".join(lines)


def classify_line(line: str, in_toctree: bool = False) -> str:
    """Classify an RST source line into a syntax category or 'content'.

    Categories:
        section_decoration  RST underline/overline (===, ---, ~~~, etc.)
        rst_label           .. _label: reference target definition
        directive_decl      .. directive:: declaration line
        directive_option    :option: value lines (indented directive options)
        toctree_entry       indented path-like entries under toctree/toclist
        content             normal text line (including inline roles, blank lines)

    Args:
        line: Source line text.
        in_toctree: If True, indented non-option lines are classified as
                    toctree_entry (context passed by caller tracking toctree blocks).

    Returns:
        Category string.
    """
    stripped = line.rstrip()
    raw = stripped.lstrip()

    # Blank / whitespace-only → content
    if not raw:
        return "content"

    # Section decoration: all same underline char, length >= 3
    if _is_underline(stripped):
        return "section_decoration"

    # RST label: .. _name: (with optional leading whitespace)
    if re.match(r"^\.\.\s+_[^:]+:\s*$", raw):
        return "rst_label"

    # Directive declaration: .. word:: (may have arguments after ::)
    if re.match(r"^\.\.\s+[\w-]+::(\s|$)", raw):
        return "directive_decl"

    # Directive option: :word: (indented, starts with colon-word-colon)
    if re.match(r"^\s{1,}:[a-z][a-z_-]*:", line):
        return "directive_option"

    # Toctree entry: indented line inside toctree/toclist context
    # (caller tracks whether we're inside a toctree directive)
    if in_toctree and re.match(r"^\s+\S", line) and not re.match(r"^\s+:[a-z]", line):
        return "toctree_entry"

    # Fallback: path-like indented lines (contain / without being directive options)
    if re.match(r"^\s+\S", line) and not re.match(r"^\s+:[a-z]", line):
        path_candidate = raw
        if "/" in path_candidate or path_candidate.endswith((".rst", ".md")):
            return "toctree_entry"

    return "content"


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
    """Concatenate title, all section titles and content from a knowledge JSON."""
    parts = []
    if data.get("title"):
        parts.append(data["title"])
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

def _classify_source_lines(source_text: str) -> list[str]:
    """Classify each line in RST/MD source text with toctree context tracking.

    Returns a list of category strings (one per line) using classify_line().
    Tracks toctree/toclist directive context so that bare path entries like
    'architecture' (no / suffix) are correctly classified as toctree_entry
    rather than content.

    toctree_indent records the indentation of the '.. toctree::' line itself.
    Entries are always more indented than the directive declaration, so
    `current_indent > toctree_indent` reliably identifies toctree body lines.
    """
    lines = source_text.splitlines()
    line_categories: list[str] = []
    in_toctree = False
    toctree_indent: int | None = None

    for line in lines:
        raw = line.lstrip()

        # Detect start of toctree/toclist directive
        if _TOCTREE_DECL_RE.match(raw):
            in_toctree = True
            toctree_indent = len(line) - len(raw)
            line_categories.append("directive_decl")
            continue

        # Inside toctree: check if still in the indented block
        if in_toctree:
            if not raw:
                # Blank line: stay in toctree (blank lines allowed between entries)
                line_categories.append("content")
                continue
            current_indent = len(line) - len(line.lstrip())
            if current_indent > (toctree_indent or 0):
                # Still inside toctree block
                cat = classify_line(line, in_toctree=True)
                line_categories.append(cat)
                continue
            else:
                # Dedented: toctree block ended
                in_toctree = False
                toctree_indent = None

        line_categories.append(classify_line(line, in_toctree=False))

    return line_categories


def _build_token_categories(source_text: str) -> dict[str, set[str]]:
    """Extract content tokens from source text, keyed by line category.

    Returns a dict mapping each token to the set of line categories where
    it appears. URLs are stripped from content lines (covered by Check D).
    Inline RST roles are reduced to their display text.
    """
    lines = source_text.splitlines()
    line_categories = _classify_source_lines(source_text)

    token_categories: dict[str, set[str]] = {}
    for line, cat in zip(lines, line_categories):
        if cat == "content":
            effective = _INLINE_ROLE_RE.sub(r"\1", line)
            effective = _URL_STRIP_RE.sub("", effective)
        else:
            effective = line
        for tok in _extract_text_tokens(effective):
            token_categories.setdefault(tok, set()).add(cat)

    return token_categories


def check_content(source_text: str, data: dict, fmt: str) -> list[str]:
    """Check B: content tokens in RST source are present in JSON (diff-based).

    Algorithm:
        1. Build JSON content token set (after strip_md_syntax to remove MD formatting)
        2. For each RST source token NOT in the JSON token set:
           a. If ALL occurrences in the source are on syntax lines → OK
              (toctree entries, directive options, RST labels, etc.)
           b. If ANY occurrence is on a content line → FAIL
              (RBKC missed converting this content token)

    For MD format: uses line-level classification (# headings are syntax, content otherwise).
    For XLSX format: always passes (no text content to verify).

    Returns:
        List of issue strings (missing content tokens). Empty = OK.
    """
    if fmt == "xlsx":
        return []
    if data.get("no_knowledge_content"):
        return []

    # Build JSON token set (strip MD formatting first)
    json_raw = _json_text(data)
    json_clean = strip_md_syntax(json_raw)
    json_tokens = set(_extract_text_tokens(json_clean))

    token_categories = _build_token_categories(source_text)

    # Find tokens that appear on content lines but are missing from JSON
    issues = []
    for token, categories in sorted(token_categories.items()):
        if token in json_tokens:
            continue
        if "content" in categories:
            issues.append(
                f"Content token missing from JSON: {token!r} "
                f"(appears on content line in source)"
            )

    return issues


# ---------------------------------------------------------------------------
# Check C: Source-driven link verification
# ---------------------------------------------------------------------------

# RST label definition: .. _label-name: or .. _`label-name`:
_RST_LABEL_DEF_RE = re.compile(r"^\.\.\s+_`?([^`:]+)`?:\s*$", re.MULTILINE)

# :ref:`label` or :ref:`display text <label>`
_RST_REF_RE = re.compile(r":ref:`([^`<]*?)(?:<([^>]*)>)?`")

# .. figure:: path  or  .. image:: path
_RST_FIGURE_RE = re.compile(r"^\.\.\s+(?:figure|image)::\s+(\S+)", re.MULTILINE)

# .. literalinclude:: path
_RST_LITERALINCLUDE_RE = re.compile(r"^\.\.\s+literalinclude::\s+(\S+)", re.MULTILINE)

# MD link: [text](url) — url must not contain [ or ] (guards against Java type notation)
_MD_SOURCE_LINK_RE = re.compile(r"\[(?:[^\]]*)\]\(([^)\[\]]+)\)")


def build_label_map(source_dir: Path) -> dict[str, Path]:
    """Scan all RST files under source_dir and collect label definitions.

    Returns:
        Dict mapping label name → RST file path.
        Duplicate labels: last definition wins (matches Sphinx behavior).
        Labels containing '外部サイト' (external site markers) are skipped.
    """
    label_map: dict[str, Path] = {}
    for rst_path in sorted(source_dir.rglob("*.rst")):
        text = rst_path.read_text(encoding="utf-8", errors="replace")
        for m in _RST_LABEL_DEF_RE.finditer(text):
            label = m.group(1).strip()
            if "外部サイト" in label:
                continue
            label_map[label] = rst_path
    return label_map


def check_source_links(
    source_text: str,
    fmt: str,
    data: dict,
    label_map: dict[str, Path],
    source_path: Path | None = None,
) -> list[str]:
    """Check C: source-driven link verification.

    For RST sources:
    - :ref:`label` or :ref:`text <label>`: resolved via label_map.
      Unresolvable → FAIL. Resolved but absent from JSON content → FAIL.
    - .. figure:: / .. image:: / .. literalinclude:: paths:
      Resolved relative to source_path. Missing file → FAIL.

    For MD sources:
    - [text](path): resolved relative to source_path.
      External (https://) links are skipped.
      Paths containing [ or ] are not treated as links (Java type notation guard).
      Missing file → FAIL.

    Returns:
        List of issue strings. Empty = OK.
    """
    issues = []
    json_content = _json_text(data)

    if fmt == "rst":
        # :ref: references
        for m in _RST_REF_RE.finditer(source_text):
            label = (m.group(2) or m.group(1)).strip()
            if label not in label_map:
                issues.append(f"Unresolvable :ref: label: {label!r}")
            elif label not in json_content:
                issues.append(f":ref: label resolved but missing from JSON: {label!r}")

        # .. figure:: / .. image:: / .. literalinclude::
        if source_path is not None:
            for pattern in (_RST_FIGURE_RE, _RST_LITERALINCLUDE_RE):
                for m in pattern.finditer(source_text):
                    rel_path = m.group(1)
                    target = (source_path.parent / rel_path).resolve()
                    if not target.exists():
                        issues.append(f"Asset/include file not found: {rel_path!r}")

    elif fmt == "md" and source_path is not None:
        for m in _MD_SOURCE_LINK_RE.finditer(source_text):
            url = m.group(1).strip()
            if re.match(r"https?://", url):
                continue
            target = (source_path.parent / url).resolve()
            if not target.exists():
                issues.append(f"MD link target not found: {url!r}")

    return issues


# ---------------------------------------------------------------------------
# Check E: JSON ↔ docs MD consistency
# ---------------------------------------------------------------------------

# Extract keywords block from docs MD: <details><summary>keywords</summary>\n\nkw1, kw2\n
_DOCS_MD_KEYWORDS_RE = re.compile(
    r"<details>\s*<summary>keywords</summary>\s*\n\n([^\n]+)\n",
    re.IGNORECASE,
)

# Extract # title from docs MD
_DOCS_MD_H1_RE = re.compile(r"^#\s+(.+)", re.MULTILINE)

# Extract ## / ### section titles from docs MD
_DOCS_MD_HEADING_RE = re.compile(r"^#{2,3}\s+(.+)", re.MULTILINE)


def check_json_docs_md_consistency(data: dict, docs_md_text: str) -> list[str]:
    """Check E: JSON and docs MD must be exactly consistent.

    Checks:
    - JSON title == docs MD # heading
    - Each JSON section title appears as ## or ### heading in docs MD
    - Each JSON section's hints appear in the corresponding keywords block
    - Each JSON section's content text appears in docs MD

    Returns:
        List of issue strings. Empty = OK.
    """
    issues = []

    # Title check
    h1_match = _DOCS_MD_H1_RE.search(docs_md_text)
    docs_title = h1_match.group(1).strip() if h1_match else ""
    json_title = data.get("title", "")
    if json_title != docs_title:
        issues.append(f"Title mismatch: JSON={json_title!r}, docs MD={docs_title!r}")

    # Collect docs MD headings and keywords blocks
    docs_headings = {m.group(1).strip() for m in _DOCS_MD_HEADING_RE.finditer(docs_md_text)}
    docs_keywords_blocks = [m.group(1) for m in _DOCS_MD_KEYWORDS_RE.finditer(docs_md_text)]
    all_keywords_text = " ".join(docs_keywords_blocks)

    for sec in data.get("sections", []):
        sec_title = sec.get("title", "")
        sec_content = sec.get("content", "")
        sec_hints = sec.get("hints", [])

        # Section title check
        if sec_title and sec_title not in docs_headings:
            issues.append(f"Section title missing from docs MD: {sec_title!r}")

        # Hints check
        for hint in sec_hints:
            if hint not in all_keywords_text:
                issues.append(f"Hint missing from docs MD keywords: {hint!r}")

        # Content check: key tokens from JSON content must appear in docs MD
        if sec_content and sec_content not in docs_md_text:
            # Token-level check: at least one distinctive phrase must appear
            # Use first 50 chars of content as a representative sample
            sample = sec_content[:50].strip()
            if sample and sample not in docs_md_text:
                issues.append(
                    f"Section content missing from docs MD: section={sec_title!r}, "
                    f"sample={sample!r}"
                )

    return issues


# ---------------------------------------------------------------------------
# Legacy Check C: kept for backward compatibility during transition
# (will be removed once check_source_links is fully integrated)
# ---------------------------------------------------------------------------

# Markdown link pattern: [text](url)
_MD_LINK_RE = re.compile(r"\[(?:[^\]]*)\]\(([^)]+)\)")


def check_internal_links(
    data: dict,
    json_path: Path,
    knowledge_dir: Path,
) -> list[str]:
    """Legacy Check C: relative links in JSON content resolve to real files.

    Deprecated: use check_source_links() instead.
    Kept for backward compatibility during Phase 17-B transition.
    """
    issues = []
    all_content = _json_text(data)

    for m in _MD_LINK_RE.finditer(all_content):
        url = m.group(1).strip()
        if re.match(r"https?://", url):
            continue
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
    """Check B for docs MD: content tokens in source are present in docs MD (diff-based).

    Uses the same diff-based algorithm as check_content():
    - RST syntax lines (toctree entries, directive options, labels) are excluded
    - Content line tokens missing from docs MD text → FAIL

    Returns:
        List of issue strings. Empty = OK.
    """
    if fmt == "xlsx":
        return []

    # Build docs MD token set (strip MD formatting first)
    docs_clean = strip_md_syntax(docs_md_text)
    docs_tokens = set(_extract_text_tokens(docs_clean))

    token_categories = _build_token_categories(source_text)

    issues = []
    for token, categories in sorted(token_categories.items()):
        if token in docs_tokens:
            continue
        if "content" in categories:
            issues.append(
                f"Content token missing from docs MD: {token!r} "
                f"(appears on content line in source)"
            )

    return issues


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

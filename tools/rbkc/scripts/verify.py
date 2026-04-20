"""RBKC verify — quality gate for RBKC output.

Checks that knowledge JSON files correctly represent their source documents.
See: tools/rbkc/docs/rbkc-verify-quality-design.md

Public API:
    check_json_docs_md_consistency(data, docs_md_text) -> list[str]  # QO5
    check_format_purity(data, fmt) -> list[str]                      # QC5
    check_hints_completeness(data, prev_hints) -> list[str]          # QC6
    check_content_completeness(source_text, data, fmt) -> list[str]  # QC1/QC2/QC3/QC4
    check_external_urls(source_text, data, fmt) -> list[str]         # QL2
    verify_file(source_path, json_path, fmt, knowledge_dir) -> list[str]
    verify_docs_md(source_path, docs_md_path, fmt) -> list[str]
    check_index_coverage(knowledge_dir, index_path) -> list[str]
    check_docs_coverage(knowledge_dir, docs_dir) -> list[str]
    build_label_map(source_dir) -> dict
    check_source_links(source_text, fmt, data, label_map, source_path) -> list[str]
"""
from __future__ import annotations

import re
from pathlib import Path


# ---------------------------------------------------------------------------
# QO5: docs MD content 完全一致
# ---------------------------------------------------------------------------

def check_json_docs_md_consistency(data: dict, docs_md_text: str) -> list[str]:
    """QO5: Verify each section's content appears verbatim in docs MD.

    Args:
        data: Knowledge JSON dict.
        docs_md_text: Full text of the corresponding docs MD file.

    Returns:
        List of FAIL messages. Empty if all content is present.
    """
    if data.get("no_knowledge_content"):
        return []

    issues = []
    for section in data.get("sections", []):
        content = section.get("content", "")
        title = section.get("title", "")
        if not content:
            continue
        # Skip sections containing assets/ links: docs.py rewrites those paths
        # (relative to docs MD location), so verbatim match would always fail.
        # assets/ link fidelity is covered by the existing test_asset_links_rewritten_to_resolve
        # test in test_index_docs.py.
        if "assets/" in content:
            continue
        if content not in docs_md_text:
            issues.append(
                f"[QO5] section '{title}': content not found verbatim in docs MD"
            )
    return issues


# ---------------------------------------------------------------------------
# QC5: 形式純粋性
# ---------------------------------------------------------------------------

# RST syntax patterns that must not appear in JSON output
_RST_ROLE_RE = re.compile(r':[a-zA-Z][a-zA-Z0-9_.-]*:`')
_RST_DIRECTIVE_RE = re.compile(r'\.\.\s+\S+.*::')
# Heading underlines (====, ----, etc.) are only checked in title fields.
# Content fields may contain code examples with lines of dashes/equals that are
# legitimate (e.g. inside fenced code blocks), so applying this check to content
# would produce false FAILs.
_RST_HEADING_UNDERLINE_RE = re.compile(r'^[=\-~^"\'`#*+<>]{4,}\s*$', re.MULTILINE)
_RST_LABEL_RE = re.compile(r'\.\.\s+_[a-zA-Z0-9_-]+:')

# MD syntax patterns that must not appear in JSON output.
# Negative lookbehind (?<![a-zA-Z]) prevents matching Java generic types like
# List<String> or Map<K, V> where < is immediately preceded by a letter (part of
# an identifier). Digits and other characters are not excluded: "Step 1<br>text"
# correctly detects the <br> tag even though a digit precedes it.
_MD_RAW_HTML_RE = re.compile(r'(?<![a-zA-Z])<[a-zA-Z][a-zA-Z0-9]*[\s>]')
_MD_BACKSLASH_ESCAPE_RE = re.compile(r'\\[*_`\[\](){}#+\-.!|]')


def _check_rst_syntax(text: str, location: str, *, is_title: bool = False) -> list[str]:
    """Check text for RST-specific syntax remnants.

    Args:
        text: The text to check.
        location: Human-readable location for error messages.
        is_title: When True, also checks for heading underlines (=====, -----).
                  Heading underlines are only meaningful in titles; content fields
                  may legitimately contain such patterns inside code blocks.
    """
    issues = []
    if _RST_ROLE_RE.search(text):
        issues.append(f"[QC5] {location}: RST role syntax detected (e.g. :role:`text`)")
    if _RST_DIRECTIVE_RE.search(text):
        issues.append(f"[QC5] {location}: RST directive syntax detected (e.g. .. directive::)")
    if is_title and _RST_HEADING_UNDERLINE_RE.search(text):
        issues.append(f"[QC5] {location}: RST heading underline detected (e.g. ====)")
    if _RST_LABEL_RE.search(text):
        issues.append(f"[QC5] {location}: RST label definition detected (e.g. .. _label:)")
    return issues


def _check_md_syntax(text: str, location: str) -> list[str]:
    """Check text for MD-specific syntax remnants."""
    issues = []
    if _MD_RAW_HTML_RE.search(text):
        issues.append(f"[QC5] {location}: raw HTML tag detected (e.g. <details>, <br>)")
    if _MD_BACKSLASH_ESCAPE_RE.search(text):
        issues.append(f"[QC5] {location}: backslash escape detected (e.g. \\*)")
    return issues


def check_format_purity(data: dict, fmt: str) -> list[str]:
    """QC5: Verify no format-specific syntax remains in JSON content/title.

    Args:
        data: Knowledge JSON dict.
        fmt: Source format ('rst', 'md', or 'xlsx').

    Returns:
        List of FAIL messages. Empty if output is format-clean.
    """
    if fmt == "xlsx":
        return []

    issues = []
    file_id = data.get("id", "?")

    # Check file-level title
    title = data.get("title", "")
    if fmt == "rst":
        issues.extend(_check_rst_syntax(title, f"{file_id}/title", is_title=True))
    elif fmt == "md":
        issues.extend(_check_md_syntax(title, f"{file_id}/title"))

    # Check each section's title and content
    for section in data.get("sections", []):
        sec_title = section.get("title", "")
        content = section.get("content", "")
        location_t = f"{file_id}/section '{sec_title}'/title"
        location_c = f"{file_id}/section '{sec_title}'/content"

        if fmt == "rst":
            # is_title=True for section titles; content fields are not checked for
            # heading underlines since code examples may contain === or --- lines.
            issues.extend(_check_rst_syntax(sec_title, location_t, is_title=True))
            issues.extend(_check_rst_syntax(content, location_c, is_title=False))
        elif fmt == "md":
            issues.extend(_check_md_syntax(sec_title, location_t))
            issues.extend(_check_md_syntax(content, location_c))

    return issues


# ---------------------------------------------------------------------------
# QC6: hints 完全性
# ---------------------------------------------------------------------------

def check_hints_completeness(
    data: dict,
    prev_hints: dict[str, dict[str, list[str]]],
) -> list[str]:
    """QC6: Verify all hints from previous run are present in current output.

    Args:
        data: Current knowledge JSON dict.
        prev_hints: {file_id: {section_title: hints}} from the previous run.

    Returns:
        List of FAIL messages for each missing hint.
    """
    file_id = data.get("id", "")
    file_prev = prev_hints.get(file_id)
    if not file_prev:
        return []

    issues = []
    for section in data.get("sections", []):
        title = section.get("title", "")
        current_hints = set(section.get("hints", []))
        expected_hints = file_prev.get(title, [])

        for hint in expected_hints:
            if hint not in current_hints:
                issues.append(
                    f"[QC6] section '{title}': hint '{hint}' missing from current output"
                )
    return issues


# ---------------------------------------------------------------------------
# QC1/QC2/QC3: Content completeness — sequential-delete algorithm (RST/MD)
# ---------------------------------------------------------------------------

def _strip_md_syntax_to_plain_lines(text: str) -> list[str]:
    """Strip Markdown syntax from JSON content, return non-empty plain-text lines."""
    result = []
    in_fence = False
    for line in text.split('\n'):
        if re.match(r'^\s*```', line):
            in_fence = not in_fence
            continue
        if in_fence:
            if line.strip():
                result.append(line)
            continue
        l = re.sub(r'^#+\s*', '', line)
        l = re.sub(r'^>\s?', '', l)
        # Strip admonition labels like "**Note:**" / "**注意:**" before bold removal
        l = re.sub(r'^\*\*[^\*]+[：:]\*\*\s*', '', l)
        # Strip bold (**text**) and italic (*text*), but not snake_case underscores
        l = re.sub(r'\*\*(.+?)\*\*', r'\1', l)
        l = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'\1', l)
        l = re.sub(r'(?<![a-zA-Z0-9_])__(.+?)__(?![a-zA-Z0-9_])', r'\1', l)
        l = re.sub(r'(?<![a-zA-Z0-9_])_([^_\s][^_]*)_(?![a-zA-Z0-9_])', r'\1', l)
        if l.strip():
            result.append(l)
    return result


def _is_rst_syntax_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return True
    if re.match(r"^[=\-~^\"'`#*+<>]{4,}\s*$", s):
        return True
    if re.match(r'^\.\.\s*(\S.*::|$)', s):
        return True
    if re.match(r'^\.\.\s+_[a-zA-Z0-9_-]+:', s):
        return True
    # Substitution definitions: ".. |name| replace:: ..."
    if re.match(r'^\.\.\s+\|', s):
        return True
    if re.match(r'^:[a-zA-Z][a-zA-Z0-9_.-]*:`', s):
        return True
    if re.match(r'^\s+:[a-zA-Z]', line):
        return True
    return False


def _is_md_syntax_line(line: str, in_frontmatter: bool = False) -> bool:
    s = line.strip()
    if not s:
        return True
    if re.match(r'^---+\s*$', s):
        return True
    if in_frontmatter:
        return True
    if re.match(r'^```', s):
        return True
    if re.match(r'^<!--', s):
        return True
    if re.match(r'^#+\s*', s):
        return True
    return False


def check_content_completeness(source_text: str, data: dict, fmt: str) -> list[str]:
    """QC1/QC2/QC3/QC4: Verify JSON content covers source via sequential-delete algorithm."""
    if data.get("no_knowledge_content"):
        return []

    sections = data.get("sections", [])
    if not sections:
        return []

    search_units: list[tuple[str, str, bool]] = []
    for sec in sections:
        title = sec.get("title", "")
        content = sec.get("content", "")
        sid = sec.get("id", "?")
        if title:
            search_units.append((title, sid, False))
        if content:
            if fmt in ("rst", "md"):
                for line in _strip_md_syntax_to_plain_lines(content):
                    search_units.append((line, sid, True))
            else:
                search_units.append((content, sid, True))

    if not search_units:
        return []

    issues: list[str] = []
    consumed: list[tuple[int, int]] = []
    current_pos = 0

    def _in_consumed(pos: int, length: int) -> bool:
        end = pos + length
        for s, e in consumed:
            if pos < e and end > s:
                return True
        return False

    for unit, sid, is_content in search_units:
        idx = source_text.find(unit, current_pos)
        if idx != -1:
            consumed.append((idx, idx + len(unit)))
            current_pos = idx + len(unit)
        else:
            prev_idx = source_text.find(unit)
            if not is_content:
                if prev_idx == -1:
                    issues.append(f"[QC2] section '{sid}': fabricated title: {unit[:50]!r}")
                elif _in_consumed(prev_idx, len(unit)):
                    issues.append(f"[QC3] section '{sid}': duplicate title: {unit[:50]!r}")
                else:
                    issues.append(f"[QC4] section '{sid}': misplaced title: {unit[:50]!r}")
            elif prev_idx == -1:
                issues.append(f"[QC2] section '{sid}': fabricated content: {unit[:50]!r}")
            elif _in_consumed(prev_idx, len(unit)):
                issues.append(f"[QC3] section '{sid}': duplicate content: {unit[:50]!r}")
            else:
                issues.append(f"[QC4] section '{sid}': misplaced content: {unit[:50]!r}")

    # QC1: check residual source for non-syntax content
    if consumed:
        consumed.sort()
        merged: list[list[int]] = []
        for s, e in consumed:
            if merged and s <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], e)
            else:
                merged.append([s, e])
        parts: list[str] = []
        prev = 0
        for s, e in merged:
            parts.append(source_text[prev:s])
            prev = e
        parts.append(source_text[prev:])
        remaining = ''.join(parts)
    else:
        remaining = source_text

    # Directives whose indented body is structure (not content to capture)
    _RST_STRUCTURAL_DIRECTIVES = re.compile(
        r'^\.\.\s+(toctree|include|image|figure|raw|csv-table|list-table'
        r'|class|only|ifconfig|replace|unicode|date|contents|sectnum'
        r'|header|footer|rubric|meta|compound|container|math'
        r'|code-block|code|sourcecode|highlight|parsed-literal'
        r'|literalinclude|testsetup|testcleanup|doctest)\s*::'
    )

    if fmt == "rst":
        in_structural_directive = False
        for line in remaining.split('\n'):
            s = line.strip()
            if s and re.match(r'\.\.\s+\S', s):
                in_structural_directive = bool(_RST_STRUCTURAL_DIRECTIVES.match(s))
            if not s:
                continue
            if in_structural_directive and re.match(r'^\s+\S', line):
                continue
            if not _is_rst_syntax_line(line):
                issues.append(f"[QC1] source content not captured: {line.strip()[:50]!r}")
    else:
        # Frontmatter only exists if source_text starts with '---'
        has_frontmatter = bool(re.match(r'^---+\s*$', source_text.split('\n')[0]))
        in_frontmatter = False
        frontmatter_seen = False
        for line in remaining.split('\n'):
            s = line.strip()
            if has_frontmatter and not frontmatter_seen and re.match(r'^---+\s*$', s):
                in_frontmatter = True
                frontmatter_seen = True
                continue
            if in_frontmatter:
                if re.match(r'^---+\s*$', s):
                    in_frontmatter = False
                continue
            if not _is_md_syntax_line(line, in_frontmatter=False):
                issues.append(f"[QC1] source content not captured: {line.strip()[:50]!r}")

    return issues


# ---------------------------------------------------------------------------
# QL2: 外部URL一致
# ---------------------------------------------------------------------------

_URL_RAW_RE = re.compile(r'https?://[^\s\'"<>)\]]+')
# RST hyperlink target definition lines: ".. _Name: url" or "__ url"
# These lines are dropped by the RST converter (they are markup, not content).
_RST_TARGET_LINE_RE = re.compile(r'^(?:\.\.?\s+_|__\s+https?://)')
# Trailing sentence punctuation that is not part of URLs
_URL_TRAILING_PUNCT_RE = re.compile(r'[.,;:]+$')


def _extract_urls_from_source(source_text: str, fmt: str = "") -> list[str]:
    """Extract external URLs from source, excluding RST target definition lines."""
    urls = []
    for line in source_text.splitlines():
        if fmt == "rst" and _RST_TARGET_LINE_RE.match(line.strip()):
            continue
        for url in _URL_RAW_RE.findall(line):
            url = _URL_TRAILING_PUNCT_RE.sub('', url)
            if url:
                urls.append(url)
    return urls


def _collect_json_urls(data: dict) -> set[str]:
    """Collect all external URLs from JSON title and sections."""
    text_parts = [data.get("title", "")]
    for section in data.get("sections", []):
        text_parts.append(section.get("title", ""))
        text_parts.append(section.get("content", ""))
    combined = "\n".join(text_parts)
    urls = set()
    for url in _URL_RAW_RE.findall(combined):
        urls.add(_URL_TRAILING_PUNCT_RE.sub('', url))
    return urls


def check_external_urls(source_text: str, data: dict, fmt: str) -> list[str]:
    """QL2: Verify all external URLs in source appear in JSON content/title.

    Args:
        source_text: Original source file text.
        data: Knowledge JSON dict.
        fmt: Source format ('rst', 'md', or 'xlsx').

    Returns:
        List of FAIL messages for each URL missing from JSON.
    """
    if fmt == "xlsx":
        return []
    if data.get("no_knowledge_content"):
        return []

    source_urls = _extract_urls_from_source(source_text, fmt)
    if not source_urls:
        return []

    json_urls = _collect_json_urls(data)
    issues = []
    seen: set[str] = set()
    for url in source_urls:
        if url in seen:
            continue
        seen.add(url)
        if url not in json_urls:
            issues.append(f"[QL2] external URL missing from JSON: {url}")
    return issues


# ---------------------------------------------------------------------------
# Stubs for future phases (V2-4 through V2-9)
# ---------------------------------------------------------------------------

def verify_file(source_path, json_path, fmt, knowledge_dir=None):
    """Stub — QC1-QC4 RST/MD (V2-5/V2-6), QC1-QC3 Excel (V2-4) not yet implemented."""
    return []


def verify_docs_md(source_path, docs_md_path, fmt):
    """Stub — not yet implemented."""
    return []


def check_index_coverage(knowledge_dir, index_path):
    """Stub — not yet implemented."""
    return []


def check_docs_coverage(knowledge_dir, docs_dir):
    """Stub — not yet implemented."""
    return []


def build_label_map(source_dir):
    """Stub — not yet implemented."""
    return {}


def check_source_links(source_text, fmt, data, label_map, source_path=None):
    """Stub — not yet implemented."""
    return []

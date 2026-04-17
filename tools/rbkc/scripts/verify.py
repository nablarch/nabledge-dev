"""RBKC verify — quality gate for RBKC output.

Checks that knowledge JSON files correctly represent their source documents.
See: tools/rbkc/docs/rbkc-verify-quality-design.md

Public API:
    check_json_docs_md_consistency(data, docs_md_text) -> list[str]  # QO5
    check_format_purity(data, fmt) -> list[str]                      # QC5
    check_hints_completeness(data, prev_hints) -> list[str]          # QC6
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

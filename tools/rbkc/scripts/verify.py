"""Knowledge file verifier for RBKC.

Checks that a generated knowledge JSON file faithfully represents its
source document.  Detects content loss or corruption.

**Verification strategy**:
- For RST/MD: extract key text tokens from source and check they appear
  in the combined section content of the JSON.
- For XLSX: verify that the section count is non-zero (basic sanity check).

The goal is not perfect semantic equivalence but practical protection
against accidental data loss or format errors.

Public API:
    verify_file(source_path, json_path, format) -> list[str]
        Returns list of issue strings.  Empty = OK.
"""
from __future__ import annotations

import json
import re
from pathlib import Path


# Minimum fraction of sampled tokens that must appear in JSON content
_MIN_TOKEN_COVERAGE = 0.7

# Max tokens to sample from source (keep test fast)
_MAX_SAMPLE = 100


def _extract_text_tokens(text: str) -> list[str]:
    """Extract significant (non-trivial) words from plain text."""
    # CJK/Kana: ≥2 chars (2-kanji words are common in Japanese)
    # Start CJK range at \u4e00 (CJK Unified Ideographs) — not \u3000 which
    # includes ideographic spaces and punctuation that are not word tokens.
    # ASCII/other word chars: ≥3 chars (filter out trivial tokens like "to", "in")
    tokens = re.findall(
        r"[\u4e00-\u9fff\u3400-\u4dbf\u30a0-\u30ff\u3040-\u309f]{2,}|\w{3,}",
        text,
    )
    return list(dict.fromkeys(tokens))  # deduplicate, preserve order


def _json_text(data: dict) -> str:
    """Concatenate all section content from a knowledge JSON."""
    parts = []
    for sec in data.get("sections", []):
        if sec.get("title"):
            parts.append(sec["title"])
        if sec.get("content"):
            parts.append(sec["content"])
    return " ".join(parts)


def _verify_rst_md(source_path: Path, data: dict) -> list[str]:
    """Verify RST or MD source against knowledge JSON."""
    issues = []

    if not data.get("sections"):
        if not data.get("no_knowledge_content"):
            issues.append("sections list is empty but no_knowledge_content is not set")
        return issues

    source_text = source_path.read_text(encoding="utf-8", errors="replace")
    # For RST, strip directive lines to get prose tokens
    source_clean = re.sub(r"^\.\.\s+\w+.*$", "", source_text, flags=re.MULTILINE)
    source_tokens = _extract_text_tokens(source_clean)

    # Sample tokens evenly across the source
    if len(source_tokens) > _MAX_SAMPLE:
        step = len(source_tokens) // _MAX_SAMPLE
        source_tokens = source_tokens[::step][:_MAX_SAMPLE]

    if not source_tokens:
        return issues  # nothing to check

    json_text = _json_text(data)
    found = sum(1 for t in source_tokens if t in json_text)
    coverage = found / len(source_tokens)

    if coverage < _MIN_TOKEN_COVERAGE:
        issues.append(
            f"Token coverage too low: {found}/{len(source_tokens)} "
            f"({coverage:.0%} < {_MIN_TOKEN_COVERAGE:.0%}) — "
            f"JSON may be missing significant content from source"
        )

    return issues


def _verify_xlsx(source_path: Path, data: dict) -> list[str]:
    """Verify XLSX source against knowledge JSON."""
    issues = []
    if not data.get("sections") and not data.get("no_knowledge_content"):
        issues.append("XLSX knowledge file has no sections")
    return issues


def verify_file(source_path: Path, json_path: Path, fmt: str) -> list[str]:
    """Verify a knowledge JSON file against its source.

    Args:
        source_path: Path to the original source file.
        json_path: Path to the generated knowledge JSON.
        fmt: File format — 'rst', 'md', or 'xlsx'.

    Returns:
        List of issue strings.  Empty list means the file passes verification.
    """
    if not source_path.exists():
        return [f"Source file not found: {source_path}"]
    if not json_path.exists():
        return [f"JSON file not found: {json_path}"]

    data = json.loads(json_path.read_text(encoding="utf-8"))

    if fmt in ("rst", "md"):
        return _verify_rst_md(source_path, data)
    elif fmt == "xlsx":
        return _verify_xlsx(source_path, data)
    else:
        return [f"Unknown format: {fmt}"]

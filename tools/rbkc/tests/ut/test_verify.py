"""Unit tests for verify.py — Phase 11 verification checks."""
from __future__ import annotations

import json
import pytest
from pathlib import Path

from scripts.verify import (
    _extract_text_tokens,
    check_titles,
    check_content,
    check_internal_links,
    check_external_urls,
    check_index_coverage,
    check_docs_coverage,
)


# ---------------------------------------------------------------------------
# _extract_text_tokens — CJK range starts too early (\u3000 = ideographic space)
# ---------------------------------------------------------------------------

class TestExtractTextTokens:
    def test_ideographic_spaces_are_not_tokens(self):
        """Consecutive ideographic spaces (\u3000) must not be treated as tokens."""
        text = "\u3000\u3000\u3000"  # three ideographic spaces
        result = _extract_text_tokens(text)
        assert result == [], f"Expected no tokens but got: {result!r}"

    def test_japanese_punctuation_sequence_is_not_token(self):
        """Sequences of Japanese punctuation (、。) must not produce tokens."""
        text = "、。、。"  # \u3001, \u3002 — CJK punctuation
        result = _extract_text_tokens(text)
        assert result == [], f"Expected no tokens but got: {result!r}"

    def test_kanji_tokens_still_extracted(self):
        """Kanji (CJK Unified Ideograph range \u4e00-\u9fff) must still match."""
        result = _extract_text_tokens("ユニバーサルDAO")
        assert any("DAO" in t or "ユニバーサル" in t for t in result)

    def test_hiragana_tokens_still_extracted(self):
        """Hiragana sequences of 2+ chars must still match."""
        result = _extract_text_tokens("ください")
        assert "ください" in result

    def test_katakana_tokens_still_extracted(self):
        """Katakana sequences of 2+ chars must still match."""
        result = _extract_text_tokens("ユニバーサル")
        assert "ユニバーサル" in result

    def test_ascii_words_still_extracted(self):
        """ASCII words of 3+ chars must still match."""
        result = _extract_text_tokens("UniversalDao pagination")
        assert "UniversalDao" in result
        assert "pagination" in result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_data(sections=None, title="Doc Title", no_knowledge_content=False):
    """Build a minimal knowledge JSON dict."""
    data = {
        "id": "test-id",
        "title": title,
        "no_knowledge_content": no_knowledge_content,
        "sections": sections if sections is not None else [],
    }
    return data


def _make_section(title, content="some content here for testing purposes"):
    return {"id": "s1", "title": title, "content": content, "hints": []}


# ---------------------------------------------------------------------------
# Check A: section titles
# ---------------------------------------------------------------------------

class TestCheckA_Titles:
    def test_rst_all_source_headings_in_json(self):
        """All h2/h3 headings in RST source must appear in JSON sections."""
        source_text = """\
========
Doc Title
========

Introduction
------------

This is intro content.

Details
-------

This is detail content.
"""
        data = _make_data(sections=[
            _make_section("Introduction"),
            _make_section("Details"),
        ])
        issues = check_titles(source_text, data, "rst")
        assert issues == []

    def test_rst_missing_heading_fails(self):
        """A heading in RST source that is absent from JSON must cause a FAIL."""
        source_text = """\
========
Doc Title
========

Introduction
------------

Content here.

Missing Section
---------------

This section is missing from JSON.
"""
        data = _make_data(sections=[
            _make_section("Introduction"),
            # "Missing Section" is NOT in JSON
        ])
        issues = check_titles(source_text, data, "rst")
        assert any("Missing Section" in issue for issue in issues)

    def test_rst_synthetic_preamble_allowed(self):
        """'概要' section in JSON does not require a matching heading in source."""
        source_text = """\
========
Doc Title
========

This is preamble text without a heading.

Details
-------

Detail content.
"""
        # JSON has 概要 (synthetic preamble) + Details
        data = _make_data(sections=[
            _make_section("概要"),
            _make_section("Details"),
        ])
        issues = check_titles(source_text, data, "rst")
        assert issues == []

    def test_rst_no_headings_passes(self):
        """RST source with no h2/h3 headings → PASS (nothing to check)."""
        source_text = "Just plain text without any headings.\n"
        data = _make_data(sections=[_make_section("概要")])
        issues = check_titles(source_text, data, "rst")
        assert issues == []

    def test_md_all_headings_in_json(self):
        """All ## headings in MD source must appear in JSON sections."""
        source_text = """\
# Doc Title

## Introduction

Intro content.

## Details

Detail content.
"""
        data = _make_data(sections=[
            _make_section("Introduction"),
            _make_section("Details"),
        ])
        issues = check_titles(source_text, data, "md")
        assert issues == []

    def test_md_missing_heading_fails(self):
        """A ## heading in MD source absent from JSON must cause a FAIL."""
        source_text = """\
# Doc Title

## Introduction

Intro content.

## Missing Section

This section is not in JSON.
"""
        data = _make_data(sections=[
            _make_section("Introduction"),
        ])
        issues = check_titles(source_text, data, "md")
        assert any("Missing Section" in issue for issue in issues)

    def test_xlsx_always_passes(self):
        """XLSX format skips title check — always returns no issues."""
        issues = check_titles("", _make_data(), "xlsx")
        assert issues == []


# ---------------------------------------------------------------------------
# Check B: content token coverage
# ---------------------------------------------------------------------------

class TestCheckB_Content:
    def test_sufficient_coverage_passes(self):
        """Token coverage >= 70% must pass."""
        # Build source text with many distinct tokens
        tokens = [f"token{i:03d}" for i in range(20)]
        source_text = " ".join(tokens)
        # Put all tokens in JSON content
        data = _make_data(sections=[_make_section("Section", " ".join(tokens))])
        issues = check_content(source_text, data, "rst")
        assert issues == []

    def test_insufficient_coverage_fails(self):
        """Token coverage < 70% must fail."""
        # Build source text with 10 distinct tokens
        tokens = [f"token{i:03d}" for i in range(10)]
        source_text = " ".join(tokens)
        # Put only 2 out of 10 tokens in JSON — coverage = 20%
        data = _make_data(sections=[_make_section("Section", "token000 token001")])
        issues = check_content(source_text, data, "rst")
        assert len(issues) > 0
        assert any("coverage" in issue.lower() or "Coverage" in issue for issue in issues)

    def test_no_sections_with_flag_passes(self):
        """no_knowledge_content=True with empty sections → PASS."""
        data = _make_data(sections=[], no_knowledge_content=True)
        issues = check_content("some source text here", data, "rst")
        assert issues == []

    def test_no_sections_without_flag_fails(self):
        """Empty sections without no_knowledge_content flag → FAIL."""
        data = _make_data(sections=[], no_knowledge_content=False)
        issues = check_content("some source text here for testing", data, "rst")
        assert len(issues) > 0


# ---------------------------------------------------------------------------
# Check C: internal links
# ---------------------------------------------------------------------------

class TestCheckC_InternalLinks:
    def test_no_links_passes(self, tmp_path):
        """Content without links → PASS."""
        data = _make_data(sections=[_make_section("Section", "No links here at all.")])
        issues = check_internal_links(data, tmp_path / "test.json", tmp_path)
        assert issues == []

    def test_http_link_skipped(self, tmp_path):
        """https:// links are external — skip, no error."""
        content = "See [docs](https://example.com/page) for details."
        data = _make_data(sections=[_make_section("Section", content)])
        issues = check_internal_links(data, tmp_path / "test.json", tmp_path)
        assert issues == []

    def test_asset_link_skipped(self, tmp_path):
        """assets/ links are skipped (assets copy not implemented)."""
        content = "See ![image](assets/diagram.png) for illustration."
        data = _make_data(sections=[_make_section("Section", content)])
        issues = check_internal_links(data, tmp_path / "test.json", tmp_path)
        assert issues == []

    def test_existing_relative_link_passes(self, tmp_path):
        """Relative link pointing to an existing file → PASS."""
        # Create a target file
        target_dir = tmp_path / "other"
        target_dir.mkdir()
        (target_dir / "page.json").write_text("{}", encoding="utf-8")

        content = "See [other page](other/page.json) for details."
        json_path = tmp_path / "current.json"
        data = _make_data(sections=[_make_section("Section", content)])
        issues = check_internal_links(data, json_path, tmp_path)
        assert issues == []

    def test_missing_relative_link_fails(self, tmp_path):
        """Relative link pointing to a non-existent file → FAIL."""
        content = "See [missing page](other/nonexistent.json) for details."
        json_path = tmp_path / "current.json"
        data = _make_data(sections=[_make_section("Section", content)])
        issues = check_internal_links(data, json_path, tmp_path)
        assert len(issues) > 0
        assert any("nonexistent.json" in issue for issue in issues)


# ---------------------------------------------------------------------------
# Check D: external URLs
# ---------------------------------------------------------------------------

class TestCheckD_ExternalURLs:
    def test_url_in_json_passes(self):
        """URL in source that also appears in JSON content → PASS."""
        source_text = "See https://example.com/page for details."
        data = _make_data(sections=[
            _make_section("Section", "See https://example.com/page for details.")
        ])
        issues = check_external_urls(source_text, data)
        assert issues == []

    def test_url_missing_from_json_fails(self):
        """URL in source that is absent from JSON content → FAIL."""
        source_text = "See https://example.com/important for details."
        data = _make_data(sections=[
            _make_section("Section", "Content without the URL.")
        ])
        issues = check_external_urls(source_text, data)
        assert len(issues) > 0
        assert any("https://example.com/important" in issue for issue in issues)

    def test_no_urls_in_source_passes(self):
        """Source with no URLs → PASS."""
        source_text = "Plain text without any links."
        data = _make_data(sections=[_make_section("Section", "Content here.")])
        issues = check_external_urls(source_text, data)
        assert issues == []

    def test_rst_definition_only_url_skipped(self):
        """RST external hyperlink definition (.. _Name: URL) only → skip."""
        source_text = "Some text.\n\n.. _Example: https://example.com/page\n"
        # URL is only in a RST definition, not in inline text
        data = _make_data(sections=[_make_section("Section", "Some text.")])
        issues = check_external_urls(source_text, data)
        assert issues == []

    def test_inline_rst_url_checked(self):
        """RST inline URL `text <URL>`_ → must be checked (present in JSON or fail)."""
        source_text = "See `Example <https://example.com/inline>`_ for details.\n"
        # URL is not in JSON
        data = _make_data(sections=[_make_section("Section", "See Example for details.")])
        issues = check_external_urls(source_text, data)
        assert len(issues) > 0
        assert any("https://example.com/inline" in issue for issue in issues)


# ---------------------------------------------------------------------------
# Check F: index.toon coverage
# ---------------------------------------------------------------------------

class TestCheckF_IndexCoverage:
    def _write_json(self, path: Path, no_knowledge=False):
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {"id": path.stem, "no_knowledge_content": no_knowledge, "sections": []}
        path.write_text(json.dumps(data), encoding="utf-8")

    def _write_index(self, index_path: Path, entries: list[str]):
        """Write a minimal index.toon with given relative path entries."""
        lines = ["# Nabledge-6 Knowledge Index\n", "\n",
                 f"files[{len(entries)},]{{title,type,category,processing_patterns,path}}:\n"]
        for entry in entries:
            lines.append(f"  Title, type, category, , {entry}\n")
        index_path.write_text("".join(lines), encoding="utf-8")

    def test_all_entries_present_passes(self, tmp_path):
        """All JSON files have entries in index.toon → PASS."""
        self._write_json(tmp_path / "cat" / "file1.json")
        self._write_json(tmp_path / "cat" / "file2.json")
        index_path = tmp_path / "index.toon"
        self._write_index(index_path, ["cat/file1.json", "cat/file2.json"])
        issues = check_index_coverage(tmp_path, index_path)
        assert issues == []

    def test_missing_entry_fails(self, tmp_path):
        """JSON file without an entry in index.toon → FAIL."""
        self._write_json(tmp_path / "cat" / "file1.json")
        self._write_json(tmp_path / "cat" / "file2.json")
        index_path = tmp_path / "index.toon"
        # Only file1 is in index
        self._write_index(index_path, ["cat/file1.json"])
        issues = check_index_coverage(tmp_path, index_path)
        assert len(issues) > 0
        assert any("file2.json" in issue for issue in issues)

    def test_no_knowledge_content_excluded(self, tmp_path):
        """JSON with no_knowledge_content=True is excluded from index check."""
        self._write_json(tmp_path / "cat" / "file1.json")
        self._write_json(tmp_path / "cat" / "no_content.json", no_knowledge=True)
        index_path = tmp_path / "index.toon"
        # Only file1 is indexed; no_content.json is excluded
        self._write_index(index_path, ["cat/file1.json"])
        issues = check_index_coverage(tmp_path, index_path)
        assert issues == []

    def test_missing_index_fails(self, tmp_path):
        """Missing index.toon → FAIL."""
        self._write_json(tmp_path / "cat" / "file1.json")
        index_path = tmp_path / "index.toon"
        # Don't create the index file
        issues = check_index_coverage(tmp_path, index_path)
        assert len(issues) > 0
        assert any("index.toon" in issue for issue in issues)


# ---------------------------------------------------------------------------
# Check H: docs (MD) coverage
# ---------------------------------------------------------------------------

class TestCheckH_DocsCoverage:
    def _write_json(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {"id": path.stem, "no_knowledge_content": False, "sections": []}
        path.write_text(json.dumps(data), encoding="utf-8")

    def _write_md(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Doc\n\nContent.\n", encoding="utf-8")

    def test_all_md_present_passes(self, tmp_path):
        """Every JSON file has a corresponding MD file → PASS."""
        knowledge_dir = tmp_path / "knowledge"
        docs_dir = tmp_path / "docs"
        self._write_json(knowledge_dir / "cat" / "file1.json")
        self._write_json(knowledge_dir / "cat" / "file2.json")
        self._write_md(docs_dir / "cat" / "file1.md")
        self._write_md(docs_dir / "cat" / "file2.md")
        issues = check_docs_coverage(knowledge_dir, docs_dir)
        assert issues == []

    def test_missing_md_fails(self, tmp_path):
        """JSON file without a corresponding MD file → FAIL."""
        knowledge_dir = tmp_path / "knowledge"
        docs_dir = tmp_path / "docs"
        self._write_json(knowledge_dir / "cat" / "file1.json")
        self._write_json(knowledge_dir / "cat" / "file2.json")
        self._write_md(docs_dir / "cat" / "file1.md")
        # file2.md is missing
        issues = check_docs_coverage(knowledge_dir, docs_dir)
        assert len(issues) > 0
        assert any("file2" in issue for issue in issues)

    def test_missing_docs_dir_fails(self, tmp_path):
        """Non-existent docs directory → FAIL."""
        knowledge_dir = tmp_path / "knowledge"
        docs_dir = tmp_path / "docs"  # does not exist
        self._write_json(knowledge_dir / "cat" / "file1.json")
        issues = check_docs_coverage(knowledge_dir, docs_dir)
        assert len(issues) > 0
        assert any("docs" in issue.lower() for issue in issues)

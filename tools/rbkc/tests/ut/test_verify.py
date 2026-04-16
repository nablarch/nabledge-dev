"""Unit tests for verify.py — Phase 12 verification checks."""
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
    check_docs_md_titles,
    check_docs_md_content,
    check_docs_md_links,
    check_docs_md_urls,
    verify_docs_md,
    strip_md_syntax,
    classify_line,
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
        """All content tokens present in JSON → PASS."""
        # Build source text with many distinct tokens
        tokens = [f"token{i:03d}" for i in range(20)]
        source_text = " ".join(tokens)
        # Put all tokens in JSON content
        data = _make_data(sections=[_make_section("Section", " ".join(tokens))])
        issues = check_content(source_text, data, "rst")
        assert issues == []

    def test_insufficient_coverage_fails(self):
        """Content tokens missing from JSON must cause FAIL (diff-based check)."""
        # Build source text with 10 distinct tokens
        tokens = [f"token{i:03d}" for i in range(10)]
        source_text = " ".join(tokens)
        # Put only 2 out of 10 tokens in JSON — 8 tokens will be reported as missing
        data = _make_data(sections=[_make_section("Section", "token000 token001")])
        issues = check_content(source_text, data, "rst")
        assert len(issues) > 0
        # New diff-based format: "Content token missing from JSON: 'tokenXXX' ..."
        assert any("missing" in issue.lower() for issue in issues)

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

    def test_toctree_only_with_flag_and_nonempty_sections_passes(self):
        """B8: no_knowledge_content=True with non-empty (but empty-content) sections → PASS.

        Toctree-only index.rst files produce sections with empty content but are
        still a non-empty list. Check B must skip the entire check when the flag is set.
        """
        # Simulates: about_nablarch/index.rst → title "Nablarchについて", toctree only
        source_text = "Nablarchについて\n====================\n\n.. toctree::\n   concept\n   license\n"
        # JSON produced by RBKC: one section with empty content, no_knowledge_content=True
        data = _make_data(sections=[_make_section("概要", "")], no_knowledge_content=True)
        issues = check_content(source_text, data, "rst")
        assert issues == []


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

    def test_asset_link_no_longer_skipped(self, tmp_path):
        """assets/ links are NOT skipped — existence is checked (B1 regression test).

        Note: TestCheckC_AssetsNotSkipped below also tests this with more specific
        assertions. This test remains as an in-class regression marker.
        """
        content = "See ![image](assets/diagram.png) for illustration."
        data = _make_data(sections=[_make_section("Section", content)])
        # No assets/ file exists → should FAIL (not silently pass)
        issues = check_internal_links(data, tmp_path / "test.json", tmp_path)
        assert len(issues) > 0

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

    def test_backtick_wrapped_url_not_captured_with_backtick(self):
        """URL inside backtick literal `https://example.com` → captured without trailing backtick."""
        # Source has URL in backtick literal — regex must not include the trailing backtick
        source_text = "Use `https://example.com/path` for reference.\n"
        data = _make_data(sections=[
            _make_section("Section", "Use https://example.com/path for reference.")
        ])
        issues = check_external_urls(source_text, data)
        assert issues == []


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


# ---------------------------------------------------------------------------
# B1: Check C — assets/ links must NOT be skipped
# ---------------------------------------------------------------------------

class TestCheckC_AssetsNotSkipped:
    def test_asset_link_missing_file_fails(self, tmp_path):
        """assets/ link to non-existent file → FAIL (must not be skipped)."""
        content = "See ![image](assets/diagram.png) for illustration."
        data = _make_data(sections=[_make_section("Section", content)])
        # No assets/diagram.png exists in tmp_path
        issues = check_internal_links(data, tmp_path / "test.json", tmp_path)
        assert len(issues) > 0
        assert any("diagram.png" in issue for issue in issues)

    def test_asset_link_existing_file_passes(self, tmp_path):
        """assets/ link to an existing file → PASS."""
        assets_dir = tmp_path / "assets"
        assets_dir.mkdir()
        (assets_dir / "diagram.png").write_bytes(b"")  # empty placeholder
        content = "See ![image](assets/diagram.png) for illustration."
        data = _make_data(sections=[_make_section("Section", content)])
        issues = check_internal_links(data, tmp_path / "test.json", tmp_path)
        assert issues == []


# ---------------------------------------------------------------------------
# B2: Check A/B/C/D for docs MD
# ---------------------------------------------------------------------------

class TestCheckDocsMdTitles:
    def test_rst_all_source_headings_in_docs_md(self):
        """All RST h2/h3 headings must appear as ##/### in docs MD."""
        source_text = """\
========
Doc Title
========

Introduction
------------

Intro content.

Details
-------

Detail content.
"""
        docs_md_text = """\
# Doc Title

## Introduction

Intro content.

## Details

Detail content.
"""
        issues = check_docs_md_titles(source_text, docs_md_text, "rst")
        assert issues == []

    def test_rst_missing_heading_in_docs_md_fails(self):
        """RST heading absent from docs MD → FAIL."""
        source_text = """\
========
Doc Title
========

Introduction
------------

Content.

Missing Section
---------------

This section is missing from docs MD.
"""
        docs_md_text = """\
# Doc Title

## Introduction

Content.
"""
        issues = check_docs_md_titles(source_text, docs_md_text, "rst")
        assert any("Missing Section" in issue for issue in issues)

    def test_md_all_headings_in_docs_md(self):
        """All MD ## headings must appear in docs MD."""
        source_text = """\
# Title

## Introduction

Content.

## Details

More content.
"""
        docs_md_text = """\
# Title

## Introduction

Content.

## Details

More content.
"""
        issues = check_docs_md_titles(source_text, docs_md_text, "md")
        assert issues == []

    def test_md_missing_heading_in_docs_md_fails(self):
        """MD heading absent from docs MD → FAIL."""
        source_text = """\
# Title

## Introduction

Content.

## Missing Section

Not in docs MD.
"""
        docs_md_text = """\
# Title

## Introduction

Content.
"""
        issues = check_docs_md_titles(source_text, docs_md_text, "md")
        assert any("Missing Section" in issue for issue in issues)

    def test_xlsx_always_passes(self):
        """XLSX format skips title check → PASS."""
        issues = check_docs_md_titles("", "# Title\n", "xlsx")
        assert issues == []


class TestCheckDocsMdContent:
    def test_sufficient_coverage_passes(self):
        """All source content tokens present in docs MD → PASS."""
        tokens = [f"token{i:03d}" for i in range(20)]
        source_text = " ".join(tokens)
        docs_md_text = "## Section\n\n" + " ".join(tokens) + "\n"
        issues = check_docs_md_content(source_text, docs_md_text, "rst")
        assert issues == []

    def test_insufficient_coverage_fails(self):
        """Content tokens missing from docs MD → FAIL (diff-based check)."""
        tokens = [f"token{i:03d}" for i in range(10)]
        source_text = " ".join(tokens)
        # Only 2 out of 10 tokens in docs MD
        docs_md_text = "## Section\n\ntoken000 token001\n"
        issues = check_docs_md_content(source_text, docs_md_text, "rst")
        assert len(issues) > 0
        # New diff-based format: "Content token missing from docs MD: 'tokenXXX' ..."
        assert any("missing" in issue.lower() for issue in issues)

    def test_toctree_token_does_not_fail(self):
        """Token in toctree entry → PASS (syntax line, not content)."""
        source_text = (
            "Contents\n"
            "========\n"
            "\n"
            ".. toctree::\n"
            "   architecture\n"
            "   feature_details\n"
        )
        # docs MD has no 'architecture' but that's OK (it's a toctree entry)
        docs_md_text = "# Contents\n\nSome overview text.\n"
        issues = check_docs_md_content(source_text, docs_md_text, "rst")
        assert issues == []

    def test_xlsx_always_passes(self):
        """XLSX format skips content check → PASS."""
        issues = check_docs_md_content("any source text", "any docs text", "xlsx")
        assert issues == []


class TestCheckDocsMdLinks:
    def test_no_links_passes(self, tmp_path):
        """Docs MD without links → PASS."""
        md_path = tmp_path / "docs" / "cat" / "file.md"
        md_path.parent.mkdir(parents=True)
        issues = check_docs_md_links("No links here.", md_path)
        assert issues == []

    def test_https_link_skipped(self, tmp_path):
        """https:// links are external — skip."""
        md_path = tmp_path / "docs" / "cat" / "file.md"
        md_path.parent.mkdir(parents=True)
        issues = check_docs_md_links("See [docs](https://example.com/page).", md_path)
        assert issues == []

    def test_existing_relative_link_passes(self, tmp_path):
        """Relative link to existing file (docs MD-relative) → PASS."""
        docs_dir = tmp_path / "docs"
        (docs_dir / "cat").mkdir(parents=True)
        # Create the target file
        target = docs_dir / "cat" / "other.md"
        target.write_text("# Other\n", encoding="utf-8")
        md_path = docs_dir / "cat" / "file.md"
        issues = check_docs_md_links("See [other](other.md) here.", md_path)
        assert issues == []

    def test_missing_relative_link_fails(self, tmp_path):
        """Relative link to non-existent file (docs MD-relative) → FAIL."""
        md_path = tmp_path / "docs" / "cat" / "file.md"
        md_path.parent.mkdir(parents=True)
        issues = check_docs_md_links("See [missing](missing.md) here.", md_path)
        assert len(issues) > 0
        assert any("missing.md" in issue for issue in issues)

    def test_asset_link_via_relative_path_checked(self, tmp_path):
        """docs MD asset link (e.g., ../../../knowledge/assets/x.png) → checked."""
        docs_dir = tmp_path / "docs" / "cat"
        docs_dir.mkdir(parents=True)
        knowledge_assets = tmp_path / "knowledge" / "assets"
        knowledge_assets.mkdir(parents=True)
        (knowledge_assets / "diagram.png").write_bytes(b"")
        md_path = docs_dir / "file.md"
        # Relative path from docs/cat/ to knowledge/assets/
        link = "../../../knowledge/assets/diagram.png"
        # Wait, the relative path depends on the actual directory structure
        # docs/cat/file.md → ../../knowledge/assets/diagram.png
        link = "../../knowledge/assets/diagram.png"
        issues = check_docs_md_links(f"See ![img]({link}) here.", md_path)
        assert issues == []


class TestCheckDocsMdUrls:
    def test_url_in_docs_md_passes(self):
        """URL in source that also appears in docs MD → PASS."""
        source_text = "See https://example.com/page for details."
        docs_md_text = "See [page](https://example.com/page) for details."
        issues = check_docs_md_urls(source_text, docs_md_text)
        assert issues == []

    def test_url_missing_from_docs_md_fails(self):
        """URL in source absent from docs MD → FAIL."""
        source_text = "See https://example.com/important for details."
        docs_md_text = "Content without the URL."
        issues = check_docs_md_urls(source_text, docs_md_text)
        assert len(issues) > 0
        assert any("https://example.com/important" in issue for issue in issues)

    def test_no_urls_in_source_passes(self):
        """Source with no URLs → PASS."""
        issues = check_docs_md_urls("Plain text.", "Content here.")
        assert issues == []

    def test_rst_definition_only_url_skipped(self):
        """RST hyperlink definition (.. _Name: URL) only → skip."""
        source_text = "Some text.\n\n.. _Example: https://example.com/page\n"
        docs_md_text = "Some text."
        issues = check_docs_md_urls(source_text, docs_md_text)
        assert issues == []

    def test_inline_rst_url_checked(self):
        """RST inline URL `text <URL>`_ must be checked against docs MD."""
        source_text = "See `Example <https://example.com/inline>`_ for details.\n"
        # URL is not in docs MD
        docs_md_text = "See Example for details."
        issues = check_docs_md_urls(source_text, docs_md_text)
        assert len(issues) > 0
        assert any("https://example.com/inline" in issue for issue in issues)


class TestVerifyDocsMd:
    def _write_source(self, path: Path, text: str):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def _write_docs_md(self, path: Path, text: str):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def test_source_not_found_fails(self, tmp_path):
        """Missing source file → FAIL."""
        docs_md = tmp_path / "docs" / "file.md"
        self._write_docs_md(docs_md, "# Title\n")
        issues = verify_docs_md(tmp_path / "source.rst", docs_md, "rst")
        assert any("Source file not found" in issue for issue in issues)

    def test_docs_md_not_found_fails(self, tmp_path):
        """Missing docs MD → FAIL."""
        source = tmp_path / "source.rst"
        self._write_source(source, "Title\n=====\n\nContent.\n")
        issues = verify_docs_md(source, tmp_path / "docs" / "file.md", "rst")
        assert any("docs MD" in issue or "not found" in issue for issue in issues)

    def test_valid_rst_passes(self, tmp_path):
        """Valid RST source with matching docs MD → PASS."""
        source = tmp_path / "source.rst"
        source_text = """\
========
My Title
========

Introduction
------------

This is introduction content with keywords here.

Details
-------

More detailed content for details section testing.
"""
        self._write_source(source, source_text)
        docs_md = tmp_path / "docs" / "file.md"
        docs_md_text = """\
# My Title

## Introduction

This is introduction content with keywords here.

## Details

More detailed content for details section testing.
"""
        self._write_docs_md(docs_md, docs_md_text)
        issues = verify_docs_md(source, docs_md, "rst")
        assert issues == []


# ---------------------------------------------------------------------------
# B3: FAIL output uses relative path (tested via run.verify integration)
# ---------------------------------------------------------------------------

class TestFailOutputRelativePath:
    """Verify that run.verify() outputs repo-relative source paths in FAIL lines."""

    def test_verify_fail_message_uses_relative_path(self, tmp_path, capsys):
        """FAIL output must include repo-relative path, not just filename."""
        import sys
        from scripts.run import verify

        # Set up a minimal repo structure
        repo_root = tmp_path
        version = "6"
        skill_dir = repo_root / ".claude" / "skills" / f"nabledge-{version}"
        output_dir = skill_dir / "knowledge"
        output_dir.mkdir(parents=True)

        # Create a source RST file with content
        source_dir = repo_root / ".lw" / "nab-official" / "v6" / "nablarch-document" / "ja" / "cat"
        source_dir.mkdir(parents=True)
        source_file = source_dir / "guide.rst"
        source_file.write_text(
            "Title\n=====\n\nContent here for testing source file.\n",
            encoding="utf-8",
        )

        # Create a mapping file for classify_sources
        mappings_dir = repo_root / "tools" / "rbkc" / "mappings"
        mappings_dir.mkdir(parents=True)

        # Create a minimal JSON that will FAIL (missing content)
        json_path = output_dir / "cat" / "guide.json"
        json_path.parent.mkdir(parents=True)
        json_path.write_text(
            json.dumps({"id": "cat-guide", "title": "Guide", "no_knowledge_content": False,
                        "sections": []}),
            encoding="utf-8",
        )

        # Patch classify_sources to return a controlled FileInfo
        from scripts.classify import FileInfo
        from unittest.mock import patch

        fi = FileInfo(
            source_path=source_file,
            file_id="cat-guide",
            output_path=Path("cat/guide.json"),
            format="rst",
            type="component",
            category="cat",
        )
        with patch("scripts.run.scan_sources", return_value=[source_file]):
            with patch("scripts.run.classify_sources", return_value=[fi]):
                with patch("scripts.run._hints_index", return_value={}):
                    result = verify(version, repo_root, output_dir)

        captured = capsys.readouterr()
        assert result is False
        # FAIL line for source files must use repo-relative path
        # (excludes "FAIL index.toon:" and "FAIL docs:" global check lines)
        source_fail_lines = [
            line for line in captured.err.splitlines()
            if line.startswith("FAIL") and not line.startswith("FAIL index.toon:")
            and not line.startswith("FAIL docs:")
        ]
        assert len(source_fail_lines) > 0
        for line in source_fail_lines:
            # Must NOT be just the filename (e.g. "FAIL guide.rst:")
            assert "FAIL guide.rst:" not in line, f"FAIL line uses only filename: {line!r}"
            # Must include directory components (slash in the path portion)
            path_part = line.split("FAIL ")[1].split(":")[0]
            assert "/" in path_part, f"FAIL line has no directory component: {line!r}"


# ---------------------------------------------------------------------------
# Phase 17-A: strip_md_syntax
# ---------------------------------------------------------------------------

class TestStripMdSyntax:
    def test_heading_markers_removed(self):
        """## and ### heading markers are removed, leaving heading text."""
        text = "## Introduction\n### Sub-section\n"
        result = strip_md_syntax(text)
        assert "##" not in result
        assert "Introduction" in result
        assert "Sub-section" in result

    def test_table_pipes_removed(self):
        """| table | syntax | → pipes removed, cell text preserved."""
        text = "| col1 | col2 |\n|------|------|\n| val1 | val2 |\n"
        result = strip_md_syntax(text)
        assert "|" not in result
        assert "col1" in result
        assert "val1" in result

    def test_bold_markers_removed(self):
        """**bold** → bold text preserved, markers removed."""
        text = "This is **important** text."
        result = strip_md_syntax(text)
        assert "**" not in result
        assert "important" in result

    def test_bullet_list_markers_removed(self):
        """- list item → dash removed, text preserved."""
        text = "- first item\n- second item\n"
        result = strip_md_syntax(text)
        assert result.count("-") == 0 or "first item" in result
        assert "first item" in result
        assert "second item" in result

    def test_inline_code_markers_removed(self):
        """`code` → backticks removed, code text preserved."""
        text = "Use `MyClass` to do this."
        result = strip_md_syntax(text)
        assert "`" not in result
        assert "MyClass" in result

    def test_link_syntax_removed(self):
        """[text](url) → link syntax removed, link text preserved."""
        text = "See [related page](other/page.json) for details."
        result = strip_md_syntax(text)
        assert "[" not in result
        assert "related page" in result

    def test_plain_text_unchanged(self):
        """Plain text without MD syntax passes through unchanged."""
        text = "UniversalDao pagination setup"
        result = strip_md_syntax(text)
        assert "UniversalDao" in result
        assert "pagination" in result


# ---------------------------------------------------------------------------
# Phase 17-A: classify_line
# ---------------------------------------------------------------------------

class TestClassifyLine:
    def test_section_decoration_underline(self):
        """RST underline-only lines → section_decoration."""
        assert classify_line("========") == "section_decoration"
        assert classify_line("--------") == "section_decoration"
        assert classify_line("~~~~~~~~") == "section_decoration"

    def test_rst_label(self):
        """.. _label: → rst_label."""
        assert classify_line(".. _my-label:") == "rst_label"
        assert classify_line(".. _some_target:") == "rst_label"

    def test_directive_decl(self):
        """.. directive:: → directive_decl."""
        assert classify_line(".. toctree::") == "directive_decl"
        assert classify_line(".. code-block:: java") == "directive_decl"
        assert classify_line(".. note::") == "directive_decl"

    def test_directive_option(self):
        """:option: lines (indented) → directive_option."""
        assert classify_line("   :maxdepth: 2") == "directive_option"
        assert classify_line("   :caption: Contents") == "directive_option"

    def test_toctree_entry(self):
        """Indented path-like entries under toctree → toctree_entry."""
        assert classify_line("   feature/overview") == "toctree_entry"
        assert classify_line("   ./subdir/page") == "toctree_entry"

    def test_content_line(self):
        """Normal text lines → content."""
        assert classify_line("This is regular text.") == "content"
        assert classify_line("UniversalDao provides pagination support.") == "content"
        assert classify_line("") == "content"

    def test_inline_role_is_content(self):
        """:ref:`target` inline role on a content line → content."""
        assert classify_line("See :ref:`some-label` for details.") == "content"

    def test_blank_line_is_content(self):
        """Blank line → content (not a syntax line)."""
        assert classify_line("") == "content"
        assert classify_line("   ") == "content"

    def test_plain_name_with_in_toctree_is_toctree_entry(self):
        """Plain indented name with in_toctree=True → toctree_entry."""
        assert classify_line("   architecture", in_toctree=True) == "toctree_entry"
        assert classify_line("   feature_details", in_toctree=True) == "toctree_entry"
        assert classify_line("   modulename", in_toctree=True) == "toctree_entry"

    def test_plain_indented_name_without_context_is_content(self):
        """Plain indented name without toctree context and no / → content."""
        assert classify_line("   architecture", in_toctree=False) == "content"
        assert classify_line("   modulename", in_toctree=False) == "content"


# ---------------------------------------------------------------------------
# Phase 17-A: check_content diff-based rewrite
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Phase 17-A: _json_text title inclusion
# ---------------------------------------------------------------------------

class TestJsonText:
    def test_title_included_in_json_text(self):
        """data['title'] must be included in the returned text."""
        from scripts.verify import _json_text
        data = {
            "id": "test",
            "title": "UniversalDaoTitle",
            "no_knowledge_content": False,
            "sections": [
                {"id": "s1", "title": "Section", "content": "content here", "hints": []},
            ],
        }
        result = _json_text(data)
        assert "UniversalDaoTitle" in result

    def test_sections_still_included(self):
        """Section titles and content are still included after title fix."""
        from scripts.verify import _json_text
        data = {
            "id": "test",
            "title": "MyTitle",
            "no_knowledge_content": False,
            "sections": [
                {"id": "s1", "title": "MySection", "content": "MyContent", "hints": []},
            ],
        }
        result = _json_text(data)
        assert "MyTitle" in result
        assert "MySection" in result
        assert "MyContent" in result

    def test_no_title_field(self):
        """If data has no 'title', no error is raised."""
        from scripts.verify import _json_text
        data = {
            "id": "test",
            "no_knowledge_content": False,
            "sections": [
                {"id": "s1", "title": "Section", "content": "content", "hints": []},
            ],
        }
        result = _json_text(data)  # must not raise
        assert "Section" in result


class TestCheckContentDiffBased:
    """Tests for the new diff-based check_content() implementation.

    New behavior:
    1. Build JSON content token set (after strip_md_syntax)
    2. For each RST token NOT in JSON tokens:
       a. If all occurrences are on syntax lines → OK (expected RST syntax)
       b. If any occurrence is on a content line → FAIL (RBKC missed content)
    """

    def _make_data(self, sections, no_knowledge_content=False):
        return {
            "id": "test",
            "title": "Doc Title",
            "no_knowledge_content": no_knowledge_content,
            "sections": sections,
        }

    def test_syntax_only_token_does_not_fail(self):
        """Token that appears only in RST syntax lines (toctree entry) → PASS.

        'maxdepth' appears only in ':maxdepth: 2' (directive option) — not in content.
        JSON doesn't have 'maxdepth' but that's OK.
        """
        source_text = (
            "My Document\n"
            "===========\n"
            "\n"
            ".. toctree::\n"
            "   :maxdepth: 2\n"
            "\n"
            "   feature/overview\n"
        )
        data = self._make_data(sections=[
            {"id": "s1", "title": "概要", "content": "Overview of the document.", "hints": []},
        ], no_knowledge_content=True)
        issues = check_content(source_text, data, "rst")
        assert issues == [], f"Expected no issues but got: {issues}"

    def test_content_token_missing_from_json_fails(self):
        """Token on a content line not present in JSON → FAIL.

        'UniversalDao' appears in a regular content line in RST but is absent from JSON.
        """
        source_text = (
            "My Document\n"
            "===========\n"
            "\n"
            "Introduction\n"
            "------------\n"
            "\n"
            "UniversalDao provides pagination support for database queries.\n"
        )
        # JSON missing 'UniversalDao'
        data = self._make_data(sections=[
            {"id": "s1", "title": "Introduction",
             "content": "Provides pagination support for database queries.", "hints": []},
        ])
        issues = check_content(source_text, data, "rst")
        assert len(issues) > 0
        assert any("UniversalDao" in issue for issue in issues)

    def test_content_token_present_in_json_passes(self):
        """Token on a content line that IS present in JSON → PASS."""
        source_text = (
            "My Document\n"
            "===========\n"
            "\n"
            "Introduction\n"
            "------------\n"
            "\n"
            "UniversalDao provides pagination support.\n"
        )
        # title matches RST h1 so h1 tokens are in json_tokens
        data = self._make_data(sections=[
            {"id": "s1", "title": "Introduction",
             "content": "UniversalDao provides pagination support.", "hints": []},
        ])
        # Override default title to match RST h1
        data["title"] = "My Document"
        issues = check_content(source_text, data, "rst")
        assert issues == []

    def test_no_knowledge_content_flag_skips_check(self):
        """no_knowledge_content=True → always PASS regardless of content."""
        source_text = "My Doc\n======\n\nSomeSpecialToken is very important here.\n"
        data = self._make_data(sections=[], no_knowledge_content=True)
        issues = check_content(source_text, data, "rst")
        assert issues == []

    def test_toctree_path_token_does_not_fail(self):
        """Indented toctree path entry tokens → PASS (toctree_entry lines are syntax).

        'feature' from '   feature/overview' should not trigger FAIL.
        """
        source_text = (
            "Contents\n"
            "========\n"
            "\n"
            ".. toctree::\n"
            "   feature/overview\n"
            "   feature/details\n"
        )
        data = self._make_data(sections=[
            {"id": "s1", "title": "概要", "content": "", "hints": []},
        ], no_knowledge_content=True)
        issues = check_content(source_text, data, "rst")
        assert issues == []

    def test_rst_label_token_does_not_fail(self):
        """RST label definition token → PASS (rst_label lines are syntax)."""
        source_text = (
            "My Document\n"
            "===========\n"
            "\n"
            ".. _UniqueLabelToken:\n"
            "\n"
            "Section\n"
            "-------\n"
            "\n"
            "Content here.\n"
        )
        # JSON has section content but not the label name itself
        # title matches RST h1 so 'Document' token is covered
        data = self._make_data(sections=[
            {"id": "s1", "title": "Section", "content": "Content here.", "hints": []},
        ])
        data["title"] = "My Document"
        issues = check_content(source_text, data, "rst")
        assert issues == []

    def test_md_format_content_check(self):
        """MD format: token on content line missing from JSON → FAIL."""
        source_text = (
            "# My Document\n"
            "\n"
            "## Introduction\n"
            "\n"
            "UniversalDao provides pagination.\n"
        )
        # JSON missing 'UniversalDao'
        data = self._make_data(sections=[
            {"id": "s1", "title": "Introduction", "content": "Provides pagination.", "hints": []},
        ])
        issues = check_content(source_text, data, "md")
        assert len(issues) > 0
        assert any("UniversalDao" in issue for issue in issues)

    def test_xlsx_always_passes(self):
        """XLSX format → always PASS."""
        issues = check_content("any content", self._make_data(sections=[]), "xlsx")
        assert issues == []

    def test_content_line_after_toctree_block_is_checked(self):
        """Token on content line after toctree block ends → FAIL if missing from JSON."""
        source_text = (
            "Contents\n"
            "========\n"
            "\n"
            ".. toctree::\n"
            "   some/page\n"
            "   other_module\n"
            "\n"
            "UniqueMissingToken appears here after toctree ends.\n"
        )
        # JSON has no 'UniqueMissingToken'
        data = self._make_data(sections=[
            {"id": "s1", "title": "Contents",
             "content": "Some content without the token.", "hints": []},
        ])
        data["title"] = "Contents"
        issues = check_content(source_text, data, "rst")
        assert any("UniqueMissingToken" in i for i in issues)

    def test_md_heading_line_is_syntax(self):
        """MD ## heading line tokens → not flagged even if missing from JSON.

        In MD format, ## headings are syntax. A token appearing only in a heading
        should not be a FAIL (the heading text is also in JSON via check_titles).
        """
        source_text = (
            "# Doc Title\n"
            "\n"
            "## UniqueSectionHeaderToken\n"
            "\n"
            "Content here.\n"
        )
        # JSON has no 'UniqueSectionHeaderToken' as a token, only as a section title
        # But section title IS in JSON sections, so it won't be in content FAIL
        data = self._make_data(sections=[
            {"id": "s1", "title": "UniqueSectionHeaderToken",
             "content": "Content here.", "hints": []},
        ])
        data["title"] = "Doc Title"
        issues = check_content(source_text, data, "md")
        assert issues == []

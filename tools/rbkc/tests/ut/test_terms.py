"""Unit tests for terms.py — terms.json generation (Phase 22-B-2).

terms.json maps technical term strings to lists of "path/to/file.json:sN" references.

Term extraction rules (from keyword-search-design.md):
1. Java class names (CamelCase)
2. Method names (camelCase)
3. Annotations (@Valid, @Published)
4. Japanese technical terms from section titles (full + verb-stripped form)
5. English abbreviations (ALL_CAPS 2+ chars)
6. Property names (dot-separated 3+ segments)
7. Compound keywords (hyphen-separated)

Exclusions:
- Common Japanese/English words, 1-char tokens, markup residue
- High-frequency terms (section_df >= 7%): terms appearing in too many sections
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.create.terms import extract_terms, build_terms_map, generate_terms


def _write_json(knowledge_dir: Path, output_path: str, data: dict) -> None:
    p = knowledge_dir / output_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# Tests for extract_terms(section) -> set[str]
# ---------------------------------------------------------------------------

class TestExtractTermsJavaClass:
    """CamelCase Java class names are extracted."""

    def test_camel_case_in_content(self):
        terms = extract_terms("UniversalDao is used here.", "")
        assert "UniversalDao" in terms

    def test_multiple_class_names(self):
        terms = extract_terms("Use BatchAction and SimpleAction.", "")
        assert "BatchAction" in terms
        assert "SimpleAction" in terms

    def test_short_camel_case_excluded(self):
        """Single-word CamelCase with length < 2 chars — edge: 'I' is excluded."""
        terms = extract_terms("I is ignored.", "")
        assert "I" not in terms


class TestExtractTermsMethodName:
    """camelCase method names (starting lowercase, has uppercase) are extracted."""

    def test_method_name_in_content(self):
        terms = extract_terms("Call batchUpdate() to update.", "")
        assert "batchUpdate" in terms

    def test_find_all_method(self):
        terms = extract_terms("findAll returns all records.", "")
        assert "findAll" in terms


class TestExtractTermsAnnotation:
    """@Annotation patterns are extracted."""

    def test_at_annotation(self):
        terms = extract_terms("Use @Valid on the parameter.", "")
        assert "@Valid" in terms

    def test_at_published_annotation(self):
        terms = extract_terms("Marked with @Published.", "")
        assert "@Published" in terms


class TestExtractTermsJapaneseSectionTitle:
    """Japanese technical terms are extracted from section titles."""

    def test_full_title_registered(self):
        terms = extract_terms("", "ドメインバリデーションを使う")
        assert "ドメインバリデーションを使う" in terms

    def test_verb_stripped_form_registered(self):
        """Trailing verb patterns are stripped to produce a shorter term."""
        terms = extract_terms("", "ドメインバリデーションを使う")
        assert "ドメインバリデーション" in terms

    def test_verb_suffix_wo_iu_stripped(self):
        terms = extract_terms("", "ページング検索を行う")
        assert "ページング検索" in terms

    def test_verb_suffix_suru_stripped(self):
        terms = extract_terms("", "バリデーションする")
        assert "バリデーション" in terms

    def test_no_stripping_needed_for_noun_title(self):
        terms = extract_terms("", "ユニバーサルDAO")
        assert "ユニバーサルDAO" in terms


class TestExtractTermsAbbreviation:
    """ALL_CAPS abbreviations of 2+ chars are extracted."""

    def test_cors(self):
        terms = extract_terms("Enable CORS support.", "")
        assert "CORS" in terms

    def test_csrf(self):
        terms = extract_terms("Protect against CSRF.", "")
        assert "CSRF" in terms

    def test_single_char_upper_excluded(self):
        terms = extract_terms("Use A or B.", "")
        assert "A" not in terms
        assert "B" not in terms


class TestExtractTermsPropertyName:
    """Dot-separated property names with 3+ segments are extracted."""

    def test_three_segment_property(self):
        terms = extract_terms("Set nablarch.core.validation=true.", "")
        assert "nablarch.core.validation" in terms

    def test_two_segment_excluded(self):
        """Two-segment properties are excluded to avoid false positives."""
        terms = extract_terms("Use nablarch.core as prefix.", "")
        assert "nablarch.core" not in terms

    def test_four_segment_property(self):
        terms = extract_terms("Configure nablarch.core.validation.enabled.", "")
        assert "nablarch.core.validation.enabled" in terms


class TestExtractTermsCompoundKeyword:
    """Hyphen-separated compound keywords are extracted."""

    def test_use_token(self):
        terms = extract_terms("Set use-token header.", "")
        assert "use-token" in terms

    def test_content_type(self):
        terms = extract_terms("Check content-type value.", "")
        assert "content-type" in terms


class TestExtractTermsExclusions:
    """Common English/Japanese words and single chars are excluded."""

    def test_common_english_excluded(self):
        terms = extract_terms("The is for and or a an to in of.", "")
        for w in ["The", "the", "is", "for", "and", "or", "a", "an", "to", "in", "of"]:
            assert w not in terms

    def test_single_char_excluded(self):
        terms = extract_terms("x y z A B.", "")
        for c in ["x", "y", "z"]:
            assert c not in terms


# ---------------------------------------------------------------------------
# Tests for build_terms_map(knowledge_dir) -> dict[str, list[str]]
# ---------------------------------------------------------------------------

class TestBuildTermsMap:
    """build_terms_map scans knowledge_dir and builds term→[path:sN] map."""

    def test_basic_mapping(self, tmp_path):
        kn = tmp_path / "knowledge"
        _write_json(kn, "component/libraries/lib.json", {
            "id": "lib", "title": "Universal DAO",
            "no_knowledge_content": False,
            "sections": [
                {"id": "s1", "title": "概要", "content": "UniversalDao is used.", "level": 2},
            ],
        })
        result = build_terms_map(kn)
        assert "UniversalDao" in result
        assert "component/libraries/lib.json:s1" in result["UniversalDao"]

    def test_section_id_format(self, tmp_path):
        """Section references use 'path:sN' format with forward slashes."""
        kn = tmp_path / "knowledge"
        _write_json(kn, "component/handlers/handler.json", {
            "id": "handler", "title": "Handler",
            "no_knowledge_content": False,
            "sections": [
                {"id": "s3", "title": "設定", "content": "HttpRequestHandler setup.", "level": 2},
            ],
        })
        result = build_terms_map(kn)
        assert "HttpRequestHandler" in result
        ref = result["HttpRequestHandler"][0]
        assert "component/handlers/handler.json:s3" == ref

    def test_no_knowledge_content_excluded(self, tmp_path):
        kn = tmp_path / "knowledge"
        _write_json(kn, "component/libraries/skip.json", {
            "id": "skip", "title": "Skip",
            "no_knowledge_content": True,
            "sections": [
                {"id": "s1", "title": "概要", "content": "BatchAction here.", "level": 2},
            ],
        })
        result = build_terms_map(kn)
        assert "BatchAction" not in result

    def test_term_appears_in_multiple_sections(self, tmp_path):
        """A term in multiple sections has multiple refs (below stop-list threshold)."""
        kn = tmp_path / "knowledge"
        # Add 30 filler sections so 2 refs = 6.7% < 7% threshold
        for i in range(15):
            _write_json(kn, f"component/filler/f{i}.json", {
                "id": f"f{i}", "title": f"Filler {i}",
                "no_knowledge_content": False,
                "sections": [
                    {"id": "s1", "title": "概要", "content": f"UniqueX{i} detail.", "level": 2},
                    {"id": "s2", "title": "詳細", "content": f"MoreX{i} info.", "level": 2},
                ],
            })
        _write_json(kn, "component/libraries/lib.json", {
            "id": "lib", "title": "Lib",
            "no_knowledge_content": False,
            "sections": [
                {"id": "s1", "title": "概要", "content": "UniversalDao usage.", "level": 2},
                {"id": "s2", "title": "設定", "content": "UniversalDao config.", "level": 2},
            ],
        })
        # Total sections: 30 + 2 = 32. UniversalDao in 2 = 6.25% < 7% → kept
        result = build_terms_map(kn)
        refs = result.get("UniversalDao", [])
        assert "component/libraries/lib.json:s1" in refs
        assert "component/libraries/lib.json:s2" in refs

    def test_high_frequency_term_excluded(self, tmp_path):
        """Terms appearing in >= 7% of all sections are excluded as stop-list."""
        kn = tmp_path / "knowledge"
        # Create enough sections to trigger stop-list (need >= 7% of total)
        # If total sections = 15, threshold = ceil(15 * 0.07) = 2
        # So a term in 2/15 sections (13.3%) should be excluded
        for i in range(14):
            _write_json(kn, f"component/libs/lib{i}.json", {
                "id": f"lib{i}", "title": f"Lib {i}",
                "no_knowledge_content": False,
                "sections": [
                    {"id": "s1", "title": "概要", "content": f"UniqueClass{i} detail.", "level": 2},
                ],
            })
        # Add a file where CommonTerm appears
        _write_json(kn, "component/libs/common1.json", {
            "id": "common1", "title": "Common",
            "no_knowledge_content": False,
            "sections": [
                {"id": "s1", "title": "概要", "content": "CommonTerm is used.", "level": 2},
                {"id": "s2", "title": "詳細", "content": "CommonTerm again.", "level": 2},
            ],
        })
        # Total sections: 14 + 2 = 16. CommonTerm in 2 sections = 12.5% >= 7% → excluded
        result = build_terms_map(kn)
        assert "CommonTerm" not in result
        # Unique terms should still be present
        assert "UniqueClass0" in result


# ---------------------------------------------------------------------------
# Tests for generate_terms(knowledge_dir, output_path) -> None
# ---------------------------------------------------------------------------

class TestGenerateTerms:
    """generate_terms writes terms.json to output_path."""

    def test_creates_valid_json(self, tmp_path):
        kn = tmp_path / "knowledge"
        _write_json(kn, "component/libraries/lib.json", {
            "id": "lib", "title": "Universal DAO",
            "no_knowledge_content": False,
            "sections": [
                {"id": "s1", "title": "概要", "content": "UniversalDao usage.", "level": 2},
            ],
        })
        out = tmp_path / "terms.json"
        generate_terms(kn, out)
        assert out.exists()
        data = json.loads(out.read_text(encoding="utf-8"))
        assert isinstance(data, dict)
        assert "UniversalDao" in data

    def test_output_sorted_by_term(self, tmp_path):
        """Output keys are sorted for deterministic diffs."""
        kn = tmp_path / "knowledge"
        _write_json(kn, "component/libraries/lib.json", {
            "id": "lib", "title": "Lib",
            "no_knowledge_content": False,
            "sections": [
                {"id": "s1", "title": "概要", "content": "ZZZClass and AAAClass.", "level": 2},
            ],
        })
        out = tmp_path / "terms.json"
        generate_terms(kn, out)
        data = json.loads(out.read_text(encoding="utf-8"))
        keys = list(data.keys())
        assert keys == sorted(keys)

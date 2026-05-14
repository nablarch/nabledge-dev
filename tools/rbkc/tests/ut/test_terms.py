"""Unit tests for terms.py — terms.json generation for keyword-search.

terms.json format:
    {term: [section_ids], ...}

where section_ids use full relative path format:
    "component/libraries/libraries-universal-dao.json:s1"

Term extraction rules (from keyword-search-design.md):
1. Java class names (CamelCase: UniversalDao, BatchAction) — ASCII >= 3
2. Method names (camelCase: batchUpdate, findAll) — ASCII >= 3
3. Annotation names (@Valid, @Published) — ASCII with @ prefix >= 3
4. Japanese technical terms from section titles:
   - Full title registered as term
   - Title with verb suffix removed also registered
5. English abbreviations (ALL_CAPS >= 2: CORS, CSP, DB)
6. Property names (dot-separated: nablarch.core.validation)
7. Compound keywords (hyphen/underscore: use-token, batch_update)

Stoplist: terms with section_df >= 7% are excluded.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.create.terms import generate_terms


def _write_json(knowledge_dir: Path, output_path: str, data: dict) -> None:
    p = knowledge_dir / output_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def _read_terms(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _add_padding_sections(knowledge_dir: Path, count: int = 20) -> None:
    """Add padding sections so rare terms stay below section_df threshold.

    With 20 padding sections, a term in 1 section = 1/21 ~= 4.8% < 7%.
    """
    sections = [{"id": f"s{i}", "title": f"PaddingSection{i}", "content": ""} for i in range(1, count + 1)]
    _write_json(knowledge_dir, "_padding/padding.json", {
        "id": "padding", "title": "Padding", "no_knowledge_content": False,
        "sections": sections,
    })


class TestAsciiTermExtraction:
    def test_class_name_from_title(self, tmp_path):
        """Java class names (CamelCase) extracted from section titles."""
        _add_padding_sections(tmp_path)
        _write_json(tmp_path, "a/foo.json", {
            "id": "foo", "title": "Foo", "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "UniversalDao", "content": ""}],
        })
        out = tmp_path / "terms.json"
        generate_terms(tmp_path, out)
        terms = _read_terms(out)
        assert "UniversalDao" in terms

    def test_class_name_from_content(self, tmp_path):
        """Java class names extracted from section content."""
        _add_padding_sections(tmp_path)
        _write_json(tmp_path, "a/foo.json", {
            "id": "foo", "title": "Foo", "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "Overview", "content": "Use UniversalDao here."}],
        })
        out = tmp_path / "terms.json"
        generate_terms(tmp_path, out)
        terms = _read_terms(out)
        assert "UniversalDao" in terms

    def test_method_name(self, tmp_path):
        """Method names (camelCase) extracted."""
        _add_padding_sections(tmp_path)
        _write_json(tmp_path, "a/foo.json", {
            "id": "foo", "title": "Foo", "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "batchUpdate", "content": ""}],
        })
        out = tmp_path / "terms.json"
        generate_terms(tmp_path, out)
        terms = _read_terms(out)
        assert "batchUpdate" in terms

    def test_short_ascii_excluded(self, tmp_path):
        """ASCII terms shorter than 3 chars excluded (except all-caps >= 2)."""
        _write_json(tmp_path, "a/foo.json", {
            "id": "foo", "title": "Foo", "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "A go do run is", "content": ""}],
        })
        out = tmp_path / "terms.json"
        generate_terms(tmp_path, out)
        terms = _read_terms(out)
        assert "A" not in terms
        assert "go" not in terms
        assert "do" not in terms
        assert "is" not in terms


class TestAnnotationExtraction:
    def test_at_prefix_preserved(self, tmp_path):
        """Annotation names like @Valid are extracted with @ prefix."""
        _add_padding_sections(tmp_path)
        _write_json(tmp_path, "a/foo.json", {
            "id": "foo", "title": "Foo", "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "@Valid annotation usage", "content": ""}],
        })
        out = tmp_path / "terms.json"
        generate_terms(tmp_path, out)
        terms = _read_terms(out)
        assert "@Valid" in terms

    def test_published_annotation(self, tmp_path):
        """@Published annotation extracted."""
        _add_padding_sections(tmp_path)
        _write_json(tmp_path, "a/foo.json", {
            "id": "foo", "title": "Foo", "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "", "content": "@Published interface"}],
        })
        out = tmp_path / "terms.json"
        generate_terms(tmp_path, out)
        terms = _read_terms(out)
        assert "@Published" in terms


class TestAbbreviationExtraction:
    def test_all_caps_two_chars(self, tmp_path):
        """English abbreviations of 2+ all-caps chars extracted (DB, IO)."""
        _add_padding_sections(tmp_path)
        _write_json(tmp_path, "a/foo.json", {
            "id": "foo", "title": "Foo", "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "DB connection pool", "content": ""}],
        })
        out = tmp_path / "terms.json"
        generate_terms(tmp_path, out)
        terms = _read_terms(out)
        assert "DB" in terms

    def test_four_char_abbreviation(self, tmp_path):
        """CORS, CSRF etc. extracted."""
        _add_padding_sections(tmp_path)
        _write_json(tmp_path, "a/foo.json", {
            "id": "foo", "title": "Foo", "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "CORS settings", "content": ""}],
        })
        out = tmp_path / "terms.json"
        generate_terms(tmp_path, out)
        terms = _read_terms(out)
        assert "CORS" in terms


class TestJapaneseTitleTerms:
    def test_full_title_registered(self, tmp_path):
        """Full Japanese section title registered as term."""
        _add_padding_sections(tmp_path)
        _write_json(tmp_path, "a/foo.json", {
            "id": "foo", "title": "Foo", "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "ドメインバリデーションを使う", "content": ""}],
        })
        out = tmp_path / "terms.json"
        generate_terms(tmp_path, out)
        terms = _read_terms(out)
        assert "ドメインバリデーションを使う" in terms

    def test_verb_suffix_removed(self, tmp_path):
        """Title with verb suffix removed also registered as term."""
        _add_padding_sections(tmp_path)
        _write_json(tmp_path, "a/foo.json", {
            "id": "foo", "title": "Foo", "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "ドメインバリデーションを使う", "content": ""}],
        })
        out = tmp_path / "terms.json"
        generate_terms(tmp_path, out)
        terms = _read_terms(out)
        assert "ドメインバリデーション" in terms

    def test_verb_suffix_wo_okonau(self, tmp_path):
        """を行う suffix removed."""
        _add_padding_sections(tmp_path)
        _write_json(tmp_path, "a/foo.json", {
            "id": "foo", "title": "Foo", "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "入力値チェックを行う", "content": ""}],
        })
        out = tmp_path / "terms.json"
        generate_terms(tmp_path, out)
        terms = _read_terms(out)
        assert "入力値チェック" in terms

    def test_verb_suffix_suru(self, tmp_path):
        """する suffix removed."""
        _add_padding_sections(tmp_path)
        _write_json(tmp_path, "a/foo.json", {
            "id": "foo", "title": "Foo", "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "バリデーションする", "content": ""}],
        })
        out = tmp_path / "terms.json"
        generate_terms(tmp_path, out)
        terms = _read_terms(out)
        assert "バリデーション" in terms

    def test_verb_suffix_ni_tsuite(self, tmp_path):
        """について suffix removed."""
        _add_padding_sections(tmp_path)
        _write_json(tmp_path, "a/foo.json", {
            "id": "foo", "title": "Foo", "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "ルーティングについて", "content": ""}],
        })
        out = tmp_path / "terms.json"
        generate_terms(tmp_path, out)
        terms = _read_terms(out)
        assert "ルーティング" in terms

    def test_verb_suffix_no_yarikata(self, tmp_path):
        """のやり方 suffix removed."""
        _add_padding_sections(tmp_path)
        _write_json(tmp_path, "a/foo.json", {
            "id": "foo", "title": "Foo", "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "テストのやり方", "content": ""}],
        })
        out = tmp_path / "terms.json"
        generate_terms(tmp_path, out)
        terms = _read_terms(out)
        assert "テスト" in terms

    def test_verb_suffix_no_houhou(self, tmp_path):
        """の方法 suffix removed."""
        _add_padding_sections(tmp_path)
        _write_json(tmp_path, "a/foo.json", {
            "id": "foo", "title": "Foo", "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "データアクセスの方法", "content": ""}],
        })
        out = tmp_path / "terms.json"
        generate_terms(tmp_path, out)
        terms = _read_terms(out)
        assert "データアクセス" in terms

    def test_verb_suffix_no_tsukaikata(self, tmp_path):
        """の使い方 suffix removed."""
        _add_padding_sections(tmp_path)
        _write_json(tmp_path, "a/foo.json", {
            "id": "foo", "title": "Foo", "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "バリデーションの使い方", "content": ""}],
        })
        out = tmp_path / "terms.json"
        generate_terms(tmp_path, out)
        terms = _read_terms(out)
        assert "バリデーション" in terms

    def test_verb_suffix_no_settei(self, tmp_path):
        """の設定 suffix removed."""
        _add_padding_sections(tmp_path)
        _write_json(tmp_path, "a/foo.json", {
            "id": "foo", "title": "Foo", "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "プロパティの設定", "content": ""}],
        })
        out = tmp_path / "terms.json"
        generate_terms(tmp_path, out)
        terms = _read_terms(out)
        assert "プロパティ" in terms

    def test_verb_suffix_wo_settei_suru(self, tmp_path):
        """を設定する suffix removed."""
        _add_padding_sections(tmp_path)
        _write_json(tmp_path, "a/foo.json", {
            "id": "foo", "title": "Foo", "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "トランザクションを設定する", "content": ""}],
        })
        out = tmp_path / "terms.json"
        generate_terms(tmp_path, out)
        terms = _read_terms(out)
        assert "トランザクション" in terms

    def test_verb_suffix_wo_sakusei_suru(self, tmp_path):
        """を作成する suffix removed."""
        _add_padding_sections(tmp_path)
        _write_json(tmp_path, "a/foo.json", {
            "id": "foo", "title": "Foo", "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "エンティティを作成する", "content": ""}],
        })
        out = tmp_path / "terms.json"
        generate_terms(tmp_path, out)
        terms = _read_terms(out)
        assert "エンティティ" in terms

    def test_verb_suffix_wo_jissou_suru(self, tmp_path):
        """を実装する suffix removed."""
        _add_padding_sections(tmp_path)
        _write_json(tmp_path, "a/foo.json", {
            "id": "foo", "title": "Foo", "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "ハンドラを実装する", "content": ""}],
        })
        out = tmp_path / "terms.json"
        generate_terms(tmp_path, out)
        terms = _read_terms(out)
        assert "ハンドラ" in terms

    def test_ascii_only_title_no_japanese_title_term(self, tmp_path):
        """Titles containing only ASCII should not generate Japanese title terms."""
        _add_padding_sections(tmp_path)
        _write_json(tmp_path, "a/foo.json", {
            "id": "foo", "title": "Foo", "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "Getting Started", "content": ""}],
        })
        out = tmp_path / "terms.json"
        generate_terms(tmp_path, out)
        terms = _read_terms(out)
        assert "Getting Started" not in terms


class TestPropertyNames:
    def test_dot_separated_property(self, tmp_path):
        """Dot-separated property names extracted as single term."""
        _add_padding_sections(tmp_path)
        _write_json(tmp_path, "a/foo.json", {
            "id": "foo", "title": "Foo", "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "", "content": "Set nablarch.core.validation property"}],
        })
        out = tmp_path / "terms.json"
        generate_terms(tmp_path, out)
        terms = _read_terms(out)
        assert "nablarch.core.validation" in terms

    def test_short_property_segments(self, tmp_path):
        """Property with short segments still extracted (a.b not useful but x.y.z ok)."""
        _add_padding_sections(tmp_path)
        _write_json(tmp_path, "a/foo.json", {
            "id": "foo", "title": "Foo", "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "", "content": "config nablarch.fw.handler property"}],
        })
        out = tmp_path / "terms.json"
        generate_terms(tmp_path, out)
        terms = _read_terms(out)
        assert "nablarch.fw.handler" in terms


class TestCompoundKeywords:
    def test_hyphen_separated(self, tmp_path):
        """Hyphen-separated compound keywords extracted."""
        _add_padding_sections(tmp_path)
        _write_json(tmp_path, "a/foo.json", {
            "id": "foo", "title": "Foo", "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "use-token header", "content": ""}],
        })
        out = tmp_path / "terms.json"
        generate_terms(tmp_path, out)
        terms = _read_terms(out)
        assert "use-token" in terms

    def test_underscore_separated(self, tmp_path):
        """Underscore-separated compound keywords extracted."""
        _add_padding_sections(tmp_path)
        _write_json(tmp_path, "a/foo.json", {
            "id": "foo", "title": "Foo", "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "batch_update method", "content": ""}],
        })
        out = tmp_path / "terms.json"
        generate_terms(tmp_path, out)
        terms = _read_terms(out)
        assert "batch_update" in terms


class TestSectionIdFormat:
    def test_uses_full_relative_path(self, tmp_path):
        """Section IDs in terms.json use full relative path format."""
        _add_padding_sections(tmp_path)
        _write_json(tmp_path, "component/lib/foo.json", {
            "id": "foo", "title": "Foo", "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "UniversalDao", "content": ""}],
        })
        out = tmp_path / "terms.json"
        generate_terms(tmp_path, out)
        terms = _read_terms(out)
        assert "UniversalDao" in terms
        assert "component/lib/foo.json:s1" in terms["UniversalDao"]


class TestFilters:
    def test_no_knowledge_content_excluded(self, tmp_path):
        """Sections from no_knowledge_content files excluded."""
        _write_json(tmp_path, "a/stub.json", {
            "id": "stub", "title": "Stub", "no_knowledge_content": True,
            "sections": [{"id": "s1", "title": "UniqueTermXyzzy", "content": ""}],
        })
        out = tmp_path / "terms.json"
        generate_terms(tmp_path, out)
        terms = _read_terms(out)
        assert "UniqueTermXyzzy" not in terms

    def test_stopword_excluded_by_section_df(self, tmp_path):
        """Terms appearing in >= 7% of sections excluded (stopwords)."""
        sections = [{"id": f"s{i}", "title": f"Section{i}", "content": ""} for i in range(1, 14)]
        _write_json(tmp_path, "a/foo.json", {
            "id": "foo", "title": "Foo", "no_knowledge_content": False,
            "sections": sections,
        })
        sections_with_term = [
            {"id": "s1", "title": "CommonWord intro", "content": ""},
            {"id": "s2", "title": "CommonWord usage", "content": ""},
        ]
        _write_json(tmp_path, "b/bar.json", {
            "id": "bar", "title": "Bar", "no_knowledge_content": False,
            "sections": sections_with_term,
        })
        out = tmp_path / "terms.json"
        generate_terms(tmp_path, out)
        terms = _read_terms(out)
        assert "CommonWord" not in terms

    def test_rare_term_included(self, tmp_path):
        """Terms in < 7% of sections included."""
        sections = [{"id": f"s{i}", "title": f"Section{i}", "content": ""} for i in range(1, 15)]
        _write_json(tmp_path, "a/foo.json", {
            "id": "foo", "title": "Foo", "no_knowledge_content": False,
            "sections": sections,
        })
        _write_json(tmp_path, "b/bar.json", {
            "id": "bar", "title": "Bar", "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "UniqueRareTerm", "content": ""}],
        })
        out = tmp_path / "terms.json"
        generate_terms(tmp_path, out)
        terms = _read_terms(out)
        assert "UniqueRareTerm" in terms

    def test_single_char_cjk_excluded(self, tmp_path):
        """CJK sequences of length 1 excluded."""
        _write_json(tmp_path, "a/foo.json", {
            "id": "foo", "title": "Foo", "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "の", "content": ""}],
        })
        out = tmp_path / "terms.json"
        generate_terms(tmp_path, out)
        terms = _read_terms(out)
        assert "の" not in terms


class TestMultiSection:
    def test_term_in_multiple_sections(self, tmp_path):
        """A term in multiple sections lists all section IDs."""
        _add_padding_sections(tmp_path, count=30)
        _write_json(tmp_path, "a/foo.json", {
            "id": "foo", "title": "Foo", "no_knowledge_content": False,
            "sections": [
                {"id": "s1", "title": "UniversalDao intro", "content": ""},
                {"id": "s3", "title": "UniversalDao advanced", "content": ""},
            ],
        })
        out = tmp_path / "terms.json"
        generate_terms(tmp_path, out)
        terms = _read_terms(out)
        assert "UniversalDao" in terms
        section_ids = terms["UniversalDao"]
        assert "a/foo.json:s1" in section_ids
        assert "a/foo.json:s3" in section_ids


class TestOutputFormat:
    def test_flat_format_no_version_key(self, tmp_path):
        """Output is flat {term: [section_ids]} — no version or terms nesting."""
        _add_padding_sections(tmp_path)
        _write_json(tmp_path, "a/foo.json", {
            "id": "foo", "title": "Foo", "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "UniversalDao", "content": ""}],
        })
        out = tmp_path / "terms.json"
        generate_terms(tmp_path, out)
        terms = _read_terms(out)
        assert "version" not in terms
        assert "terms" not in terms
        assert isinstance(terms.get("UniversalDao"), list)

    def test_section_ids_sorted(self, tmp_path):
        """Section ID lists are sorted for deterministic output."""
        _add_padding_sections(tmp_path, count=30)
        _write_json(tmp_path, "b/bar.json", {
            "id": "bar", "title": "Bar", "no_knowledge_content": False,
            "sections": [
                {"id": "s5", "title": "UniversalDao", "content": ""},
                {"id": "s1", "title": "UniversalDao", "content": ""},
            ],
        })
        out = tmp_path / "terms.json"
        generate_terms(tmp_path, out)
        terms = _read_terms(out)
        ids = terms["UniversalDao"]
        assert ids == sorted(ids)


class TestReturnValue:
    def test_returns_term_count(self, tmp_path):
        """Returns number of terms written."""
        _add_padding_sections(tmp_path)
        _write_json(tmp_path, "a/foo.json", {
            "id": "foo", "title": "Foo", "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "UniversalDao", "content": ""}],
        })
        out = tmp_path / "terms.json"
        count = generate_terms(tmp_path, out)
        assert count >= 1

    def test_empty_dir_returns_zero(self, tmp_path):
        """Empty knowledge dir returns 0 and writes empty JSON."""
        out = tmp_path / "terms.json"
        count = generate_terms(tmp_path, out)
        assert count == 0
        assert _read_terms(out) == {}

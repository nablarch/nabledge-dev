"""Unit tests for Phase 3: hints extraction (Stage 1 + Stage 2 merge)."""
import pytest
from scripts.hints import extract_hints, merge_hints


# ---------------------------------------------------------------------------
# extract_hints — Stage 1: regex-based mechanical extraction
# ---------------------------------------------------------------------------

class TestExtractHintsStage1:
    """extract_hints(content) extracts identifiers from Markdown content."""

    def test_pascal_case_class_name(self):
        hints = extract_hints("Use `BasicDaoContextFactory` to configure.")
        assert "BasicDaoContextFactory" in hints

    def test_multiple_pascal_case(self):
        hints = extract_hints("`UniversalDao` and `DeferredEntityList` are used.")
        assert "UniversalDao" in hints
        assert "DeferredEntityList" in hints

    def test_annotation(self):
        hints = extract_hints("Annotate with `@Table` and `@Entity`.")
        assert "@Table" in hints
        assert "@Entity" in hints

    def test_package_name(self):
        hints = extract_hints("`nablarch.common.dao.UniversalDao` を参照。")
        assert "nablarch.common.dao.UniversalDao" in hints

    def test_bold_text_extracted(self):
        hints = extract_hints("**1回で検索できるSQL** を作成する。")
        assert "1回で検索できるSQL" in hints

    def test_section_heading_in_content(self):
        # ## heading text within section content (h4+)
        hints = extract_hints("#### モジュール一覧\n\nContent.")
        assert "モジュール一覧" in hints

    def test_no_duplicates(self):
        hints = extract_hints("`FooClass` and `FooClass` again.")
        assert hints.count("FooClass") == 1

    def test_returns_list(self):
        hints = extract_hints("Some content.")
        assert isinstance(hints, list)

    def test_empty_content(self):
        hints = extract_hints("")
        assert hints == []

    def test_short_pascal_case_skipped(self):
        # Single-word short tokens (≤2 chars) should not be extracted
        hints = extract_hints("Use `Fo` class.")
        assert "Fo" not in hints

    def test_xml_element_name(self):
        # XML property names like daoContextFactory
        hints = extract_hints('name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory"')
        assert "BasicDaoContextFactory" in hints

    def test_java_method_reference(self):
        # UniversalDao#defer → extract class name
        hints = extract_hints("`UniversalDao#defer` メソッドを呼び出す。")
        assert "UniversalDao" in hints


# ---------------------------------------------------------------------------
# merge_hints — Stage 1 + Stage 2 dedup and sort
# ---------------------------------------------------------------------------

class TestMergeHints:
    def test_combines_stage1_and_stage2(self):
        stage1 = ["FooClass", "BarUtil"]
        stage2 = ["BazService", "FooClass"]
        result = merge_hints(stage1, stage2)
        assert "FooClass" in result
        assert "BarUtil" in result
        assert "BazService" in result

    def test_no_duplicates_after_merge(self):
        stage1 = ["Foo", "Bar"]
        stage2 = ["Bar", "Baz"]
        result = merge_hints(stage1, stage2)
        assert result.count("Bar") == 1

    def test_returns_sorted_list(self):
        stage1 = ["Zebra", "Apple"]
        stage2 = ["Mango"]
        result = merge_hints(stage1, stage2)
        assert result == sorted(result)

    def test_empty_inputs(self):
        assert merge_hints([], []) == []

    def test_stage2_only(self):
        result = merge_hints([], ["HintA", "HintB"])
        assert "HintA" in result
        assert "HintB" in result

    def test_stage1_only(self):
        result = merge_hints(["HintX"], [])
        assert "HintX" in result

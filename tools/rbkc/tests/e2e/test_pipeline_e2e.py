"""E2E tests for Phase 2+3 pipeline: RST convert → hints extraction.

Verifies the full pipeline: RST source → convert() → extract_hints() →
merge_hints() with Stage 2 cache lookup. Tests that each stage correctly
feeds the next.
"""
from pathlib import Path

import pytest

from scripts.converters.rst import convert
from scripts.hints import build_hints_index, extract_hints, lookup_hints, merge_hints

V6_DOC_ROOT = Path(".lw/nab-official/v6/nablarch-document/ja")
V6_CACHE_ROOT = Path("tools/knowledge-creator/.cache/v6")
UNIVERSAL_DAO_RST = (
    V6_DOC_ROOT
    / "application_framework/application_framework/libraries/database/universal_dao.rst"
)


@pytest.fixture(scope="module")
def dao_result():
    return convert(UNIVERSAL_DAO_RST.read_text(), "libraries-universal_dao")


@pytest.fixture(scope="module")
def hints_index():
    if not V6_CACHE_ROOT.exists():
        pytest.skip("v6 KC cache not available")
    return build_hints_index(V6_CACHE_ROOT)


class TestStage1ExtractionFromConvertedRST:
    """Stage 1: extract_hints() on converter output sections."""

    def test_pascal_case_extracted_from_content(self, dao_result):
        # '使用方法' section contains UniversalDao class references
        section = next(s for s in dao_result.sections if s.title == "使用方法")
        hints = extract_hints(section.content)
        assert "UniversalDao" in hints, \
            f"Expected 'UniversalDao' in hints, got: {hints[:10]}"

    def test_annotation_extracted(self, dao_result):
        # RST source contains @Table, @Entity, etc.
        all_hints: list[str] = []
        for s in dao_result.sections:
            all_hints.extend(extract_hints(s.content))
        assert any(h.startswith("@") for h in all_hints), \
            "Expected at least one @Annotation hint across all sections"

    def test_no_empty_hints_from_empty_sections(self, dao_result):
        # extract_hints on empty content must return []
        empty_sections = [s for s in dao_result.sections if not s.content.strip()]
        for s in empty_sections:
            assert extract_hints(s.content) == [], \
                f"Expected [] for empty section {s.title!r}"


class TestStage2LookupAndMerge:
    """Stage 2: lookup_hints() + merge_hints() adds cache-derived hints."""

    def test_merge_produces_superset_of_stage1(self, dao_result, hints_index):
        # For a section with Stage 2 cache hits, merged result >= Stage 1 alone
        section = next(
            s for s in dao_result.sections
            if lookup_hints(hints_index, "libraries-universal_dao", s.title)
        )
        stage1 = extract_hints(section.content)
        stage2 = lookup_hints(hints_index, "libraries-universal_dao", section.title)
        merged = merge_hints(stage1, stage2)

        assert len(merged) >= len(stage1), \
            "Merged hints must be >= Stage 1 hints"
        for h in stage2:
            assert h in merged, f"Stage 2 hint {h!r} missing from merged result"

    def test_merged_hints_are_sorted_and_deduped(self, dao_result, hints_index):
        all_merged: list[str] = []
        for s in dao_result.sections:
            stage1 = extract_hints(s.content)
            stage2 = lookup_hints(hints_index, "libraries-universal_dao", s.title)
            merged = merge_hints(stage1, stage2)
            assert merged == sorted(set(merged)), \
                f"Section {s.title!r}: merged hints not sorted/deduped"
            all_merged.extend(merged)

    def test_cache_lookup_uses_section_title_as_key(self, dao_result, hints_index):
        # Ensure section titles from convert() match cache keys
        cache_sections = hints_index.get("libraries-universal_dao", {})
        converter_titles = {s.title for s in dao_result.sections}
        matched = converter_titles & set(cache_sections)
        assert len(matched) > 0, (
            "No section titles from converter matched cache keys. "
            f"Converter titles sample: {list(converter_titles)[:5]}. "
            f"Cache keys sample: {list(cache_sections)[:5]}"
        )

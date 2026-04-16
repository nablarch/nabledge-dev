"""E2E tests for Phase 2+3 pipeline: RST convert → hints lookup.

Verifies the full pipeline: RST source → convert() → lookup_hints() from
KC cache index. Tests that section titles from the converter match cache
keys, and that hints can be retrieved per section.

Note: Stage 1 (regex-based extract_hints) was removed in Phase 10-6.
Hints are now derived exclusively from KC cache via Step A/B mapping.
"""
from pathlib import Path

import pytest

from scripts.converters.rst import convert
from scripts.hints import build_hints_index, lookup_hints

_REPO_ROOT = Path(__file__).parents[4]
V6_DOC_ROOT = _REPO_ROOT / ".lw/nab-official/v6/nablarch-document/ja"
V6_CACHE_ROOT = _REPO_ROOT / "tools/knowledge-creator/.cache/v6"
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


class TestHintsLookup:
    """Hints lookup: lookup_hints() returns cache-derived hints per section."""

    def test_hints_returned_for_section_with_cache_hit(self, dao_result, hints_index):
        # At least one section in universal_dao should have hints in the cache
        sections_with_hints = [
            s for s in dao_result.sections
            if lookup_hints(hints_index, "libraries-universal_dao", s.title)
        ]
        assert len(sections_with_hints) > 0, (
            "Expected at least one section to have cache hints for libraries-universal_dao"
        )

    def test_lookup_returns_list_for_unknown_section(self, hints_index):
        # lookup_hints never raises; returns [] for unknown keys
        result = lookup_hints(hints_index, "libraries-universal_dao", "__nonexistent__")
        assert result == []

    def test_lookup_returns_list_for_unknown_file(self, hints_index):
        result = lookup_hints(hints_index, "__nonexistent_file__", "any_section")
        assert result == []

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

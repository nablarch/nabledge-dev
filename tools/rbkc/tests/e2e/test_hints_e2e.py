"""E2E tests for Phase 1: hints index against real v6 KC cache.

Verifies that build_hints_index works correctly on actual cache data,
not just synthetic fixtures.
"""
from pathlib import Path

import pytest

from scripts.hints import build_hints_index, lookup_hints

V6_CACHE_ROOT = Path("tools/knowledge-creator/.cache/v6")


@pytest.fixture(scope="module")
def hints_index():
    if not V6_CACHE_ROOT.exists():
        pytest.skip("v6 KC cache not available")
    return build_hints_index(V6_CACHE_ROOT)


class TestBuildHintsIndexV6:
    def test_returns_non_empty_dict(self, hints_index):
        assert len(hints_index) > 100, f"Expected >100 file_ids, got {len(hints_index)}"

    def test_known_file_id_present(self, hints_index):
        assert "libraries-universal_dao" in hints_index

    def test_no_split_suffix_in_keys(self, hints_index):
        # Split files (foo--s1, foo--s2) must be merged under base id
        for key in hints_index:
            assert "--s" not in key, f"Split suffix leaked into index key: {key!r}"

    def test_sections_are_dicts(self, hints_index):
        for file_id, sections in hints_index.items():
            assert isinstance(sections, dict), \
                f"{file_id!r}: expected dict, got {type(sections)}"

    def test_hints_are_lists(self, hints_index):
        for file_id, sections in hints_index.items():
            for title, hints in sections.items():
                assert isinstance(hints, list), \
                    f"{file_id!r}/{title!r}: expected list, got {type(hints)}"


class TestLookupHintsV6:
    def test_known_section_returns_hints(self, hints_index):
        hints = lookup_hints(
            hints_index,
            "libraries-universal_dao",
            "データサイズの大きいバイナリデータを登録（更新）する",
        )
        assert len(hints) > 0

    def test_unknown_file_id_returns_empty(self, hints_index):
        assert lookup_hints(hints_index, "nonexistent-file-id", "概要") == []

    def test_unknown_section_returns_empty(self, hints_index):
        assert lookup_hints(hints_index, "libraries-universal_dao", "存在しないセクション") == []

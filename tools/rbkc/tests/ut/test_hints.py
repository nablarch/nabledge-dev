"""Unit tests for hints.py — Phase 1: KC cache hints mapping."""
import json
import pytest
from pathlib import Path
from scripts.create.hints import build_hints_index, lookup_hints, _map_step_a


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def cache_dir(tmp_path):
    """Create a minimal fake KC cache directory."""
    knowledge_dir = tmp_path / "knowledge"
    knowledge_dir.mkdir()

    # File without split suffix — single-section file
    (knowledge_dir / "guide").mkdir()
    single = {
        "id": "some-guide",
        "title": "ガイド",
        "no_knowledge_content": False,
        "official_doc_urls": ["https://example.com/guide.html"],
        "index": [
            {"id": "s1", "title": "概要", "hints": ["HintA", "HintB"]},
            {"id": "s2", "title": "使い方", "hints": ["HintC"]},
        ],
        "sections": {},
    }
    (knowledge_dir / "guide" / "some-guide.json").write_text(
        json.dumps(single, ensure_ascii=False)
    )

    # File with split suffix --s1
    (knowledge_dir / "component").mkdir()
    split_s1 = {
        "id": "foo-bar--s1",
        "title": "Fooコンポーネント",
        "no_knowledge_content": False,
        "official_doc_urls": [],
        "index": [
            {"id": "s1", "title": "モジュール一覧", "hints": ["FooClass", "BarClass"]},
        ],
        "sections": {},
    }
    (knowledge_dir / "component" / "foo-bar--s1.json").write_text(
        json.dumps(split_s1, ensure_ascii=False)
    )

    # Same base file, split --s2
    split_s2 = {
        "id": "foo-bar--s2",
        "title": "Fooコンポーネント",
        "no_knowledge_content": False,
        "official_doc_urls": [],
        "index": [
            {"id": "s1", "title": "設定方法", "hints": ["FooConfig", "BazUtil"]},
        ],
        "sections": {},
    }
    (knowledge_dir / "component" / "foo-bar--s2.json").write_text(
        json.dumps(split_s2, ensure_ascii=False)
    )

    # no_knowledge_content=True — should still be included (hints may exist)
    (knowledge_dir / "about").mkdir()
    nav_only = {
        "id": "about-index",
        "title": "目次",
        "no_knowledge_content": True,
        "official_doc_urls": [],
        "index": [],
        "sections": {},
    }
    (knowledge_dir / "about" / "about-index.json").write_text(
        json.dumps(nav_only, ensure_ascii=False)
    )

    return tmp_path


# ---------------------------------------------------------------------------
# build_hints_index
# ---------------------------------------------------------------------------

class TestBuildHintsIndex:
    def test_returns_dict(self, cache_dir):
        result = build_hints_index(cache_dir)
        assert isinstance(result, dict)

    def test_file_ids_are_base_ids(self, cache_dir):
        result = build_hints_index(cache_dir)
        # Split files should be merged under base id "foo-bar"
        assert "foo-bar" in result
        # Non-split file id unchanged
        assert "some-guide" in result

    def test_no_split_suffix_in_keys(self, cache_dir):
        result = build_hints_index(cache_dir)
        for key in result:
            assert "--s" not in key, f"Split suffix found in key: {key!r}"

    def test_section_titles_present(self, cache_dir):
        result = build_hints_index(cache_dir)
        assert "概要" in result["some-guide"]
        assert "使い方" in result["some-guide"]

    def test_hints_values_correct(self, cache_dir):
        result = build_hints_index(cache_dir)
        assert result["some-guide"]["概要"] == ["HintA", "HintB"]
        assert result["some-guide"]["使い方"] == ["HintC"]

    def test_split_files_merged(self, cache_dir):
        result = build_hints_index(cache_dir)
        # Sections from both --s1 and --s2 should appear under "foo-bar"
        assert "モジュール一覧" in result["foo-bar"]
        assert "設定方法" in result["foo-bar"]

    def test_split_hints_correct(self, cache_dir):
        result = build_hints_index(cache_dir)
        assert result["foo-bar"]["モジュール一覧"] == ["FooClass", "BarClass"]
        assert result["foo-bar"]["設定方法"] == ["FooConfig", "BazUtil"]

    def test_empty_index_file_included(self, cache_dir):
        result = build_hints_index(cache_dir)
        # no_knowledge_content=True, index=[] → key exists but empty dict
        assert "about-index" in result
        assert result["about-index"] == {}

    def test_missing_cache_dir_raises(self, tmp_path):
        with pytest.raises((FileNotFoundError, NotADirectoryError)):
            build_hints_index(tmp_path / "nonexistent")


# ---------------------------------------------------------------------------
# lookup_hints
# ---------------------------------------------------------------------------

class TestLookupHints:
    @pytest.fixture
    def hints_map(self, cache_dir):
        return build_hints_index(cache_dir)

    def test_found_returns_hints_list(self, hints_map):
        result = lookup_hints(hints_map, "some-guide", "概要")
        assert result == ["HintA", "HintB"]

    def test_unknown_file_id_returns_empty_list(self, hints_map):
        result = lookup_hints(hints_map, "nonexistent-file", "概要")
        assert result == []

    def test_unknown_section_title_returns_empty_list(self, hints_map):
        result = lookup_hints(hints_map, "some-guide", "存在しないセクション")
        assert result == []

    def test_both_unknown_returns_empty_list(self, hints_map):
        result = lookup_hints(hints_map, "no-such-file", "no-such-section")
        assert result == []

    def test_returns_list_not_none(self, hints_map):
        result = lookup_hints(hints_map, "x", "y")
        assert result is not None
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# _map_step_a — substring match must respect pointer order
# ---------------------------------------------------------------------------

class TestMapStepAPointer:
    def test_substring_match_does_not_reuse_past_expected(self):
        """Substring match must search from pointer, not from index 0.

        Scenario: expected = ["セクションA", "詳細"]
        kc_index = [
            {"title": "セクションAの詳細", "hints": ["H1"]},
                # substring "セクションA" → pointer advances to 1
            {"title": "セクションAの概要", "hints": ["H2"]},
                # BUG (before fix): "セクションA" is STILL a substring even though
                # pointer is now 1.  Without the fix, H2 is mistakenly assigned to
                # the already-consumed "セクションA" instead of the current "詳細".
        ]
        Expected with fix: H2 → "詳細" (fallback to pointer=1), not back to "セクションA".
        """
        expected = ["セクションA", "詳細"]
        kc_index = [
            {"title": "セクションAの詳細", "hints": ["H1"]},
            {"title": "セクションAの概要", "hints": ["H2"]},
        ]
        result = _map_step_a(kc_index, expected)
        assert "H1" in result["セクションA"]
        # H2 must NOT go back to the already-consumed "セクションA"
        assert "H2" not in result["セクションA"]
        # H2 should fall through to "詳細" (pointer=1 fallback)
        assert "H2" in result["詳細"]

    def test_substring_match_at_pointer_zero_works(self):
        """Substring match at the start of expected list still works."""
        expected = ["概要", "詳細"]
        kc_index = [
            {"title": "概要セクション", "hints": ["A"]},
            {"title": "詳細説明",       "hints": ["B"]},
        ]
        result = _map_step_a(kc_index, expected)
        assert "A" in result["概要"]
        assert "B" in result["詳細"]

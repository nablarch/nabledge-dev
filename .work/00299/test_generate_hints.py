#!/usr/bin/env python3
"""Unit tests for generate_hints.py — Phase 21-H (TDD RED phase).

Covers:
- R1〜R6 resolution rules (§4-2)
- Normalization boundary cases (§4-3 R4)
- Dash-split boundary (§4-3 R5)
- xlsx special case (§4-4)
- Validators V1/V2 (§5-1)

Run:
    pytest .pr/00299/test_generate_hints.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from generate_hints import (  # noqa: E402
    build_file_hints,
    normalize,
    normalize_parens,
    strip_trailing_paren,
    try_split_dash,
    resolve_sid,
)


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------


class TestNormalize:
    def test_identity(self):
        assert normalize("概要") == "概要"

    def test_nfkc_width(self):
        # 全角英数 → 半角
        assert normalize("ＡＢＣ１２３") == normalize("ABC123")

    def test_whitespace_collapse(self):
        assert normalize("  a   b  ") == normalize("a b")

    def test_empty(self):
        assert normalize("") == ""

    def test_none_like(self):
        assert normalize("  ") == normalize("")


class TestNormalizeParens:
    def test_half_to_full(self):
        assert normalize_parens("abc(def)") == normalize_parens("abc（def）")

    def test_no_parens(self):
        assert normalize_parens("abc") == "abc"


class TestStripTrailingParen:
    def test_half_paren(self):
        assert strip_trailing_paren("ツールの特徴(設定ファイル不要)") == "ツールの特徴"

    def test_full_paren(self):
        assert strip_trailing_paren("ツールの特徴（設定ファイル不要）") == "ツールの特徴"

    def test_mid_paren_not_stripped(self):
        assert strip_trailing_paren("abc(x)def") == "abc(x)def"

    def test_no_paren(self):
        assert strip_trailing_paren("abc") == "abc"


class TestTrySplitDash:
    def test_em_dash(self):
        assert try_split_dash("A — B") == ["A", "B"]

    def test_en_dash(self):
        assert try_split_dash("A – B") == ["A", "B"]

    def test_hyphen(self):
        assert try_split_dash("A - B") == ["A", "B"]

    def test_colon_half(self):
        assert try_split_dash("A: B") == ["A", "B"]

    def test_colon_full(self):
        assert try_split_dash("A：B") == ["A", "B"]

    def test_pipe(self):
        assert try_split_dash("A|B") == ["A", "B"]

    def test_no_separator(self):
        assert try_split_dash("ABC") is None

    def test_multi_part(self):
        # Should split all pieces
        result = try_split_dash("A — B — C")
        assert result is not None
        assert "A" in result and "C" in result


# ---------------------------------------------------------------------------
# resolve_sid — R1〜R6
# ---------------------------------------------------------------------------


def make_headings(*items):
    """Build [(level, title, line_no)] list."""
    return [(lvl, title, ln) for lvl, title, ln in items]


class TestResolveR1:
    """R1: catalog.section_map[sid].heading が非空 かつ ソースに完全一致."""

    def test_hits_when_catalog_heading_exists_in_source(self):
        sm = {"s1": "Nablarchについて"}
        headings = make_headings((1, "トップ", 0), (2, "Nablarchについて", 5))
        heading, rule = resolve_sid(
            sid="s1",
            catalog_section_map=sm,
            cache_title="AI創作ラベル",
            source_headings=headings,
        )
        assert rule == "R1"
        assert heading == "Nablarchについて"

    def test_skips_r1_when_catalog_heading_not_in_source(self):
        # catalog records a stale heading — R1 must not use it
        sm = {"s1": "捨てられた見出し"}
        headings = make_headings((1, "存在タイトル", 0))
        heading, rule = resolve_sid(
            sid="s1",
            catalog_section_map=sm,
            cache_title="AI創作",
            source_headings=headings,
        )
        assert rule != "R1"  # must fall through to R2/R6


class TestResolveR2:
    """R2: catalog.section_map[sid].heading が空 → ソースの h1."""

    def test_empty_catalog_heading_goes_to_h1(self):
        sm = {"s1": ""}
        headings = make_headings((1, "h1タイトル", 0), (2, "h2タイトル", 5))
        heading, rule = resolve_sid(
            sid="s1",
            catalog_section_map=sm,
            cache_title="",
            source_headings=headings,
        )
        assert rule == "R2"
        assert heading == "h1タイトル"

    def test_r2_preferred_over_r3_when_catalog_is_empty(self):
        # When catalog says empty, we use h1 — even if cache.title matches h2
        sm = {"s1": ""}
        headings = make_headings((1, "h1", 0), (2, "h2", 5))
        heading, rule = resolve_sid(
            sid="s1",
            catalog_section_map=sm,
            cache_title="h2",
            source_headings=headings,
        )
        assert rule == "R2"
        assert heading == "h1"


class TestResolveR3:
    """R3: cache.title directly matches a source heading at any level."""

    def test_matches_h3(self):
        sm = {}  # sid not in catalog
        headings = make_headings(
            (1, "Top", 0),
            (2, "Section", 5),
            (3, "Subsection", 10),
        )
        heading, rule = resolve_sid(
            sid="s99",
            catalog_section_map=sm,
            cache_title="Subsection",
            source_headings=headings,
        )
        assert rule == "R3"
        assert heading == "Subsection"

    def test_prefers_deepest_when_multiple_levels_share_title(self):
        sm = {}
        headings = make_headings(
            (1, "同じ名前", 0),
            (2, "h2", 5),
            (3, "同じ名前", 10),
        )
        heading, rule = resolve_sid(
            sid="s1",
            catalog_section_map=sm,
            cache_title="同じ名前",
            source_headings=headings,
        )
        assert rule == "R3"
        # Must point to the actual match; deepest level preferred
        assert heading == "同じ名前"


class TestResolveR4:
    """R4: normalized (NFKC + whitespace + parens) match."""

    def test_nfkc_match(self):
        sm = {}
        headings = make_headings((1, "Top", 0), (2, "ABC123", 5))
        heading, rule = resolve_sid(
            sid="s1",
            catalog_section_map=sm,
            cache_title="ＡＢＣ１２３",  # full-width
            source_headings=headings,
        )
        assert rule == "R4"
        assert heading == "ABC123"  # must return SOURCE string, not cache string

    def test_paren_strip_match(self):
        sm = {}
        headings = make_headings((1, "Top", 0), (2, "ツールの特徴", 5))
        heading, rule = resolve_sid(
            sid="s1",
            catalog_section_map=sm,
            cache_title="ツールの特徴（設定ファイル不要）",
            source_headings=headings,
        )
        assert rule == "R4"
        assert heading == "ツールの特徴"


class TestResolveR5:
    """R5: dash-split: 'A — B' where A or B exists in source."""

    def test_latter_side_match_preferred(self):
        sm = {}
        headings = make_headings((1, "Top", 0), (2, "Mapping", 5), (3, "Implementation", 10))
        heading, rule = resolve_sid(
            sid="s1",
            catalog_section_map=sm,
            cache_title="Mapping — Implementation",
            source_headings=headings,
        )
        assert rule == "R5"
        assert heading == "Implementation"  # latter (more specific) side

    def test_only_one_side_match(self):
        sm = {}
        headings = make_headings((1, "Top", 0), (2, "使用方法", 5))
        heading, rule = resolve_sid(
            sid="s1",
            catalog_section_map=sm,
            cache_title="使用方法 — 設定ファイルの準備",
            source_headings=headings,
        )
        assert rule == "R5"
        assert heading == "使用方法"


class TestResolveR2Prime:
    """R2': sid not in catalog_section_map → send hints to h1.

    This is the case where catalog didn't record ANY section for this sid,
    typically because the source had no sub-structure (h1-only FAQ etc.).
    """

    def test_sid_not_in_catalog_goes_to_h1(self):
        sm = {"s1": "ある見出し"}  # s99 NOT in catalog
        headings = make_headings((1, "FAQ", 0))
        heading, rule = resolve_sid(
            sid="s99",
            catalog_section_map=sm,
            cache_title="AI創作ラベル",
            source_headings=headings,
        )
        assert rule == "R2p"
        assert heading == "FAQ"

    def test_r3_beats_r2prime(self):
        # sid not in catalog, but cache.title matches source heading
        # R3 must resolve before falling to R2'
        sm = {}
        headings = make_headings((1, "h1", 0), (2, "section", 5))
        heading, rule = resolve_sid(
            sid="s99",
            catalog_section_map=sm,
            cache_title="section",
            source_headings=headings,
        )
        assert rule == "R3"


class TestResolveR6:
    """R6: h1 fallback — catalog has entry but disagrees with source."""

    def test_falls_back_to_h1_when_catalog_entry_stale(self):
        sm = {"s99": "存在しない見出し"}  # catalog HAS s99 but heading not in source
        headings = make_headings((1, "ページタイトル", 0), (2, "section", 5))
        heading, rule = resolve_sid(
            sid="s99",
            catalog_section_map=sm,
            cache_title="AIが創作した存在しないタイトル",
            source_headings=headings,
        )
        assert rule == "R6"
        assert heading == "ページタイトル"


class TestResolveERR:
    """ERR: no h1 available."""

    def test_empty_headings_raises(self):
        sm = {}
        with pytest.raises(ValueError):
            resolve_sid(
                sid="s1",
                catalog_section_map=sm,
                cache_title="anything",
                source_headings=[],
            )


# ---------------------------------------------------------------------------
# build_file_hints — integration at base_name scope (union + dedup)
# ---------------------------------------------------------------------------


class TestBuildFileHints:
    def test_unions_hints_for_same_heading(self):
        catalog_section_map = {"s1": "概要", "s2": "概要"}
        headings = make_headings((1, "Top", 0), (2, "概要", 5))
        cache_index = [
            {"id": "s1", "title": "概要", "hints": ["alpha", "beta"]},
            {"id": "s2", "title": "概要", "hints": ["beta", "gamma"]},
        ]
        result, stats = build_file_hints(
            base_name="sample",
            catalog_section_map=catalog_section_map,
            cache_index=cache_index,
            source_headings=headings,
            fmt="rst",
        )
        assert result == {"概要": ["alpha", "beta", "gamma"]}
        assert stats["R1"] == 2

    def test_drops_empty_hints(self):
        catalog_section_map = {"s1": "section"}
        headings = make_headings((1, "Top", 0), (2, "section", 5))
        cache_index = [{"id": "s1", "title": "section", "hints": []}]
        result, _ = build_file_hints(
            base_name="sample",
            catalog_section_map=catalog_section_map,
            cache_index=cache_index,
            source_headings=headings,
            fmt="rst",
        )
        assert result == {}

    def test_r6_aggregates_to_h1(self):
        # sids s1,s2 ARE in catalog with stale headings → R6
        catalog_section_map = {"s1": "古い見出しA", "s2": "古い見出しB"}
        headings = make_headings((1, "h1", 0))  # h1 only source
        cache_index = [
            {"id": "s1", "title": "創作1", "hints": ["k1"]},
            {"id": "s2", "title": "創作2", "hints": ["k2"]},
        ]
        result, stats = build_file_hints(
            base_name="sample",
            catalog_section_map=catalog_section_map,
            cache_index=cache_index,
            source_headings=headings,
            fmt="rst",
        )
        assert result == {"h1": ["k1", "k2"]}
        assert stats["R6"] == 2

    def test_r2prime_aggregates_to_h1(self):
        # sids NOT in catalog → R2' (not R6)
        catalog_section_map = {}  # no catalog entries
        headings = make_headings((1, "FAQ-h1", 0))
        cache_index = [
            {"id": "s1", "title": "AI創作1", "hints": ["k1"]},
            {"id": "s2", "title": "AI創作2", "hints": ["k2"]},
        ]
        result, stats = build_file_hints(
            base_name="sample",
            catalog_section_map=catalog_section_map,
            cache_index=cache_index,
            source_headings=headings,
            fmt="rst",
        )
        assert result == {"FAQ-h1": ["k1", "k2"]}
        assert stats["R2p"] == 2

    def test_xlsx_aggregates_to_file_key(self):
        cache_index = [
            {"id": "s1", "title": "anything", "hints": ["a"]},
            {"id": "s2", "title": "other", "hints": ["b", "a"]},
        ]
        result, stats = build_file_hints(
            base_name="sample",
            catalog_section_map={},
            cache_index=cache_index,
            source_headings=[],  # xlsx has no headings
            fmt="xlsx",
        )
        assert result == {"__file__": ["a", "b"]}
        assert stats["xlsx"] == 2

    def test_no_hints_lost(self):
        """V2 invariant: hints count in output == total input hints."""
        catalog_section_map = {"s1": "s1h"}
        headings = make_headings((1, "h1", 0), (2, "s1h", 5))
        cache_index = [
            {"id": "s1", "title": "s1h", "hints": ["a", "b"]},
            {"id": "s2", "title": "創作", "hints": ["c", "d"]},  # will R6
        ]
        result, _ = build_file_hints(
            base_name="sample",
            catalog_section_map=catalog_section_map,
            cache_index=cache_index,
            source_headings=headings,
            fmt="rst",
        )
        all_hints = [h for hs in result.values() for h in hs]
        assert sorted(all_hints) == ["a", "b", "c", "d"]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))

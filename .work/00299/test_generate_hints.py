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
        # catalog records a stale heading — R1 must not use it, must fall to R6
        sm = {"s1": "捨てられた見出し"}
        headings = make_headings((1, "存在タイトル", 0))
        heading, rule = resolve_sid(
            sid="s1",
            catalog_section_map=sm,
            cache_title="AI創作",
            source_headings=headings,
        )
        # Positive assertion: must specifically land on R6 (h1 fallback)
        # since cache_title doesn't match either
        assert rule == "R6"
        assert heading == "存在タイトル"


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

    def test_r2_without_h1_raises(self):
        """R2 requires an h1. If catalog heading is empty AND source has no h1,
        must raise ERR (not silently use a lower-level heading)."""
        sm = {"s1": ""}
        with pytest.raises(ValueError):
            resolve_sid(
                sid="s1",
                catalog_section_map=sm,
                cache_title="x",
                source_headings=[],  # no h1 at all
            )

    def test_r2_with_only_h2_source_raises(self):
        """h2-only source (no h1 at level 1) must not silently fall back to h2."""
        sm = {"s1": ""}
        with pytest.raises(ValueError):
            resolve_sid(
                sid="s1",
                catalog_section_map=sm,
                cache_title="x",
                source_headings=[(2, "h2only", 0)],
            )


class TestRulePriority:
    """Explicit rule-order tests (R1 > R2 > R3 > R4 > R5 > R2' > R6)."""

    def test_r3_beats_r4(self):
        """R3 (literal) must fire before R4 (normalized)."""
        sm = {}
        # "ABC" literal match AND full-width "ＡＢＣ" would normalize-match too
        headings = make_headings((1, "Top", 0), (2, "ABC", 5), (3, "ＡＢＣ", 10))
        heading, rule = resolve_sid(
            sid="s1",
            catalog_section_map=sm,
            cache_title="ABC",
            source_headings=headings,
        )
        assert rule == "R3"
        assert heading == "ABC"

    def test_r3_beats_r5(self):
        """R3 (literal) must fire before R5 (dash-split)."""
        sm = {}
        # cache_title "ABC" — literal exists AND dash-split would match "ABC" too
        headings = make_headings((1, "Top", 0), (2, "ABC", 5), (3, "X — ABC", 10))
        heading, rule = resolve_sid(
            sid="s1",
            catalog_section_map=sm,
            cache_title="ABC",
            source_headings=headings,
        )
        assert rule == "R3"

    def test_r4_beats_r5(self):
        """R4 (normalized) must fire before R5 (dash-split)."""
        sm = {}
        # cache_title "ＡＢＣ" normalizes to "ABC" — R4 hits before R5 split
        headings = make_headings((1, "Top", 0), (2, "ABC", 5), (3, "X — Y", 10))
        heading, rule = resolve_sid(
            sid="s1",
            catalog_section_map=sm,
            cache_title="ＡＢＣ",
            source_headings=headings,
        )
        assert rule == "R4"


class TestEverEmptyPriority:
    """R2 (via ever_empty) must fire even when cache_title matches an h2."""

    def test_ever_empty_beats_r3(self):
        sm = {"s1": "後付け"}  # merged heading non-empty but sid was ever empty
        headings = make_headings((1, "h1", 0), (2, "cache_matches", 5))
        heading, rule = resolve_sid(
            sid="s1",
            catalog_section_map=sm,
            cache_title="cache_matches",  # R3 would match if evaluated
            source_headings=headings,
            catalog_ever_empty={"s1"},
        )
        assert rule == "R2"
        assert heading == "h1"


class TestNormalizationCombos:
    """Combined normalization: NFKC + paren-strip together."""

    def test_nfkc_plus_paren_strip(self):
        sm = {}
        headings = make_headings((1, "Top", 0), (2, "ABC", 5))
        # Full-width + trailing annotation: "ＡＢＣ（注）" → NFKC → "ABC(注)" → strip → "ABC"
        heading, rule = resolve_sid(
            sid="s1",
            catalog_section_map=sm,
            cache_title="ＡＢＣ（注）",
            source_headings=headings,
        )
        assert rule == "R4"
        assert heading == "ABC"

    def test_full_width_space_collapsed(self):
        sm = {}
        headings = make_headings((1, "Top", 0), (2, "A B", 5))
        # full-width space U+3000 normalizes to ASCII space under NFKC
        heading, rule = resolve_sid(
            sid="s1",
            catalog_section_map=sm,
            cache_title="A　B",
            source_headings=headings,
        )
        assert rule == "R4"
        assert heading == "A B"


class TestResolveEverEmpty:
    """H2-SE: if a sid was empty in ANY split section_map entry,
    R2 must fire even when merged map has a non-empty heading that
    doesn't match source."""

    def test_ever_empty_triggers_r2(self):
        sm = {"s1": "後から付いた見出し"}  # merged heading is non-empty
        headings = make_headings((1, "h1", 0))
        heading, rule = resolve_sid(
            sid="s1",
            catalog_section_map=sm,
            cache_title="",
            source_headings=headings,
            catalog_ever_empty={"s1"},  # was empty in one of the split entries
        )
        # R2 fires because catalog once had empty heading for this sid
        # (would otherwise fall through to R6)
        assert rule == "R2"
        assert heading == "h1"


# ---------------------------------------------------------------------------
# build_file_hints — integration at base_name scope (union + dedup)
# ---------------------------------------------------------------------------


def _titles(result):
    return [e["title"] for e in result]


def _hints_for(result, title):
    """Return union of hints for all entries matching title (for simple tests)."""
    out = []
    for e in result:
        if e["title"] == title:
            out.extend(e["hints"])
    return out


class TestBuildFileHints:
    def test_overflow_goes_to_h1_not_wraparound(self):
        """Two sids both resolve to "概要" but source has only 1 "概要" slot.
        First sid fills the slot; second overflows to h1 (reclassified R6)
        rather than wrapping and conflating hints from distinct catalog sids."""
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
        titles = _titles(result)
        # h1 slot got overflow, 概要 slot got first sid
        assert "Top" in titles and "概要" in titles
        gaiyou = next(e for e in result if e["title"] == "概要")
        top = next(e for e in result if e["title"] == "Top")
        assert gaiyou["hints"] == ["alpha", "beta"]
        # Second sid overflowed to h1; dedup removes "beta" since dedup is per-slot
        assert top["hints"] == ["beta", "gamma"]
        # R1 was evaluated for both, overflow reclassified as R6
        assert stats.get("R1", 0) == 1
        assert stats.get("R6", 0) == 1

    def test_duplicate_heading_kept_as_separate_entries(self):
        """Same-title headings at different source positions must remain
        distinct array entries — so hints for section A don't pollute section B."""
        catalog_section_map = {"s1": "使用方法", "s2": "使用方法"}
        headings = make_headings(
            (1, "Top", 0),
            (2, "BeanUtil", 3),
            (3, "使用方法", 5),
            (2, "BeanValidator", 10),
            (3, "使用方法", 12),
        )
        cache_index = [
            {"id": "s1", "title": "使用方法", "hints": ["copyProperties"]},
            {"id": "s2", "title": "使用方法", "hints": ["validate"]},
        ]
        result, _ = build_file_hints(
            base_name="sample",
            catalog_section_map=catalog_section_map,
            cache_index=cache_index,
            source_headings=headings,
            fmt="rst",
        )
        # Two distinct entries, source-order preserved
        assert len(result) == 2
        assert result[0] == {"title": "使用方法", "hints": ["copyProperties"]}
        assert result[1] == {"title": "使用方法", "hints": ["validate"]}

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
        assert result == []

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
        assert result == [{"title": "h1", "hints": ["k1", "k2"]}]
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
        assert result == [{"title": "FAQ-h1", "hints": ["k1", "k2"]}]
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
        assert result == [{"title": "__file__", "hints": ["a", "b"]}]
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
        all_hints = [h for e in result for h in e["hints"]]
        assert sorted(all_hints) == ["a", "b", "c", "d"]

    def test_v2_retention_across_mixed_rules(self):
        """V2 global invariant: every distinct input hint reaches the output
        regardless of which rule resolves each sid."""
        catalog_section_map = {
            "s1": "Exact",
            "s2": "",
            "s3": "stale",
        }
        headings = make_headings((1, "h1", 0), (2, "Exact", 5), (3, "NotInCatalog", 10))
        cache_index = [
            {"id": "s1", "title": "Exact", "hints": ["r1hint"]},
            {"id": "s2", "title": "xx", "hints": ["r2hint"]},
            {"id": "s3", "title": "bogus", "hints": ["r6hint"]},
            {"id": "s4", "title": "NotInCatalog", "hints": ["r3hint"]},
        ]
        result, _ = build_file_hints(
            base_name="sample",
            catalog_section_map=catalog_section_map,
            cache_index=cache_index,
            source_headings=headings,
            fmt="rst",
        )
        all_hints = {h for e in result for h in e["hints"]}
        assert all_hints == {"r1hint", "r2hint", "r6hint", "r3hint"}

    def test_v1_titles_all_in_source(self):
        """V1 invariant: every emitted title (except __file__) exists verbatim
        in source headings."""
        catalog_section_map = {"s1": "real", "s2": ""}
        headings = make_headings((1, "h1", 0), (2, "real", 5))
        cache_index = [
            {"id": "s1", "title": "real", "hints": ["a"]},
            {"id": "s2", "title": "ignored", "hints": ["b"]},
        ]
        result, _ = build_file_hints(
            base_name="sample",
            catalog_section_map=catalog_section_map,
            cache_index=cache_index,
            source_headings=headings,
            fmt="rst",
        )
        source_titles = {t for _, t, _ in headings}
        for entry in result:
            assert entry["title"] in source_titles

    def test_source_order_preserved(self):
        """Array entries follow source heading order (not cache_index order)."""
        catalog_section_map = {"s1": "B", "s2": "A"}
        headings = make_headings((1, "Top", 0), (2, "A", 5), (2, "B", 10))
        cache_index = [
            {"id": "s1", "title": "B", "hints": ["b-hint"]},
            {"id": "s2", "title": "A", "hints": ["a-hint"]},
        ]
        result, _ = build_file_hints(
            base_name="sample",
            catalog_section_map=catalog_section_map,
            cache_index=cache_index,
            source_headings=headings,
            fmt="rst",
        )
        # Source order: A first, then B
        assert _titles(result) == ["A", "B"]

    def test_overflow_reclassified_as_r6(self):
        """H-SE: 3 sids resolve to a title that appears only 2 times in source.
        The 3rd sid must NOT silently wrap to slot 0 (hint pollution). Instead,
        it must go to h1 and be counted as R6."""
        catalog_section_map = {"s1": "使用方法", "s2": "使用方法", "s3": "使用方法"}
        headings = make_headings(
            (1, "h1", 0),
            (2, "A", 3), (3, "使用方法", 5),
            (2, "B", 10), (3, "使用方法", 12),
        )
        cache_index = [
            {"id": "s1", "title": "使用方法", "hints": ["x"]},
            {"id": "s2", "title": "使用方法", "hints": ["y"]},
            {"id": "s3", "title": "使用方法", "hints": ["overflow"]},
        ]
        result, stats = build_file_hints(
            base_name="sample",
            catalog_section_map=catalog_section_map,
            cache_index=cache_index,
            source_headings=headings,
            fmt="rst",
        )
        # First two sids fill the two 使用方法 slots, third overflows to h1
        titles = _titles(result)
        assert "h1" in titles, f"overflow must land on h1, got {titles}"
        # overflow hint lives on h1, not on "使用方法"
        h1_entry = next(e for e in result if e["title"] == "h1")
        assert "overflow" in h1_entry["hints"]
        # The two 使用方法 slots got x and y exactly
        shimei_entries = [e for e in result if e["title"] == "使用方法"]
        assert len(shimei_entries) == 2
        assert shimei_entries[0]["hints"] == ["x"]
        assert shimei_entries[1]["hints"] == ["y"]
        # R6 count includes the reclassified overflow
        assert stats.get("R6", 0) >= 1

    def test_lone_sid_fills_first_duplicate_slot(self):
        """H-QA: 1 sid matching a title that appears 2 times → first slot wins,
        second slot stays empty (and is dropped by empty-filter)."""
        catalog_section_map = {"s1": "dup"}
        headings = make_headings((1, "h1", 0), (2, "dup", 5), (3, "dup", 10))
        cache_index = [{"id": "s1", "title": "dup", "hints": ["only"]}]
        result, _ = build_file_hints(
            base_name="sample",
            catalog_section_map=catalog_section_map,
            cache_index=cache_index,
            source_headings=headings,
            fmt="rst",
        )
        # Only first "dup" slot gets filled; the second is empty → dropped
        dup_entries = [e for e in result if e["title"] == "dup"]
        assert len(dup_entries) == 1
        assert dup_entries[0]["hints"] == ["only"]

    def test_mixed_rule_source_order(self):
        """Order follows source headings regardless of which rule resolved each sid."""
        catalog_section_map = {"s1": "C", "s2": ""}  # s1 R1→C, s2 R2→h1
        headings = make_headings((1, "h1", 0), (2, "A", 5), (3, "B", 10), (2, "C", 15))
        cache_index = [
            {"id": "s1", "title": "C", "hints": ["c-hint"]},
            {"id": "s2", "title": "x", "hints": ["h1-hint"]},
            {"id": "s3", "title": "B", "hints": ["b-hint"]},  # R3
        ]
        result, _ = build_file_hints(
            base_name="sample",
            catalog_section_map=catalog_section_map,
            cache_index=cache_index,
            source_headings=headings,
            fmt="rst",
        )
        # Source order: h1, B, C (A has no hints, dropped)
        assert _titles(result) == ["h1", "B", "C"]

    def test_xlsx_empty_hints_returns_empty(self):
        """All-empty xlsx hints → empty array (not a dummy __file__ entry)."""
        result, stats = build_file_hints(
            base_name="sample",
            catalog_section_map={},
            cache_index=[{"id": "s1", "title": "x", "hints": []}],
            source_headings=[],
            fmt="xlsx",
        )
        assert result == []
        assert stats["xlsx"] == 1


class TestMergeSectionMaps:
    """H2-SE: merge_section_maps must preserve the 'ever empty' info across
    split catalog entries."""

    def test_tracks_ever_empty(self):
        from generate_hints import merge_section_maps  # noqa: E402

        entries = [
            {"section_map": [{"section_id": "s1", "heading": ""}]},
            {"section_map": [{"section_id": "s1", "heading": "後から付いた"}]},
        ]
        merged, ever_empty = merge_section_maps(entries)
        # merged prefers non-empty
        assert merged["s1"] == "後から付いた"
        # but ever_empty remembers the original empty entry
        assert "s1" in ever_empty

    def test_non_empty_only_not_in_ever_empty(self):
        from generate_hints import merge_section_maps  # noqa: E402

        entries = [
            {"section_map": [{"section_id": "s1", "heading": "h"}]},
        ]
        merged, ever_empty = merge_section_maps(entries)
        assert merged["s1"] == "h"
        assert "s1" not in ever_empty


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))

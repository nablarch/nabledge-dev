"""Tests for question-side term extraction used by the ids variant.

term_extract provides the deterministic grep-term extractor that mirrors
classify_terms.py's patterns. search_ids.py consumes this instead of asking
AI-1 to generate term_queries.
"""
from __future__ import annotations

import json

import pytest

from tools.benchmark.bench.term_extract import (
    PATTERNS,
    extract_terms,
    filter_terms,
)


def test_extract_picks_up_annotation_camel_lower_camel():
    q = "@UseToken で TransactionManagementHandler を concurrentNumber とともに使うには？"
    terms = extract_terms(q)
    assert "@UseToken" in terms
    assert "TransactionManagementHandler" in terms
    assert "concurrentNumber" in terms


def test_extract_picks_up_japanese_4_plus_chars():
    q = "二重サブミット防止 の 実装方法 について"
    terms = extract_terms(q)
    assert "二重サブミット防止" in terms
    # 3-char words are intentionally excluded; they over-match in the corpus.
    assert "実装" not in terms
    # But 4+ char kanji words are kept.
    assert "実装方法" in terms


def test_extract_does_not_include_3_char_katakana():
    # 3-char words are too generic; the spec excludes everything under 4 chars.
    q = "ログ の 設定"
    terms = extract_terms(q)
    assert "ログ" not in terms


def test_extract_deduplicates_preserving_order():
    q = "concurrentNumber は concurrentNumber で指定。二重サブミット防止 も 二重サブミット防止。"
    terms = extract_terms(q)
    counts = {t: terms.count(t) for t in set(terms)}
    assert counts.get("concurrentNumber") == 1
    assert counts.get("二重サブミット防止") == 1
    # First occurrence order is preserved.
    assert terms.index("concurrentNumber") < terms.index("二重サブミット防止")


def test_extract_drops_java_stoplist():
    q = "HashMap と ArrayList の違いは？"
    terms = extract_terms(q)
    assert "HashMap" not in terms
    assert "ArrayList" not in terms


def test_extract_returns_empty_for_prose_only_question():
    q = "よろしく お願い します"
    # 4+ kanji words may match — but the three hiragana words should all be absent.
    terms = extract_terms(q)
    assert "よろしく" not in terms
    assert "お願い" not in terms


def test_filter_terms_applies_stoplist():
    terms = ["transactionName", "トランザクション", "設定"]
    stop = {"トランザクション"}  # pretend df_pct > 20%
    kept = filter_terms(terms, stopset=stop)
    assert "トランザクション" not in kept
    assert "transactionName" in kept


def test_filter_terms_preserves_order():
    terms = ["a-term", "b-term", "c-term"]
    assert filter_terms(terms, stopset={"b-term"}) == ["a-term", "c-term"]


def test_patterns_contract():
    # PATTERNS must stay aligned with classify_terms.py. This is an anchor
    # test: if either side changes, someone has to look at both.
    keys = {name for name, _ in PATTERNS}
    assert keys == {"annotation", "camel", "lower_camel", "katakana", "kanji", "mixed"}

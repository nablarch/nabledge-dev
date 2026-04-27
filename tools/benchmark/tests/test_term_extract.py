"""Tests for question-side term extraction used by the next variant.

term_extract provides the deterministic grep-term extractor that mirrors
classify_terms.py's patterns. search_next.py consumes this instead of asking
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


def test_extract_deduplicates():
    q = "concurrentNumber は concurrentNumber で指定。@UseToken も @UseToken。"
    terms = extract_terms(q)
    counts = {t: terms.count(t) for t in set(terms)}
    assert counts.get("concurrentNumber") == 1
    assert counts.get("@UseToken") == 1


def test_extract_drops_java_stoplist():
    q = "HashMap と ArrayList の違いは？"
    terms = extract_terms(q)
    assert "HashMap" not in terms
    assert "ArrayList" not in terms


def test_extract_returns_empty_for_prose_only_question():
    q = "よろしく お願い します"
    # Hiragana was never matched; now kanji/katakana are also out.
    assert extract_terms(q) == []


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
    # PATTERNS is identifier-only by design — Japanese is handled by
    # index-llm.md. Guard against accidental re-introduction.
    keys = {name for name, _ in PATTERNS}
    assert keys == {"annotation", "camel", "lower_camel"}


# ---- min-length policy: every emitted term must be 4+ chars (docs) ----

def test_extract_rejects_3char_annotation():
    # @Ab is 3 chars — below the 4+ minimum, even though re pattern would match.
    terms = extract_terms("@Ab で始まる 3 字の注釈 @AbCd が混在")
    assert "@Ab" not in terms
    assert "@AbCd" in terms


def test_extract_rejects_3char_camel():
    # AaB is 3 chars (old pattern allowed it).
    terms = extract_terms("AaB と AaBc を比較")
    assert "AaB" not in terms
    assert "AaBc" in terms


def test_extract_rejects_3char_lower_camel():
    # aaBc was already 4 chars under the old pattern; guard against
    # regression if someone loosens it.
    terms = extract_terms("a1B と aaB と aaBc")
    for t in ("aaB", "a1B"):
        assert t not in terms
    assert "aaBc" in terms


def test_extract_min_length_all_patterns():
    """No emitted term should ever be shorter than 4 chars."""
    terms = extract_terms(
        "@Ab AaB aaB テスト 実装 実装方法 暗号化 暗号化処理 悲観 悲観ロック"
    )
    assert all(len(t) >= 4 for t in terms), terms


# ---- identifier-only policy for grep path ----
# Japanese terms from the question do not reliably hit body text (orthographic
# drift) and when they do hit they are usually generic (チェック / レコード),
# producing noise that eats the per-term cap. The index-llm.md path handles
# the Japanese-concept layer already, so the grep path is restricted to
# ASCII identifiers (@Annotation / CamelCase / camelCase).

def test_extract_drops_japanese_terms():
    q = "@UseToken と TransactionManagementHandler と concurrentNumber と トランザクション と 悲観ロック"
    terms = extract_terms(q)
    assert "@UseToken" in terms
    assert "TransactionManagementHandler" in terms
    assert "concurrentNumber" in terms
    assert "トランザクション" not in terms
    assert "悲観ロック" not in terms


def test_extract_returns_empty_for_japanese_only_question():
    q = "二重サブミット防止 の 実装方法 を 教えて"
    assert extract_terms(q) == []

"""Unit tests for verify.py — _extract_text_tokens regex."""
import pytest
from scripts.verify import _extract_text_tokens


# ---------------------------------------------------------------------------
# _extract_text_tokens — CJK range starts too early (\u3000 = ideographic space)
# ---------------------------------------------------------------------------

class TestExtractTextTokens:
    def test_ideographic_spaces_are_not_tokens(self):
        """Consecutive ideographic spaces (\u3000) must not be treated as tokens.

        The CJK character class previously started at \u3000 (IDEOGRAPHIC SPACE),
        so two or more consecutive full-width spaces matched the pattern.
        """
        text = "\u3000\u3000\u3000"  # three ideographic spaces
        result = _extract_text_tokens(text)
        assert result == [], f"Expected no tokens but got: {result!r}"

    def test_japanese_punctuation_sequence_is_not_token(self):
        """Sequences of Japanese punctuation (、。) must not produce tokens."""
        text = "、。、。"  # \u3001, \u3002 — CJK punctuation
        result = _extract_text_tokens(text)
        assert result == [], f"Expected no tokens but got: {result!r}"

    def test_kanji_tokens_still_extracted(self):
        """Kanji (CJK Unified Ideograph range \u4e00-\u9fff) must still match."""
        result = _extract_text_tokens("ユニバーサルDAO")
        assert any("DAO" in t or "ユニバーサル" in t for t in result)

    def test_hiragana_tokens_still_extracted(self):
        """Hiragana sequences of 2+ chars must still match."""
        result = _extract_text_tokens("ください")
        assert "ください" in result

    def test_katakana_tokens_still_extracted(self):
        """Katakana sequences of 2+ chars must still match."""
        result = _extract_text_tokens("ユニバーサル")
        assert "ユニバーサル" in result

    def test_ascii_words_still_extracted(self):
        """ASCII words of 3+ chars must still match."""
        result = _extract_text_tokens("UniversalDao pagination")
        assert "UniversalDao" in result
        assert "pagination" in result

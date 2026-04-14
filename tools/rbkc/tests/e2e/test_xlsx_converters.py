"""E2E tests for Phase 6: Excel converters.

Uses actual Nablarch official Excel files from .lw/nab-official/.
"""
from __future__ import annotations

from pathlib import Path

import pytest

# Paths to actual Excel files
_ROOT = Path(__file__).parents[4]  # repo root
_V6_RELEASENOTE = _ROOT / ".lw/nab-official/v6/nablarch-document/ja/releases/nablarch6-releasenote.xlsx"
_V6U1_RELEASENOTE = _ROOT / ".lw/nab-official/v6/nablarch-document/ja/releases/nablarch6u1-releasenote.xlsx"
# nablarch5u14 has no "XuYY変更点" line → header ends at row 2, data at row 5
_V5U14_RELEASENOTE = _ROOT / ".lw/nab-official/v5/nablarch-document/ja/releases/nablarch5u14-releasenote.xlsx"
_V5U26_RELEASENOTE = _ROOT / ".lw/nab-official/v5/nablarch-document/ja/releases/nablarch5u26-releasenote.xlsx"
_V6_SECURITY = _ROOT / ".lw/nab-official/v6/nablarch-system-development-guide/Sample_Project/設計書/Nablarch機能のセキュリティ対応表.xlsx"
_V5_SECURITY = _ROOT / ".lw/nab-official/v5/nablarch-system-development-guide/Sample_Project/設計書/Nablarch機能のセキュリティ対応表.xlsx"


# ---------------------------------------------------------------------------
# Release note converter tests
# ---------------------------------------------------------------------------

class TestReleasenoteConverter:
    @pytest.fixture(scope="class")
    def result_v6(self):
        from scripts.converters.xlsx_releasenote import convert
        return convert(_V6_RELEASENOTE)

    @pytest.fixture(scope="class")
    def result_v6u1(self):
        from scripts.converters.xlsx_releasenote import convert
        return convert(_V6U1_RELEASENOTE)

    @pytest.fixture(scope="class")
    def result_v5u14(self):
        from scripts.converters.xlsx_releasenote import convert
        return convert(_V5U14_RELEASENOTE)

    @pytest.fixture(scope="class")
    def result_v5u26(self):
        from scripts.converters.xlsx_releasenote import convert
        return convert(_V5U26_RELEASENOTE)

    def test_title_extracted(self, result_v6):
        """Title is extracted from first row, '■' prefix stripped."""
        assert "Nablarch 6 リリースノート" in result_v6.title

    def test_section_count_v6(self, result_v6):
        """nablarch6-releasenote.xlsx has 9 data rows → 9 sections."""
        assert len(result_v6.sections) == 9

    def test_section_count_v6u1(self, result_v6u1):
        """nablarch6u1-releasenote.xlsx has more entries."""
        assert len(result_v6u1.sections) >= 10

    def test_first_section_title_contains_no(self, result_v6):
        """Section titles contain No. prefix."""
        assert result_v6.sections[0].title.startswith("No.1")

    def test_first_section_title_text(self, result_v6):
        """First section title includes the タイトル field."""
        assert "Jakarta EE 10対応" in result_v6.sections[0].title

    def test_section_content_contains_overview(self, result_v6):
        """Section content contains the 概要 text."""
        assert "Jakarta EE 10" in result_v6.sections[0].content

    def test_section_content_contains_ref_url(self, result_v6):
        """Section content contains the 参照先 URL when non-empty."""
        assert "https://nablarch.github.io/docs/6/doc/migration" in result_v6.sections[0].content

    def test_section_content_has_release_type(self, result_v6):
        """Section content includes リリース区分."""
        assert "変更" in result_v6.sections[0].content

    def test_no_knowledge_content_false(self, result_v6):
        """Release notes always have knowledge content."""
        assert result_v6.no_knowledge_content is False

    def test_category_rows_skipped(self, result_v6):
        """Category rows (e.g. 'アプリケーションフレームワーク') are not sections."""
        titles = [s.title for s in result_v6.sections]
        assert not any("アプリケーションフレームワーク" in t for t in titles)

    def test_empty_ref_not_added(self, result_v6):
        """Sections with ref='-' do not add a meaningless dash as URL."""
        # No.2 has ref='-'
        sec = result_v6.sections[1]
        # Should not contain a lone '-' as a markdown link
        assert "[- ]" not in sec.content
        assert "(-)" not in sec.content

    def test_v5u14_no_header_rows_skipped(self, result_v5u14):
        """nablarch5u14 has 2-row header (not 3): No.1 must not be skipped."""
        # nablarch5u14 header ends at row 2 (0-indexed row 1), data at row 5
        assert len(result_v5u14.sections) >= 1
        assert result_v5u14.sections[0].title.startswith("No.1")

    def test_v5u26_section_count(self, result_v5u26):
        """v5 release note produces correct number of sections (>= 1)."""
        assert len(result_v5u26.sections) >= 1


# ---------------------------------------------------------------------------
# Security table converter tests
# ---------------------------------------------------------------------------

class TestSecurityConverter:
    @pytest.fixture(scope="class")
    def result_v6(self):
        from scripts.converters.xlsx_security import convert
        return convert(_V6_SECURITY)

    @pytest.fixture(scope="class")
    def result_v5(self):
        from scripts.converters.xlsx_security import convert
        return convert(_V5_SECURITY)

    def test_section_count_v6(self, result_v6):
        """v6 security table has 11 vulnerability groups → 11 sections."""
        assert len(result_v6.sections) == 11

    def test_section_count_v5(self, result_v5):
        """v5 security table has same structure."""
        assert len(result_v5.sections) == 11

    def test_first_section_title(self, result_v6):
        """First section is SQLインジェクション."""
        assert "SQLインジェクション" in result_v6.sections[0].title

    def test_section_title_contains_no(self, result_v6):
        """Section titles include the vulnerability number."""
        assert result_v6.sections[0].title.startswith("1.")

    def test_csrf_section_exists(self, result_v6):
        """CSRF section is present (vulnerability No.6)."""
        titles = [s.title for s in result_v6.sections]
        assert any("CSRF" in t for t in titles)

    def test_section_content_has_nablarch_feature(self, result_v6):
        """Section content mentions Nablarch feature names."""
        sql_section = result_v6.sections[0]
        assert "ユニバーサルDAO" in sql_section.content

    def test_section_content_has_support_status(self, result_v6):
        """Section content includes 対応状況 symbols (〇/×/△)."""
        sql_section = result_v6.sections[0]
        assert "〇" in sql_section.content or "×" in sql_section.content

    def test_section_content_has_measure_items(self, result_v6):
        """Section content includes 実施項目 text."""
        sql_section = result_v6.sections[0]
        assert "プレースホルダ" in sql_section.content

    def test_no_knowledge_content_false(self, result_v6):
        """Security table always has knowledge content."""
        assert result_v6.no_knowledge_content is False

    def test_title_extracted(self, result_v6):
        """Document title is extracted."""
        assert result_v6.title  # non-empty

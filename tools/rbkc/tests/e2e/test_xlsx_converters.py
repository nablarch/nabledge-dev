"""E2E tests for Phase 6: Excel converters.

Uses actual Nablarch official Excel files from .lw/nab-official/.
"""
from __future__ import annotations

from pathlib import Path

import pytest

# Paths to actual Excel files
_ROOT = Path(__file__).parents[4]  # repo root
_V13_XLS = _ROOT / ".lw/nab-official/all-releasenote/nablarch-1.3-all-releasenote/1.3.0/nablarch_toolbox-1.3.0-releasenote-detail.xls"
_V13_1_XLS = _ROOT / ".lw/nab-official/all-releasenote/nablarch-1.3-all-releasenote/1.3.1/nablarch_ライブラリ-1.3.1-releasenote-detail.xls"
_V12_XLS = _ROOT / ".lw/nab-official/all-releasenote/nablarch-1.2-all-releasenote/1.2.0/nablarch_toolbox-1.2.0-releasenote-detail.xls"
_V12_1_XLS = _ROOT / ".lw/nab-official/all-releasenote/nablarch-1.2-all-releasenote/1.2.1/nablarch_ライブラリ-1.2.1-releasenote-detail.xls"
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
        from scripts.create.converters.xlsx_releasenote import convert
        return convert(_V6_RELEASENOTE)

    @pytest.fixture(scope="class")
    def result_v6u1(self):
        from scripts.create.converters.xlsx_releasenote import convert
        return convert(_V6U1_RELEASENOTE)

    @pytest.fixture(scope="class")
    def result_v5u14(self):
        from scripts.create.converters.xlsx_releasenote import convert
        return convert(_V5U14_RELEASENOTE)

    @pytest.fixture(scope="class")
    def result_v5u26(self):
        from scripts.create.converters.xlsx_releasenote import convert
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
        from scripts.create.converters.xlsx_security import convert
        return convert(_V6_SECURITY)

    @pytest.fixture(scope="class")
    def result_v5(self):
        from scripts.create.converters.xlsx_security import convert
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


# ---------------------------------------------------------------------------
# XLS (legacy) release note converter tests
# ---------------------------------------------------------------------------

class TestXlsReleasenoteConverter:
    @pytest.fixture(scope="class")
    def result_v13(self):
        from scripts.create.converters.xlsx_releasenote import convert
        return convert(_V13_XLS)

    @pytest.fixture(scope="class")
    def result_v13_1(self):
        from scripts.create.converters.xlsx_releasenote import convert
        return convert(_V13_1_XLS)

    @pytest.fixture(scope="class")
    def result_v12(self):
        from scripts.create.converters.xlsx_releasenote import convert
        return convert(_V12_XLS)

    @pytest.fixture(scope="class")
    def result_v12_1(self):
        from scripts.create.converters.xlsx_releasenote import convert
        return convert(_V12_1_XLS)

    def test_title_extracted_v13(self, result_v13):
        """Title extracted from first row, '■' stripped."""
        assert result_v13.title
        assert "■" not in result_v13.title

    def test_sections_exist_v13(self, result_v13):
        """v1.3.0 xls has at least 1 data section."""
        assert len(result_v13.sections) >= 1

    def test_section_title_contains_no_v13(self, result_v13):
        """Section title contains No. prefix."""
        assert result_v13.sections[0].title.startswith("No.")

    def test_section_content_nonempty_v13(self, result_v13):
        """Section content is non-empty."""
        assert result_v13.sections[0].content.strip()

    def test_category_rows_not_sections(self, result_v13):
        """Category-separator rows ('Toolbox', '開発ガイド') do not become sections."""
        titles = [s.title for s in result_v13.sections]
        assert not any(t in ("Toolbox", "開発ガイド", "ライブラリ") for t in titles)

    def test_sections_exist_v12(self, result_v12):
        """v1.2.0 xls has at least 1 data section."""
        assert len(result_v12.sections) >= 1

    def test_no_knowledge_content_false(self, result_v13):
        """XLS release notes always have knowledge content."""
        assert result_v13.no_knowledge_content is False

    def test_impact_ari_included_in_content(self, result_v13_1):
        """Rows with impact='あり' have detail text in content."""
        contents = " ".join(s.content for s in result_v13_1.sections)
        assert "影響:" in contents

    def test_impact_nashi_not_in_content(self, result_v13):
        """Rows with impact='なし' do not have '影響:' in content."""
        for sec in result_v13.sections:
            assert "影響: なし" not in sec.content

    def test_sections_exist_v12_1(self, result_v12_1):
        """v1.2.1 xls has at least 1 section."""
        assert len(result_v12_1.sections) >= 1

    def test_no_section_title_is_empty(self, result_v13):
        """All section titles are non-empty."""
        assert all(s.title.strip() for s in result_v13.sections)

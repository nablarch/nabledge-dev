"""E2E tests for Phase 5: MD converter against real v6 documentation."""
from pathlib import Path

import pytest

from scripts.converters.md import convert

V6_GUIDE_ROOT = Path(
    ".lw/nab-official/v6/nablarch-system-development-guide"
    "/Nablarchシステム開発ガイド/docs/nablarch-patterns"
)

ASYNC_MD = V6_GUIDE_ROOT / "Nablarchでの非同期処理.md"
BATCH_MD = V6_GUIDE_ROOT / "Nablarchバッチ処理パターン.md"
ANTI_MD = V6_GUIDE_ROOT / "Nablarchアンチパターン.md"


@pytest.fixture(scope="module")
def async_result():
    if not ASYNC_MD.exists():
        pytest.skip("v6 guide MD not available")
    return convert(ASYNC_MD.read_text(encoding="utf-8"), "nablarch-async-pattern")


@pytest.fixture(scope="module")
def batch_result():
    if not BATCH_MD.exists():
        pytest.skip("v6 guide MD not available")
    return convert(BATCH_MD.read_text(encoding="utf-8"), "nablarch-batch-pattern")


@pytest.fixture(scope="module")
def anti_result():
    if not ANTI_MD.exists():
        pytest.skip("v6 guide MD not available")
    return convert(ANTI_MD.read_text(encoding="utf-8"), "nablarch-anti-pattern")


class TestAsyncMD:
    def test_title(self, async_result):
        assert async_result.title == "Nablarchでの非同期処理"

    def test_not_no_knowledge_content(self, async_result):
        assert async_result.no_knowledge_content is False

    def test_has_sections(self, async_result):
        assert len(async_result.sections) >= 1

    def test_image_ref_preserved(self, async_result):
        all_content = " ".join(s.content for s in async_result.sections)
        assert "nablarch-async-pattern.png" in all_content

    def test_links_preserved(self, async_result):
        all_content = " ".join(s.content for s in async_result.sections)
        assert "nablarch.github.io" in all_content


class TestBatchMD:
    def test_title(self, batch_result):
        assert batch_result.title == "Nablarchバッチ処理パターン"

    def test_h2_sections_split(self, batch_result):
        titles = [s.title for s in batch_result.sections]
        assert "起動方法による分類" in titles
        assert "入出力による分類" in titles

    def test_h3_sections_split(self, batch_result):
        titles = [s.title for s in batch_result.sections]
        assert "FILE to DB" in titles

    def test_table_preserved(self, batch_result):
        # The MD has a comparison table with ○/✕
        all_content = " ".join(s.content for s in batch_result.sections)
        assert "○" in all_content

    def test_html_comments_removed(self, batch_result):
        all_content = " ".join(s.content for s in batch_result.sections)
        assert "textlint-disable" not in all_content
        assert "textlint-enable" not in all_content


class TestAntiPatternMD:
    def test_title(self, anti_result):
        assert anti_result.title == "Nablarchアンチパターン"

    def test_nested_h3_under_h2(self, anti_result):
        titles = [s.title for s in anti_result.sections]
        assert "N+1問題" in titles

    def test_section_count_reasonable(self, anti_result):
        # Has multiple h2 and h3 sections
        assert len(anti_result.sections) >= 4

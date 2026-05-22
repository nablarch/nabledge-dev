"""Integration tests for keyword-search.sh."""
import json
import os
import subprocess
import tempfile
from pathlib import Path

import pytest

SCRIPT_PATH = (
    Path(__file__).resolve().parents[2]
    / "components"
    / "scripts"
    / "keyword-search.sh"
)


@pytest.fixture()
def knowledge_dir():
    """Create a minimal knowledge directory with knowledge files (no terms.json)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        kdir = Path(tmpdir) / "knowledge"
        kdir.mkdir()

        lib_dir = kdir / "component" / "libraries"
        lib_dir.mkdir(parents=True)
        lib_dir.joinpath("libraries-universal-dao.json").write_text(
            json.dumps(
                {
                    "title": "ユニバーサルDAO",
                    "content": "UniversalDaoの概要",
                    "sections": [
                        {"id": "s1", "title": "機能概要", "content": "UniversalDaoは..."},
                        {"id": "s2", "title": "使用方法", "content": "batchUpdateメソッドで..."},
                        {"id": "s3", "title": "検索", "content": "findAllBySqlFileで検索する"},
                    ],
                }
            ),
            encoding="utf-8",
        )
        lib_dir.joinpath("libraries-bean-validation.json").write_text(
            json.dumps(
                {
                    "title": "Bean Validation",
                    "content": "バリデーション機能",
                    "sections": [
                        {"id": "s1", "title": "機能概要", "content": "Bean Validationは..."},
                        {"id": "s2", "title": "ドメインバリデーション", "content": "ドメインバリデーションの詳細"},
                    ],
                }
            ),
            encoding="utf-8",
        )

        handler_dir = kdir / "component" / "handlers"
        handler_dir.mkdir(parents=True)
        handler_dir.joinpath("handlers-cors.json").write_text(
            json.dumps(
                {
                    "title": "CORSハンドラ",
                    "content": "CORSの概要",
                    "sections": [
                        {"id": "s1", "title": "CORSとは", "content": "Cross-Origin Resource Sharing"},
                        {"id": "s2", "title": "設定方法", "content": "CorsHandlerの設定"},
                    ],
                }
            ),
            encoding="utf-8",
        )

        no_content_dir = kdir / "about"
        no_content_dir.mkdir(parents=True)
        no_content_dir.joinpath("about-nablarch.json").write_text(
            json.dumps(
                {
                    "title": "Nablarchとは",
                    "no_knowledge_content": True,
                    "content": "",
                    "sections": [
                        {"id": "s1", "title": "概要", "content": ""},
                    ],
                }
            ),
            encoding="utf-8",
        )

        yield kdir


def run_keyword_search(knowledge_dir: Path, *keywords: str) -> subprocess.CompletedProcess:
    """Run keyword-search.sh with KNOWLEDGE_DIR env var pointing to our fixture."""
    env = os.environ.copy()
    env["KNOWLEDGE_DIR"] = str(knowledge_dir)
    proc = subprocess.run(
        ["bash", str(SCRIPT_PATH), *keywords],
        capture_output=True,
        text=True,
        env=env,
    )
    return proc


def parse_output(proc: subprocess.CompletedProcess) -> list:
    assert proc.returncode == 0, f"Script failed: {proc.stderr}"
    return json.loads(proc.stdout)


class TestBasicMatching:
    """Case-insensitive partial match works correctly."""

    def test_exact_match(self, knowledge_dir):
        proc = run_keyword_search(knowledge_dir, "UniversalDao")
        result = parse_output(proc)
        section_ids = _extract_section_ids(result)
        assert "component/libraries/libraries-universal-dao.json:s1" in section_ids

    def test_exact_match_all_sections(self, knowledge_dir):
        """All sections whose title or content contains the keyword are returned."""
        proc = run_keyword_search(knowledge_dir, "UniversalDao")
        result = parse_output(proc)
        section_ids = _extract_section_ids(result)
        # s1 title contains UniversalDao, s2 content contains batchUpdate (no UniversalDao)
        # s3 content has findAllBySqlFile (no UniversalDao)
        # Only s1 matches "UniversalDao" in title or content
        assert "component/libraries/libraries-universal-dao.json:s1" in section_ids

    def test_case_insensitive(self, knowledge_dir):
        proc = run_keyword_search(knowledge_dir, "universaldao")
        result = parse_output(proc)
        section_ids = _extract_section_ids(result)
        assert "component/libraries/libraries-universal-dao.json:s1" in section_ids

    def test_case_insensitive_upper(self, knowledge_dir):
        proc = run_keyword_search(knowledge_dir, "UNIVERSALDAO")
        result = parse_output(proc)
        section_ids = _extract_section_ids(result)
        assert "component/libraries/libraries-universal-dao.json:s1" in section_ids

    def test_partial_match_in_content(self, knowledge_dir):
        proc = run_keyword_search(knowledge_dir, "batchUpdate")
        result = parse_output(proc)
        section_ids = _extract_section_ids(result)
        assert "component/libraries/libraries-universal-dao.json:s2" in section_ids

    def test_partial_match_in_title(self, knowledge_dir):
        proc = run_keyword_search(knowledge_dir, "ドメインバリデーション")
        result = parse_output(proc)
        section_ids = _extract_section_ids(result)
        assert "component/libraries/libraries-bean-validation.json:s2" in section_ids

    def test_japanese_keyword(self, knowledge_dir):
        proc = run_keyword_search(knowledge_dir, "ドメインバリデーション")
        result = parse_output(proc)
        section_ids = _extract_section_ids(result)
        assert "component/libraries/libraries-bean-validation.json:s2" in section_ids

    def test_abbreviation_keyword(self, knowledge_dir):
        proc = run_keyword_search(knowledge_dir, "CORS")
        result = parse_output(proc)
        section_ids = _extract_section_ids(result)
        assert "component/handlers/handlers-cors.json:s1" in section_ids
        assert "component/handlers/handlers-cors.json:s2" in section_ids

    def test_partial_substring_match(self, knowledge_dir):
        """'Validation' partially matches 'Bean Validation' in section title/content."""
        proc = run_keyword_search(knowledge_dir, "Validation")
        result = parse_output(proc)
        section_ids = _extract_section_ids(result)
        assert "component/libraries/libraries-bean-validation.json:s1" in section_ids

    def test_keyword_matches_page_title(self, knowledge_dir):
        """Keyword matching the page-level title/content includes sections."""
        proc = run_keyword_search(knowledge_dir, "CorsHandler")
        result = parse_output(proc)
        section_ids = _extract_section_ids(result)
        assert "component/handlers/handlers-cors.json:s2" in section_ids


class TestMultiKeywordAND:
    """Multiple keywords: page-level AND, section-level OR."""

    def test_two_keywords_same_page(self, knowledge_dir):
        proc = run_keyword_search(knowledge_dir, "UniversalDao", "batchUpdate")
        result = parse_output(proc)
        section_ids = _extract_section_ids(result)
        assert "component/libraries/libraries-universal-dao.json:s1" in section_ids
        assert "component/libraries/libraries-universal-dao.json:s2" in section_ids
        assert not any("bean-validation" in sid for sid in section_ids)

    def test_two_keywords_no_common_page(self, knowledge_dir):
        """CORS + batchUpdate have no common page → empty result."""
        proc = run_keyword_search(knowledge_dir, "CORS", "batchUpdate")
        result = parse_output(proc)
        assert result == []

    def test_and_narrows_results(self, knowledge_dir):
        """Adding a second keyword reduces pages to those containing both."""
        proc1 = run_keyword_search(knowledge_dir, "UniversalDao")
        r1 = parse_output(proc1)
        proc2 = run_keyword_search(knowledge_dir, "UniversalDao", "batchUpdate")
        r2 = parse_output(proc2)
        pages1 = _extract_pages(r1)
        pages2 = _extract_pages(r2)
        assert pages2 <= pages1


class TestMinimumKeywordLength:
    """Keywords shorter than 2 chars are ignored."""

    def test_single_char_ignored(self, knowledge_dir):
        proc = run_keyword_search(knowledge_dir, "A")
        result = parse_output(proc)
        assert result == []

    def test_two_char_accepted(self, knowledge_dir):
        proc = run_keyword_search(knowledge_dir, "DAO")
        result = parse_output(proc)
        section_ids = _extract_section_ids(result)
        assert len(section_ids) > 0


class TestNoKnowledgeContent:
    """Files with no_knowledge_content=true are excluded."""

    def test_no_knowledge_excluded(self, knowledge_dir):
        proc = run_keyword_search(knowledge_dir, "概要")
        result = parse_output(proc)
        section_ids = _extract_section_ids(result)
        assert not any("about-nablarch" in sid for sid in section_ids)
        assert any("libraries-universal-dao" in sid for sid in section_ids)


class TestOutputFormat:
    """Output is valid JSON with category > page > section hierarchy."""

    def test_json_structure(self, knowledge_dir):
        proc = run_keyword_search(knowledge_dir, "UniversalDao")
        result = parse_output(proc)
        assert isinstance(result, list)
        for cat_entry in result:
            assert "category" in cat_entry
            assert "pages" in cat_entry
            for page in cat_entry["pages"]:
                assert "page_title" in page
                assert "sections" in page
                for sec in page["sections"]:
                    assert "section_id" in sec
                    assert "section_title" in sec

    def test_category_grouping(self, knowledge_dir):
        proc = run_keyword_search(knowledge_dir, "UniversalDao")
        result = parse_output(proc)
        categories = [c["category"] for c in result]
        assert "component/libraries" in categories

    def test_sorted_by_category(self, knowledge_dir):
        proc = run_keyword_search(knowledge_dir, "概要")
        result = parse_output(proc)
        categories = [c["category"] for c in result]
        assert categories == sorted(categories)

    def test_pages_sorted_by_hit_count_desc(self, knowledge_dir):
        proc = run_keyword_search(knowledge_dir, "概要")
        result = parse_output(proc)
        for cat_entry in result:
            pages = cat_entry["pages"]
            counts = [len(p["sections"]) for p in pages]
            assert counts == sorted(counts, reverse=True)


class TestFullTextScan:
    """Full-text scan specific: searches across title and content of all sections."""

    def test_no_terms_json_needed(self, knowledge_dir):
        """Script works without terms.json present."""
        assert not (knowledge_dir / "terms.json").exists()
        proc = run_keyword_search(knowledge_dir, "UniversalDao")
        assert proc.returncode == 0

    def test_keyword_in_section_content_only(self, knowledge_dir):
        """Keyword found only in section content (not title) is matched."""
        proc = run_keyword_search(knowledge_dir, "findAllBySqlFile")
        result = parse_output(proc)
        section_ids = _extract_section_ids(result)
        assert "component/libraries/libraries-universal-dao.json:s3" in section_ids

    def test_keyword_only_in_page_content_returns_no_sections(self, knowledge_dir):
        """Keyword only in page-level content (not any section) returns empty — sections must match."""
        # "バリデーション機能" appears only in page-level content, not in any section
        proc = run_keyword_search(knowledge_dir, "バリデーション機能")
        result = parse_output(proc)
        section_ids = _extract_section_ids(result)
        # Page-level content match does NOT cause sections to be returned
        assert not any("libraries-bean-validation" in sid for sid in section_ids)


class TestErrorHandling:
    """Edge cases and error conditions."""

    def test_no_arguments(self, knowledge_dir):
        env = os.environ.copy()
        env["KNOWLEDGE_DIR"] = str(knowledge_dir)
        proc = subprocess.run(
            ["bash", str(SCRIPT_PATH)],
            capture_output=True,
            text=True,
            env=env,
        )
        assert proc.returncode == 1
        assert "Usage" in proc.stderr

    def test_no_match_returns_empty(self, knowledge_dir):
        proc = run_keyword_search(knowledge_dir, "NonExistentTerm12345")
        result = parse_output(proc)
        assert result == []

    def test_empty_knowledge_dir(self):
        """Empty knowledge directory returns empty result (no crash)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            kdir = Path(tmpdir) / "knowledge"
            kdir.mkdir()
            env = os.environ.copy()
            env["KNOWLEDGE_DIR"] = str(kdir)
            proc = subprocess.run(
                ["bash", str(SCRIPT_PATH), "test"],
                capture_output=True,
                text=True,
                env=env,
            )
            assert proc.returncode == 0
            assert json.loads(proc.stdout) == []


def _extract_section_ids(result: list) -> set:
    ids = set()
    for cat in result:
        for page in cat["pages"]:
            for sec in page["sections"]:
                ids.add(sec["section_id"])
    return ids


def _extract_pages(result: list) -> set:
    pages = set()
    for cat in result:
        for page in cat["pages"]:
            pages.add(page["page_title"])
    return pages

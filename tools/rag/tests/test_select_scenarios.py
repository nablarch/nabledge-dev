"""Unit tests for tools/rag/scripts/select_scenarios.py."""

import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "scripts"))
from select_scenarios import (  # noqa: E402
    build_text,
    find_truncated_pages,
    page_id_from_section_ref,
    select_scenarios,
)


class TestBuildText:
    def test_correct_concatenation_with_newlines(self):
        # Given
        page_title = "Page Title"
        section_title = "Section Title"
        section_content = "Section content body."

        # When
        result = build_text(page_title, section_title, section_content)

        # Then
        assert result == "Page Title\nSection Title\nSection content body."

    def test_empty_strings_still_joined_with_newlines(self):
        # Given / When
        result = build_text("", "", "")

        # Then
        assert result == "\n\n"

    def test_multiline_content_preserved(self):
        # Given
        content = "line1\nline2\nline3"

        # When
        result = build_text("T", "S", content)

        # Then
        assert result == "T\nS\nline1\nline2\nline3"


class TestPageIdFromSectionRef:
    def test_extracts_path_without_json_suffix(self):
        # Given
        section_ref = "path/to/file.json:s1"

        # When
        result = page_id_from_section_ref(section_ref)

        # Then
        assert result == "path/to/file"

    def test_simple_filename(self):
        # Given
        section_ref = "foo.json:s1"

        # When
        result = page_id_from_section_ref(section_ref)

        # Then
        assert result == "foo"

    def test_deeply_nested_path(self):
        # Given
        section_ref = "a/b/c/d/e.json:s99"

        # When
        result = page_id_from_section_ref(section_ref)

        # Then
        assert result == "a/b/c/d/e"

    def test_section_id_with_number_is_stripped(self):
        # Given
        section_ref = "page.json:s123"

        # When
        result = page_id_from_section_ref(section_ref)

        # Then
        assert result == "page"


class TestFindTruncatedPages:
    def _write_page(self, directory: pathlib.Path, name: str, title: str, sections: list) -> None:
        """Helper: write a knowledge JSON file under directory."""
        page = {"title": title, "sections": sections}
        path = directory / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(page), encoding="utf-8")

    def test_page_with_all_sections_within_limit_not_in_result(self, tmp_path):
        # Given: a page whose largest section text is well under 2048 chars
        self._write_page(
            tmp_path,
            "short.json",
            "Short Page",
            [{"id": "s1", "title": "Sec1", "content": "x" * 10}],
        )

        # When
        result = find_truncated_pages(tmp_path)

        # Then
        assert "short" not in result

    def test_page_with_section_exactly_2048_chars_not_in_result(self, tmp_path):
        # Given: build_text produces exactly 2048 chars
        # "Title\nSecTitle\n" = 14 chars; content fills the rest
        page_title = "T"    # 1 char
        sec_title = "S"     # 1 char
        # build_text => "T\nS\n<content>" — 4 fixed chars + len(content)
        # target total = 2048 → content len = 2048 - 4 = 2044
        content = "c" * (2048 - len(page_title) - len(sec_title) - 2)
        assert len(build_text(page_title, sec_title, content)) == 2048
        self._write_page(
            tmp_path,
            "boundary.json",
            page_title,
            [{"id": "s1", "title": sec_title, "content": content}],
        )

        # When
        result = find_truncated_pages(tmp_path)

        # Then: boundary is NOT truncated (condition is strictly > 2048)
        assert "boundary" not in result

    def test_page_with_section_2049_chars_is_in_result(self, tmp_path):
        # Given: build_text produces exactly 2049 chars
        page_title = "T"
        sec_title = "S"
        content = "c" * (2049 - len(page_title) - len(sec_title) - 2)
        assert len(build_text(page_title, sec_title, content)) == 2049
        self._write_page(
            tmp_path,
            "over.json",
            page_title,
            [{"id": "s1", "title": sec_title, "content": content}],
        )

        # When
        result = find_truncated_pages(tmp_path)

        # Then: page is truncated
        assert "over" in result
        assert result["over"] == ["s1"]

    def test_only_over_limit_sections_listed_per_page(self, tmp_path):
        # Given: page with one ok section and one over-limit section
        page_title = "P"
        sec_title = "S"
        short_content = "ok"
        over_content = "c" * (2049 - len(page_title) - len(sec_title) - 2)
        self._write_page(
            tmp_path,
            "mixed.json",
            page_title,
            [
                {"id": "s1", "title": sec_title, "content": short_content},
                {"id": "s2", "title": sec_title, "content": over_content},
            ],
        )

        # When
        result = find_truncated_pages(tmp_path)

        # Then: only s2 listed
        assert "mixed" in result
        assert result["mixed"] == ["s2"]

    def test_nested_json_files_are_found(self, tmp_path):
        # Given: JSON file in a subdirectory
        self._write_page(
            tmp_path,
            "sub/dir/page.json",
            "P",
            [{"id": "s1", "title": "S", "content": "c" * (2049 - 1 - 1 - 2)}],
        )

        # When
        result = find_truncated_pages(tmp_path)

        # Then: page_id uses relative path without suffix
        assert "sub/dir/page" in result


class TestSelectScenarios:
    def _scenario(self, id_: str, must: list = None, acceptable: list = None) -> dict:
        return {
            "id": id_,
            "then": {
                "must": must or [],
                "acceptable": acceptable or [],
            },
        }

    def test_scenario_referencing_truncated_page_is_ineligible(self):
        # Given
        truncated = {"path/to/page": ["s1"]}
        scenario = self._scenario(
            "sc-01",
            must=[{"section": "path/to/page.json:s1"}],
        )

        # When
        eligible, ineligible = select_scenarios([scenario], truncated)

        # Then
        assert len(eligible) == 0
        assert len(ineligible) == 1
        assert ineligible[0]["id"] == "sc-01"
        assert ineligible[0]["reason"] == "excluded"
        assert "path/to/page" in ineligible[0]["truncated_pages"]

    def test_scenario_referencing_non_truncated_page_is_eligible(self):
        # Given: truncated has a different page
        truncated = {"other/page": ["s1"]}
        scenario = self._scenario(
            "sc-02",
            must=[{"section": "good/page.json:s1"}],
        )

        # When
        eligible, ineligible = select_scenarios([scenario], truncated)

        # Then
        assert len(eligible) == 1
        assert len(ineligible) == 0
        assert eligible[0]["id"] == "sc-02"
        assert eligible[0]["reason"] == "all referenced pages have sections within 2048 chars"

    def test_fact_only_items_in_must_are_skipped(self):
        # Given: must items that have only "fact" (no "section" key)
        truncated = {"some/page": ["s1"]}
        scenario = self._scenario(
            "sc-03",
            must=[{"fact": "some fact without section ref"}],
        )

        # When
        eligible, ineligible = select_scenarios([scenario], truncated)

        # Then: fact-only item contributes no page ref → vacuously eligible
        assert len(eligible) == 1
        assert len(ineligible) == 0
        assert eligible[0]["id"] == "sc-03"

    def test_mixed_fact_and_section_items_only_section_refs_extracted(self):
        # Given: must has one fact-only item and one section item pointing to truncated page
        truncated = {"bad/page": ["s1"]}
        scenario = self._scenario(
            "sc-04",
            must=[
                {"fact": "some fact"},
                {"section": "bad/page.json:s1"},
            ],
        )

        # When
        eligible, ineligible = select_scenarios([scenario], truncated)

        # Then: the section ref hits truncated → ineligible
        assert len(eligible) == 0
        assert len(ineligible) == 1
        assert ineligible[0]["id"] == "sc-04"

    def test_scenario_with_empty_must_is_vacuously_eligible(self):
        # Given: scenario with no must or acceptable items
        truncated = {"any/page": ["s1"]}
        scenario = self._scenario("sc-05")

        # When
        eligible, ineligible = select_scenarios([scenario], truncated)

        # Then
        assert len(eligible) == 1
        assert len(ineligible) == 0
        assert eligible[0]["id"] == "sc-05"
        assert eligible[0]["referenced_pages"] == []

    def test_acceptable_section_refs_also_checked(self):
        # Given: must is clean but acceptable references a truncated page
        truncated = {"bad/page": ["s2"]}
        scenario = self._scenario(
            "sc-06",
            must=[{"section": "good/page.json:s1"}],
            acceptable=[{"section": "bad/page.json:s2"}],
        )

        # When
        eligible, ineligible = select_scenarios([scenario], truncated)

        # Then
        assert len(eligible) == 0
        assert len(ineligible) == 1
        assert ineligible[0]["id"] == "sc-06"

    def test_multiple_scenarios_split_correctly(self):
        # Given
        truncated = {"bad/page": ["s1"]}
        scenarios = [
            self._scenario("sc-good", must=[{"section": "ok/page.json:s1"}]),
            self._scenario("sc-bad", must=[{"section": "bad/page.json:s1"}]),
        ]

        # When
        eligible, ineligible = select_scenarios(scenarios, truncated)

        # Then
        assert [s["id"] for s in eligible] == ["sc-good"]
        assert [s["id"] for s in ineligible] == ["sc-bad"]

"""Unit tests for MD converter schema (Phase 21-D).

Preamble (content between h1 and the first h2+) goes to top-level content;
`sections` contains only real h2+ sections.
"""
from __future__ import annotations

from scripts.create.converters.md import convert


class TestTopLevelContent:
    def test_preamble_before_h2_goes_to_top_level_content(self):
        source = (
            "# Title\n"
            "\n"
            "これは前書きの段落。\n"
            "\n"
            "## SectionA\n"
            "\n"
            "A の本文。\n"
        )
        result = convert(source, "example")
        assert result.title == "Title"
        assert "これは前書きの段落" in result.content
        assert len(result.sections) == 1
        assert result.sections[0].title == "SectionA"
        # No empty-title preamble section
        assert all(s.title for s in result.sections)

    def test_no_h2_means_all_content_at_top_level(self):
        source = (
            "# Solo\n"
            "\n"
            "段落のみ。\n"
        )
        result = convert(source, "example")
        assert result.title == "Solo"
        assert "段落のみ" in result.content
        assert result.sections == []

    def test_empty_preamble_means_empty_top_level_content(self):
        source = (
            "# Title\n"
            "\n"
            "## SectionA\n"
            "\n"
            "A本文。\n"
        )
        result = convert(source, "example")
        assert result.title == "Title"
        assert result.content.strip() == ""
        assert len(result.sections) == 1

    def test_no_h1_means_empty_title(self):
        source = "段落のみ。\n"
        result = convert(source, "example")
        assert result.title == ""
        assert "段落のみ" in result.content
        assert result.sections == []

    def test_multiple_h2(self):
        source = (
            "# T\n"
            "\n"
            "前書き。\n"
            "\n"
            "## A\n"
            "\n"
            "A本文。\n"
            "\n"
            "## B\n"
            "\n"
            "B本文。\n"
        )
        result = convert(source, "example")
        assert result.title == "T"
        assert "前書き" in result.content
        assert [s.title for s in result.sections] == ["A", "B"]

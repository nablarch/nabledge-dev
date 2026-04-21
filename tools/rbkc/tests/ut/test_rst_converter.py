"""Unit tests for RST converter schema (Phase 21-D).

These tests cover the new JSON schema where preamble (content between h1 and
the first h2/h3) goes to the top-level `content` field, and `sections`
contains only real h2/h3 sections from the source.
"""
from __future__ import annotations

import pytest

from scripts.create.converters.rst import convert


class TestTopLevelContent:
    """Preamble is placed in top-level content, not as a '概要' section."""

    def test_preamble_before_h2_goes_to_top_level_content(self):
        source = (
            "タイトル\n"
            "========\n"
            "\n"
            "これは前書きの段落。\n"
            "\n"
            "セクションA\n"
            "----------\n"
            "\n"
            "A の本文。\n"
        )
        result = convert(source, "example")
        assert result.title == "タイトル"
        assert "これは前書きの段落" in result.content
        assert len(result.sections) == 1
        assert result.sections[0].title == "セクションA"
        # No fabricated "概要" section
        assert all(s.title != "概要" for s in result.sections)

    def test_no_h2_means_all_content_at_top_level(self):
        source = (
            "孤立タイトル\n"
            "=============\n"
            "\n"
            "唯一の段落。\n"
        )
        result = convert(source, "example")
        assert result.title == "孤立タイトル"
        assert "唯一の段落" in result.content
        assert result.sections == []

    def test_no_h2_content_not_duplicated(self):
        """Regression: when there are no h2/h3, top-level content must not be duplicated."""
        source = (
            "孤立タイトル\n"
            "=============\n"
            "\n"
            "段落A。\n"
            "\n"
            "段落B。\n"
        )
        result = convert(source, "example")
        assert result.sections == []
        assert result.content.count("段落A") == 1
        assert result.content.count("段落B") == 1

    def test_empty_preamble_means_empty_top_level_content(self):
        source = (
            "タイトル\n"
            "========\n"
            "\n"
            "セクションA\n"
            "----------\n"
            "\n"
            "A の本文。\n"
        )
        result = convert(source, "example")
        assert result.title == "タイトル"
        assert result.content.strip() == ""
        assert len(result.sections) == 1
        assert result.sections[0].title == "セクションA"

    def test_no_h1_no_h2_means_empty_title(self):
        source = "段落だけのファイル。\n"
        result = convert(source, "example")
        assert result.title == ""
        assert "段落だけのファイル" in result.content
        assert result.sections == []

    def test_multiple_h2_kept_as_sections(self):
        source = (
            "Title\n"
            "=====\n"
            "\n"
            "前書き。\n"
            "\n"
            "SectionA\n"
            "--------\n"
            "\n"
            "A本文。\n"
            "\n"
            "SectionB\n"
            "--------\n"
            "\n"
            "B本文。\n"
        )
        result = convert(source, "example")
        assert result.title == "Title"
        assert "前書き" in result.content
        assert [s.title for s in result.sections] == ["SectionA", "SectionB"]

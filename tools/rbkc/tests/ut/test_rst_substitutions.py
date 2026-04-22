"""Tests for scripts/common/rst_substitutions.py — Phase 21-X.

Spec (rbkc-verify-quality-design.md §3-1):
  - Pass 1: collect `.. |name| replace:: text` and `.. |name| raw:: html`
    definitions; return dict.
  - Pass 2: expand `|name|` references.
  - `raw:: html` with <br> / <br/> → "\n"; other HTML → kept verbatim.
  - Undefined substitution reference → raise UndefinedSubstitutionError.
  - Cycle detection → raise SubstitutionCycleError.
"""
from __future__ import annotations

import pytest


class TestCollectDefinitions:
    def _collect(self, text):
        from scripts.common.rst_substitutions import collect_substitutions
        return collect_substitutions(text)

    def test_replace_directive(self):
        text = ".. |foo| replace:: bar baz\n"
        assert self._collect(text) == {"foo": "bar baz"}

    def test_replace_multiline_body(self):
        text = (
            ".. |long| replace:: first line\n"
            "   second line\n"
        )
        assert self._collect(text) == {"long": "first line second line"}

    def test_raw_html_br(self):
        text = ".. |br| raw:: html\n\n   <br>\n"
        assert self._collect(text) == {"br": "\n"}

    def test_raw_html_br_self_closing(self):
        text = ".. |br| raw:: html\n\n   <br/>\n"
        assert self._collect(text) == {"br": "\n"}

    def test_raw_html_other_tag_kept_verbatim(self):
        text = ".. |emph| raw:: html\n\n   <em>x</em>\n"
        assert self._collect(text) == {"emph": "<em>x</em>"}

    def test_multiple_definitions(self):
        text = (
            ".. |a| replace:: aaa\n"
            ".. |b| replace:: bbb\n"
        )
        assert self._collect(text) == {"a": "aaa", "b": "bbb"}

    def test_no_definitions(self):
        assert self._collect("just some prose\n") == {}

    def test_indented_definition_is_still_captured(self):
        # Per docutils, substitution definitions may appear at column 0.
        # Indented definitions inside directive body are NOT top-level definitions;
        # we accept top-level only to match converter behaviour.
        text = "   .. |x| replace:: ignored\n"
        assert self._collect(text) == {}


class TestExpand:
    def _expand(self, text, subs):
        from scripts.common.rst_substitutions import expand_substitutions
        return expand_substitutions(text, subs)

    def test_simple_expansion(self):
        assert self._expand("use |foo| here", {"foo": "BAR"}) == "use BAR here"

    def test_multiple_occurrences(self):
        assert self._expand("|x| and |x|", {"x": "Y"}) == "Y and Y"

    def test_br_expands_to_newline(self):
        assert self._expand("a|br|b", {"br": "\n"}) == "a\nb"

    def test_undefined_reference_raises(self):
        from scripts.common.rst_substitutions import UndefinedSubstitutionError
        with pytest.raises(UndefinedSubstitutionError):
            self._expand("hello |missing| world", {"other": "x"})

    def test_nested_expansion(self):
        # |outer| expands to text containing |inner|
        result = self._expand("|outer|", {"outer": "A |inner| B", "inner": "i"})
        assert result == "A i B"

    def test_cycle_detection(self):
        from scripts.common.rst_substitutions import SubstitutionCycleError
        with pytest.raises(SubstitutionCycleError):
            self._expand("|a|", {"a": "|b|", "b": "|a|"})

    def test_does_not_match_grid_table_pipes(self):
        # "| cell |" (spaces inside, or non-identifier contents) must not be treated
        # as a substitution reference.
        text = "| col1 | col2 |"
        assert self._expand(text, {"col1": "X"}) == text

    def test_multi_char_identifier(self):
        assert self._expand("|jsr352|", {"jsr352": "JSR 352"}) == "JSR 352"


class TestCollectAndExpandIntegration:
    def test_end_to_end(self):
        from scripts.common.rst_substitutions import (
            collect_substitutions,
            expand_substitutions,
        )
        text = (
            ".. |br| raw:: html\n\n"
            "   <br>\n"
            ".. |name| replace:: Nablarch\n"
            "\n"
            "Title|br|goes here with |name|.\n"
        )
        subs = collect_substitutions(text)
        assert subs == {"br": "\n", "name": "Nablarch"}
        # Body (after the definitions) may still contain |br| and |name|
        expanded = expand_substitutions(text, subs)
        assert "|br|" not in expanded
        assert "|name|" not in expanded
        assert "Nablarch" in expanded
        assert "Title\ngoes here" in expanded

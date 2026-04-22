"""Tests for scripts/common/rst_admonition.py — Phase 21-X-4a.

Shared RST admonition → MD blockquote conversion rules used by both the
tokenizer (verify) and the converter (create). This module is the single
source of truth for the mapping.
"""
from __future__ import annotations

import pytest


def _mod():
    from scripts.common import rst_admonition
    return rst_admonition


class TestAdmonitionLabels:
    def test_note_label(self):
        assert _mod().ADMONITION_LABELS["note"] == "Note"

    def test_tip_label(self):
        assert _mod().ADMONITION_LABELS["tip"] == "Tip"

    def test_warning_label(self):
        assert _mod().ADMONITION_LABELS["warning"] == "Warning"

    def test_see_also_label(self):
        assert _mod().ADMONITION_LABELS["seealso"] == "See Also"

    def test_version_added(self):
        assert _mod().ADMONITION_LABELS["versionadded"] == "Version Added"

    def test_version_changed(self):
        assert _mod().ADMONITION_LABELS["versionchanged"] == "Version Changed"

    def test_all_14_directive_names_mapped(self):
        # Closed set per design doc §3-1 group B.
        expected = {
            "note", "tip", "warning", "important", "attention", "hint",
            "admonition", "caution", "danger", "error", "seealso",
            "deprecated", "versionadded", "versionchanged",
        }
        assert set(_mod().ADMONITION_LABELS) == expected


class TestRenderHeader:
    def test_named_note(self):
        assert _mod().render_header("note") == "> **Note:**"

    def test_named_tip(self):
        assert _mod().render_header("tip") == "> **Tip:**"

    def test_custom_admonition_with_title(self):
        # `.. admonition:: My Title` renders as `> **My Title**` (no colon,
        # per the converter convention for custom-titled admonitions).
        assert _mod().render_header("admonition", "My Title") == "> **My Title**"

    def test_admonition_without_title_defaults_to_note(self):
        assert _mod().render_header("admonition") == "> **Note:**"

    def test_unknown_directive_raises(self):
        with pytest.raises(KeyError):
            _mod().render_header("notanadmonition")


class TestIsAdmonition:
    def test_named(self):
        assert _mod().is_admonition("note")
        assert _mod().is_admonition("warning")

    def test_admonition_fallback(self):
        assert _mod().is_admonition("admonition")

    def test_non_admonition(self):
        assert not _mod().is_admonition("code-block")
        assert not _mod().is_admonition("table")


class TestDirectiveNamesConstant:
    def test_exposes_name_set(self):
        names = _mod().ADMONITION_DIRECTIVES
        # Must match the keys of ADMONITION_LABELS
        assert names == set(_mod().ADMONITION_LABELS)

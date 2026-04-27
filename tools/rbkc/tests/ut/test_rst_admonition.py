"""Tests for scripts/common/rst_admonition.ADMONITION_LABELS.

The label table is the single source of truth for the bold label used by
the Visitor when rendering admonition blockquotes.
"""
from __future__ import annotations


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

    def test_admonition_default_label_is_note(self):
        assert _mod().ADMONITION_LABELS["admonition"] == "Note"

    def test_all_10_directive_names_mapped(self):
        # Closed set (Phase 21-Y): only the 10 docutils-native admonitions
        # appear in the Nablarch corpus. Sphinx-only `seealso`, `deprecated`,
        # `versionadded`, `versionchanged` are excluded (Y-1 probe 0 hits).
        expected = {
            "note", "tip", "warning", "important", "attention", "hint",
            "admonition", "caution", "danger", "error",
        }
        assert set(_mod().ADMONITION_LABELS) == expected

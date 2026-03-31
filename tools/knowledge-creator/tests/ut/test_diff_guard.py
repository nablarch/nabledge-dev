"""Phase E diff guard unit tests.

Tests for _extract_allowed_sections and _apply_diff_guard, plus
integration tests verifying fix_one() applies the guard correctly.
"""
import os
import json
import subprocess
import pytest
import sys

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(TOOL_DIR, "scripts"))

from conftest import load_fixture
from common import load_json, write_json


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_knowledge(sections=None, index=None, extra=None):
    k = {
        "id": "test-file",
        "title": "Test",
        "no_knowledge_content": False,
        "official_doc_urls": ["https://example.com"],
        "index": index or [
            {"id": "s1", "title": "Section 1", "hints": ["Hint1"]},
            {"id": "s2", "title": "Section 2", "hints": ["Hint2"]},
        ],
        "sections": sections or {
            "s1": "original s1 content here that is long enough",
            "s2": "original s2 content here that is long enough",
        },
    }
    if extra:
        k.update(extra)
    return k


def _mock_fn(output):
    def fn(prompt, json_schema=None, log_dir=None, file_id=None, **kwargs):
        return subprocess.CompletedProcess(
            args=["claude"], returncode=0,
            stdout=json.dumps(output), stderr=""
        )
    return fn


# ---------------------------------------------------------------------------
# _extract_allowed_sections
# ---------------------------------------------------------------------------

class TestExtractAllowedSections:

    def test_extracts_section_ids_from_locations(self):
        from phase_e_fix import _extract_allowed_sections
        findings = [
            {"category": "omission", "severity": "critical",
             "location": "s1", "description": "missing"},
            {"category": "fabrication", "severity": "critical",
             "location": "s3", "description": "fabricated"},
        ]
        ids, is_full_rebuild = _extract_allowed_sections(findings)
        assert "s1" in ids
        assert "s3" in ids
        assert not is_full_rebuild

    def test_no_knowledge_content_invalid_is_full_rebuild(self):
        from phase_e_fix import _extract_allowed_sections
        findings = [
            {"category": "no_knowledge_content_invalid", "severity": "critical",
             "location": "file", "description": "has content"},
        ]
        ids, is_full_rebuild = _extract_allowed_sections(findings)
        assert is_full_rebuild

    def test_hints_missing_extracts_section_id(self):
        from phase_e_fix import _extract_allowed_sections
        findings = [
            {"category": "hints_missing", "severity": "minor",
             "location": "s2", "description": "missing hints"},
        ]
        ids, is_full_rebuild = _extract_allowed_sections(findings)
        assert "s2" in ids
        assert not is_full_rebuild

    def test_empty_findings_returns_empty_set(self):
        from phase_e_fix import _extract_allowed_sections
        ids, is_full_rebuild = _extract_allowed_sections([])
        assert len(ids) == 0
        assert not is_full_rebuild

    def test_section_issue_with_v3_description_location_triggers_full_rebuild(self):
        """section_issue finding with V3-style location (no sN ID) must trigger full rebuild.

        When LLM returns a location like "S9: Section count 2 < source headings 3",
        the sN regex extracts nothing.  Without the full-rebuild fallback the diff guard
        would block the structural fix entirely.  This test verifies the fallback fires.
        """
        from phase_e_fix import _extract_allowed_sections
        findings = [
            {"category": "section_issue", "severity": "minor",
             "location": "S9: Section count 2 < source headings 3",
             "description": "knowledge has 2 sections but source has 3 h2 headings"},
        ]
        ids, is_full_rebuild = _extract_allowed_sections(findings)
        assert is_full_rebuild, "section_issue with no sN location must fall back to full rebuild"

    def test_section_issue_with_sn_location_extracts_section_id(self):
        """section_issue finding with a plain sN location is handled normally."""
        from phase_e_fix import _extract_allowed_sections
        findings = [
            {"category": "section_issue", "severity": "minor",
             "location": "s3", "description": "section too short"},
        ]
        ids, is_full_rebuild = _extract_allowed_sections(findings)
        assert "s3" in ids
        assert not is_full_rebuild


# ---------------------------------------------------------------------------
# _apply_diff_guard — reverts unscoped, keeps scoped
# ---------------------------------------------------------------------------

class TestDiffGuardReverts:

    def test_diff_guard_reverts_unscoped_sections(self):
        """Changes to sections not in allowed_sections are reverted to input."""
        from phase_e_fix import _apply_diff_guard
        input_k = _make_knowledge()
        output_k = _make_knowledge(sections={
            "s1": "CHANGED s1 — not in scope",
            "s2": "FIXED s2 — in scope",
        })
        guarded = _apply_diff_guard(input_k, output_k, {"s2"})
        assert guarded["sections"]["s1"] == "original s1 content here that is long enough"
        assert guarded["sections"]["s2"] == "FIXED s2 — in scope"

    def test_diff_guard_preserves_scoped_sections(self):
        """Changes to sections in allowed_sections are kept."""
        from phase_e_fix import _apply_diff_guard
        input_k = _make_knowledge()
        output_k = _make_knowledge(sections={
            "s1": "original s1 content here that is long enough",
            "s2": "FIXED s2 content with new info that is long enough",
        })
        guarded = _apply_diff_guard(input_k, output_k, {"s2"})
        assert guarded["sections"]["s2"] == "FIXED s2 content with new info that is long enough"

    def test_diff_guard_protects_metadata(self):
        """Top-level fields (id, title, official_doc_urls) are preserved from input."""
        from phase_e_fix import _apply_diff_guard
        input_k = _make_knowledge()
        output_k = _make_knowledge(sections={
            "s1": "FIXED s1 content here that is long enough",
            "s2": "original s2 content here that is long enough",
        })
        output_k["id"] = "CHANGED-id"
        output_k["title"] = "CHANGED title"
        output_k["official_doc_urls"] = []
        guarded = _apply_diff_guard(input_k, output_k, {"s1"})
        assert guarded["id"] == "test-file"
        assert guarded["title"] == "Test"
        assert guarded["official_doc_urls"] == ["https://example.com"]

    def test_diff_guard_allows_hints_update(self):
        """hints_missing finding (section in allowed_sections) allows hints modification."""
        from phase_e_fix import _apply_diff_guard
        input_k = _make_knowledge()
        output_k = _make_knowledge(index=[
            {"id": "s1", "title": "Section 1", "hints": ["Hint1", "NewHint"]},  # allowed
            {"id": "s2", "title": "Section 2", "hints": ["CHANGED"]},           # not allowed
        ])
        guarded = _apply_diff_guard(input_k, output_k, {"s1"})
        s1_entry = next(e for e in guarded["index"] if e["id"] == "s1")
        s2_entry = next(e for e in guarded["index"] if e["id"] == "s2")
        assert "NewHint" in s1_entry["hints"]
        assert s2_entry["hints"] == ["Hint2"]

    def test_diff_guard_full_rebuild_passes_through(self):
        """no_knowledge_content_invalid: entire output passes through unchanged."""
        from phase_e_fix import _apply_diff_guard
        input_k = {"id": "x", "title": "X", "no_knowledge_content": True,
                   "official_doc_urls": [], "index": [], "sections": {}}
        output_k = {"id": "x", "title": "X rebuilt", "no_knowledge_content": False,
                    "official_doc_urls": ["https://example.com"],
                    "index": [{"id": "s1", "title": "S1", "hints": ["H1"]}],
                    "sections": {"s1": "new content"}}
        # For full rebuild, caller should pass all_sections; guard accepts it as-is
        guarded = _apply_diff_guard(input_k, output_k, set(), is_full_rebuild=True)
        assert guarded["no_knowledge_content"] is False
        assert guarded["sections"]["s1"] == "new content"


# ---------------------------------------------------------------------------
# fix_one() integration — diff guard wired in
# ---------------------------------------------------------------------------

class TestDiffGuardIntegratedInFixOne:

    def _setup_file(self, ctx, file_id, knowledge):
        file_info = {
            "id": file_id,
            "source_path": f".lw/nab-official/v6/nablarch-document/ja/{file_id}.rst",
            "output_path": f"component/handlers/{file_id}.json",
            "format": "rst",
        }
        src = f"{ctx.repo}/{file_info['source_path']}"
        os.makedirs(os.path.dirname(src), exist_ok=True)
        with open(src, "w") as f:
            f.write("source content")
        kpath = f"{ctx.knowledge_cache_dir}/{file_info['output_path']}"
        os.makedirs(os.path.dirname(kpath), exist_ok=True)
        write_json(kpath, knowledge)
        return file_info, kpath

    def test_diff_guard_integrated_in_fix_one(self, ctx):
        """fix_one reverts unscoped sections, keeps scoped changes."""
        from phase_e_fix import PhaseEFix

        input_knowledge = _make_knowledge(sections={
            "s1": "original s1 content here that is long enough",
            "s2": "original s2 content here that is long enough",
        })
        # LLM changes both s1 (scoped) and s2 (not scoped)
        fix_output = _make_knowledge(sections={
            "s1": "FIXED s1 content here that is long enough",
            "s2": "COLLATERAL DAMAGE to s2 should be reverted",
        })

        file_info, kpath = self._setup_file(ctx, "guard-int-test", input_knowledge)

        os.makedirs(ctx.findings_dir, exist_ok=True)
        write_json(f"{ctx.findings_dir}/guard-int-test_r1.json", {
            "file_id": "guard-int-test", "status": "has_issues",
            "findings": [{"category": "omission", "severity": "critical",
                          "location": "s1", "description": "missing info"}]
        })

        fixer = PhaseEFix(ctx, run_claude_fn=_mock_fn(fix_output))
        fixer.round_num = 1
        result = fixer.fix_one(file_info)

        assert result["status"] == "fixed"
        saved = load_json(kpath)
        assert saved["sections"]["s1"] == "FIXED s1 content here that is long enough"
        assert saved["sections"]["s2"] == "original s2 content here that is long enough"

    def test_diff_guard_rejects_empty_fix(self, ctx):
        """fix_one returns error when LLM makes no changes in allowed sections."""
        from phase_e_fix import PhaseEFix

        input_knowledge = _make_knowledge()
        # LLM returns unchanged content for s1 (the scoped section)
        fix_output = _make_knowledge()  # identical to input

        file_info, kpath = self._setup_file(ctx, "empty-fix-test", input_knowledge)

        os.makedirs(ctx.findings_dir, exist_ok=True)
        write_json(f"{ctx.findings_dir}/empty-fix-test_r1.json", {
            "file_id": "empty-fix-test", "status": "has_issues",
            "findings": [{"category": "omission", "severity": "critical",
                          "location": "s1", "description": "missing info"}]
        })

        fixer = PhaseEFix(ctx, run_claude_fn=_mock_fn(fix_output))
        fixer.round_num = 1
        result = fixer.fix_one(file_info)

        assert result["status"] == "error"
        assert "no changes" in result.get("error", "").lower()

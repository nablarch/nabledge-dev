"""Phase E per-section fix unit tests.

Tests for _group_findings_by_section and per-section fix_one behavior.
"""
import os
import json
import subprocess
import pytest
import sys

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(TOOL_DIR, "scripts"))

from common import load_json, write_json


def _make_knowledge(sections=None, index=None):
    return {
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


class TestGroupFindingsBySection:

    def test_groups_by_section_id(self):
        from phase_e_fix import _group_findings_by_section
        findings = [
            {"category": "omission", "severity": "critical",
             "location": "s1", "description": "missing A"},
            {"category": "fabrication", "severity": "minor",
             "location": "s2", "description": "fabricated B"},
            {"category": "omission", "severity": "minor",
             "location": "s1", "description": "missing C"},
        ]
        groups, structural = _group_findings_by_section(findings)
        assert len(groups["s1"]) == 2
        assert len(groups["s2"]) == 1
        assert len(structural) == 0

    def test_structural_findings_separated(self):
        from phase_e_fix import _group_findings_by_section
        findings = [
            {"category": "section_issue", "severity": "minor",
             "location": "S9: count mismatch", "description": "structural"},
            {"category": "no_knowledge_content_invalid", "severity": "critical",
             "location": "file", "description": "has content"},
        ]
        groups, structural = _group_findings_by_section(findings)
        assert len(groups) == 0
        assert len(structural) == 2

    def test_hints_missing_grouped_by_section(self):
        from phase_e_fix import _group_findings_by_section
        findings = [
            {"category": "hints_missing", "severity": "minor",
             "location": "s2", "description": "missing hint"},
        ]
        groups, structural = _group_findings_by_section(findings)
        assert "s2" in groups
        assert len(structural) == 0

    def test_uppercase_location_normalized(self):
        from phase_e_fix import _group_findings_by_section
        findings = [
            {"category": "omission", "severity": "critical",
             "location": "S1", "description": "uppercase"},
            {"category": "omission", "severity": "critical",
             "location": "sections.S3", "description": "dotted uppercase"},
        ]
        groups, structural = _group_findings_by_section(findings)
        assert "s1" in groups
        assert "s3" in groups


class TestPerSectionFix:

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
            f.write("source content about s1 topic\n\nsource content about s2 topic")
        kpath = f"{ctx.knowledge_cache_dir}/{file_info['output_path']}"
        os.makedirs(os.path.dirname(kpath), exist_ok=True)
        write_json(kpath, knowledge)
        return file_info, kpath

    def test_only_target_section_changes(self, ctx):
        """E-1: fix for s1 must not change s2."""
        from phase_e_fix import PhaseEFix

        input_knowledge = _make_knowledge()
        file_info, kpath = self._setup_file(ctx, "e1-test", input_knowledge)

        os.makedirs(ctx.findings_dir, exist_ok=True)
        write_json(f"{ctx.findings_dir}/e1-test_r1.json", {
            "file_id": "e1-test", "status": "has_issues",
            "findings": [{"category": "omission", "severity": "critical",
                          "location": "s1", "description": "missing info"}]
        })

        def mock_fn(prompt, json_schema=None, log_dir=None, file_id=None, **kwargs):
            return subprocess.CompletedProcess(
                args=["claude"], returncode=0,
                stdout=json.dumps({"section_text": "FIXED s1 content with added info"}),
                stderr=""
            )

        fixer = PhaseEFix(ctx, run_claude_fn=mock_fn)
        fixer.round_num = 1
        result = fixer.fix_one(file_info)

        assert result["status"] == "fixed"
        saved = load_json(kpath)
        assert saved["sections"]["s1"] == "FIXED s1 content with added info"
        assert saved["sections"]["s2"] == "original s2 content here that is long enough"

    def test_structural_finding_uses_full_output(self, ctx):
        """section_issue and no_knowledge_content_invalid use full knowledge output."""
        from phase_e_fix import PhaseEFix

        input_knowledge = _make_knowledge()
        input_knowledge["no_knowledge_content"] = True
        input_knowledge["sections"] = {}
        input_knowledge["index"] = []
        file_info, kpath = self._setup_file(ctx, "structural-test", input_knowledge)

        os.makedirs(ctx.findings_dir, exist_ok=True)
        write_json(f"{ctx.findings_dir}/structural-test_r1.json", {
            "file_id": "structural-test", "status": "has_issues",
            "findings": [{"category": "no_knowledge_content_invalid",
                          "severity": "critical",
                          "location": "file",
                          "description": "has content"}]
        })

        rebuilt = _make_knowledge(
            sections={"s1": "rebuilt content"},
            index=[{"id": "s1", "title": "S1", "hints": ["H1"]}]
        )
        rebuilt["no_knowledge_content"] = False

        def mock_fn(prompt, json_schema=None, log_dir=None, file_id=None, **kwargs):
            return subprocess.CompletedProcess(
                args=["claude"], returncode=0,
                stdout=json.dumps(rebuilt), stderr=""
            )

        fixer = PhaseEFix(ctx, run_claude_fn=mock_fn)
        fixer.round_num = 1
        result = fixer.fix_one(file_info)

        assert result["status"] == "fixed"
        saved = load_json(kpath)
        assert saved["no_knowledge_content"] is False
        assert "s1" in saved["sections"]

    def test_hints_missing_updates_only_hints(self, ctx):
        """hints_missing fix updates index hints without changing section content."""
        from phase_e_fix import PhaseEFix

        input_knowledge = _make_knowledge()
        file_info, kpath = self._setup_file(ctx, "hints-test", input_knowledge)

        os.makedirs(ctx.findings_dir, exist_ok=True)
        write_json(f"{ctx.findings_dir}/hints-test_r1.json", {
            "file_id": "hints-test", "status": "has_issues",
            "findings": [{"category": "hints_missing", "severity": "minor",
                          "location": "s1", "description": "missing NewHint"}]
        })

        def mock_fn(prompt, json_schema=None, log_dir=None, file_id=None, **kwargs):
            return subprocess.CompletedProcess(
                args=["claude"], returncode=0,
                stdout=json.dumps({"hints": ["Hint1", "NewHint"]}),
                stderr=""
            )

        fixer = PhaseEFix(ctx, run_claude_fn=mock_fn)
        fixer.round_num = 1
        result = fixer.fix_one(file_info)

        assert result["status"] == "fixed"
        saved = load_json(kpath)
        assert saved["sections"]["s1"] == "original s1 content here that is long enough"
        s1_hints = next(e for e in saved["index"] if e["id"] == "s1")["hints"]
        assert "NewHint" in s1_hints

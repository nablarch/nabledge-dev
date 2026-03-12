"""Findings round history tests for Phase D/E."""
import os
import json
import pytest
import sys

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(TOOL_DIR, "scripts"))

from conftest import make_mock_run_claude
from common import load_json, write_json


class TestPhaseDRoundOutput:
    """Phase D outputs findings with round number in filename."""

    def test_check_one_writes_round_file(self, ctx):
        """check_one writes {file_id}_r{N}.json, not {file_id}.json."""
        from phase_d_content_check import PhaseDContentCheck

        findings_output = {
            "file_id": "test-file",
            "status": "has_issues",
            "findings": [{"category": "fabrication", "severity": "critical",
                          "location": "s1", "description": "test"}]
        }
        mock = make_mock_run_claude(findings_output=findings_output)
        checker = PhaseDContentCheck(ctx, run_claude_fn=mock)
        checker.round_num = 1

        file_info = {
            "id": "test-file",
            "source_path": ".lw/nab-official/v6/nablarch-document/ja/test.rst",
            "output_path": "component/handlers/test-file.json",
            "format": "rst",
        }
        src = f"{ctx.repo}/{file_info['source_path']}"
        os.makedirs(os.path.dirname(src), exist_ok=True)
        with open(src, "w") as f:
            f.write("test source")
        kpath = f"{ctx.knowledge_cache_dir}/{file_info['output_path']}"
        os.makedirs(os.path.dirname(kpath), exist_ok=True)
        write_json(kpath, {"id": "test-file", "title": "Test", "index": [], "sections": {}})

        result = checker.check_one(file_info)

        round_path = f"{ctx.findings_dir}/test-file_r1.json"
        assert os.path.exists(round_path), f"Expected {round_path}"
        old_path = f"{ctx.findings_dir}/test-file.json"
        assert not os.path.exists(old_path), f"Old-style {old_path} should not exist"
        data = load_json(round_path)
        assert data["file_id"] == "test-file"
        assert data["status"] == "has_issues"

    def test_check_one_skips_if_round_file_exists(self, ctx):
        """check_one returns cached result if _r{N}.json already exists."""
        from phase_d_content_check import PhaseDContentCheck

        checker = PhaseDContentCheck(ctx, dry_run=True)
        checker.round_num = 2

        os.makedirs(ctx.findings_dir, exist_ok=True)
        cached = {"file_id": "cached-file", "status": "clean", "findings": []}
        write_json(f"{ctx.findings_dir}/cached-file_r2.json", cached)

        file_info = {"id": "cached-file", "source_path": "x", "output_path": "x", "format": "rst"}
        result = checker.check_one(file_info)
        assert result["status"] == "clean"

    def test_round_2_does_not_reuse_round_1(self, ctx):
        """Round 2 check creates new file even if round 1 exists."""
        from phase_d_content_check import PhaseDContentCheck

        findings_output = {
            "file_id": "multi-round",
            "status": "clean",
            "findings": []
        }
        mock = make_mock_run_claude(findings_output=findings_output)
        checker = PhaseDContentCheck(ctx, run_claude_fn=mock)
        checker.round_num = 2

        os.makedirs(ctx.findings_dir, exist_ok=True)
        write_json(f"{ctx.findings_dir}/multi-round_r1.json", {
            "file_id": "multi-round", "status": "has_issues",
            "findings": [{"category": "fabrication", "severity": "critical",
                          "location": "s1", "description": "old"}]
        })

        file_info = {
            "id": "multi-round",
            "source_path": ".lw/nab-official/v6/nablarch-document/ja/test.rst",
            "output_path": "component/handlers/multi-round.json",
            "format": "rst",
        }
        src = f"{ctx.repo}/{file_info['source_path']}"
        os.makedirs(os.path.dirname(src), exist_ok=True)
        with open(src, "w") as f:
            f.write("test")
        kpath = f"{ctx.knowledge_cache_dir}/{file_info['output_path']}"
        os.makedirs(os.path.dirname(kpath), exist_ok=True)
        write_json(kpath, {"id": "multi-round", "title": "T", "index": [], "sections": {}})

        result = checker.check_one(file_info)

        assert os.path.exists(f"{ctx.findings_dir}/multi-round_r1.json")
        assert os.path.exists(f"{ctx.findings_dir}/multi-round_r2.json")
        r1 = load_json(f"{ctx.findings_dir}/multi-round_r1.json")
        assert r1["status"] == "has_issues"


class TestPhaseEPreservesHistory:
    """Phase E reads round-specific findings and does NOT delete them."""

    def test_fix_one_reads_round_file(self, ctx):
        """fix_one reads {file_id}_r{N}.json."""
        from phase_e_fix import PhaseEFix

        fixed_output = {
            "id": "fix-target", "title": "T", "no_knowledge_content": False,
            "official_doc_urls": [], "index": [], "sections": {"s1": "fixed content here that is long enough"}
        }
        mock = make_mock_run_claude(fix_output=fixed_output)
        fixer = PhaseEFix(ctx, run_claude_fn=mock)
        fixer.round_num = 1

        os.makedirs(ctx.findings_dir, exist_ok=True)
        write_json(f"{ctx.findings_dir}/fix-target_r1.json", {
            "file_id": "fix-target", "status": "has_issues",
            "findings": [{"category": "omission", "severity": "critical",
                          "location": "s1", "description": "missing info"}]
        })

        file_info = {
            "id": "fix-target",
            "source_path": ".lw/nab-official/v6/nablarch-document/ja/test.rst",
            "output_path": "component/handlers/fix-target.json",
            "format": "rst",
        }
        src = f"{ctx.repo}/{file_info['source_path']}"
        os.makedirs(os.path.dirname(src), exist_ok=True)
        with open(src, "w") as f:
            f.write("source content")
        kpath = f"{ctx.knowledge_cache_dir}/{file_info['output_path']}"
        os.makedirs(os.path.dirname(kpath), exist_ok=True)
        write_json(kpath, {
            "id": "fix-target", "title": "T", "no_knowledge_content": False,
            "official_doc_urls": [], "index": [], "sections": {"s1": "original content here that is long enough"}
        })

        result = fixer.fix_one(file_info)
        assert result["status"] == "fixed"
        assert os.path.exists(f"{ctx.findings_dir}/fix-target_r1.json")

    def test_fix_one_skips_if_no_round_file(self, ctx):
        """fix_one returns skip if _r{N}.json does not exist."""
        from phase_e_fix import PhaseEFix

        fixer = PhaseEFix(ctx, dry_run=True)
        fixer.round_num = 1

        file_info = {"id": "no-findings", "source_path": "x", "output_path": "x", "format": "rst"}
        result = fixer.fix_one(file_info)
        assert result["status"] == "skip"


class TestCleanerRoundFiles:
    """Cleaner handles round-numbered findings files."""

    def test_list_d_artifacts_with_rounds(self, ctx):
        """list_d_artifacts finds _r{N}.json files for target."""
        from cleaner import list_d_artifacts

        os.makedirs(ctx.findings_dir, exist_ok=True)
        write_json(f"{ctx.findings_dir}/target_r1.json", {})
        write_json(f"{ctx.findings_dir}/target_r2.json", {})
        write_json(f"{ctx.findings_dir}/other_r1.json", {})

        result = list_d_artifacts(ctx, target_ids=["target"])
        assert len(result) == 2
        assert all("target_r" in p for p in result)

    def test_list_d_artifacts_returns_dir_when_no_target(self, ctx):
        """list_d_artifacts returns dir itself when target_ids is None."""
        from cleaner import list_d_artifacts

        os.makedirs(ctx.findings_dir, exist_ok=True)
        write_json(f"{ctx.findings_dir}/a_r1.json", {})

        result = list_d_artifacts(ctx, target_ids=None)
        assert len(result) == 1
        assert result[0] == ctx.findings_dir


class TestAggregateFindings:
    """_aggregate_findings collects findings for a specific round."""

    def test_aggregate_specific_round(self, ctx):
        """Aggregates only the specified round's findings."""
        os.makedirs(ctx.findings_dir, exist_ok=True)
        write_json(f"{ctx.findings_dir}/file-a_r1.json", {
            "file_id": "file-a", "status": "has_issues",
            "findings": [{"category": "fabrication", "severity": "critical",
                          "location": "s1", "description": "r1 finding"}]
        })
        write_json(f"{ctx.findings_dir}/file-a_r2.json", {
            "file_id": "file-a", "status": "clean", "findings": []
        })
        write_json(f"{ctx.findings_dir}/file-b_r1.json", {
            "file_id": "file-b", "status": "has_issues",
            "findings": [{"category": "omission", "severity": "minor",
                          "location": "s2", "description": "r1 finding"}]
        })

        sys.path.insert(0, os.path.join(TOOL_DIR, "scripts"))
        from run import _aggregate_findings
        result = _aggregate_findings(ctx, round_num=1)
        assert result["total"] == 2
        assert result["critical"] == 1
        assert result["minor"] == 1

        result2 = _aggregate_findings(ctx, round_num=2)
        assert result2["total"] == 0

    def test_aggregate_without_round_uses_latest(self, ctx):
        """Without round_num, aggregates latest round per file."""
        os.makedirs(ctx.findings_dir, exist_ok=True)
        # file-a: r1 has issues, r2 clean → latest is r2 (clean)
        write_json(f"{ctx.findings_dir}/file-a_r1.json", {
            "file_id": "file-a", "status": "has_issues",
            "findings": [{"category": "fabrication", "severity": "critical",
                          "location": "s1", "description": "old"}]
        })
        write_json(f"{ctx.findings_dir}/file-a_r2.json", {
            "file_id": "file-a", "status": "clean", "findings": []
        })
        # file-b: only r1 with issues → latest is r1
        write_json(f"{ctx.findings_dir}/file-b_r1.json", {
            "file_id": "file-b", "status": "has_issues",
            "findings": [{"category": "omission", "severity": "minor",
                          "location": "s2", "description": "still there"}]
        })

        from run import _aggregate_findings
        result = _aggregate_findings(ctx)
        # file-a r2 is clean (0 findings), file-b r1 has 1 finding → total 1
        assert result["total"] == 1
        assert result["minor"] == 1

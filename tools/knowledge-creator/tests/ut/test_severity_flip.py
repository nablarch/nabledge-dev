"""Phase D severity flip detection unit tests."""
import os
import json
import logging
import pytest
import sys

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(TOOL_DIR, "scripts"))

from common import write_json


class TestSeverityFlipDetection:

    def test_severity_flip_detection(self, ctx, caplog):
        """Same location+category with different severity across rounds → logged as warning."""
        from phase_d_content_check import PhaseDContentCheck

        os.makedirs(ctx.findings_dir, exist_ok=True)
        write_json(f"{ctx.findings_dir}/flip-test_r1.json", {
            "file_id": "flip-test", "status": "has_issues",
            "findings": [
                {"category": "omission", "severity": "critical",
                 "location": "s1", "description": "old finding"},
            ]
        })

        checker = PhaseDContentCheck(ctx)
        # Ensure propagation AFTER init (setup_logger resets it to False)
        logging.getLogger("knowledge_creator").propagate = True
        current = {
            "file_id": "flip-test", "status": "has_issues",
            "findings": [
                {"category": "omission", "severity": "minor",
                 "location": "s1", "description": "same location, flipped severity"},
            ]
        }
        prev_path = f"{ctx.findings_dir}/flip-test_r1.json"

        with caplog.at_level(logging.WARNING, logger="knowledge_creator"):
            checker._detect_severity_flips(current, prev_path)

        assert any(
            "flip" in r.message.lower() or "severity" in r.message.lower()
            for r in caplog.records
        )

    def test_no_flip_when_severity_same(self, ctx, caplog):
        """Same severity in both rounds → no warning."""
        from phase_d_content_check import PhaseDContentCheck

        os.makedirs(ctx.findings_dir, exist_ok=True)
        write_json(f"{ctx.findings_dir}/stable-test_r1.json", {
            "file_id": "stable-test", "status": "has_issues",
            "findings": [
                {"category": "fabrication", "severity": "critical",
                 "location": "s2", "description": "same"},
            ]
        })

        checker = PhaseDContentCheck(ctx)
        current = {
            "file_id": "stable-test", "status": "has_issues",
            "findings": [
                {"category": "fabrication", "severity": "critical",
                 "location": "s2", "description": "same content"},
            ]
        }
        prev_path = f"{ctx.findings_dir}/stable-test_r1.json"

        with caplog.at_level(logging.WARNING, logger="knowledge_creator"):
            checker._detect_severity_flips(current, prev_path)

        assert len(caplog.records) == 0

    def test_no_flip_when_prev_file_missing(self, ctx, caplog):
        """No warning when previous round file does not exist."""
        from phase_d_content_check import PhaseDContentCheck

        checker = PhaseDContentCheck(ctx)
        current = {
            "file_id": "new-file", "status": "has_issues",
            "findings": [
                {"category": "omission", "severity": "critical",
                 "location": "s1", "description": "first time"},
            ]
        }
        prev_path = f"{ctx.findings_dir}/nonexistent_r1.json"

        with caplog.at_level(logging.WARNING, logger="knowledge_creator"):
            checker._detect_severity_flips(current, prev_path)

        assert len(caplog.records) == 0

    def test_flip_detection_wired_in_check_one(self, ctx, caplog):
        """check_one calls flip detection for round >= 2."""
        from phase_d_content_check import PhaseDContentCheck
        import subprocess

        os.makedirs(ctx.findings_dir, exist_ok=True)
        # Round 1 findings: critical
        write_json(f"{ctx.findings_dir}/wire-test_r1.json", {
            "file_id": "wire-test", "status": "has_issues",
            "findings": [
                {"category": "omission", "severity": "critical",
                 "location": "s1", "description": "r1 finding"},
            ]
        })

        # Round 2 LLM output: same location but minor
        findings_r2 = {
            "file_id": "wire-test", "status": "has_issues",
            "findings": [
                {"category": "omission", "severity": "minor",
                 "location": "s1", "description": "r2 finding"},
            ]
        }

        def mock_fn(prompt, json_schema=None, log_dir=None, file_id=None, **kwargs):
            return subprocess.CompletedProcess(
                args=["claude"], returncode=0,
                stdout=json.dumps(findings_r2), stderr=""
            )

        checker = PhaseDContentCheck(ctx, run_claude_fn=mock_fn)
        checker.round_num = 2

        file_info = {
            "id": "wire-test",
            "source_path": ".lw/nab-official/v6/nablarch-document/ja/wire-test.rst",
            "output_path": "component/handlers/wire-test.json",
            "format": "rst",
        }
        src = f"{ctx.repo}/{file_info['source_path']}"
        os.makedirs(os.path.dirname(src), exist_ok=True)
        with open(src, "w") as f:
            f.write("source content")
        from common import write_json as wj
        kpath = f"{ctx.knowledge_cache_dir}/{file_info['output_path']}"
        os.makedirs(os.path.dirname(kpath), exist_ok=True)
        wj(kpath, {"id": "wire-test", "title": "T", "no_knowledge_content": False,
                   "official_doc_urls": [], "index": [], "sections": {"s1": "content"}})

        with caplog.at_level(logging.WARNING, logger="knowledge_creator"):
            checker.check_one(file_info)

        assert any(
            "flip" in r.message.lower() or "severity" in r.message.lower()
            for r in caplog.records
        )

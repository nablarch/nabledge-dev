"""Phase D severity lock and finding exclusion tests."""
import os
import json
import logging
import subprocess
import pytest
import sys

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(TOOL_DIR, "scripts"))

from common import write_json, load_json


class TestSeverityLock:

    def test_severity_locked_when_content_unchanged(self, ctx, caplog):
        """D-1: severity forced to prior round value when knowledge unchanged."""
        import hashlib
        from phase_d_content_check import PhaseDContentCheck

        os.makedirs(ctx.findings_dir, exist_ok=True)

        # Compute hash of the section content
        section_text = "content"
        section_hash = hashlib.sha256(section_text.encode()).hexdigest()

        write_json(f"{ctx.findings_dir}/lock-test_r1.json", {
            "file_id": "lock-test", "status": "has_issues",
            "findings": [
                {"category": "omission", "severity": "critical",
                 "location": "s1", "description": "r1 finding",
                 "_section_hash": section_hash},
            ]
        })

        findings_r2 = {
            "file_id": "lock-test", "status": "has_issues",
            "findings": [
                {"category": "omission", "severity": "minor",
                 "location": "s1", "description": "r2 flipped to minor",
                 "_section_hash": section_hash},
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
            "id": "lock-test",
            "source_path": ".lw/nab-official/v6/nablarch-document/ja/lock-test.rst",
            "output_path": "component/handlers/lock-test.json",
            "format": "rst",
        }
        src = f"{ctx.repo}/{file_info['source_path']}"
        os.makedirs(os.path.dirname(src), exist_ok=True)
        with open(src, "w") as f:
            f.write("source content")
        kpath = f"{ctx.knowledge_cache_dir}/{file_info['output_path']}"
        os.makedirs(os.path.dirname(kpath), exist_ok=True)
        write_json(kpath, {"id": "lock-test", "title": "T", "no_knowledge_content": False,
                   "official_doc_urls": [], "index": [], "sections": {"s1": "content"}})

        logging.getLogger("knowledge_creator").propagate = True
        with caplog.at_level(logging.WARNING, logger="knowledge_creator"):
            result = checker.check_one(file_info)

        assert result["findings"][0]["severity"] == "critical", (
            f"Expected 'critical' (locked) but got '{result['findings'][0]['severity']}'"
        )

    def test_severity_not_locked_when_content_changed(self, ctx):
        """New severity accepted when knowledge content was modified by Phase E."""
        from phase_d_content_check import PhaseDContentCheck

        os.makedirs(ctx.findings_dir, exist_ok=True)
        # r1: critical
        write_json(f"{ctx.findings_dir}/changed-test_r1.json", {
            "file_id": "changed-test", "status": "has_issues",
            "findings": [
                {"category": "omission", "severity": "critical",
                 "location": "s1", "description": "r1",
                 "_section_hash": "old_hash"},
            ]
        })

        findings_r2 = {
            "file_id": "changed-test", "status": "has_issues",
            "findings": [
                {"category": "omission", "severity": "minor",
                 "location": "s1", "description": "r2 minor after fix",
                 "_section_hash": "new_hash"},
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
            "id": "changed-test",
            "source_path": ".lw/nab-official/v6/nablarch-document/ja/changed-test.rst",
            "output_path": "component/handlers/changed-test.json",
            "format": "rst",
        }
        src = f"{ctx.repo}/{file_info['source_path']}"
        os.makedirs(os.path.dirname(src), exist_ok=True)
        with open(src, "w") as f:
            f.write("source content")
        kpath = f"{ctx.knowledge_cache_dir}/{file_info['output_path']}"
        os.makedirs(os.path.dirname(kpath), exist_ok=True)
        # Knowledge content is DIFFERENT from r1 (Phase E modified it)
        write_json(kpath, {"id": "changed-test", "title": "T", "no_knowledge_content": False,
                   "official_doc_urls": [], "index": [], "sections": {"s1": "MODIFIED content by Phase E"}})

        result = checker.check_one(file_info)

        # Severity should be the new value (minor) because content changed
        assert result["findings"][0]["severity"] == "minor"

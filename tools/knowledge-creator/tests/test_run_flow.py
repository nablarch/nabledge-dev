"""Tests for run.py pipeline flow with split files."""
import json
import os
import pytest
import subprocess
from common import load_json, write_json


class TestRunFlowWithSplitFiles:
    """Test that split files flow correctly through the pipeline."""

    def test_phase_b_no_longer_merges(self, ctx):
        """Phase B no longer merges split files."""
        from phase_b_generate import PhaseBGenerate

        # Mock run_claude
        def mock_run_claude(prompt, json_schema=None, log_dir=None, file_id=None, **kwargs):
            knowledge = {
                "id": file_id,
                "no_knowledge_content": False,
                "title": "Test",
                "official_doc_urls": ["https://example.com"],
                "index": [{"id": "section1", "title": "Section 1", "hints": ["s1"]}],
                "sections": {"section1": "Content for " + file_id}
            }
            return subprocess.CompletedProcess(
                args=["claude"], returncode=0,
                stdout=json.dumps({
                    "knowledge": knowledge,
                    "trace": {
                        "sections": [
                            {"section_id": "section1", "source_heading": "Section 1",
                             "heading_level": "h2", "h3_split": False,
                             "h3_split_reason": "Small section"}
                        ]
                    }
                }),
                stderr=""
            )

        # Setup: split file entries
        os.makedirs(f"{ctx.repo}/test", exist_ok=True)
        with open(f"{ctx.repo}/test/test.rst", "w") as f:
            f.write("Test\n====\n\nSection 1\n---------\nContent\n")

        classified = {
            "version": "6",
            "generated_at": "2026-01-01T00:00:00Z",
            "files": [
                {
                    "id": "test--section-1",
                    "source_path": "test/test.rst",
                    "format": "rst",
                    "filename": "test.rst",
                    "type": "component",
                    "category": "test",
                    "output_path": "component/test/test--section-1.json",
                    "assets_dir": "component/test/assets/test--section-1/",
                    "split_info": {
                        "is_split": True,
                        "original_id": "test",
                        "part": 1,
                        "total_parts": 2
                    },
                    "section_range": {
                        "start_line": 0,
                        "end_line": 10,
                        "sections": ["Section 1"]
                    }
                },
                {
                    "id": "test--section-2",
                    "source_path": "test/test.rst",
                    "format": "rst",
                    "filename": "test.rst",
                    "type": "component",
                    "category": "test",
                    "output_path": "component/test/test--section-2.json",
                    "assets_dir": "component/test/assets/test--section-2/",
                    "split_info": {
                        "is_split": True,
                        "original_id": "test",
                        "part": 2,
                        "total_parts": 2
                    },
                    "section_range": {
                        "start_line": 10,
                        "end_line": 20,
                        "sections": ["Section 2"]
                    }
                }
            ]
        }
        write_json(ctx.classified_list_path, classified)

        # Execute Phase B
        phase_b = PhaseBGenerate(ctx, run_claude_fn=mock_run_claude, dry_run=False)
        phase_b.run()

        # Verify: part files exist (NOT merged)
        assert os.path.exists(f"{ctx.knowledge_dir}/component/test/test--section-1.json")
        assert os.path.exists(f"{ctx.knowledge_dir}/component/test/test--section-2.json")

        # Verify: merged file does NOT exist
        assert not os.path.exists(f"{ctx.knowledge_dir}/component/test/test.json")

        # Verify: classified.json still has split entries
        updated = load_json(ctx.classified_list_path)
        ids = [f["id"] for f in updated["files"]]
        assert "test--section-1" in ids
        assert "test--section-2" in ids
        assert "test" not in ids

    def test_split_ids_pass_through_cde_loop(self, ctx):
        """Split file IDs pass through C -> D -> E loop correctly."""
        from phase_c_structure_check import PhaseCStructureCheck
        from phase_d_content_check import PhaseDContentCheck
        from phase_e_fix import PhaseEFix

        # Mock run_claude for Phase D (content check) and Phase E (fix)
        call_tracker = {"d": [], "e": [], "d_round": 1}

        def mock_run_claude(prompt, json_schema=None, log_dir=None, file_id=None, **kwargs):
            schema_str = json.dumps(json_schema) if json_schema else ""

            if "findings" in schema_str:
                # Phase D: content check
                call_tracker["d"].append(file_id)
                # Round 1: first file has issues, others clean
                # Round 2+: all clean
                if call_tracker["d_round"] == 1 and file_id == "test--section-1":
                    return subprocess.CompletedProcess(
                        args=["claude"], returncode=0,
                        stdout=json.dumps({
                            "file_id": file_id,
                            "status": "has_issues",
                            "findings": [
                                {"category": "omission", "severity": "minor",
                                 "location": "section1", "description": "test finding"}
                            ]
                        }),
                        stderr=""
                    )
                else:
                    return subprocess.CompletedProcess(
                        args=["claude"], returncode=0,
                        stdout=json.dumps({
                            "file_id": file_id,
                            "status": "clean",
                            "findings": []
                        }),
                        stderr=""
                    )
            else:
                # Phase E: fix
                call_tracker["e"].append(file_id)
                knowledge = load_json(f"{ctx.knowledge_dir}/component/test/{file_id}.json")
                # Return same knowledge (fixed)
                return subprocess.CompletedProcess(
                    args=["claude"], returncode=0,
                    stdout=json.dumps(knowledge),
                    stderr=""
                )

        # Setup: split files already generated
        part1 = {
            "id": "test--section-1",
            "no_knowledge_content": False,
            "title": "Test",
            "official_doc_urls": ["https://example.com"],
            "index": [{"id": "section1", "title": "Section 1", "hints": ["s1"]}],
            "sections": {"section1": "Content 1 with enough characters for validation"}
        }
        part2 = {
            "id": "test--section-2",
            "no_knowledge_content": False,
            "title": "Test",
            "official_doc_urls": ["https://example.com"],
            "index": [{"id": "section2", "title": "Section 2", "hints": ["s2"]}],
            "sections": {"section2": "Content 2 with enough characters for validation"}
        }

        os.makedirs(f"{ctx.knowledge_dir}/component/test", exist_ok=True)
        write_json(f"{ctx.knowledge_dir}/component/test/test--section-1.json", part1)
        write_json(f"{ctx.knowledge_dir}/component/test/test--section-2.json", part2)

        os.makedirs(f"{ctx.repo}/test", exist_ok=True)
        with open(f"{ctx.repo}/test/test.rst", "w") as f:
            f.write("Test\n====\n\nSection 1\n---------\nContent 1\n\nSection 2\n---------\nContent 2\n")

        classified = {
            "version": "6",
            "generated_at": "2026-01-01T00:00:00Z",
            "files": [
                {
                    "id": "test--section-1",
                    "source_path": "test/test.rst",
                    "format": "rst",
                    "filename": "test.rst",
                    "type": "component",
                    "category": "test",
                    "output_path": "component/test/test--section-1.json",
                    "assets_dir": "component/test/assets/test--section-1/",
                    "split_info": {
                        "is_split": True,
                        "original_id": "test",
                        "part": 1,
                        "total_parts": 2
                    },
                    "section_range": {
                        "start_line": 0,
                        "end_line": 7,
                        "sections": ["Section 1"]
                    }
                },
                {
                    "id": "test--section-2",
                    "source_path": "test/test.rst",
                    "format": "rst",
                    "filename": "test.rst",
                    "type": "component",
                    "category": "test",
                    "output_path": "component/test/test--section-2.json",
                    "assets_dir": "component/test/assets/test--section-2/",
                    "split_info": {
                        "is_split": True,
                        "original_id": "test",
                        "part": 2,
                        "total_parts": 2
                    },
                    "section_range": {
                        "start_line": 7,
                        "end_line": 15,
                        "sections": ["Section 2"]
                    }
                }
            ]
        }
        write_json(ctx.classified_list_path, classified)

        # Execute Phase C
        phase_c = PhaseCStructureCheck(ctx)
        c_result = phase_c.run()

        # Verify Phase C: both parts passed
        assert c_result["pass"] == 2
        assert "test--section-1" in c_result["pass_ids"]
        assert "test--section-2" in c_result["pass_ids"]

        # Execute Phase D (round 1: will find issues)
        phase_d = PhaseDContentCheck(ctx, run_claude_fn=mock_run_claude)
        d_result = phase_d.run(target_ids=c_result["pass_ids"])

        # Verify Phase D: both parts checked (only first has issues in mock)
        assert len(call_tracker["d"]) == 2
        assert "test--section-1" in call_tracker["d"]
        assert "test--section-2" in call_tracker["d"]

        # Execute Phase E: fix issues
        phase_e = PhaseEFix(ctx, run_claude_fn=mock_run_claude, dry_run=False)
        e_result = phase_e.run(target_ids=d_result["issue_file_ids"])

        # Verify Phase E: called for the file with issues
        assert len(call_tracker["e"]) >= 1

        # Execute Phase D (round 2: should be clean now)
        call_tracker["d"].clear()
        call_tracker["d_round"] = 2
        phase_d2 = PhaseDContentCheck(ctx, run_claude_fn=mock_run_claude)
        d_result2 = phase_d2.run(target_ids=c_result["pass_ids"])

        # Verify: all clean in round 2
        assert len(d_result2["issue_file_ids"]) == 0
        assert d_result2["issues_count"] == 0

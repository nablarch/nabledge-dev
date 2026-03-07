"""Tests for verification loop (D→E→C) with --max-rounds option."""
import pytest
import subprocess
import json
from phase_c_structure_check import PhaseCStructureCheck
from phase_d_content_check import PhaseDContentCheck
from phase_e_fix import PhaseEFix
from common import load_json, write_json


class TestVerificationLoopMultipleRounds:
    """Test D→E→C loop executes multiple times based on --max-rounds."""

    def test_two_rounds_until_clean(self, ctx):
        """Round 1: issues → Round 2: clean (max_rounds=2)"""
        # Set max_rounds
        ctx.max_rounds = 2

        # Create fixture source file
        import os
        source_path = f"{ctx.repo}/tests/fixtures/sample_source.rst"
        os.makedirs(os.path.dirname(source_path), exist_ok=True)
        with open(source_path, "w") as f:
            f.write("Test Source\n-----------\n\nContent here.")

        # Create classified.json with one file
        classified = {
            "files": [{
                "id": "test-file",
                "source_path": "tests/fixtures/sample_source.rst",
                "output_path": "component/handlers/test-file.json",
                "format": "rst",
                "type": "component",
                "category": "handlers"
            }]
        }
        write_json(ctx.classified_list_path, classified)

        # Track which rounds executed
        rounds_executed = []

        def mock_run_claude(prompt, json_schema=None, log_dir=None, file_id=None, **kwargs):
            schema_str = json.dumps(json_schema) if json_schema else ""

            if "findings" in schema_str:
                # Phase D: content check
                current_round = len(rounds_executed) + 1
                rounds_executed.append(current_round)

                if current_round == 1:
                    # Round 1: has issues
                    return subprocess.CompletedProcess(
                        args=["claude"], returncode=0,
                        stdout=json.dumps({
                            "file_id": file_id,
                            "status": "has_issues",
                            "findings": [{
                                "category": "omission",
                                "severity": "minor",
                                "location": "overview",
                                "description": "Missing detail"
                            }]
                        }),
                        stderr=""
                    )
                else:
                    # Round 2: clean
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
                knowledge = load_json(f"{ctx.knowledge_dir}/component/handlers/test-file.json")
                return subprocess.CompletedProcess(
                    args=["claude"], returncode=0,
                    stdout=json.dumps(knowledge),
                    stderr=""
                )

        # Create initial knowledge file
        knowledge = {
            "id": "test-file",
            "no_knowledge_content": False,
            "title": "Test",
            "official_doc_urls": ["https://example.com/test"],
            "index": [{"id": "overview", "title": "Overview", "hints": ["test"]}],
            "sections": {"overview": "This is test content with sufficient length for validation."}
        }
        write_json(f"{ctx.knowledge_dir}/component/handlers/test-file.json", knowledge)

        # Execute loop: C → D → E → C → D
        phase_c = PhaseCStructureCheck(ctx)
        phase_d = PhaseDContentCheck(ctx, run_claude_fn=mock_run_claude)
        phase_e = PhaseEFix(ctx, run_claude_fn=mock_run_claude)

        # Round 1
        c_result = phase_c.run()
        d_result = phase_d.run(target_ids=c_result["pass_ids"])
        assert len(d_result["issue_file_ids"]) == 1
        e_result = phase_e.run(target_ids=d_result["issue_file_ids"])

        # Round 2
        c_result2 = phase_c.run()
        d_result2 = phase_d.run(target_ids=c_result2["pass_ids"])
        assert len(d_result2["issue_file_ids"]) == 0  # Clean now

        # Verify 2 rounds executed
        assert len(rounds_executed) == 2
        assert rounds_executed == [1, 2]

    def test_max_rounds_limit_reached(self, ctx):
        """Issues remain after max_rounds → stop with warning"""
        ctx.max_rounds = 3

        # Create fixture source file
        import os
        source_path = f"{ctx.repo}/tests/fixtures/sample_source.rst"
        os.makedirs(os.path.dirname(source_path), exist_ok=True)
        with open(source_path, "w") as f:
            f.write("Test Source\n-----------\n\nContent here.")

        classified = {
            "files": [{
                "id": "test-file",
                "source_path": "tests/fixtures/sample_source.rst",
                "output_path": "component/handlers/test-file.json",
                "format": "rst",
                "type": "component",
                "category": "handlers"
            }]
        }
        write_json(ctx.classified_list_path, classified)

        rounds_executed = []

        def mock_run_claude(prompt, json_schema=None, log_dir=None, file_id=None, **kwargs):
            schema_str = json.dumps(json_schema) if json_schema else ""

            if "findings" in schema_str:
                current_round = len(rounds_executed) + 1
                rounds_executed.append(current_round)

                # All rounds: always has issues (never clean)
                return subprocess.CompletedProcess(
                    args=["claude"], returncode=0,
                    stdout=json.dumps({
                        "file_id": file_id,
                        "status": "has_issues",
                        "findings": [{
                            "category": "omission",
                            "severity": "minor",
                            "location": "overview",
                            "description": f"Issue in round {current_round}"
                        }]
                    }),
                    stderr=""
                )
            else:
                # Phase E: fix
                knowledge = load_json(f"{ctx.knowledge_dir}/component/handlers/test-file.json")
                return subprocess.CompletedProcess(
                    args=["claude"], returncode=0,
                    stdout=json.dumps(knowledge),
                    stderr=""
                )

        knowledge = {
            "id": "test-file",
            "no_knowledge_content": False,
            "title": "Test",
            "official_doc_urls": ["https://example.com/test"],
            "index": [{"id": "overview", "title": "Overview", "hints": ["test"]}],
            "sections": {"overview": "This is test content with sufficient length for validation."}
        }
        write_json(f"{ctx.knowledge_dir}/component/handlers/test-file.json", knowledge)

        phase_c = PhaseCStructureCheck(ctx)
        phase_d = PhaseDContentCheck(ctx, run_claude_fn=mock_run_claude)
        phase_e = PhaseEFix(ctx, run_claude_fn=mock_run_claude)

        # Execute max_rounds (3 rounds)
        for round_num in range(1, ctx.max_rounds + 1):
            c_result = phase_c.run()
            d_result = phase_d.run(target_ids=c_result["pass_ids"])

            if len(d_result["issue_file_ids"]) == 0:
                break  # Clean, stop early

            if round_num < ctx.max_rounds:
                # Not last round, execute fix
                e_result = phase_e.run(target_ids=d_result["issue_file_ids"])

        # Verify 3 rounds executed (max_rounds reached)
        assert len(rounds_executed) == 3
        assert rounds_executed == [1, 2, 3]

    def test_early_stop_when_clean(self, ctx):
        """Clean after round 1 → stop early (max_rounds=3 but only 1 used)"""
        ctx.max_rounds = 3

        # Create fixture source file
        import os
        source_path = f"{ctx.repo}/tests/fixtures/sample_source.rst"
        os.makedirs(os.path.dirname(source_path), exist_ok=True)
        with open(source_path, "w") as f:
            f.write("Test Source\n-----------\n\nContent here.")

        classified = {
            "files": [{
                "id": "test-file",
                "source_path": "tests/fixtures/sample_source.rst",
                "output_path": "component/handlers/test-file.json",
                "format": "rst",
                "type": "component",
                "category": "handlers"
            }]
        }
        write_json(ctx.classified_list_path, classified)

        rounds_executed = []

        def mock_run_claude(prompt, json_schema=None, log_dir=None, file_id=None, **kwargs):
            schema_str = json.dumps(json_schema) if json_schema else ""

            if "findings" in schema_str:
                current_round = len(rounds_executed) + 1
                rounds_executed.append(current_round)

                # Always clean
                return subprocess.CompletedProcess(
                    args=["claude"], returncode=0,
                    stdout=json.dumps({
                        "file_id": file_id,
                        "status": "clean",
                        "findings": []
                    }),
                    stderr=""
                )

        knowledge = {
            "id": "test-file",
            "no_knowledge_content": False,
            "title": "Test",
            "official_doc_urls": ["https://example.com/test"],
            "index": [{"id": "overview", "title": "Overview", "hints": ["test"]}],
            "sections": {"overview": "This is test content with sufficient length for validation."}
        }
        write_json(f"{ctx.knowledge_dir}/component/handlers/test-file.json", knowledge)

        phase_c = PhaseCStructureCheck(ctx)
        phase_d = PhaseDContentCheck(ctx, run_claude_fn=mock_run_claude)

        # Execute loop
        for round_num in range(1, ctx.max_rounds + 1):
            c_result = phase_c.run()
            d_result = phase_d.run(target_ids=c_result["pass_ids"])

            if len(d_result["issue_file_ids"]) == 0:
                break  # Clean, stop early

        # Verify only 1 round executed (early stop)
        assert len(rounds_executed) == 1
        assert rounds_executed == [1]

    def test_multiple_files_different_rounds(self, ctx):
        """Multiple files: file1 clean in round 1, file2 clean in round 2"""
        ctx.max_rounds = 2

        # Create fixture source file
        import os
        source_path = f"{ctx.repo}/tests/fixtures/sample_source.rst"
        os.makedirs(os.path.dirname(source_path), exist_ok=True)
        with open(source_path, "w") as f:
            f.write("Section 1\n---------\n\nContent here.")

        classified = {
            "files": [
                {
                    "id": "file-1",
                    "source_path": "tests/fixtures/sample_source.rst",
                    "output_path": "component/handlers/file-1.json",
                    "format": "rst",
                    "type": "component",
                    "category": "handlers"
                },
                {
                    "id": "file-2",
                    "source_path": "tests/fixtures/sample_source.rst",
                    "output_path": "component/handlers/file-2.json",
                    "format": "rst",
                    "type": "component",
                    "category": "handlers"
                }
            ]
        }
        write_json(ctx.classified_list_path, classified)

        d_calls = {"file-1": [], "file-2": []}

        def mock_run_claude(prompt, json_schema=None, log_dir=None, file_id=None, **kwargs):
            schema_str = json.dumps(json_schema) if json_schema else ""

            if "findings" in schema_str:
                # Track which round each file was checked
                current_round = max(len(d_calls[file_id]) + 1, 1)
                d_calls[file_id].append(current_round)

                # file-1: always clean
                # file-2: round 1 has issues, round 2 clean
                if file_id == "file-1":
                    return subprocess.CompletedProcess(
                        args=["claude"], returncode=0,
                        stdout=json.dumps({
                            "file_id": file_id,
                            "status": "clean",
                            "findings": []
                        }),
                        stderr=""
                    )
                else:  # file-2
                    if current_round == 1:
                        return subprocess.CompletedProcess(
                            args=["claude"], returncode=0,
                            stdout=json.dumps({
                                "file_id": file_id,
                                "status": "has_issues",
                                "findings": [{
                                    "category": "omission",
                                    "severity": "minor",
                                    "location": "section1",
                                    "description": "Issue"
                                }]
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
                knowledge = load_json(f"{ctx.knowledge_dir}/component/handlers/{file_id}.json")
                return subprocess.CompletedProcess(
                    args=["claude"], returncode=0,
                    stdout=json.dumps(knowledge),
                    stderr=""
                )

        # Create knowledge files
        for file_id in ["file-1", "file-2"]:
            knowledge = {
                "id": file_id,
                "no_knowledge_content": False,
                "title": "Test",
                "official_doc_urls": ["https://example.com/test"],
                "index": [{"id": "section1", "title": "Section", "hints": ["test"]}],
                "sections": {"section1": "This is test content with sufficient length for validation."}
            }
            write_json(f"{ctx.knowledge_dir}/component/handlers/{file_id}.json", knowledge)

        phase_c = PhaseCStructureCheck(ctx)
        phase_d = PhaseDContentCheck(ctx, run_claude_fn=mock_run_claude)
        phase_e = PhaseEFix(ctx, run_claude_fn=mock_run_claude)

        # Round 1
        c_result = phase_c.run()
        d_result = phase_d.run(target_ids=c_result["pass_ids"])
        assert len(d_result["issue_file_ids"]) == 1  # file-2 has issues
        assert "file-2" in d_result["issue_file_ids"]
        e_result = phase_e.run(target_ids=d_result["issue_file_ids"])

        # Round 2
        c_result2 = phase_c.run()
        d_result2 = phase_d.run(target_ids=c_result2["pass_ids"])
        assert len(d_result2["issue_file_ids"]) == 0  # All clean

        # Verify call counts
        # file-1: checked once (clean in round 1, never fixed, no need to re-check)
        # file-2: checked twice (issues in round 1, fixed, then checked again in round 2)
        assert len(d_calls["file-1"]) == 1
        assert len(d_calls["file-2"]) == 2

"""Tests for split file validation through Phase C/D/E."""
import json
import os
import pytest
import subprocess
from steps.common import load_json, write_json


class TestSplitFileStructureCheck:
    """Test Phase C with split files."""

    def test_split_file_passes_structure_check(self, ctx, mock_claude):
        """Split file with split_info passes Phase C."""
        from steps.phase_c_structure_check import PhaseCStructureCheck

        # Setup: split file entry
        knowledge = {
            "id": "libraries-tag--overview",
            "no_knowledge_content": False,
            "title": "タグライブラリ",
            "official_doc_urls": ["https://example.com/tag.html"],
            "index": [
                {"id": "overview", "title": "概要", "hints": ["tag"]}
            ],
            "sections": {
                "overview": "タグライブラリの概要です。JSPファイルで使用します。"
            }
        }

        source_content = """.. _tag-label:

タグライブラリ
==========================================

概要
-----

タグライブラリの概要。
"""

        os.makedirs(f"{ctx.knowledge_dir}/component/libraries", exist_ok=True)
        write_json(f"{ctx.knowledge_dir}/component/libraries/libraries-tag--overview.json", knowledge)

        os.makedirs(f"{ctx.repo}/test", exist_ok=True)
        with open(f"{ctx.repo}/test/tag.rst", "w", encoding="utf-8") as f:
            f.write(source_content)

        classified = {
            "version": "6",
            "generated_at": "2026-01-01T00:00:00Z",
            "files": [
                {
                    "id": "libraries-tag--overview",
                    "source_path": "test/tag.rst",
                    "format": "rst",
                    "filename": "tag.rst",
                    "type": "component",
                    "category": "libraries",
                    "output_path": "component/libraries/libraries-tag--overview.json",
                    "assets_dir": "component/libraries/assets/libraries-tag--overview/",
                    "split_info": {
                        "is_split": True,
                        "original_id": "libraries-tag",
                        "part": 1,
                        "total_parts": 2
                    },
                    "section_range": {
                        "start_line": 0,
                        "end_line": 30,
                        "sections": ["概要"]
                    }
                }
            ]
        }
        write_json(ctx.classified_list_path, classified)

        # Execute
        phase_c = PhaseCStructureCheck(ctx)
        result = phase_c.run()

        # Verify: passes without error
        assert result["error"] == 0
        assert "libraries-tag--overview" in result["pass_ids"]

    def test_split_file_s9_uses_section_range(self, ctx, mock_claude):
        """S9 check uses section_range instead of full source."""
        from steps.phase_c_structure_check import PhaseCStructureCheck

        # Setup: source has 4 h2 sections, but part 1 only has 2
        knowledge = {
            "id": "test--section-1",
            "no_knowledge_content": False,
            "title": "Test",
            "official_doc_urls": ["https://example.com/test.html"],
            "index": [
                {"id": "section1", "title": "Section 1", "hints": ["s1"]},
                {"id": "section2", "title": "Section 2", "hints": ["s2"]}
            ],
            "sections": {
                "section1": "Content 1 - Test section with enough characters",
                "section2": "Content 2 - Test section with enough characters"
            }
        }

        # Source has 4 h2 headings
        source_content = """Test
====

Section 1
---------
Content 1

Section 2
---------
Content 2

Section 3
---------
Content 3

Section 4
---------
Content 4
"""

        os.makedirs(f"{ctx.knowledge_dir}/component/test", exist_ok=True)
        write_json(f"{ctx.knowledge_dir}/component/test/test--section-1.json", knowledge)

        os.makedirs(f"{ctx.repo}/test", exist_ok=True)
        with open(f"{ctx.repo}/test/test.rst", "w", encoding="utf-8") as f:
            f.write(source_content)

        # Case 1: WITH section_range - should pass
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
                    "section_range": {
                        "start_line": 0,
                        "end_line": 50,
                        "sections": ["Section 1", "Section 2"]
                    }
                }
            ]
        }
        write_json(ctx.classified_list_path, classified)

        phase_c = PhaseCStructureCheck(ctx)
        result = phase_c.run()

        # Should pass: expected=2 (from section_range), actual=2
        assert result["error"] == 0
        assert "test--section-1" in result["pass_ids"]

        # Case 2: WITHOUT section_range - should fail S9
        classified["files"][0].pop("section_range")
        write_json(ctx.classified_list_path, classified)

        result = phase_c.run()

        # Should fail: expected=4 (from source), actual=2
        assert result["error"] == 1
        assert "test--section-1" not in result["pass_ids"]


class TestSplitFileContentCheck:
    """Test Phase D with split files."""

    def test_split_file_content_check_uses_section_range(self, ctx):
        """Phase D uses section_range to extract source."""
        from steps.phase_d_content_check import PhaseDContentCheck

        # Mock run_claude that captures the prompt
        captured_prompt = []

        def mock_run_claude(prompt, json_schema=None, log_dir=None, file_id=None, **kwargs):
            captured_prompt.append(prompt)
            return subprocess.CompletedProcess(
                args=["claude"], returncode=0,
                stdout=json.dumps({
                    "file_id": file_id,
                    "status": "clean",
                    "findings": []
                }),
                stderr=""
            )

        # Setup: split file with section_range
        knowledge = {
            "id": "test--section-1",
            "no_knowledge_content": False,
            "title": "Test",
            "official_doc_urls": ["https://example.com"],
            "index": [{"id": "section1", "title": "Section 1", "hints": ["s1"]}],
            "sections": {"section1": "Content 1 - Test section with enough characters for S13"}
        }

        source_content = """Test
====

Section 1
---------
Content 1

Section 2
---------
Content 2 (should NOT be in prompt)
"""

        os.makedirs(f"{ctx.knowledge_dir}/component/test", exist_ok=True)
        write_json(f"{ctx.knowledge_dir}/component/test/test--section-1.json", knowledge)

        os.makedirs(f"{ctx.repo}/test", exist_ok=True)
        with open(f"{ctx.repo}/test/test.rst", "w", encoding="utf-8") as f:
            f.write(source_content)

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
                    "section_range": {
                        "start_line": 0,
                        "end_line": 7,  # Only includes Section 1 (lines 0-6)
                        "sections": ["Section 1"]
                    }
                }
            ]
        }
        write_json(ctx.classified_list_path, classified)

        # Execute
        phase_d = PhaseDContentCheck(ctx, run_claude_fn=mock_run_claude)
        phase_d.check_one(classified["files"][0])

        # Verify: prompt contains only Section 1, not Section 2
        assert len(captured_prompt) == 1
        prompt_text = captured_prompt[0]
        assert "Section 1" in prompt_text
        assert "Content 1" in prompt_text
        assert "Section 2" not in prompt_text
        assert "should NOT be in prompt" not in prompt_text


class TestSplitFileFix:
    """Test Phase E with split files."""

    def test_split_file_fix_uses_section_range(self, ctx):
        """Phase E uses section_range to extract source."""
        from steps.phase_e_fix import PhaseEFix

        # Mock run_claude that captures the prompt
        captured_prompt = []

        def mock_run_claude(prompt, json_schema=None, log_dir=None, file_id=None, **kwargs):
            captured_prompt.append(prompt)
            # Return fixed knowledge
            fixed = {
                "id": "test--section-1",
                "title": "Test Fixed",
                "official_doc_urls": ["https://example.com"],
                "index": [{"id": "section1", "title": "Section 1", "hints": ["s1", "fixed"]}],
                "sections": {"section1": "Content 1 - Fixed with enough characters for validation"}
            }
            return subprocess.CompletedProcess(
                args=["claude"], returncode=0,
                stdout=json.dumps(fixed),
                stderr=""
            )

        # Setup: split file with issues
        knowledge = {
            "id": "test--section-1",
            "no_knowledge_content": False,
            "title": "Test",
            "official_doc_urls": ["https://example.com"],
            "index": [{"id": "section1", "title": "Section 1", "hints": ["s1"]}],
            "sections": {"section1": "Content 1 - Test section with enough characters for S13"}
        }

        source_content = """Test
====

Section 1
---------
Content 1

Section 2
---------
Content 2 (should NOT be in prompt)
"""

        os.makedirs(f"{ctx.knowledge_dir}/component/test", exist_ok=True)
        write_json(f"{ctx.knowledge_dir}/component/test/test--section-1.json", knowledge)

        os.makedirs(f"{ctx.repo}/test", exist_ok=True)
        with open(f"{ctx.repo}/test/test.rst", "w", encoding="utf-8") as f:
            f.write(source_content)

        os.makedirs(f"{ctx.findings_dir}", exist_ok=True)
        findings = {
            "file_id": "test--section-1",
            "status": "has_issues",
            "findings": [
                {"category": "omission", "severity": "minor", "location": "section1", "description": "test finding"}
            ]
        }
        write_json(f"{ctx.findings_dir}/test--section-1.json", findings)

        file_info = {
            "id": "test--section-1",
            "source_path": "test/test.rst",
            "format": "rst",
            "filename": "test.rst",
            "type": "component",
            "category": "test",
            "output_path": "component/test/test--section-1.json",
            "assets_dir": "component/test/assets/test--section-1/",
            "section_range": {
                "start_line": 0,
                "end_line": 7,  # Only Section 1 (lines 0-6)
                "sections": ["Section 1"]
            }
        }

        # Execute
        phase_e = PhaseEFix(ctx, run_claude_fn=mock_run_claude)
        phase_e.fix_one(file_info)

        # Verify: prompt contains only Section 1
        assert len(captured_prompt) == 1
        prompt_text = captured_prompt[0]
        assert "Section 1" in prompt_text
        assert "Content 1" in prompt_text
        assert "Section 2" not in prompt_text
        assert "should NOT be in prompt" not in prompt_text

    def test_fix_rejects_drastically_shrunk_output(self, ctx):
        """Phase E rejects output that shrunk to < 50%."""
        from steps.phase_e_fix import PhaseEFix

        # Mock that returns drastically shrunk output (5% of original)
        def mock_run_claude(prompt, json_schema=None, log_dir=None, file_id=None, **kwargs):
            shrunk = {
                "id": "test--section-1",
                "title": "Test",
                "official_doc_urls": ["https://example.com"],
                "index": [{"id": "s1", "title": "S1", "hints": []}],
                "sections": {"s1": "X" * 500}  # Only 500 chars vs 10000 in input
            }
            return subprocess.CompletedProcess(
                args=["claude"], returncode=0,
                stdout=json.dumps(shrunk),
                stderr=""
            )

        # Setup: large input (10 sections, 10000 chars)
        sections = {f"section{i}": "Content " * 100 for i in range(1, 11)}  # ~1000 chars each
        knowledge = {
            "id": "test--section-1",
            "no_knowledge_content": False,
            "title": "Test",
            "official_doc_urls": ["https://example.com"],
            "index": [{"id": f"section{i}", "title": f"Section {i}", "hints": []} for i in range(1, 11)],
            "sections": sections
        }

        os.makedirs(f"{ctx.knowledge_dir}/component/test", exist_ok=True)
        write_json(f"{ctx.knowledge_dir}/component/test/test--section-1.json", knowledge)

        os.makedirs(f"{ctx.repo}/test", exist_ok=True)
        with open(f"{ctx.repo}/test/test.rst", "w", encoding="utf-8") as f:
            f.write("Test source")

        os.makedirs(f"{ctx.findings_dir}", exist_ok=True)
        findings = {
            "file_id": "test--section-1",
            "status": "has_issues",
            "findings": [{"category": "omission", "severity": "minor", "location": "section1", "description": "test"}]
        }
        write_json(f"{ctx.findings_dir}/test--section-1.json", findings)

        file_info = {
            "id": "test--section-1",
            "source_path": "test/test.rst",
            "format": "rst",
            "filename": "test.rst",
            "type": "component",
            "category": "test",
            "output_path": "component/test/test--section-1.json",
            "assets_dir": "component/test/assets/test--section-1/"
        }

        # Execute
        phase_e = PhaseEFix(ctx, run_claude_fn=mock_run_claude, dry_run=False)
        result = phase_e.fix_one(file_info)

        # Verify: rejected with error
        assert result["status"] == "error"
        assert "Output too small" in result["error"]

        # Verify: original file NOT overwritten
        unchanged = load_json(f"{ctx.knowledge_dir}/component/test/test--section-1.json")
        assert len(unchanged["sections"]) == 10  # Original 10 sections preserved

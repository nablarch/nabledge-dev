"""End-to-end tests for split-aware pipeline."""
import json
import os
import pytest
import subprocess
from common import load_json, write_json


class TestE2ESplitPipeline:
    """Test full pipeline flow with split files."""

    def test_full_pipeline_split_to_final(self, ctx):
        """Full pipeline: Phase B → C → D(clean) → M with split files."""
        from phase_b_generate import PhaseBGenerate
        from phase_c_structure_check import PhaseCStructureCheck
        from phase_d_content_check import PhaseDContentCheck
        from phase_m_finalize import PhaseMFinalize

        # Mock run_claude for Phase B, D, and F
        def mock_run_claude(prompt, json_schema=None, log_dir=None, file_id=None, **kwargs):
            schema_str = json.dumps(json_schema) if json_schema else ""

            if "trace" in schema_str:
                # Phase B: generate knowledge (now both sections in one file)
                knowledge = {
                    "id": file_id,
                    "no_knowledge_content": False,
                    "title": "Test Title",
                    "official_doc_urls": ["https://example.com/test.html"],
                    "processing_patterns": ["nablarch-batch"],
                    "index": [
                        {"id": "section1", "title": "Section 1",
                         "hints": ["hint1", "test"]},
                        {"id": "section2", "title": "Section 2",
                         "hints": ["hint2", "test"]}
                    ],
                    "sections": {
                        "section1": "Content for section 1 with enough characters for validation.",
                        "section2": "Content for section 2 with enough characters for validation."
                    }
                }
                return subprocess.CompletedProcess(
                    args=["claude"], returncode=0,
                    stdout=json.dumps({
                        "knowledge": knowledge,
                        "trace": {
                            "file_id": file_id,
                            "generated_at": "2026-01-01T00:00:00Z",
                            "internal_labels": ["section1", "section2", "test"],
                            "sections": [
                                {"section_id": "section1",
                                 "source_heading": "Section 1",
                                 "heading_level": "h2", "h3_split": False,
                                 "h3_split_reason": "Small section"},
                                {"section_id": "section2",
                                 "source_heading": "Section 2",
                                 "heading_level": "h2", "h3_split": False,
                                 "h3_split_reason": "Small section"}
                            ]
                        }
                    }),
                    stderr=""
                )
            elif "findings" in schema_str:
                # Phase D: content check - all clean
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
                raise ValueError(f"Unexpected schema: {schema_str}")

        # Setup: 1-part split classified.json (both sections grouped under 400 lines)
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
                        "total_parts": 1,
                        "group_line_count": 11
                    },
                    "section_range": {
                        "start_line": 0,
                        "end_line": 11,
                        "sections": ["Section 1", "Section 2"]
                    }
                }
            ]
        }
        write_json(ctx.classified_list_path, classified)

        # Execute Phase B: generate
        phase_b = PhaseBGenerate(ctx, run_claude_fn=mock_run_claude, dry_run=False)
        phase_b.run()

        # Execute Phase C: structure check
        phase_c = PhaseCStructureCheck(ctx)
        c_result = phase_c.run()
        assert c_result["pass"] == 1

        # Execute Phase D: content check (all clean)
        phase_d = PhaseDContentCheck(ctx, run_claude_fn=mock_run_claude)
        d_result = phase_d.run(target_ids=c_result["pass_ids"])
        assert d_result["issues_count"] == 0

        # Execute Phase M: finalize (merge + resolve + docs)
        phase_m = PhaseMFinalize(ctx, dry_run=False, run_claude_fn=mock_run_claude)
        phase_m.run()

        # Verify 1: Merged knowledge JSON exists and is correct
        merged_path = f"{ctx.knowledge_dir}/component/test/test.json"
        assert os.path.exists(merged_path), "Merged knowledge file should exist"

        merged = load_json(merged_path)
        assert merged["id"] == "test", "Merged file should have original_id"
        assert len(merged["index"]) == 2, "Should have both sections in index"
        assert len(merged["sections"]) == 2, "Should have both sections"
        assert "section1" in merged["sections"]
        assert "section2" in merged["sections"]
        assert "Content for section 1" in merged["sections"]["section1"]
        assert "Content for section 2" in merged["sections"]["section2"]

        # Verify 2: Part file deleted
        assert not os.path.exists(f"{ctx.knowledge_dir}/component/test/test--section-1.json"), \
            "Part file test--section-1.json should be deleted after merge"

        # Verify 3: classified.json restored to split state after Phase M
        updated = load_json(ctx.classified_list_path)
        ids = [f["id"] for f in updated["files"]]
        assert "test--section-1" in ids, "Split file ID should remain in classified.json"

        # Verify 4: Resolved version exists
        resolved_path = f"{ctx.knowledge_resolved_dir}/component/test/test.json"
        assert os.path.exists(resolved_path), "Resolved knowledge file should exist"

        # Verify 5: Browsable MD exists
        md_path = f"{ctx.docs_dir}/component/test/test.md"
        assert os.path.exists(md_path), "Browsable MD file should exist"

        # Verify 6: index.toon contains correct entry
        index_path = f"{ctx.knowledge_dir}/index.toon"
        assert os.path.exists(index_path), "index.toon should exist"
        with open(index_path, "r", encoding="utf-8") as f:
            index_content = f.read()
        assert "test.json" in index_content, "index.toon should reference merged file"
        assert "test--section-1.json" not in index_content, "index.toon should not reference part file"
        assert "nablarch-batch" in index_content, "index.toon should contain classified patterns"

    def test_full_pipeline_split_with_fix_cycle(self, ctx):
        """Full pipeline with fix cycle: B → C → D(issues) → E(fix) → C → D(clean) → M."""
        from phase_b_generate import PhaseBGenerate
        from phase_c_structure_check import PhaseCStructureCheck
        from phase_d_content_check import PhaseDContentCheck
        from phase_e_fix import PhaseEFix
        from phase_m_finalize import PhaseMFinalize

        # Use stateful mock to control Phase D responses per round
        def make_stateful_mock():
            """Phase D responses change based on call count."""
            call_count = {"d": 0}

            def mock_fn(prompt, json_schema=None, log_dir=None, file_id=None, **kwargs):
                schema_str = json.dumps(json_schema) if json_schema else ""

                if "findings" in schema_str:
                    # Phase D: content check
                    call_count["d"] += 1
                    if call_count["d"] <= 1:  # Round 1: 1 part file has issues
                        return subprocess.CompletedProcess(
                            args=["claude"], returncode=0,
                            stdout=json.dumps({
                                "file_id": file_id,
                                "status": "has_issues",
                                "findings": [
                                    {"category": "omission", "severity": "minor",
                                     "location": "overview", "description": "Missing important detail"}
                                ]
                            }),
                            stderr=""
                        )
                    else:  # Round 2: all clean after fix
                        return subprocess.CompletedProcess(
                            args=["claude"], returncode=0,
                            stdout=json.dumps({
                                "file_id": file_id,
                                "status": "clean",
                                "findings": []
                            }),
                            stderr=""
                        )
                elif "trace" in schema_str:
                    # Phase B: generate knowledge (both sections in one file)
                    knowledge = {
                        "id": file_id,
                        "no_knowledge_content": False,
                        "title": "Test Title",
                        "official_doc_urls": ["https://example.com/test.html"],
                        "processing_patterns": [],
                        "index": [
                            {"id": "section1", "title": "Section 1",
                             "hints": ["hint1", "test"]},
                            {"id": "section2", "title": "Section 2",
                             "hints": ["hint2", "test"]}
                        ],
                        "sections": {
                            "section1": "Content for section 1 with enough characters.",
                            "section2": "Content for section 2 with enough characters."
                        }
                    }
                    return subprocess.CompletedProcess(
                        args=["claude"], returncode=0,
                        stdout=json.dumps({
                            "knowledge": knowledge,
                            "trace": {
                                "file_id": file_id,
                                "generated_at": "2026-01-01T00:00:00Z",
                                "internal_labels": ["section1", "section2", "test"],
                                "sections": [
                                    {"section_id": "section1",
                                     "source_heading": "Section 1",
                                     "heading_level": "h2", "h3_split": False,
                                     "h3_split_reason": "Small"},
                                    {"section_id": "section2",
                                     "source_heading": "Section 2",
                                     "heading_level": "h2", "h3_split": False,
                                     "h3_split_reason": "Small"}
                                ]
                            }
                        }),
                        stderr=""
                    )
                else:
                    # Phase E: fix - return fixed knowledge (add FIXED marker)
                    knowledge = load_json(f"{ctx.knowledge_cache_dir}/component/test/{file_id}.json")
                    # Preserve all sections and index (critical for regression prevention)
                    for section_id in knowledge["sections"]:
                        knowledge["sections"][section_id] += " FIXED"
                    return subprocess.CompletedProcess(
                        args=["claude"], returncode=0,
                        stdout=json.dumps(knowledge),
                        stderr=""
                    )

            return mock_fn

        mock_fn = make_stateful_mock()

        # Setup: 1-part split classified.json (both sections grouped under 400 lines)
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
                        "total_parts": 1,
                        "group_line_count": 11
                    },
                    "section_range": {
                        "start_line": 0,
                        "end_line": 11,
                        "sections": ["Section 1", "Section 2"]
                    }
                }
            ]
        }
        write_json(ctx.classified_list_path, classified)

        # Execute Phase B: generate
        phase_b = PhaseBGenerate(ctx, run_claude_fn=mock_fn, dry_run=False)
        phase_b.run()

        # Execute Phase C: structure check (round 1)
        phase_c = PhaseCStructureCheck(ctx)
        c_result = phase_c.run()
        assert c_result["pass"] == 1

        # Execute Phase D: content check (round 1 - has issues)
        phase_d = PhaseDContentCheck(ctx, run_claude_fn=mock_fn)
        d_result1 = phase_d.run(target_ids=c_result["pass_ids"])
        assert d_result1["issues_count"] > 0, "Should find issues in round 1"
        assert len(d_result1["issue_file_ids"]) == 1, "Single part should have issues"

        # Execute Phase E: fix
        phase_e = PhaseEFix(ctx, run_claude_fn=mock_fn, dry_run=False)
        e_result = phase_e.run(target_ids=d_result1["issue_file_ids"])

        # Verify: Fixed file has FIXED marker and preserves all sections
        for file_id in d_result1["issue_file_ids"]:
            fixed = load_json(f"{ctx.knowledge_cache_dir}/component/test/{file_id}.json")

            # Critical: both sections should still exist (regression prevention)
            assert "section1" in fixed["sections"], \
                "Section 1 should be preserved after fix"
            assert "section2" in fixed["sections"], \
                "Section 2 should be preserved after fix"
            assert "FIXED" in fixed["sections"]["section1"], \
                "Fixed marker should be present in section1"
            assert "FIXED" in fixed["sections"]["section2"], \
                "Fixed marker should be present in section2"

            # Critical: index should still exist with both entries
            assert len(fixed["index"]) == 2, "Index should have both entries after fix"
            assert any(item["id"] == "section1" for item in fixed["index"]), \
                "Section 1 should be in index after fix"
            assert any(item["id"] == "section2" for item in fixed["index"]), \
                "Section 2 should be in index after fix"

        # Execute Phase C again (round 2)
        phase_c2 = PhaseCStructureCheck(ctx)
        c_result2 = phase_c2.run()
        assert c_result2["pass"] == 1, "Should still pass structure check after fix"

        # Execute Phase D: content check (round 2 - all clean)
        phase_d2 = PhaseDContentCheck(ctx, run_claude_fn=mock_fn)
        d_result2 = phase_d2.run(target_ids=c_result2["pass_ids"])
        assert d_result2["issues_count"] == 0, "Should be clean in round 2"

        # Execute Phase M: finalize
        phase_m = PhaseMFinalize(ctx, dry_run=False, run_claude_fn=mock_fn)
        phase_m.run()

        # Verify: Final merged file has all sections preserved (critical)
        merged_path = f"{ctx.knowledge_dir}/component/test/test.json"
        assert os.path.exists(merged_path)

        merged = load_json(merged_path)
        assert merged["id"] == "test"
        assert len(merged["sections"]) == 2, "All sections should be preserved in merge"
        assert "section1" in merged["sections"], "Section 1 should be preserved"
        assert "section2" in merged["sections"], "Section 2 should be preserved"
        assert "FIXED" in merged["sections"]["section1"], "Fixed content should be in merged file"
        assert "FIXED" in merged["sections"]["section2"], "Fixed content should be in merged file"

        # Verify: Index preserved
        assert len(merged["index"]) == 2, "All index entries should be preserved"

    def test_mixed_split_and_nonsplit(self, ctx):
        """Mixed pipeline: split files + non-split files."""
        from phase_b_generate import PhaseBGenerate
        from phase_c_structure_check import PhaseCStructureCheck
        from phase_d_content_check import PhaseDContentCheck
        from phase_m_finalize import PhaseMFinalize

        # Mock run_claude
        def mock_run_claude(prompt, json_schema=None, log_dir=None, file_id=None, **kwargs):
            schema_str = json.dumps(json_schema) if json_schema else ""

            if "trace" in schema_str:
                # Phase B: generate knowledge
                if file_id.startswith("split"):
                    # Split file with both sections grouped
                    knowledge = {
                        "id": file_id,
                        "no_knowledge_content": False,
                        "title": "Split Title",
                        "official_doc_urls": ["https://example.com/split.html"],
                        "index": [
                            {"id": "section1", "title": "Section 1",
                             "hints": ["hint1"]},
                            {"id": "section2", "title": "Section 2",
                             "hints": ["hint2"]}
                        ],
                        "sections": {
                            "section1": "Split content 1 with enough characters.",
                            "section2": "Split content 2 with enough characters."
                        }
                    }
                else:
                    # Non-split file
                    knowledge = {
                        "id": file_id,
                        "no_knowledge_content": False,
                        "title": "Regular Title",
                        "official_doc_urls": ["https://example.com/regular.html"],
                        "index": [
                            {"id": "regular-section", "title": "Regular Section",
                             "hints": ["regular"]}
                        ],
                        "sections": {
                            "regular-section": "Regular content with enough characters for validation."
                        }
                    }

                return subprocess.CompletedProcess(
                    args=["claude"], returncode=0,
                    stdout=json.dumps({
                        "knowledge": knowledge,
                        "trace": {
                            "file_id": file_id,
                            "generated_at": "2026-01-01T00:00:00Z",
                            "internal_labels": list(knowledge["sections"].keys()),
                            "sections": [
                                {"section_id": sid, "source_heading": knowledge["index"][0]["title"],
                                 "heading_level": "h2", "h3_split": False,
                                 "h3_split_reason": "Small"}
                                for sid in knowledge["sections"].keys()
                            ]
                        }
                    }),
                    stderr=""
                )
            elif "findings" in schema_str:
                # Phase D: all clean
                return subprocess.CompletedProcess(
                    args=["claude"], returncode=0,
                    stdout=json.dumps({
                        "file_id": file_id,
                        "status": "clean",
                        "findings": []
                    }),
                    stderr=""
                )
            elif "patterns" in schema_str:
                # Phase F: pattern classification
                return subprocess.CompletedProcess(
                    args=["claude"], returncode=0,
                    stdout=json.dumps({
                        "patterns": ["nablarch-batch"],
                        "reasoning": [{"pattern": "nablarch-batch", "matched": True, "evidence": "test"}]
                    }),
                    stderr=""
                )
            else:
                raise ValueError(f"Unexpected schema: {schema_str}")

        # Setup: mix of split and non-split files (split has both sections grouped)
        os.makedirs(f"{ctx.repo}/test", exist_ok=True)
        with open(f"{ctx.repo}/test/split.rst", "w") as f:
            f.write("Split\n=====\n\nSection 1\n---------\nContent 1\n\nSection 2\n---------\nContent 2\n")
        with open(f"{ctx.repo}/test/regular.rst", "w") as f:
            f.write("Regular\n=======\n\nContent\n-------\nRegular content\n")

        classified = {
            "version": "6",
            "generated_at": "2026-01-01T00:00:00Z",
            "files": [
                {
                    "id": "split--section-1",
                    "source_path": "test/split.rst",
                    "format": "rst",
                    "filename": "split.rst",
                    "type": "component",
                    "category": "test",
                    "output_path": "component/test/split--section-1.json",
                    "assets_dir": "component/test/assets/split--section-1/",
                    "split_info": {
                        "is_split": True,
                        "original_id": "split",
                        "part": 1,
                        "total_parts": 1,
                        "group_line_count": 11
                    },
                    "section_range": {
                        "start_line": 0,
                        "end_line": 11,
                        "sections": ["Section 1", "Section 2"]
                    }
                },
                {
                    "id": "regular",
                    "source_path": "test/regular.rst",
                    "format": "rst",
                    "filename": "regular.rst",
                    "type": "component",
                    "category": "test",
                    "output_path": "component/test/regular.json",
                    "assets_dir": "component/test/assets/regular/"
                    # no split_info
                }
            ]
        }
        write_json(ctx.classified_list_path, classified)

        # Execute Phase B: generate
        phase_b = PhaseBGenerate(ctx, run_claude_fn=mock_run_claude, dry_run=False)
        phase_b.run()

        # Execute Phase C: structure check
        phase_c = PhaseCStructureCheck(ctx)
        c_result = phase_c.run()
        assert c_result["pass"] == 2, "All files (1 split + 1 regular) should pass"

        # Execute Phase D: content check
        phase_d = PhaseDContentCheck(ctx, run_claude_fn=mock_run_claude)
        d_result = phase_d.run(target_ids=c_result["pass_ids"])
        assert d_result["issues_count"] == 0

        # Execute Phase M: finalize
        phase_m = PhaseMFinalize(ctx, dry_run=False, run_claude_fn=mock_run_claude)
        phase_m.run()

        # Verify: Both split (merged) and non-split files exist
        split_merged_path = f"{ctx.knowledge_dir}/component/test/split.json"
        regular_path = f"{ctx.knowledge_dir}/component/test/regular.json"

        assert os.path.exists(split_merged_path), "Merged split file should exist"
        assert os.path.exists(regular_path), "Regular file should exist"

        # Verify: Split part deleted
        assert not os.path.exists(f"{ctx.knowledge_dir}/component/test/split--section-1.json")

        # Verify: classified.json restored to split state after Phase M
        updated = load_json(ctx.classified_list_path)
        ids = [f["id"] for f in updated["files"]]
        assert "split--section-1" in ids, "Split file ID should remain in classified.json"
        assert "regular" in ids, "Regular file should be in classified.json"

        # Verify: Both in index.toon
        with open(f"{ctx.knowledge_dir}/index.toon", "r", encoding="utf-8") as f:
            index_content = f.read()
        assert "split.json" in index_content
        assert "regular.json" in index_content

        # Verify: Resolved versions exist for both
        assert os.path.exists(f"{ctx.knowledge_resolved_dir}/component/test/split.json")
        assert os.path.exists(f"{ctx.knowledge_resolved_dir}/component/test/regular.json")

        # Verify: Browsable MDs exist for both
        assert os.path.exists(f"{ctx.docs_dir}/component/test/split.md")
        assert os.path.exists(f"{ctx.docs_dir}/component/test/regular.md")

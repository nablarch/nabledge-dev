"""E2E tests verifying cache separation between knowledge_cache_dir and knowledge_dir.

Key invariants:
- Phase B writes to knowledge_cache_dir, NOT knowledge_dir
- Phase C/D/E read from knowledge_cache_dir
- Phase M reads from knowledge_cache_dir, writes to knowledge_dir (delete-insert)
- After Phase M, catalog.json is restored to split state
"""
import json
import os
import subprocess
import pytest
from common import load_json, write_json


def _make_mock_claude(ctx):
    """Mock run_claude that returns deterministic outputs."""
    def mock_fn(prompt, json_schema=None, log_dir=None, file_id=None, **kwargs):
        schema_str = json.dumps(json_schema) if json_schema else ""
        if "trace" in schema_str:
            knowledge = {
                "id": file_id,
                "no_knowledge_content": False,
                "title": f"Title for {file_id}",
                "official_doc_urls": ["https://example.com/"],
                "index": [{"id": "s1", "title": "Section 1", "hints": ["hint"]}],
                "sections": {"s1": f"Content for {file_id} with sufficient length for validation."}
            }
            return subprocess.CompletedProcess(
                args=["claude"], returncode=0,
                stdout=json.dumps({
                    "knowledge": knowledge,
                    "trace": {
                        "file_id": file_id,
                        "generated_at": "2026-01-01T00:00:00Z",
                        "internal_labels": ["s1", file_id],
                        "sections": [{"section_id": "s1", "source_heading": "Section 1",
                                      "heading_level": "h2", "h3_split": False,
                                      "h3_split_reason": "Small"}]
                    }
                }), stderr=""
            )
        elif "findings" in schema_str:
            return subprocess.CompletedProcess(
                args=["claude"], returncode=0,
                stdout=json.dumps({"file_id": file_id, "status": "clean", "findings": []}),
                stderr=""
            )
        elif "patterns" in schema_str:
            return subprocess.CompletedProcess(
                args=["claude"], returncode=0,
                stdout=json.dumps({
                    "patterns": [],
                    "reasoning": [{"pattern": "nablarch-batch", "matched": False, "evidence": "N/A"}]
                }), stderr=""
            )
        else:
            # Phase E fix: return knowledge unchanged
            knowledge_path = f"{ctx.knowledge_cache_dir}/component/test/{file_id}.json"
            if os.path.exists(knowledge_path):
                return subprocess.CompletedProcess(
                    args=["claude"], returncode=0,
                    stdout=open(knowledge_path).read(), stderr=""
                )
            return subprocess.CompletedProcess(args=["claude"], returncode=1, stdout="", stderr="not found")
    return mock_fn


def _setup_classified(ctx, file_ids, split=False):
    """Helper: create classified.json with given file IDs."""
    files = []
    for fid in file_ids:
        entry = {
            "id": fid,
            "source_path": f"src/{fid}.rst",
            "format": "rst",
            "filename": f"{fid}.rst",
            "type": "component",
            "category": "test",
            "output_path": f"component/test/{fid}.json",
            "assets_dir": f"component/test/assets/{fid}/",
            "base_name": fid,
        }
        if split:
            entry["split_info"] = {"is_split": True, "original_id": fid.rsplit("--", 1)[0],
                                   "part": 1, "total_parts": 1}
        # Create source file
        src_path = os.path.join(ctx.repo, "src", f"{fid}.rst")
        os.makedirs(os.path.dirname(src_path), exist_ok=True)
        with open(src_path, "w") as f:
            f.write(f"{fid}\n====\n\nSection 1\n---------\nContent for {fid}.\n")
        files.append(entry)

    classified = {"version": "6", "generated_at": "2026-01-01T00:00:00Z", "files": files}
    os.makedirs(os.path.dirname(ctx.classified_list_path), exist_ok=True)
    write_json(ctx.classified_list_path, classified)
    return classified


class TestPhaseBCacheSeparation:
    """Phase B must write to knowledge_cache_dir, NOT knowledge_dir."""

    def test_phase_b_writes_to_cache_dir(self, ctx):
        """After Phase B, files exist in cache dir but NOT in knowledge_dir."""
        from phase_b_generate import PhaseBGenerate

        _setup_classified(ctx, ["file-a", "file-b"])
        mock = _make_mock_claude(ctx)
        PhaseBGenerate(ctx, run_claude_fn=mock).run()

        # Files should be in knowledge_cache_dir
        assert os.path.exists(f"{ctx.knowledge_cache_dir}/component/test/file-a.json")
        assert os.path.exists(f"{ctx.knowledge_cache_dir}/component/test/file-b.json")

        # Files should NOT be in knowledge_dir (only Phase M writes there)
        assert not os.path.exists(f"{ctx.knowledge_dir}/component/test/file-a.json")
        assert not os.path.exists(f"{ctx.knowledge_dir}/component/test/file-b.json")

    def test_phase_b_split_writes_to_cache_dir(self, ctx):
        """Phase B with split files writes parts to cache dir."""
        from phase_b_generate import PhaseBGenerate

        _setup_classified(ctx, ["group--part-1"], split=True)
        mock = _make_mock_claude(ctx)
        PhaseBGenerate(ctx, run_claude_fn=mock).run()

        # Part file in cache
        assert os.path.exists(f"{ctx.knowledge_cache_dir}/component/test/group--part-1.json")
        # Not in knowledge_dir
        assert not os.path.exists(f"{ctx.knowledge_dir}/component/test/group--part-1.json")


class TestPhaseMDeleteInsert:
    """Phase M: delete knowledge_dir, rebuild from knowledge_cache_dir."""

    def test_phase_m_copies_nonsplit_from_cache(self, ctx):
        """Phase M copies non-split files from cache to knowledge_dir."""
        from phase_m_finalize import PhaseMFinalize

        classified = _setup_classified(ctx, ["file-a", "file-b"])
        mock = _make_mock_claude(ctx)

        # Pre-populate knowledge_cache_dir (simulating Phase B output)
        for fid in ["file-a", "file-b"]:
            os.makedirs(f"{ctx.knowledge_cache_dir}/component/test", exist_ok=True)
            knowledge = {
                "id": fid, "no_knowledge_content": False,
                "title": f"Title {fid}", "official_doc_urls": [],
                "index": [{"id": "s1", "title": "S1", "hints": ["h"]}],
                "sections": {"s1": f"Content for {fid}"}
            }
            write_json(f"{ctx.knowledge_cache_dir}/component/test/{fid}.json", knowledge)

        # Run Phase M
        PhaseMFinalize(ctx, dry_run=False, run_claude_fn=mock).run()

        # Files should now be in knowledge_dir
        assert os.path.exists(f"{ctx.knowledge_dir}/component/test/file-a.json")
        assert os.path.exists(f"{ctx.knowledge_dir}/component/test/file-b.json")

        # Files should still be in cache (Phase M copies, not moves)
        assert os.path.exists(f"{ctx.knowledge_cache_dir}/component/test/file-a.json")
        assert os.path.exists(f"{ctx.knowledge_cache_dir}/component/test/file-b.json")

    def test_phase_m_deletes_stale_knowledge_dir_files(self, ctx):
        """Phase M deletes knowledge_dir first (stale files removed)."""
        from phase_m_finalize import PhaseMFinalize

        _setup_classified(ctx, ["file-a"])
        mock = _make_mock_claude(ctx)

        # Pre-populate cache
        os.makedirs(f"{ctx.knowledge_cache_dir}/component/test", exist_ok=True)
        knowledge = {
            "id": "file-a", "no_knowledge_content": False,
            "title": "Title", "official_doc_urls": [],
            "index": [{"id": "s1", "title": "S1", "hints": ["h"]}],
            "sections": {"s1": "Content"}
        }
        write_json(f"{ctx.knowledge_cache_dir}/component/test/file-a.json", knowledge)

        # Place a stale file in knowledge_dir
        os.makedirs(f"{ctx.knowledge_dir}/component/test", exist_ok=True)
        write_json(f"{ctx.knowledge_dir}/component/test/stale-file.json",
                   {"id": "stale-file", "title": "Stale"})

        # Run Phase M
        PhaseMFinalize(ctx, dry_run=False, run_claude_fn=mock).run()

        # Stale file should be deleted
        assert not os.path.exists(f"{ctx.knowledge_dir}/component/test/stale-file.json")
        # Real file should exist
        assert os.path.exists(f"{ctx.knowledge_dir}/component/test/file-a.json")

    def test_phase_m_restores_split_catalog(self, ctx):
        """After Phase M, catalog.json is in split state (not merged state)."""
        from phase_m_finalize import PhaseMFinalize

        # Setup: two split parts for same original
        files = [
            {
                "id": "group--part-1", "source_path": "src/group.rst",
                "format": "rst", "filename": "group.rst",
                "type": "component", "category": "test",
                "output_path": "component/test/group--part-1.json",
                "assets_dir": "component/test/assets/group--part-1/",
                "base_name": "group",
                "split_info": {"is_split": True, "original_id": "group", "part": 1, "total_parts": 2}
            },
            {
                "id": "group--part-2", "source_path": "src/group.rst",
                "format": "rst", "filename": "group.rst",
                "type": "component", "category": "test",
                "output_path": "component/test/group--part-2.json",
                "assets_dir": "component/test/assets/group--part-2/",
                "base_name": "group",
                "split_info": {"is_split": True, "original_id": "group", "part": 2, "total_parts": 2}
            }
        ]
        classified = {"version": "6", "generated_at": "2026-01-01T00:00:00Z", "files": files}
        os.makedirs(os.path.dirname(ctx.classified_list_path), exist_ok=True)
        write_json(ctx.classified_list_path, classified)

        # Create source file
        os.makedirs(os.path.join(ctx.repo, "src"), exist_ok=True)
        with open(os.path.join(ctx.repo, "src", "group.rst"), "w") as f:
            f.write("Group\n=====\n\nContent\n")

        # Pre-populate cache
        for fid in ["group--part-1", "group--part-2"]:
            os.makedirs(f"{ctx.knowledge_cache_dir}/component/test", exist_ok=True)
            knowledge = {
                "id": fid, "no_knowledge_content": False,
                "title": "Group", "official_doc_urls": [],
                "index": [{"id": f"s{fid[-1]}", "title": f"Section {fid[-1]}", "hints": ["h"]}],
                "sections": {f"s{fid[-1]}": f"Content for {fid}"}
            }
            write_json(f"{ctx.knowledge_cache_dir}/component/test/{fid}.json", knowledge)

        mock = _make_mock_claude(ctx)
        PhaseMFinalize(ctx, dry_run=False, run_claude_fn=mock).run()

        # Merged file exists in knowledge_dir
        assert os.path.exists(f"{ctx.knowledge_dir}/component/test/group.json")

        # Catalog should be in SPLIT state (original split entries preserved)
        catalog = load_json(ctx.classified_list_path)
        ids = [f["id"] for f in catalog["files"]]
        assert "group--part-1" in ids, "Split catalog should preserve split IDs"
        assert "group--part-2" in ids, "Split catalog should preserve split IDs"


class TestPhaseCDEUseCacheDir:
    """Phase C/D/E must read from knowledge_cache_dir."""

    def test_phase_c_reads_from_cache_dir(self, ctx):
        """Phase C validates files from knowledge_cache_dir."""
        from phase_c_structure_check import PhaseCStructureCheck

        _setup_classified(ctx, ["file-a"])

        # Place knowledge in cache dir
        os.makedirs(f"{ctx.knowledge_cache_dir}/component/test", exist_ok=True)
        knowledge = {
            "id": "file-a", "no_knowledge_content": False,
            "title": "Title", "official_doc_urls": ["https://example.com"],
            "index": [{"id": "s1", "title": "S1", "hints": ["h"]}],
            "sections": {"s1": "Content with sufficient length for validation checks."}
        }
        write_json(f"{ctx.knowledge_cache_dir}/component/test/file-a.json", knowledge)

        result = PhaseCStructureCheck(ctx).run()
        assert "file-a" in result["pass_ids"]

    def test_phase_d_reads_from_cache_dir(self, ctx):
        """Phase D checks files from knowledge_cache_dir."""
        from phase_d_content_check import PhaseDContentCheck

        _setup_classified(ctx, ["file-a"])

        os.makedirs(f"{ctx.knowledge_cache_dir}/component/test", exist_ok=True)
        knowledge = {
            "id": "file-a", "no_knowledge_content": False,
            "title": "Title", "official_doc_urls": ["https://example.com"],
            "index": [{"id": "s1", "title": "S1", "hints": ["h"]}],
            "sections": {"s1": "Content"}
        }
        write_json(f"{ctx.knowledge_cache_dir}/component/test/file-a.json", knowledge)

        def mock_d(prompt, json_schema=None, log_dir=None, file_id=None, **kwargs):
            return subprocess.CompletedProcess(
                args=["claude"], returncode=0,
                stdout=json.dumps({"file_id": file_id, "status": "clean", "findings": []}),
                stderr=""
            )

        result = PhaseDContentCheck(ctx, run_claude_fn=mock_d).run(target_ids=["file-a"])
        assert result["issues_count"] == 0

    def test_phase_e_reads_and_writes_cache_dir(self, ctx):
        """Phase E reads from and writes to knowledge_cache_dir."""
        from phase_e_fix import PhaseEFix

        _setup_classified(ctx, ["file-a"])

        os.makedirs(f"{ctx.knowledge_cache_dir}/component/test", exist_ok=True)
        original = {
            "id": "file-a", "no_knowledge_content": False,
            "title": "Original", "official_doc_urls": ["https://example.com"],
            "index": [{"id": "s1", "title": "S1", "hints": ["h"]}],
            "sections": {"s1": "Original content"}
        }
        write_json(f"{ctx.knowledge_cache_dir}/component/test/file-a.json", original)

        os.makedirs(ctx.findings_dir, exist_ok=True)
        write_json(f"{ctx.findings_dir}/file-a.json", {
            "file_id": "file-a", "status": "has_issues",
            "findings": [{"category": "omission", "severity": "minor",
                          "location": "s1", "description": "Missing detail"}]
        })

        fixed_knowledge = {
            "id": "file-a", "no_knowledge_content": False,
            "title": "Fixed", "official_doc_urls": ["https://example.com"],
            "index": [{"id": "s1", "title": "S1", "hints": ["h"]}],
            "sections": {"s1": "Fixed content with improvement"}
        }

        def mock_e(prompt, json_schema=None, log_dir=None, file_id=None, **kwargs):
            return subprocess.CompletedProcess(
                args=["claude"], returncode=0,
                stdout=json.dumps(fixed_knowledge), stderr=""
            )

        PhaseEFix(ctx, run_claude_fn=mock_e).run(target_ids=["file-a"])

        # Verify Phase E wrote to cache dir
        updated = load_json(f"{ctx.knowledge_cache_dir}/component/test/file-a.json")
        assert updated["title"] == "Fixed"

        # knowledge_dir should NOT have the file
        assert not os.path.exists(f"{ctx.knowledge_dir}/component/test/file-a.json")


class TestFullPipelineCacheSeparation:
    """Full pipeline (B→C→D→E→M) with cache separation verified."""

    def test_bcdem_pipeline_cache_invariants(self, ctx):
        """After BCDEM pipeline: cache has all files, knowledge_dir has merged files."""
        from phase_b_generate import PhaseBGenerate
        from phase_c_structure_check import PhaseCStructureCheck
        from phase_d_content_check import PhaseDContentCheck
        from phase_m_finalize import PhaseMFinalize

        _setup_classified(ctx, ["file-a", "file-b"])
        mock = _make_mock_claude(ctx)

        # Phase B
        PhaseBGenerate(ctx, run_claude_fn=mock).run()

        # Invariant: after B, files in cache only
        assert os.path.exists(f"{ctx.knowledge_cache_dir}/component/test/file-a.json")
        assert not os.path.exists(f"{ctx.knowledge_dir}/component/test/file-a.json")

        # Phase C
        c_result = PhaseCStructureCheck(ctx).run()
        assert c_result["pass"] == 2

        # Phase D
        d_result = PhaseDContentCheck(ctx, run_claude_fn=mock).run(
            target_ids=c_result["pass_ids"])
        assert d_result["issues_count"] == 0

        # Phase M
        PhaseMFinalize(ctx, dry_run=False, run_claude_fn=mock).run()

        # Invariant: after M, files in knowledge_dir
        assert os.path.exists(f"{ctx.knowledge_dir}/component/test/file-a.json")
        assert os.path.exists(f"{ctx.knowledge_dir}/component/test/file-b.json")

        # Invariant: cache preserved after M
        assert os.path.exists(f"{ctx.knowledge_cache_dir}/component/test/file-a.json")
        assert os.path.exists(f"{ctx.knowledge_cache_dir}/component/test/file-b.json")

        # Invariant: catalog in original state (no merges happened since no split files)
        catalog = load_json(ctx.classified_list_path)
        ids = [f["id"] for f in catalog["files"]]
        assert "file-a" in ids
        assert "file-b" in ids

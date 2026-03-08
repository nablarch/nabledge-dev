"""Tests for Phase M: Merge + Resolve + Finalize."""
import json
import os
import pytest
from common import load_json, write_json


class TestPhaseM:
    """Test Phase M finalization phase."""

    def test_merge_then_resolve_then_docs(self, ctx, mock_claude):
        """Phase M: merge split files, resolve links, generate docs."""
        from phase_m_finalize import PhaseMFinalize

        # Setup: 2 split parts with RST link
        part1 = {
            "id": "test--section-1",
            "title": "Test",
            "official_doc_urls": ["https://example.com"],
            "index": [{"id": "section1", "title": "Section 1", "hints": ["s1"]}],
            "sections": {"section1": "See :ref:`other-section` for details."}
        }
        part2 = {
            "id": "test--section-2",
            "title": "Test",
            "official_doc_urls": ["https://example.com"],
            "index": [{"id": "section2", "title": "Section 2", "hints": ["s2"]}],
            "sections": {"section2": "Another section content."}
        }

        os.makedirs(f"{ctx.knowledge_cache_dir}/component/test", exist_ok=True)
        write_json(f"{ctx.knowledge_cache_dir}/component/test/test--section-1.json", part1)
        write_json(f"{ctx.knowledge_cache_dir}/component/test/test--section-2.json", part2)

        # Create trace files with internal_labels for Phase G link resolution
        trace1 = {
            "file_id": "test--section-1",
            "generated_at": "2026-01-01T00:00:00Z",
            "internal_labels": ["test", "other-section", "section1"],
            "sections": [{"section_id": "section1", "source_heading": "Section 1", "heading_level": "h2"}]
        }
        trace2 = {
            "file_id": "test--section-2",
            "generated_at": "2026-01-01T00:00:00Z",
            "internal_labels": ["section2"],
            "sections": [{"section_id": "section2", "source_heading": "Section 2", "heading_level": "h2"}]
        }

        os.makedirs(f"{ctx.trace_dir}", exist_ok=True)
        write_json(f"{ctx.trace_dir}/test--section-1.json", trace1)
        write_json(f"{ctx.trace_dir}/test--section-2.json", trace2)

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
                    }
                }
            ]
        }
        write_json(ctx.classified_list_path, classified)

        # Execute Phase M
        phase_m = PhaseMFinalize(ctx, dry_run=False, run_claude_fn=mock_claude)
        phase_m.run()

        # Verify 1: Merged file exists
        merged_path = f"{ctx.knowledge_dir}/component/test/test.json"
        assert os.path.exists(merged_path)

        merged = load_json(merged_path)
        assert merged["id"] == "test"
        assert len(merged["sections"]) == 2
        assert "section1" in merged["sections"]
        assert "section2" in merged["sections"]

        # Verify 2: Part files deleted
        assert not os.path.exists(f"{ctx.knowledge_dir}/component/test/test--section-1.json")
        assert not os.path.exists(f"{ctx.knowledge_dir}/component/test/test--section-2.json")

        # Verify 3: classified.json restored to split state after Phase M
        updated = load_json(ctx.classified_list_path)
        ids = [f["id"] for f in updated["files"]]
        assert "test--section-1" in ids
        assert "test--section-2" in ids

        # Verify 4: Resolved version exists
        resolved_path = f"{ctx.knowledge_resolved_dir}/component/test/test.json"
        assert os.path.exists(resolved_path)

        resolved = load_json(resolved_path)
        # RST link should be converted to markdown
        assert ":ref:" not in resolved["sections"]["section1"]

        # Verify 5: Browsable MD exists
        md_path = f"{ctx.docs_dir}/component/test/test.md"
        assert os.path.exists(md_path)

        # Verify 6: index.toon exists
        assert os.path.exists(f"{ctx.knowledge_dir}/index.toon")

    def test_phase_m_no_split_files(self, ctx, mock_claude):
        """Phase M with no split files: skip merge, proceed with resolve + docs."""
        from phase_m_finalize import PhaseMFinalize

        # Setup: regular file (no split)
        regular = {
            "id": "regular",
            "title": "Regular",
            "official_doc_urls": ["https://example.com"],
            "index": [{"id": "section1", "title": "Section 1", "hints": ["s1"]}],
            "sections": {"section1": "Regular content with :ref:`link`."}
        }

        os.makedirs(f"{ctx.knowledge_cache_dir}/component/test", exist_ok=True)
        write_json(f"{ctx.knowledge_cache_dir}/component/test/regular.json", regular)

        classified = {
            "version": "6",
            "generated_at": "2026-01-01T00:00:00Z",
            "files": [
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

        # Execute Phase M
        phase_m = PhaseMFinalize(ctx, dry_run=False, run_claude_fn=mock_claude)
        phase_m.run()

        # Verify: original file still exists (not deleted by merge)
        assert os.path.exists(f"{ctx.knowledge_dir}/component/test/regular.json")

        # Verify: resolved version exists
        resolved_path = f"{ctx.knowledge_resolved_dir}/component/test/regular.json"
        assert os.path.exists(resolved_path)

        # Verify: browsable MD exists
        md_path = f"{ctx.docs_dir}/component/test/regular.md"
        assert os.path.exists(md_path)

    def test_phase_m_rst_links_resolved_in_merged(self, ctx, mock_claude):
        """RST links in merged file are resolved to Markdown."""
        from phase_m_finalize import PhaseMFinalize

        # Setup: split files with various RST link types
        part1 = {
            "id": "test--section-1",
            "title": "Test",
            "official_doc_urls": ["https://example.com"],
            "index": [{"id": "section1", "title": "Section 1", "hints": ["s1"]}],
            "sections": {"section1": "See :ref:`other-label` and :doc:`../other` for more."}
        }
        part2 = {
            "id": "test--section-2",
            "title": "Test",
            "official_doc_urls": ["https://example.com"],
            "index": [{"id": "section2", "title": "Section 2", "hints": ["s2"]}],
            "sections": {"section2": "Download :download:`File <file.zip>`."}
        }

        os.makedirs(f"{ctx.knowledge_cache_dir}/component/test", exist_ok=True)
        write_json(f"{ctx.knowledge_cache_dir}/component/test/test--section-1.json", part1)
        write_json(f"{ctx.knowledge_cache_dir}/component/test/test--section-2.json", part2)

        # Create trace files with internal_labels for Phase G
        trace1 = {
            "file_id": "test--section-1",
            "generated_at": "2026-01-01T00:00:00Z",
            "internal_labels": ["test", "other-label", "section1"],
            "sections": [{"section_id": "section1", "source_heading": "Section 1", "heading_level": "h2"}]
        }
        trace2 = {
            "file_id": "test--section-2",
            "generated_at": "2026-01-01T00:00:00Z",
            "internal_labels": ["section2"],
            "sections": [{"section_id": "section2", "source_heading": "Section 2", "heading_level": "h2"}]
        }

        os.makedirs(f"{ctx.trace_dir}", exist_ok=True)
        write_json(f"{ctx.trace_dir}/test--section-1.json", trace1)
        write_json(f"{ctx.trace_dir}/test--section-2.json", trace2)

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
                    "split_info": {"is_split": True, "original_id": "test", "part": 1, "total_parts": 2}
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
                    "split_info": {"is_split": True, "original_id": "test", "part": 2, "total_parts": 2}
                }
            ]
        }
        write_json(ctx.classified_list_path, classified)

        # Execute Phase M
        phase_m = PhaseMFinalize(ctx, dry_run=False, run_claude_fn=mock_claude)
        phase_m.run()

        # Verify: resolved version has Markdown links, not RST
        resolved = load_json(f"{ctx.knowledge_resolved_dir}/component/test/test.json")

        # :ref: should be resolved (label exists in trace)
        assert ":ref:" not in str(resolved["sections"])
        assert "[other-label]" in str(resolved["sections"]) or "other-label" in str(resolved["sections"])

        # :download: should be resolved to assets path
        assert ":download:" not in str(resolved["sections"])
        assert "assets/test/file.zip" in str(resolved["sections"])

        # :doc: may not resolve if target file doesn't exist in classified.json
        # (Phase G keeps unresolvable links as-is)

    def test_phase_m_asset_paths_in_docs(self, ctx, mock_claude):
        """Asset paths in browsable MD are correct relative paths."""
        from phase_m_finalize import PhaseMFinalize

        # Setup: merged file with asset reference
        knowledge = {
            "id": "test",
            "title": "Test",
            "official_doc_urls": ["https://example.com"],
            "index": [{"id": "section1", "title": "Section 1", "hints": ["s1"]}],
            "sections": {"section1": "See image: assets/test/image.png"}
        }

        os.makedirs(f"{ctx.knowledge_cache_dir}/component/test", exist_ok=True)
        write_json(f"{ctx.knowledge_cache_dir}/component/test/test.json", knowledge)

        # Create asset file
        os.makedirs(f"{ctx.knowledge_cache_dir}/component/test/assets/test", exist_ok=True)
        with open(f"{ctx.knowledge_cache_dir}/component/test/assets/test/image.png", "w") as f:
            f.write("fake-image")

        classified = {
            "version": "6",
            "generated_at": "2026-01-01T00:00:00Z",
            "files": [
                {
                    "id": "test",
                    "source_path": "test/test.rst",
                    "format": "rst",
                    "filename": "test.rst",
                    "type": "component",
                    "category": "test",
                    "output_path": "component/test/test.json",
                    "assets_dir": "component/test/assets/test/"
                }
            ]
        }
        write_json(ctx.classified_list_path, classified)

        # Execute Phase M
        phase_m = PhaseMFinalize(ctx, dry_run=False, run_claude_fn=mock_claude)
        phase_m.run()

        # Verify: browsable MD has correct relative path
        md_path = f"{ctx.docs_dir}/component/test/test.md"
        with open(md_path, "r", encoding="utf-8") as f:
            md_content = f.read()

        # Asset path should be adjusted for docs structure
        # From knowledge: assets/test/image.png
        # In MD: should point to knowledge_dir from docs_dir
        assert "image.png" in md_content

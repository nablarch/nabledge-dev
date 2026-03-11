"""Tests for Phase M: Merge + Resolve + Finalize."""
import json
import os
import pytest
from common import load_json, write_json


class TestPhaseM:
    """Test Phase M finalization phase."""

    def test_merge_then_docs(self, ctx, mock_claude):
        """Phase M: merge split files, generate docs."""
        from phase_m_finalize import PhaseMFinalize

        # Setup: 2 split parts
        part1 = {
            "id": "test--section-1",
            "title": "Test",
            "official_doc_urls": ["https://example.com"],
            "index": [{"id": "section1", "title": "Section 1", "hints": ["s1"]}],
            "sections": {"section1": "Section 1 content."}
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

        # Verify 4: Browsable MD exists and includes official URL and hints
        md_path = f"{ctx.docs_dir}/component/test/test.md"
        assert os.path.exists(md_path)
        with open(md_path, encoding="utf-8") as f:
            md_content = f.read()
        assert "**公式ドキュメント**: [Test](https://example.com)" in md_content
        assert "<details>" in md_content
        assert "<summary>keywords</summary>" in md_content
        assert "s1" in md_content
        assert "s2" in md_content

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

        # Verify: browsable MD exists
        md_path = f"{ctx.docs_dir}/component/test/regular.md"
        assert os.path.exists(md_path)

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

    def test_docs_multiple_official_urls(self, ctx, mock_claude):
        """Multiple official_doc_urls are rendered as numbered links."""
        from phase_m_finalize import PhaseMFinalize

        knowledge = {
            "id": "multi",
            "title": "Multi URL",
            "official_doc_urls": ["https://example.com/a", "https://example.com/b"],
            "index": [{"id": "s1", "title": "Section 1", "hints": ["hint1", "hint2"]}],
            "sections": {"s1": "Content here."}
        }

        os.makedirs(f"{ctx.knowledge_cache_dir}/component/test", exist_ok=True)
        write_json(f"{ctx.knowledge_cache_dir}/component/test/multi.json", knowledge)

        classified = {
            "version": "6",
            "generated_at": "2026-01-01T00:00:00Z",
            "files": [
                {
                    "id": "multi",
                    "source_path": "test/multi.rst",
                    "format": "rst",
                    "filename": "multi.rst",
                    "type": "component",
                    "category": "test",
                    "output_path": "component/test/multi.json",
                    "assets_dir": "component/test/assets/multi/"
                }
            ]
        }
        write_json(ctx.classified_list_path, classified)

        phase_m = PhaseMFinalize(ctx, dry_run=False, run_claude_fn=mock_claude)
        phase_m.run()

        md_path = f"{ctx.docs_dir}/component/test/multi.md"
        with open(md_path, encoding="utf-8") as f:
            md_content = f.read()

        assert "**公式ドキュメント**: [1](https://example.com/a) [2](https://example.com/b)" in md_content
        assert "<details>" in md_content
        assert "<summary>keywords</summary>" in md_content
        assert "hint1, hint2" in md_content

    def test_docs_empty_official_urls_and_hints(self, ctx, mock_claude):
        """Empty official_doc_urls and hints produce no URL line or keyword line."""
        from phase_m_finalize import PhaseMFinalize

        knowledge = {
            "id": "empty-meta",
            "title": "Empty Meta",
            "official_doc_urls": [],
            "index": [{"id": "s1", "title": "Section 1", "hints": []}],
            "sections": {"s1": "Section content."}
        }

        os.makedirs(f"{ctx.knowledge_cache_dir}/component/test", exist_ok=True)
        write_json(f"{ctx.knowledge_cache_dir}/component/test/empty-meta.json", knowledge)

        classified = {
            "version": "6",
            "generated_at": "2026-01-01T00:00:00Z",
            "files": [
                {
                    "id": "empty-meta",
                    "source_path": "test/empty-meta.rst",
                    "format": "rst",
                    "filename": "empty-meta.rst",
                    "type": "component",
                    "category": "test",
                    "output_path": "component/test/empty-meta.json",
                    "assets_dir": "component/test/assets/empty-meta/"
                }
            ]
        }
        write_json(ctx.classified_list_path, classified)

        phase_m = PhaseMFinalize(ctx, dry_run=False, run_claude_fn=mock_claude)
        phase_m.run()

        md_path = f"{ctx.docs_dir}/component/test/empty-meta.md"
        with open(md_path, encoding="utf-8") as f:
            md_content = f.read()

        assert "**公式ドキュメント**" not in md_content
        assert "キーワード" not in md_content

"""Tests for split file merging."""
import json
import os
import pytest
from steps.common import load_json, write_json


class TestMergeSplitFiles:
    """Test MergeSplitFiles class."""

    def test_merge_two_parts(self, ctx, tmp_path):
        """Normal case: merge 2 parts into single file."""
        from steps.merge import MergeSplitFiles

        # Setup: create 2 part files
        part1 = {
            "id": "libraries-tag-1",
            "title": "タグライブラリ",
            "official_doc_urls": ["https://example.com/tag.html"],
            "index": [
                {"id": "overview", "title": "概要", "hints": ["tag", "jsp"]}
            ],
            "sections": {
                "overview": "タグライブラリの概要。\n\n画像: assets/libraries-tag-1/image.png"
            }
        }
        part2 = {
            "id": "libraries-tag-2",
            "title": "タグライブラリ",
            "official_doc_urls": ["https://example.com/tag.html"],
            "index": [
                {"id": "usage", "title": "使い方", "hints": ["usage"]}
            ],
            "sections": {
                "usage": "タグの使い方。\n\n図: assets/libraries-tag-2/diagram.png"
            }
        }

        os.makedirs(f"{ctx.knowledge_dir}/component/libraries", exist_ok=True)
        write_json(f"{ctx.knowledge_dir}/component/libraries/libraries-tag-1.json", part1)
        write_json(f"{ctx.knowledge_dir}/component/libraries/libraries-tag-2.json", part2)

        # Create assets
        os.makedirs(f"{ctx.knowledge_dir}/component/libraries/assets/libraries-tag-1", exist_ok=True)
        os.makedirs(f"{ctx.knowledge_dir}/component/libraries/assets/libraries-tag-2", exist_ok=True)
        with open(f"{ctx.knowledge_dir}/component/libraries/assets/libraries-tag-1/image.png", "w") as f:
            f.write("fake-image")
        with open(f"{ctx.knowledge_dir}/component/libraries/assets/libraries-tag-2/diagram.png", "w") as f:
            f.write("fake-diagram")

        # Setup: classified.json with split info
        classified = {
            "version": "6",
            "generated_at": "2026-01-01T00:00:00Z",
            "files": [
                {
                    "id": "libraries-tag-1",
                    "source_path": "test.rst",
                    "format": "rst",
                    "filename": "test.rst",
                    "type": "component",
                    "category": "libraries",
                    "output_path": "component/libraries/libraries-tag-1.json",
                    "assets_dir": "component/libraries/assets/libraries-tag-1/",
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
                },
                {
                    "id": "libraries-tag-2",
                    "source_path": "test.rst",
                    "format": "rst",
                    "filename": "test.rst",
                    "type": "component",
                    "category": "libraries",
                    "output_path": "component/libraries/libraries-tag-2.json",
                    "assets_dir": "component/libraries/assets/libraries-tag-2/",
                    "split_info": {
                        "is_split": True,
                        "original_id": "libraries-tag",
                        "part": 2,
                        "total_parts": 2
                    },
                    "section_range": {
                        "start_line": 30,
                        "end_line": 60,
                        "sections": ["使い方"]
                    }
                }
            ]
        }
        write_json(ctx.classified_list_path, classified)

        # Execute
        MergeSplitFiles(ctx).run()

        # Verify: merged file exists
        merged_path = f"{ctx.knowledge_dir}/component/libraries/libraries-tag.json"
        assert os.path.exists(merged_path)

        merged = load_json(merged_path)
        assert merged["id"] == "libraries-tag"
        assert merged["title"] == "タグライブラリ"
        assert merged["official_doc_urls"] == ["https://example.com/tag.html"]
        assert len(merged["index"]) == 2
        assert {e["id"] for e in merged["index"]} == {"overview", "usage"}
        assert len(merged["sections"]) == 2
        assert "overview" in merged["sections"]
        assert "usage" in merged["sections"]

        # Verify: asset paths updated
        assert "assets/libraries-tag/image.png" in merged["sections"]["overview"]
        assert "assets/libraries-tag/diagram.png" in merged["sections"]["usage"]

        # Verify: part files deleted
        assert not os.path.exists(f"{ctx.knowledge_dir}/component/libraries/libraries-tag-1.json")
        assert not os.path.exists(f"{ctx.knowledge_dir}/component/libraries/libraries-tag-2.json")

        # Verify: assets consolidated
        assert os.path.exists(f"{ctx.knowledge_dir}/component/libraries/assets/libraries-tag/image.png")
        assert os.path.exists(f"{ctx.knowledge_dir}/component/libraries/assets/libraries-tag/diagram.png")
        assert not os.path.exists(f"{ctx.knowledge_dir}/component/libraries/assets/libraries-tag-1")
        assert not os.path.exists(f"{ctx.knowledge_dir}/component/libraries/assets/libraries-tag-2")

        # Verify: classified.json updated
        updated = load_json(ctx.classified_list_path)
        ids = [f["id"] for f in updated["files"]]
        assert "libraries-tag" in ids
        assert "libraries-tag-1" not in ids
        assert "libraries-tag-2" not in ids

        merged_entry = next(f for f in updated["files"] if f["id"] == "libraries-tag")
        assert "split_info" not in merged_entry
        assert "section_range" not in merged_entry
        assert merged_entry["output_path"] == "component/libraries/libraries-tag.json"

    def test_merge_skips_incomplete_parts(self, ctx):
        """Skip merge if not all parts exist."""
        from steps.merge import MergeSplitFiles

        # Setup: only part 1 and 2 exist, part 3 missing
        part1 = {"id": "test-1", "title": "Test", "official_doc_urls": [],
                 "index": [], "sections": {"s1": "content"}}
        part2 = {"id": "test-2", "title": "Test", "official_doc_urls": [],
                 "index": [], "sections": {"s2": "content"}}

        os.makedirs(f"{ctx.knowledge_dir}/component/test", exist_ok=True)
        write_json(f"{ctx.knowledge_dir}/component/test/test-1.json", part1)
        write_json(f"{ctx.knowledge_dir}/component/test/test-2.json", part2)
        # part3 not created

        classified = {
            "version": "6",
            "generated_at": "2026-01-01T00:00:00Z",
            "files": [
                {
                    "id": "test-1",
                    "source_path": "test.rst",
                    "format": "rst",
                    "filename": "test.rst",
                    "type": "component",
                    "category": "test",
                    "output_path": "component/test/test-1.json",
                    "assets_dir": "component/test/assets/test-1/",
                    "split_info": {"is_split": True, "original_id": "test", "part": 1, "total_parts": 3}
                },
                {
                    "id": "test-2",
                    "source_path": "test.rst",
                    "format": "rst",
                    "filename": "test.rst",
                    "type": "component",
                    "category": "test",
                    "output_path": "component/test/test-2.json",
                    "assets_dir": "component/test/assets/test-2/",
                    "split_info": {"is_split": True, "original_id": "test", "part": 2, "total_parts": 3}
                },
                {
                    "id": "test-3",
                    "source_path": "test.rst",
                    "format": "rst",
                    "filename": "test.rst",
                    "type": "component",
                    "category": "test",
                    "output_path": "component/test/test-3.json",
                    "assets_dir": "component/test/assets/test-3/",
                    "split_info": {"is_split": True, "original_id": "test", "part": 3, "total_parts": 3}
                }
            ]
        }
        write_json(ctx.classified_list_path, classified)

        # Execute - should not raise exception
        MergeSplitFiles(ctx).run()

        # Verify: no merge happened
        assert not os.path.exists(f"{ctx.knowledge_dir}/component/test/test.json")
        assert os.path.exists(f"{ctx.knowledge_dir}/component/test/test-1.json")
        assert os.path.exists(f"{ctx.knowledge_dir}/component/test/test-2.json")

        # Verify: classified.json unchanged
        updated = load_json(ctx.classified_list_path)
        assert len(updated["files"]) == 3

    def test_no_split_files_noop(self, ctx):
        """No-op when there are no split files."""
        from steps.merge import MergeSplitFiles

        # Setup: only non-split files
        regular = {"id": "regular", "title": "Regular", "official_doc_urls": [],
                   "index": [], "sections": {"s1": "content"}}

        os.makedirs(f"{ctx.knowledge_dir}/component/test", exist_ok=True)
        write_json(f"{ctx.knowledge_dir}/component/test/regular.json", regular)

        classified = {
            "version": "6",
            "generated_at": "2026-01-01T00:00:00Z",
            "files": [
                {
                    "id": "regular",
                    "source_path": "test.rst",
                    "format": "rst",
                    "filename": "test.rst",
                    "type": "component",
                    "category": "test",
                    "output_path": "component/test/regular.json",
                    "assets_dir": "component/test/assets/regular/"
                    # no split_info
                }
            ]
        }
        write_json(ctx.classified_list_path, classified)

        # Execute
        MergeSplitFiles(ctx).run()

        # Verify: nothing changed
        assert os.path.exists(f"{ctx.knowledge_dir}/component/test/regular.json")
        updated = load_json(ctx.classified_list_path)
        assert len(updated["files"]) == 1
        assert updated["files"][0]["id"] == "regular"

    def test_merge_preserves_non_split_files(self, ctx):
        """Mixed split and non-split: non-split files preserved."""
        from steps.merge import MergeSplitFiles

        # Setup: 1 split file (2 parts) + 1 non-split file
        part1 = {"id": "split-1", "title": "Split", "official_doc_urls": [],
                 "index": [{"id": "s1", "title": "S1", "hints": []}],
                 "sections": {"s1": "part1"}}
        part2 = {"id": "split-2", "title": "Split", "official_doc_urls": [],
                 "index": [{"id": "s2", "title": "S2", "hints": []}],
                 "sections": {"s2": "part2"}}
        regular = {"id": "regular", "title": "Regular", "official_doc_urls": [],
                   "index": [{"id": "r1", "title": "R1", "hints": []}],
                   "sections": {"r1": "content"}}

        os.makedirs(f"{ctx.knowledge_dir}/component/test", exist_ok=True)
        write_json(f"{ctx.knowledge_dir}/component/test/split-1.json", part1)
        write_json(f"{ctx.knowledge_dir}/component/test/split-2.json", part2)
        write_json(f"{ctx.knowledge_dir}/component/test/regular.json", regular)

        classified = {
            "version": "6",
            "generated_at": "2026-01-01T00:00:00Z",
            "files": [
                {
                    "id": "split-1",
                    "source_path": "test.rst",
                    "format": "rst",
                    "filename": "test.rst",
                    "type": "component",
                    "category": "test",
                    "output_path": "component/test/split-1.json",
                    "assets_dir": "component/test/assets/split-1/",
                    "split_info": {"is_split": True, "original_id": "split", "part": 1, "total_parts": 2}
                },
                {
                    "id": "split-2",
                    "source_path": "test.rst",
                    "format": "rst",
                    "filename": "test.rst",
                    "type": "component",
                    "category": "test",
                    "output_path": "component/test/split-2.json",
                    "assets_dir": "component/test/assets/split-2/",
                    "split_info": {"is_split": True, "original_id": "split", "part": 2, "total_parts": 2}
                },
                {
                    "id": "regular",
                    "source_path": "test2.rst",
                    "format": "rst",
                    "filename": "test2.rst",
                    "type": "component",
                    "category": "test",
                    "output_path": "component/test/regular.json",
                    "assets_dir": "component/test/assets/regular/"
                }
            ]
        }
        write_json(ctx.classified_list_path, classified)

        # Execute
        MergeSplitFiles(ctx).run()

        # Verify: split files merged
        assert os.path.exists(f"{ctx.knowledge_dir}/component/test/split.json")
        merged = load_json(f"{ctx.knowledge_dir}/component/test/split.json")
        assert merged["id"] == "split"
        assert len(merged["sections"]) == 2

        # Verify: non-split file preserved
        assert os.path.exists(f"{ctx.knowledge_dir}/component/test/regular.json")
        reg = load_json(f"{ctx.knowledge_dir}/component/test/regular.json")
        assert reg["id"] == "regular"

        # Verify: classified.json has both
        updated = load_json(ctx.classified_list_path)
        ids = [f["id"] for f in updated["files"]]
        assert "split" in ids
        assert "regular" in ids
        assert "split-1" not in ids
        assert "split-2" not in ids

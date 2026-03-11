"""Tests for split file merging."""
import json
import os
import pytest
from common import load_json, write_json


class TestMergeSplitFiles:
    """Test MergeSplitFiles class."""

    def test_merge_two_parts(self, ctx, tmp_path):
        """Normal case: merge 2 parts into single file."""
        from merge import MergeSplitFiles

        # Setup: create 2 part files
        part1 = {
            "id": "libraries-tag--overview",
            "title": "タグライブラリ",
            "official_doc_urls": ["https://example.com/tag.html"],
            "index": [
                {"id": "overview", "title": "概要", "hints": ["tag", "jsp"]}
            ],
            "sections": {
                "overview": "タグライブラリの概要。\n\n画像: assets/libraries-tag--overview/image.png"
            }
        }
        part2 = {
            "id": "libraries-tag--usage",
            "title": "タグライブラリ",
            "official_doc_urls": ["https://example.com/tag.html"],
            "index": [
                {"id": "usage", "title": "使い方", "hints": ["usage"]}
            ],
            "sections": {
                "usage": "タグの使い方。\n\n図: assets/libraries-tag--usage/diagram.png"
            }
        }

        os.makedirs(f"{ctx.knowledge_cache_dir}/component/libraries", exist_ok=True)
        write_json(f"{ctx.knowledge_cache_dir}/component/libraries/libraries-tag--overview.json", part1)
        write_json(f"{ctx.knowledge_cache_dir}/component/libraries/libraries-tag--usage.json", part2)

        # Create assets
        os.makedirs(f"{ctx.knowledge_cache_dir}/component/libraries/assets/libraries-tag--overview", exist_ok=True)
        os.makedirs(f"{ctx.knowledge_cache_dir}/component/libraries/assets/libraries-tag--usage", exist_ok=True)
        with open(f"{ctx.knowledge_cache_dir}/component/libraries/assets/libraries-tag--overview/image.png", "w") as f:
            f.write("fake-image")
        with open(f"{ctx.knowledge_cache_dir}/component/libraries/assets/libraries-tag--usage/diagram.png", "w") as f:
            f.write("fake-diagram")

        # Setup: classified.json with split info
        classified = {
            "version": "6",
            "generated_at": "2026-01-01T00:00:00Z",
            "files": [
                {
                    "id": "libraries-tag--overview",
                    "source_path": "test.rst",
                    "format": "rst",
                    "filename": "test.rst",
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
                },
                {
                    "id": "libraries-tag--usage",
                    "source_path": "test.rst",
                    "format": "rst",
                    "filename": "test.rst",
                    "type": "component",
                    "category": "libraries",
                    "output_path": "component/libraries/libraries-tag--usage.json",
                    "assets_dir": "component/libraries/assets/libraries-tag--usage/",
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
        merged_catalog = MergeSplitFiles(ctx).run()

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

        # Verify: part files preserved in cache (not deleted)
        assert os.path.exists(f"{ctx.knowledge_cache_dir}/component/libraries/libraries-tag--overview.json")
        assert os.path.exists(f"{ctx.knowledge_cache_dir}/component/libraries/libraries-tag--usage.json")

        # Verify: assets consolidated
        assert os.path.exists(f"{ctx.knowledge_dir}/component/libraries/assets/libraries-tag/image.png")
        assert os.path.exists(f"{ctx.knowledge_dir}/component/libraries/assets/libraries-tag/diagram.png")
        assert not os.path.exists(f"{ctx.knowledge_dir}/component/libraries/assets/libraries-tag-1")
        assert not os.path.exists(f"{ctx.knowledge_dir}/component/libraries/assets/libraries-tag-2")

        # Verify: merged catalog returned (not written to classified.json)
        assert merged_catalog is not None
        ids = [f["id"] for f in merged_catalog["files"]]
        assert "libraries-tag" in ids
        assert "libraries-tag--overview" not in ids
        assert "libraries-tag--usage" not in ids

        merged_entry = next(f for f in merged_catalog["files"] if f["id"] == "libraries-tag")
        assert "split_info" not in merged_entry
        assert "section_range" not in merged_entry
        assert merged_entry["output_path"] == "component/libraries/libraries-tag.json"

    def test_merge_skips_incomplete_parts(self, ctx):
        """Skip merge if not all parts exist."""
        from merge import MergeSplitFiles

        # Setup: only part 1 and 2 exist, part 3 missing
        part1 = {"id": "test--section-1", "title": "Test", "official_doc_urls": [],
                 "index": [], "sections": {"s1": "content"}}
        part2 = {"id": "test--section-2", "title": "Test", "official_doc_urls": [],
                 "index": [], "sections": {"s2": "content"}}

        os.makedirs(f"{ctx.knowledge_cache_dir}/component/test", exist_ok=True)
        write_json(f"{ctx.knowledge_cache_dir}/component/test/test--section-1.json", part1)
        write_json(f"{ctx.knowledge_cache_dir}/component/test/test--section-2.json", part2)
        # part3 not created

        classified = {
            "version": "6",
            "generated_at": "2026-01-01T00:00:00Z",
            "files": [
                {
                    "id": "test--section-1",
                    "source_path": "test.rst",
                    "format": "rst",
                    "filename": "test.rst",
                    "type": "component",
                    "category": "test",
                    "output_path": "component/test/test--section-1.json",
                    "assets_dir": "component/test/assets/test--section-1/",
                    "split_info": {"is_split": True, "original_id": "test", "part": 1, "total_parts": 3}
                },
                {
                    "id": "test--section-2",
                    "source_path": "test.rst",
                    "format": "rst",
                    "filename": "test.rst",
                    "type": "component",
                    "category": "test",
                    "output_path": "component/test/test--section-2.json",
                    "assets_dir": "component/test/assets/test--section-2/",
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
        # Parts preserved in cache (not deleted)
        assert os.path.exists(f"{ctx.knowledge_cache_dir}/component/test/test--section-1.json")
        assert os.path.exists(f"{ctx.knowledge_cache_dir}/component/test/test--section-2.json")

        # Verify: classified.json unchanged
        updated = load_json(ctx.classified_list_path)
        assert len(updated["files"]) == 3

    def test_no_split_files_noop(self, ctx):
        """No-op when there are no split files."""
        from merge import MergeSplitFiles

        # Setup: only non-split files
        regular = {"id": "regular", "title": "Regular", "official_doc_urls": [],
                   "index": [], "sections": {"s1": "content"}}

        os.makedirs(f"{ctx.knowledge_cache_dir}/component/test", exist_ok=True)
        write_json(f"{ctx.knowledge_cache_dir}/component/test/regular.json", regular)

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
        from merge import MergeSplitFiles

        # Setup: 1 split file (2 parts) + 1 non-split file
        part1 = {"id": "split--section-1", "title": "Split", "official_doc_urls": [],
                 "index": [{"id": "s1", "title": "S1", "hints": []}],
                 "sections": {"s1": "part1"}}
        part2 = {"id": "split--section-2", "title": "Split", "official_doc_urls": [],
                 "index": [{"id": "s2", "title": "S2", "hints": []}],
                 "sections": {"s2": "part2"}}
        regular = {"id": "regular", "title": "Regular", "official_doc_urls": [],
                   "index": [{"id": "r1", "title": "R1", "hints": []}],
                   "sections": {"r1": "content"}}

        os.makedirs(f"{ctx.knowledge_cache_dir}/component/test", exist_ok=True)
        write_json(f"{ctx.knowledge_cache_dir}/component/test/split--section-1.json", part1)
        write_json(f"{ctx.knowledge_cache_dir}/component/test/split--section-2.json", part2)
        write_json(f"{ctx.knowledge_cache_dir}/component/test/regular.json", regular)

        classified = {
            "version": "6",
            "generated_at": "2026-01-01T00:00:00Z",
            "files": [
                {
                    "id": "split--section-1",
                    "source_path": "test.rst",
                    "format": "rst",
                    "filename": "test.rst",
                    "type": "component",
                    "category": "test",
                    "output_path": "component/test/split--section-1.json",
                    "assets_dir": "component/test/assets/split--section-1/",
                    "split_info": {"is_split": True, "original_id": "split", "part": 1, "total_parts": 2}
                },
                {
                    "id": "split--section-2",
                    "source_path": "test.rst",
                    "format": "rst",
                    "filename": "test.rst",
                    "type": "component",
                    "category": "test",
                    "output_path": "component/test/split--section-2.json",
                    "assets_dir": "component/test/assets/split--section-2/",
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
        merged_catalog = MergeSplitFiles(ctx).run()

        # Verify: split files merged
        assert os.path.exists(f"{ctx.knowledge_dir}/component/test/split.json")
        merged = load_json(f"{ctx.knowledge_dir}/component/test/split.json")
        assert merged["id"] == "split"
        assert len(merged["sections"]) == 2

        # Verify: non-split file preserved
        assert os.path.exists(f"{ctx.knowledge_dir}/component/test/regular.json")
        reg = load_json(f"{ctx.knowledge_dir}/component/test/regular.json")
        assert reg["id"] == "regular"

        # Verify: merged catalog returned has both
        assert merged_catalog is not None
        ids = [f["id"] for f in merged_catalog["files"]]
        assert "split" in ids
        assert "regular" in ids
        assert "split--section-1" not in ids
        assert "split--section-2" not in ids

    def test_merge_warns_on_index_section_mismatch(self, ctx, caplog):
        """Merge must log warning when merged result has index-section mismatch."""
        import logging
        from merge import MergeSplitFiles

        part1 = {
            "id": "libs-bind--p1",
            "title": "Data Bind",
            "official_doc_urls": ["https://example.com"],
            "index": [
                {"id": "ext", "title": "拡張", "hints": ["extension"]}
            ],
            "sections": {"section-ext": "拡張の内容"}
        }
        part2 = {
            "id": "libs-bind--p2",
            "title": "Data Bind",
            "official_doc_urls": ["https://example.com"],
            "index": [
                {"id": "csv", "title": "CSV", "hints": ["csv"]}
            ],
            "sections": {"csv": "CSV content"}
        }

        os.makedirs(f"{ctx.knowledge_cache_dir}/component/libraries", exist_ok=True)
        write_json(f"{ctx.knowledge_cache_dir}/component/libraries/libs-bind--p1.json", part1)
        write_json(f"{ctx.knowledge_cache_dir}/component/libraries/libs-bind--p2.json", part2)

        catalog = load_json(ctx.classified_list_path)
        catalog["files"] = [
            {
                "source_path": "tests/fixtures/sample_source.rst", "format": "rst",
                "type": "component", "category": "libraries",
                "id": "libs-bind--p1",
                "output_path": "component/libraries/libs-bind--p1.json",
                "assets_dir": "component/libraries/assets/libs-bind--p1/",
                "split_info": {"is_split": True, "original_id": "libs-bind", "part": 1, "total": 2}
            },
            {
                "source_path": "tests/fixtures/sample_source.rst", "format": "rst",
                "type": "component", "category": "libraries",
                "id": "libs-bind--p2",
                "output_path": "component/libraries/libs-bind--p2.json",
                "assets_dir": "component/libraries/assets/libs-bind--p2/",
                "split_info": {"is_split": True, "original_id": "libs-bind", "part": 2, "total": 2}
            }
        ]
        write_json(ctx.classified_list_path, catalog)

        with caplog.at_level(logging.WARNING, logger="knowledge_creator"):
            MergeSplitFiles(ctx).run()

        warning_messages = [r.message for r in caplog.records if "index-section mismatch" in r.message]
        assert len(warning_messages) > 0, "No index-section mismatch warning logged"
        assert any("libs-bind" in msg for msg in warning_messages)

    def test_merge_index_order_is_part_sequential(self, ctx):
        """Merged index must follow part1 all sections -> part2 new sections order."""
        from merge import MergeSplitFiles

        part1 = {
            "id": "libraries-tag--p1",
            "title": "タグ",
            "official_doc_urls": ["https://example.com"],
            "index": [
                {"id": "section-a", "title": "A", "hints": ["a"]},
                {"id": "section-b", "title": "B", "hints": ["b"]}
            ],
            "sections": {"section-a": "content A", "section-b": "content B"}
        }
        part2 = {
            "id": "libraries-tag--p2",
            "title": "タグ",
            "official_doc_urls": ["https://example.com"],
            "index": [
                {"id": "section-b", "title": "B", "hints": ["b", "extra"]},
                {"id": "section-c", "title": "C", "hints": ["c"]},
                {"id": "section-d", "title": "D", "hints": ["d"]}
            ],
            "sections": {
                "section-b": "content B moved",
                "section-c": "content C",
                "section-d": "content D"
            }
        }

        os.makedirs(f"{ctx.knowledge_cache_dir}/component/libraries", exist_ok=True)
        write_json(f"{ctx.knowledge_cache_dir}/component/libraries/libraries-tag--p1.json", part1)
        write_json(f"{ctx.knowledge_cache_dir}/component/libraries/libraries-tag--p2.json", part2)

        catalog = load_json(ctx.classified_list_path)
        catalog["files"] = [
            {
                "source_path": "tests/fixtures/sample_source.rst", "format": "rst",
                "type": "component", "category": "libraries",
                "id": "libraries-tag--p1",
                "output_path": "component/libraries/libraries-tag--p1.json",
                "assets_dir": "component/libraries/assets/libraries-tag--p1/",
                "split_info": {"is_split": True, "original_id": "libraries-tag", "part": 1, "total": 2}
            },
            {
                "source_path": "tests/fixtures/sample_source.rst", "format": "rst",
                "type": "component", "category": "libraries",
                "id": "libraries-tag--p2",
                "output_path": "component/libraries/libraries-tag--p2.json",
                "assets_dir": "component/libraries/assets/libraries-tag--p2/",
                "split_info": {"is_split": True, "original_id": "libraries-tag", "part": 2, "total": 2}
            }
        ]
        write_json(ctx.classified_list_path, catalog)

        MergeSplitFiles(ctx).run()

        merged = load_json(f"{ctx.knowledge_dir}/component/libraries/libraries-tag.json")
        index_ids = [e["id"] for e in merged["index"]]
        assert index_ids == ["section-a", "section-b", "section-c", "section-d"]

        section_b_entry = [e for e in merged["index"] if e["id"] == "section-b"][0]
        assert "b" in section_b_entry["hints"]
        assert "extra" in section_b_entry["hints"]

    def test_merge_skips_group_when_cache_missing(self, ctx, caplog):
        """If any split part's cache file is missing, skip that group entirely."""
        import logging
        from merge import MergeSplitFiles

        part1 = {
            "id": "libs-comp--p1", "title": "Comparison",
            "official_doc_urls": [], "processing_patterns": [],
            "index": [{"id": "overview", "title": "概要", "hints": ["x"]}],
            "sections": {"overview": "content for overview section here"}
        }
        os.makedirs(f"{ctx.knowledge_cache_dir}/component/libraries", exist_ok=True)
        write_json(f"{ctx.knowledge_cache_dir}/component/libraries/libs-comp--p1.json", part1)
        # Part 2 does NOT exist in cache

        catalog = load_json(ctx.classified_list_path)
        catalog["files"] = [
            {
                "source_path": "tests/fixtures/sample_source.rst", "format": "rst",
                "type": "component", "category": "libraries",
                "id": "libs-comp--p1",
                "output_path": "component/libraries/libs-comp--p1.json",
                "assets_dir": "component/libraries/assets/libs-comp--p1/",
                "split_info": {"is_split": True, "original_id": "libs-comp", "part": 1, "total": 2}
            },
            {
                "source_path": "tests/fixtures/sample_source.rst", "format": "rst",
                "type": "component", "category": "libraries",
                "id": "libs-comp--p2",
                "output_path": "component/libraries/libs-comp--p2.json",
                "assets_dir": "component/libraries/assets/libs-comp--p2/",
                "split_info": {"is_split": True, "original_id": "libs-comp", "part": 2, "total": 2}
            }
        ]
        write_json(ctx.classified_list_path, catalog)

        with caplog.at_level(logging.INFO, logger="knowledge_creator"):
            MergeSplitFiles(ctx).run()

        merged_path = f"{ctx.knowledge_dir}/component/libraries/libs-comp.json"
        assert not os.path.exists(merged_path), "Merged file must not exist when cache is incomplete"
        assert any("SKIP" in r.message and "libs-comp" in r.message for r in caplog.records)


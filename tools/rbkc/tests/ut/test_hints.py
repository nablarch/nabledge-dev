"""Unit tests for hints.py — build_hints_index file_id normalization."""
from __future__ import annotations

import json
import pytest


class TestBuildHintsIndexNormalization:
    """build_hints_index normalizes KC base_id underscores to hyphens.

    KC cache uses original filenames (e.g. adapters-doma_adaptor).
    RBKC generates file_ids with _ replaced by - (e.g. adapters-doma-adaptor).
    The index keys must use RBKC-style (hyphens only) so lookup_hints works.
    """

    def _build(self, cache_dir):
        from scripts.create.hints import build_hints_index
        return build_hints_index(cache_dir)

    def _write_kc_file(self, knowledge_dir, file_id, section_title, hints):
        """Write a minimal KC-format JSON file."""
        data = {
            "id": file_id,
            "index": [{"title": section_title, "hints": hints}],
            "sections": {},
        }
        path = knowledge_dir / f"{file_id}.json"
        path.write_text(json.dumps(data), encoding="utf-8")

    def test_underscore_id_normalized_to_hyphen(self, tmp_path):
        """KC file_id with underscore is indexed with hyphen key."""
        kd = tmp_path / "knowledge"
        kd.mkdir()
        self._write_kc_file(kd, "adapters-doma_adaptor", "概要", ["DomAdapter"])
        index = self._build(tmp_path)
        assert "adapters-doma-adaptor" in index
        assert index["adapters-doma-adaptor"].get("概要") == ["DomAdapter"]

    def test_hyphen_only_id_unchanged(self, tmp_path):
        """KC file_id with only hyphens stays as-is."""
        kd = tmp_path / "knowledge"
        kd.mkdir()
        self._write_kc_file(kd, "about-nablarch-architecture", "概要", ["hint1"])
        index = self._build(tmp_path)
        assert "about-nablarch-architecture" in index

    def test_multiple_underscores_all_normalized(self, tmp_path):
        """Multiple underscores in a KC file_id are all replaced."""
        kd = tmp_path / "knowledge"
        kd.mkdir()
        self._write_kc_file(kd, "some_file_with_many_underscores", "Section", ["h1"])
        index = self._build(tmp_path)
        assert "some-file-with-many-underscores" in index
        assert "some_file_with_many_underscores" not in index

    def test_split_suffix_stripped_then_normalized(self, tmp_path):
        """KC split files (--s1, --s2) are grouped and normalized."""
        kd = tmp_path / "knowledge"
        kd.mkdir()
        self._write_kc_file(kd, "adapters-doma_adaptor--s1", "概要", ["h1"])
        self._write_kc_file(kd, "adapters-doma_adaptor--s2", "詳細", ["h2"])
        index = self._build(tmp_path)
        assert "adapters-doma-adaptor" in index
        entry = index["adapters-doma-adaptor"]
        assert "概要" in entry
        assert "詳細" in entry


class TestBuildHintsIndexCatalogSplitHandling:
    """catalog_index must use part-1 entry for split files.

    When a file is split into --s1/--s2/.../--sN, each part has its own
    catalog entry. catalog_index must keep the part-1 entry (which contains
    the RST-aligned section_range.sections), not the last part's entry
    (which may contain KC-level titles).
    """

    def _build(self, cache_dir, catalog_path, repo_root=None):
        from scripts.create.hints import build_hints_index
        return build_hints_index(cache_dir, catalog_path, repo_root)

    def _write_catalog(self, path, entries):
        path.write_text(json.dumps({"files": entries}), encoding="utf-8")

    def _write_kc_file(self, knowledge_dir, file_id, index_entries):
        data = {"id": file_id, "index": index_entries, "sections": {}}
        (knowledge_dir / f"{file_id}.json").write_text(json.dumps(data), encoding="utf-8")

    def test_part1_sections_used_when_multiple_splits(self, tmp_path):
        """For split files, part-1 catalog entry's section_range.sections are used."""
        kd = tmp_path / "knowledge"
        kd.mkdir()
        cat_path = tmp_path / "catalog.json"

        # Part 1: RST-aligned sections
        # Part 2: KC-level sections (should NOT be used as keys)
        self._write_catalog(cat_path, [
            {
                "id": "file-a--s1", "base_name": "file-a",
                "source_path": "",
                "section_range": {"sections": ["RST概要", "RST設定"]},
            },
            {
                "id": "file-a--s2", "base_name": "file-a",
                "source_path": "",
                "section_range": {"sections": ["KC詳細タイトル"]},
            },
        ])
        self._write_kc_file(kd, "file-a--s1", [
            {"title": "RST概要", "hints": ["h1"]},
        ])
        self._write_kc_file(kd, "file-a--s2", [
            {"title": "KC詳細タイトル", "hints": ["h2"]},
        ])

        index = self._build(tmp_path, cat_path)
        # Keys must come from part-1 sections (RST-aligned)
        assert "RST概要" in index.get("file-a", {})
        assert "KC詳細タイトル" not in index.get("file-a", {})

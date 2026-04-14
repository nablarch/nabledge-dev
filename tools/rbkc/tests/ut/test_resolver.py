"""Unit tests for Phase 4: cross-reference resolution and asset copying."""
import shutil
from pathlib import Path

import pytest

from scripts.resolver import AssetRef, build_label_map, collect_asset_refs, copy_assets


# ---------------------------------------------------------------------------
# build_label_map
# ---------------------------------------------------------------------------

class TestBuildLabelMap:
    def test_single_label(self, tmp_path):
        (tmp_path / "page.rst").write_text(".. _my-label:\n\nContent.\n")
        label_map = build_label_map(tmp_path)
        assert label_map["my-label"] == "page"

    def test_multiple_labels_in_one_file(self, tmp_path):
        (tmp_path / "page.rst").write_text(
            ".. _alpha:\n\n.. _beta:\n\nContent.\n"
        )
        label_map = build_label_map(tmp_path)
        assert label_map["alpha"] == "page"
        assert label_map["beta"] == "page"

    def test_multiple_files(self, tmp_path):
        (tmp_path / "a.rst").write_text(".. _label-a:\n\n")
        (tmp_path / "b.rst").write_text(".. _label-b:\n\n")
        label_map = build_label_map(tmp_path)
        assert label_map["label-a"] == "a"
        assert label_map["label-b"] == "b"

    def test_empty_dir(self, tmp_path):
        assert build_label_map(tmp_path) == {}

    def test_backtick_quoted_label(self, tmp_path):
        """RST labels can be quoted with backticks for labels containing special chars."""
        (tmp_path / "page.rst").write_text(".. _`label with spaces`:\n\nContent.\n")
        label_map = build_label_map(tmp_path)
        assert "label with spaces" in label_map

    def test_custom_path_to_id(self, tmp_path):
        subdir = tmp_path / "sub"
        subdir.mkdir()
        (subdir / "page.rst").write_text(".. _label:\n\n")
        label_map = build_label_map(
            tmp_path, path_to_id=lambda p: "custom-" + p.stem
        )
        assert label_map["label"] == "custom-page"

    def test_recursive_search(self, tmp_path):
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "nested.rst").write_text(".. _nested-label:\n\n")
        label_map = build_label_map(tmp_path)
        assert "nested-label" in label_map


# ---------------------------------------------------------------------------
# collect_asset_refs
# ---------------------------------------------------------------------------

class TestCollectAssetRefs:
    def _make_rst_with_image(self, tmp_path: Path, img_rel: str = "images/diagram.png") -> Path:
        img_path = tmp_path / img_rel
        img_path.parent.mkdir(parents=True, exist_ok=True)
        img_path.write_bytes(b"\x89PNG")
        rst_path = tmp_path / "doc.rst"
        rst_path.write_text(
            f"Title\n=====\n\n.. image:: {img_rel}\n   :alt: A diagram\n\n"
        )
        return rst_path

    def test_image_directive(self, tmp_path):
        rst_path = self._make_rst_with_image(tmp_path)
        refs = collect_asset_refs(rst_path, "doc")
        assert len(refs) == 1
        assert refs[0].dest_rel == "assets/doc/diagram.png"
        assert refs[0].source_path.name == "diagram.png"

    def test_figure_directive(self, tmp_path):
        img = tmp_path / "img.png"
        img.write_bytes(b"\x89PNG")
        rst = tmp_path / "doc.rst"
        rst.write_text("Title\n=====\n\n.. figure:: img.png\n\n   Caption.\n\n")
        refs = collect_asset_refs(rst, "doc")
        assert len(refs) == 1
        assert refs[0].dest_rel == "assets/doc/img.png"

    def test_missing_image_skipped(self, tmp_path):
        """If source file does not exist, skip the ref."""
        rst = tmp_path / "doc.rst"
        rst.write_text("Title\n=====\n\n.. image:: nonexistent.png\n\n")
        refs = collect_asset_refs(rst, "doc")
        assert refs == []

    def test_download_directive(self, tmp_path):
        dl = tmp_path / "sample.zip"
        dl.write_bytes(b"PK")
        rst = tmp_path / "doc.rst"
        rst.write_text(
            "Get :download:`sample file <sample.zip>` here.\n"
        )
        refs = collect_asset_refs(rst, "doc")
        assert len(refs) == 1
        assert refs[0].dest_rel == "assets/doc/sample.zip"

    def test_no_assets(self, tmp_path):
        rst = tmp_path / "doc.rst"
        rst.write_text("Title\n=====\n\nNo assets here.\n")
        refs = collect_asset_refs(rst, "doc")
        assert refs == []

    def test_dedup_same_asset(self, tmp_path):
        """Same image referenced twice → only one ref."""
        img = tmp_path / "icon.png"
        img.write_bytes(b"\x89PNG")
        rst = tmp_path / "doc.rst"
        rst.write_text(
            ".. image:: icon.png\n\n.. image:: icon.png\n   :alt: again\n\n"
        )
        refs = collect_asset_refs(rst, "doc")
        assert len(refs) == 1


# ---------------------------------------------------------------------------
# copy_assets
# ---------------------------------------------------------------------------

class TestCopyAssets:
    def test_copies_file(self, tmp_path):
        src = tmp_path / "src" / "img.png"
        src.parent.mkdir()
        src.write_bytes(b"\x89PNG")
        out_dir = tmp_path / "out"

        refs = [AssetRef(source_path=src, dest_rel="assets/doc/img.png")]
        copied = copy_assets(refs, out_dir)

        assert len(copied) == 1
        dest = out_dir / "assets" / "doc" / "img.png"
        assert dest.exists()
        assert dest.read_bytes() == b"\x89PNG"

    def test_creates_parent_dirs(self, tmp_path):
        src = tmp_path / "src.txt"
        src.write_text("hello")
        out_dir = tmp_path / "out"

        refs = [AssetRef(source_path=src, dest_rel="assets/a/b/c/src.txt")]
        copy_assets(refs, out_dir)

        assert (out_dir / "assets" / "a" / "b" / "c" / "src.txt").exists()

    def test_empty_refs(self, tmp_path):
        copied = copy_assets([], tmp_path / "out")
        assert copied == []

    def test_returns_dest_paths(self, tmp_path):
        src = tmp_path / "f.txt"
        src.write_text("x")
        out = tmp_path / "out"
        refs = [AssetRef(source_path=src, dest_rel="assets/x/f.txt")]
        copied = copy_assets(refs, out)
        assert copied[0] == out / "assets" / "x" / "f.txt"

    def test_skip_missing_source(self, tmp_path):
        """Missing source files are skipped, not raised."""
        refs = [AssetRef(
            source_path=tmp_path / "missing.png",
            dest_rel="assets/x/missing.png",
        )]
        copied = copy_assets(refs, tmp_path / "out")
        assert copied == []

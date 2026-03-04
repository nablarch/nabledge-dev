"""Tests for steps/source_tracker.py"""
import os
import pytest
from steps.common import write_json, load_json
from steps.source_tracker import _compute_hash, save_hashes, detect_changed


def _make_classified(files):
    """Helper to create classified.json structure."""
    return {
        "version": "6", "generated_at": "2026-01-01T00:00:00Z",
        "files": [{
            "id": f["id"],
            "source_path": f["source_path"],
            "format": "rst", "filename": f["id"] + ".rst",
            "type": "component", "category": "handlers",
            "output_path": f"component/handlers/{f['id']}.json",
            "assets_dir": f"component/handlers/assets/{f['id']}/"
        } for f in files]
    }


class TestComputeHash:

    def test_same_content_same_hash(self, tmp_path):
        (tmp_path / "a.txt").write_text("hello")
        (tmp_path / "b.txt").write_text("hello")
        assert _compute_hash(str(tmp_path / "a.txt")) == _compute_hash(str(tmp_path / "b.txt"))

    def test_different_content_different_hash(self, tmp_path):
        (tmp_path / "a.txt").write_text("hello")
        (tmp_path / "b.txt").write_text("world")
        assert _compute_hash(str(tmp_path / "a.txt")) != _compute_hash(str(tmp_path / "b.txt"))


class TestSaveHashes:

    def test_saves_hash_for_each_file(self, ctx):
        src_path = f"{ctx.repo}/src/test.rst"
        os.makedirs(os.path.dirname(src_path), exist_ok=True)
        with open(src_path, "w") as f:
            f.write("content")

        classified = _make_classified([
            {"id": "test-file", "source_path": "src/test.rst"}
        ])
        write_json(ctx.classified_list_path, classified)

        save_hashes(ctx)

        hash_path = f"{ctx.log_dir}/source_hashes.json"
        assert os.path.exists(hash_path)
        data = load_json(hash_path)
        assert "test-file" in data
        assert len(data["test-file"]["hash"]) == 64  # SHA256 hex length


class TestDetectChanged:

    def test_no_hash_file_returns_none(self, ctx):
        """No previous hash file → return None (= treat as all new)."""
        write_json(ctx.classified_list_path, _make_classified([]))
        assert detect_changed(ctx) is None

    def test_unchanged_file_returns_empty(self, ctx):
        src_path = f"{ctx.repo}/src/test.rst"
        os.makedirs(os.path.dirname(src_path), exist_ok=True)
        with open(src_path, "w") as f:
            f.write("content")

        classified = _make_classified([
            {"id": "test-file", "source_path": "src/test.rst"}
        ])
        write_json(ctx.classified_list_path, classified)
        save_hashes(ctx)

        assert detect_changed(ctx) == []

    def test_changed_file_detected(self, ctx):
        src_path = f"{ctx.repo}/src/test.rst"
        os.makedirs(os.path.dirname(src_path), exist_ok=True)
        with open(src_path, "w") as f:
            f.write("original")

        classified = _make_classified([
            {"id": "test-file", "source_path": "src/test.rst"}
        ])
        write_json(ctx.classified_list_path, classified)
        save_hashes(ctx)

        # Modify source
        with open(src_path, "w") as f:
            f.write("modified")

        assert detect_changed(ctx) == ["test-file"]

    def test_new_file_detected_as_changed(self, ctx):
        """File not in previous hashes → detected as changed."""
        write_json(f"{ctx.log_dir}/source_hashes.json", {})

        src_path = f"{ctx.repo}/src/new.rst"
        os.makedirs(os.path.dirname(src_path), exist_ok=True)
        with open(src_path, "w") as f:
            f.write("new content")

        classified = _make_classified([
            {"id": "new-file", "source_path": "src/new.rst"}
        ])
        write_json(ctx.classified_list_path, classified)

        assert detect_changed(ctx) == ["new-file"]

    def test_multiple_files_only_changed_reported(self, ctx):
        """2 files: 1 unchanged, 1 changed → only changed returned."""
        for name, content in [("a", "aaa"), ("b", "bbb")]:
            p = f"{ctx.repo}/src/{name}.rst"
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w") as f:
                f.write(content)

        classified = _make_classified([
            {"id": "file-a", "source_path": "src/a.rst"},
            {"id": "file-b", "source_path": "src/b.rst"},
        ])
        write_json(ctx.classified_list_path, classified)
        save_hashes(ctx)

        # Change only file-b
        with open(f"{ctx.repo}/src/b.rst", "w") as f:
            f.write("bbb-changed")

        result = detect_changed(ctx)
        assert result == ["file-b"]

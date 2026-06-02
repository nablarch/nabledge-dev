"""Unit tests for run.py — CLI layer only (argument validation, command routing)."""
# No create-side logic tests: verify.py is the quality gate for output correctness.
# See .claude/rules/rbkc.md for the test coverage policy.

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

_REPO_ROOT = Path(__file__).parents[4]  # repo root


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make_file_info(fmt: str = "rst") -> MagicMock:
    """Return a FileInfo mock using a real file under repo root so relative_to() works."""
    fi = MagicMock()
    fi.format = fmt
    fi.file_id = "test-file"
    fi.output_path = "subdir/test.json"
    # Use a real file under repo_root to satisfy relative_to() in verify()
    fi.source_path = _REPO_ROOT / "tools/rbkc/tests/ut/test_run.py"
    return fi


def _make_valid_json(output_dir: Path, rel: str) -> Path:
    p = output_dir / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({
        "id": "test-file",
        "title": "Title",
        "no_knowledge_content": False,
        "sections": [{"id": "s1", "title": "概要", "content": "Content."}],
    }), encoding="utf-8")
    return p


def _make_valid_docs_md(docs_dir: Path, rel: str) -> Path:
    p = docs_dir / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("# Title\n\n## 概要\n\nContent.\n", encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# V-skip: verify() FAIL on missing JSON
# ---------------------------------------------------------------------------

class TestVerifyMissingJson:
    """verify() must FAIL (return False) when JSON file is missing, not silently skip."""

    def _run_verify(self, tmp_path, file_infos):
        from scripts.run import verify
        output_dir = tmp_path / "knowledge"
        output_dir.mkdir()
        (output_dir.parent / "docs").mkdir()

        with patch("scripts.run.scan_sources", return_value=[MagicMock()]), \
             patch("scripts.run.classify_sources", return_value=file_infos), \
             patch("scripts.run.build_label_map", return_value={}), \
             patch("scripts.create.scan._source_roots", return_value=[]):
            return verify(
                version="6",
                repo_root=_REPO_ROOT,
                output_dir=output_dir,
                files=["dummy/source.rst"],
            )

    def test_fail_when_json_missing(self, tmp_path):
        """verify returns False when JSON output file does not exist."""
        fi = _make_file_info()
        # Do NOT create the JSON file → should FAIL
        result = self._run_verify(tmp_path, [fi])
        assert result is False

    def test_pass_when_json_present(self, tmp_path):
        """verify returns True (for this check) when JSON and docs MD exist and are valid."""
        fi = _make_file_info()
        output_dir = tmp_path / "knowledge"
        output_dir.mkdir()
        _make_valid_json(output_dir, fi.output_path)
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        _make_valid_docs_md(docs_dir, Path(fi.output_path).with_suffix(".md"))

        from scripts.run import verify
        with patch("scripts.run.scan_sources", return_value=[MagicMock()]), \
             patch("scripts.run.classify_sources", return_value=[fi]), \
             patch("scripts.run.build_label_map", return_value={}), \
             patch("scripts.run.verify_file", return_value=[]), \
             patch("scripts.run.check_source_links", return_value=[]), \
             patch("scripts.run.verify_docs_md", return_value=[]), \
             patch("scripts.run.check_json_docs_md_consistency", return_value=[]), \
             patch("scripts.create.scan._source_roots", return_value=[]):
            result = verify(
                version="6",
                repo_root=_REPO_ROOT,
                output_dir=output_dir,
                files=["dummy/source.rst"],
            )
        assert result is True


# ---------------------------------------------------------------------------
# V-skip: verify() FAIL on missing docs MD
# ---------------------------------------------------------------------------

class TestVerifyMissingDocsMd:
    """verify() must FAIL when docs MD is missing for non-no_knowledge_content files."""

    def _run_verify(self, tmp_path, fi, json_data: dict):
        from scripts.run import verify
        output_dir = tmp_path / "knowledge"
        output_dir.mkdir()
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        # Write JSON file
        json_path = output_dir / fi.output_path
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(json_data), encoding="utf-8")
        # Do NOT create docs MD

        with patch("scripts.run.scan_sources", return_value=[MagicMock()]), \
             patch("scripts.run.classify_sources", return_value=[fi]), \
             patch("scripts.run.build_label_map", return_value={}), \
             patch("scripts.run.verify_file", return_value=[]), \
             patch("scripts.run.check_source_links", return_value=[]), \
             patch("scripts.create.scan._source_roots", return_value=[]):
            return verify(
                version="6",
                repo_root=_REPO_ROOT,
                output_dir=output_dir,
                files=["dummy/source.rst"],
            )

    def test_fail_when_docs_md_missing_for_knowledge_file(self, tmp_path):
        """verify returns False when docs MD is missing for a non-NKC file."""
        fi = _make_file_info()
        json_data = {
            "id": "test-file", "title": "Title", "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "概要", "content": "Content."}],
        }
        result = self._run_verify(tmp_path, fi, json_data)
        assert result is False

    def test_pass_when_docs_md_missing_for_no_knowledge_content(self, tmp_path):
        """verify returns True when docs MD is absent but no_knowledge_content=True."""
        fi = _make_file_info()
        json_data = {
            "id": "test-file", "title": "Title", "no_knowledge_content": True,
            "sections": [],
        }
        result = self._run_verify(tmp_path, fi, json_data)
        assert result is True


# ---------------------------------------------------------------------------
# index.toon must NOT be generated (legacy file removed)
# ---------------------------------------------------------------------------

class TestIndexToonNotGenerated:
    """create/update/delete must not produce index.toon."""

    def _patches(self, tmp_path):
        output_dir = tmp_path / "knowledge"
        output_dir.mkdir()
        return output_dir, [
            patch("scripts.run.scan_sources", return_value=[]),
            patch("scripts.run.classify_sources", return_value=[]),
            patch("scripts.run.build_label_doc_map", return_value=({}, {})),
            patch("scripts.run._load_sheet_subtype_map", return_value={}),
            patch("scripts.run.generate_index_md"),
            patch("scripts.run.generate_docs"),
            patch("scripts.run.copy_assets"),
            patch("scripts.create.scan._source_roots", return_value=[]),
        ]

    def test_create_does_not_write_index_toon(self, tmp_path):
        """create() must not produce index.toon."""
        from scripts.run import create
        output_dir, patches = self._patches(tmp_path)
        with patches[0], patches[1], patches[2], patches[3], \
             patches[4], patches[5], patches[6], patches[7]:
            create(version="6", repo_root=_REPO_ROOT, output_dir=output_dir,
                   state_dir=tmp_path, files=None)
        assert not (output_dir / "index.toon").exists()

    def test_update_does_not_write_index_toon(self, tmp_path):
        """update() must not produce index.toon."""
        from scripts.run import update
        output_dir, patches = self._patches(tmp_path)
        with patches[0], patches[1], patches[2], patches[3], \
             patches[4], patches[5], patches[6], patches[7]:
            update(version="6", repo_root=_REPO_ROOT, output_dir=output_dir,
                   state_dir=tmp_path, files=None)
        assert not (output_dir / "index.toon").exists()

    def test_delete_does_not_write_index_toon(self, tmp_path):
        """delete() must not produce index.toon."""
        from scripts.run import delete
        output_dir, patches = self._patches(tmp_path)
        with patches[0], patches[1], \
             patch("scripts.run.build_label_doc_map", return_value=({}, {})), \
             patch("scripts.run.diff_snapshot", return_value=([], [], [])), \
             patch("scripts.run.load_snapshot", return_value={"files": {}}), \
             patch("scripts.run.make_snapshot", return_value={"files": {}}), \
             patch("scripts.run.save_snapshot"), \
             patches[4], patches[5], patches[6], patches[7]:
            delete(version="6", repo_root=_REPO_ROOT, output_dir=output_dir,
                   state_dir=tmp_path, files=None)
        assert not (output_dir / "index.toon").exists()


# ---------------------------------------------------------------------------
# Task 2-F: javadoc_generate wired into create() and update()
# ---------------------------------------------------------------------------

class TestJavadocGenerateWiring:
    """create() and update() must call javadoc_generate() and pass javadoc_map to RST converter."""

    def _patches_for_create(self, tmp_path):
        output_dir = tmp_path / "knowledge"
        output_dir.mkdir()
        from unittest.mock import patch
        return output_dir, [
            patch("scripts.run.scan_sources", return_value=[]),
            patch("scripts.run.classify_sources", return_value=[]),
            patch("scripts.run.build_label_doc_map", return_value=({}, {})),
            patch("scripts.run._load_sheet_subtype_map", return_value={}),
            patch("scripts.run.generate_index_md"),
            patch("scripts.run.generate_docs"),
            patch("scripts.run.copy_assets"),
            patch("scripts.create.scan._source_roots", return_value=[]),
        ]

    def test_create_calls_javadoc_generate(self, tmp_path):
        """create() calls javadoc_generate() before RST conversion."""
        from scripts.run import create
        from unittest.mock import patch
        output_dir, base_patches = self._patches_for_create(tmp_path)
        with (
            base_patches[0], base_patches[1], base_patches[2],
            base_patches[3], base_patches[4], base_patches[5],
            base_patches[6], base_patches[7],
            patch("scripts.run.javadoc_generate", return_value={"nablarch.A": "javadoc-A"}) as mock_jdoc,
            patch("scripts.run.make_snapshot", return_value={"files": {}}),
            patch("scripts.run.save_snapshot"),
        ):
            create(version="6", repo_root=_REPO_ROOT, output_dir=output_dir,
                   state_dir=tmp_path, files=None)
        mock_jdoc.assert_called_once()

    def test_update_calls_javadoc_generate(self, tmp_path):
        """update() calls javadoc_generate() before RST conversion."""
        from scripts.run import update
        from unittest.mock import patch
        output_dir, base_patches = self._patches_for_create(tmp_path)
        output_dir.mkdir(exist_ok=True)
        with (
            base_patches[0], base_patches[1], base_patches[2],
            base_patches[3], base_patches[4], base_patches[5],
            base_patches[6], base_patches[7],
            patch("scripts.run.javadoc_generate", return_value={}) as mock_jdoc,
            patch("scripts.run.diff_snapshot", return_value=([], [], [])),
            patch("scripts.run.load_snapshot", return_value={"files": {}}),
            patch("scripts.run.make_snapshot", return_value={"files": {}}),
            patch("scripts.run.save_snapshot"),
        ):
            update(version="6", repo_root=_REPO_ROOT, output_dir=output_dir,
                   state_dir=tmp_path, files=None)
        mock_jdoc.assert_called_once()

    def test_convert_and_write_passes_javadoc_map_to_rst_convert(self, tmp_path):
        """_convert_and_write passes javadoc_map to RST convert function."""
        from scripts.run import _convert_and_write
        from unittest.mock import patch, MagicMock

        fi = _make_file_info(fmt="rst")
        fi.output_path = "test.json"

        javadoc_map = {"nablarch.A": "javadoc-A"}
        mock_result = MagicMock()
        mock_result.title = "T"
        mock_result.content = ""
        mock_result.no_knowledge_content = False
        mock_result.sections = []
        mock_result.warnings = []
        mock_result.meta = None

        output_dir = tmp_path / "knowledge"
        output_dir.mkdir()

        mock_convert_fn = MagicMock(return_value=mock_result)
        with patch("scripts.run._converter_for", return_value=mock_convert_fn):
            _convert_and_write(fi, output_dir, javadoc_map=javadoc_map)
            call_kwargs = mock_convert_fn.call_args[1] if mock_convert_fn.call_args else {}
            assert call_kwargs.get("javadoc_map") == javadoc_map, (
                f"Expected javadoc_map={javadoc_map!r} passed to RST convert, got: {call_kwargs}"
            )

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
        "sections": [{"id": "s1", "title": "概要", "content": "Content.", "hints": []}],
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
            "sections": [{"id": "s1", "title": "概要", "content": "Content.", "hints": []}],
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

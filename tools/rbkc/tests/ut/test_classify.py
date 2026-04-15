"""Unit tests for classify.py — Phase 14: collision detection + auto-disambiguation."""
from __future__ import annotations

import pytest
from pathlib import Path
from unittest.mock import patch

from scripts.classify import classify_sources, FileInfo, _parent_prefix
from scripts.scan import SourceFile


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_source(path_str: str, fmt: str) -> SourceFile:
    return SourceFile(
        path=Path(path_str),
        format=fmt,
        filename=Path(path_str).name,
    )


def _mock_mappings() -> dict:
    """Minimal mapping that produces predictable file_ids."""
    return {
        "rst": [
            {
                "pattern": "development_tools/testing_framework/",
                "type": "development-tools",
                "category": "testing-framework",
            },
            {
                "pattern": "application_framework/application_framework/libraries/",
                "type": "component",
                "category": "libraries",
            },
        ],
        "md": {},
        "xlsx": {},
        "xlsx_patterns": [],
    }


# ---------------------------------------------------------------------------
# Test: _parent_prefix helper
# ---------------------------------------------------------------------------

class TestParentPrefix:
    def test_1_level(self):
        p = Path("/a/b/c/file.rst")
        assert _parent_prefix(p, 1) == "c"

    def test_2_levels(self):
        p = Path("/a/b/c/d/file.rst")
        assert _parent_prefix(p, 2) == "c-d"

    def test_underscore_to_hyphen(self):
        p = Path("/a/b/my_dir/file.rst")
        assert _parent_prefix(p, 1) == "my-dir"

    def test_uppercase_lowercased(self):
        p = Path("/a/FAQ/batch/1.rst")
        assert _parent_prefix(p, 1) == "batch"

    def test_2_levels_mixes_case(self):
        p = Path("/a/FAQ/batch/1.rst")
        assert _parent_prefix(p, 2) == "faq-batch"


# ---------------------------------------------------------------------------
# Test: auto-disambiguation (1-level parent)
# ---------------------------------------------------------------------------

class TestAutoDisambiguation:
    """Colliding files get unique IDs via parent dir prefix."""

    def test_two_files_same_name_different_dirs_resolved(self, tmp_path):
        sources = [
            _make_source(
                ".lw/nab-official/v6/nablarch-document/ja/"
                "development_tools/testing_framework/guide/"
                "05_UnitTestGuide/02_RequestUnitTest/batch.rst",
                "rst",
            ),
            _make_source(
                ".lw/nab-official/v6/nablarch-document/ja/"
                "development_tools/testing_framework/guide/"
                "05_UnitTestGuide/03_DealUnitTest/batch.rst",
                "rst",
            ),
        ]
        with patch("scripts.classify._load_mappings", return_value=_mock_mappings()):
            result = classify_sources(sources, "6", tmp_path)

        assert len(result) == 2
        output_paths = {fi.output_path for fi in result}
        assert len(output_paths) == 2  # no collision

    def test_disambiguated_ids_contain_parent_dir(self, tmp_path):
        sources = [
            _make_source(
                ".lw/nab-official/v6/nablarch-document/ja/"
                "development_tools/testing_framework/guide/"
                "05_UnitTestGuide/02_RequestUnitTest/batch.rst",
                "rst",
            ),
            _make_source(
                ".lw/nab-official/v6/nablarch-document/ja/"
                "development_tools/testing_framework/guide/"
                "05_UnitTestGuide/03_DealUnitTest/batch.rst",
                "rst",
            ),
        ]
        with patch("scripts.classify._load_mappings", return_value=_mock_mappings()):
            result = classify_sources(sources, "6", tmp_path)

        ids = {fi.file_id for fi in result}
        # Each ID should contain the disambiguating parent dir name
        assert any("02requestunittest" in i or "requestunittest" in i or "02" in i for i in ids)
        assert any("03dealunittest" in i or "dealunittest" in i or "03" in i for i in ids)

    def test_no_collision_single_file_unchanged(self, tmp_path):
        """Single file with no collision keeps original ID."""
        sources = [
            _make_source(
                ".lw/nab-official/v6/nablarch-document/ja/"
                "development_tools/testing_framework/guide/"
                "05_UnitTestGuide/02_RequestUnitTest/batch.rst",
                "rst",
            ),
        ]
        with patch("scripts.classify._load_mappings", return_value=_mock_mappings()):
            result = classify_sources(sources, "6", tmp_path)

        assert len(result) == 1
        assert result[0].file_id == "testing-framework-batch"

    def test_triple_collision_resolved(self, tmp_path):
        """Three files colliding (functional_comparison) all get distinct IDs."""
        sources = [
            _make_source(
                ".lw/nab-official/v6/nablarch-document/ja/"
                "application_framework/application_framework/libraries/data_io/functional_comparison.rst",
                "rst",
            ),
            _make_source(
                ".lw/nab-official/v6/nablarch-document/ja/"
                "application_framework/application_framework/libraries/validation/functional_comparison.rst",
                "rst",
            ),
            _make_source(
                ".lw/nab-official/v6/nablarch-document/ja/"
                "application_framework/application_framework/libraries/database/functional_comparison.rst",
                "rst",
            ),
        ]
        with patch("scripts.classify._load_mappings", return_value=_mock_mappings()):
            result = classify_sources(sources, "6", tmp_path)

        assert len(result) == 3
        output_paths = {fi.output_path for fi in result}
        assert len(output_paths) == 3


# ---------------------------------------------------------------------------
# Test: irresolvable collision raises ValueError
# ---------------------------------------------------------------------------

class TestIrresolvableCollision:
    """If disambiguation fails after 2 levels, ValueError is raised."""

    def test_raises_value_error_when_unresolvable(self, tmp_path):
        """Two files with identical path structure (same parent dirs) raise ValueError."""
        # Manufacture a case where even 2-level parent dirs are identical
        # by using the exact same 2 levels above filename
        sources = [
            _make_source(
                ".lw/nab-official/v6/nablarch-document/ja/"
                "development_tools/testing_framework/guide/"
                "05_UnitTestGuide/02_RequestUnitTest/batch.rst",
                "rst",
            ),
            _make_source(
                # Same path — simulates a true duplicate
                ".lw/nab-official/v6/nablarch-document/ja/"
                "development_tools/testing_framework/guide/"
                "05_UnitTestGuide/02_RequestUnitTest/batch.rst",
                "rst",
            ),
        ]
        with patch("scripts.classify._load_mappings", return_value=_mock_mappings()):
            with pytest.raises(ValueError, match="output_path collision"):
                classify_sources(sources, "6", tmp_path)

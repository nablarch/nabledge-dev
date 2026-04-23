"""Unit tests for ``scripts.common.file_id``.

The oracle in this module is the **mapping spec** (``mappings/v{N}.json`` + the
naming rules documented in ``rbkc-converter-design.md``), not the output of
``classify_sources``.  This keeps the tests from becoming circular once both
create and verify consume :func:`derive_file_id`.

Phase 22-B-16b-prep: file_id derivation is moved from ``create/classify.py``
into ``common/file_id.py`` so verify can reuse the same implementation without
duplicating the naming spec.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


def _repo_root() -> Path:
    # tests/ut/test_file_id.py → repo root is 4 levels up
    return Path(__file__).resolve().parents[4]


class TestDeriveFileId_RST:
    """RST pattern matching + file_id composition (spec: longest pattern wins)."""

    def test_basic_pattern_match_returns_type_category_file_id(self):
        from scripts.common.file_id import derive_file_id

        repo = _repo_root()
        p = repo / ".lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/universal_dao.rst"

        fc = derive_file_id(p, "rst", "6", repo)

        assert fc is not None
        assert fc.type == "component"
        assert fc.category == "libraries"
        # spec §… generate_id: base = filename stem with `_`→`-`, prefixed by category
        assert fc.file_id == "libraries-universal-dao"

    def test_longer_pattern_wins_over_shorter(self):
        """Longest mapping pattern wins — the short prefix ``batch/`` would
        route this path to ``processing-pattern/nablarch-batch``; the longer
        ``batch/jsr352`` prefix must win and route it to
        ``processing-pattern/jakarta-batch``.  Flipping the sort order breaks
        this assertion.
        """
        from scripts.common.file_id import derive_file_id

        repo = _repo_root()
        p = repo / ".lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/batch/jsr352/overview.rst"

        fc = derive_file_id(p, "rst", "6", repo)

        assert fc is not None
        assert fc.type == "processing-pattern"
        assert fc.category == "jakarta-batch"
        assert fc.file_id == "jakarta-batch-overview"

    def test_longer_pattern_wins_type_differs(self):
        """Even across different ``type`` values: ``batch/jBatchHandler``
        (type=component) must win over ``batch/`` (type=processing-pattern).
        """
        from scripts.common.file_id import derive_file_id

        repo = _repo_root()
        p = repo / ".lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/batch/jBatchHandler/foo.rst"

        fc = derive_file_id(p, "rst", "6", repo)

        assert fc is not None
        assert fc.type == "component"
        assert fc.category == "handlers"
        assert fc.file_id == "handlers-foo"

    def test_index_rst_uses_path_context_instead_of_literal_index(self):
        from scripts.common.file_id import derive_file_id

        repo = _repo_root()
        # pattern "application_framework/application_framework/libraries/" with index.rst
        # under libraries/universal_dao/index.rst → file_id = "libraries-universal-dao"
        p = repo / ".lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/universal_dao/index.rst"

        fc = derive_file_id(p, "rst", "6", repo)

        assert fc is not None
        assert fc.file_id == "libraries-universal-dao"

    def test_top_level_index_rst_maps_to_about_nablarch(self):
        from scripts.common.file_id import derive_file_id

        repo = _repo_root()
        # Top-level index.rst — spec fallback: type="about", category="about-nablarch",
        # matched_pattern="" (no pattern), so the path-context rewrite does not
        # trigger and base stays "index".
        p = repo / ".lw/nab-official/v6/nablarch-document/ja/index.rst"

        fc = derive_file_id(p, "rst", "6", repo)

        assert fc is not None
        assert fc.type == "about"
        assert fc.category == "about-nablarch"
        assert fc.file_id == "about-nablarch-index"

    def test_unmapped_rst_returns_none(self, tmp_path):
        from scripts.common.file_id import derive_file_id

        repo = _repo_root()
        # A path that matches no mapping pattern AND is not top-level index.rst
        p = tmp_path / "some/unrelated/path/file.rst"

        fc = derive_file_id(p, "rst", "6", repo)

        assert fc is None


class TestDeriveFileId_MD:
    def test_md_exact_filename_match(self):
        from scripts.common.file_id import derive_file_id

        repo = _repo_root()
        # v6 mapping: "Nablarchバッチ処理パターン.md" → guide/nablarch-patterns
        p = repo / ".lw/nab-official/v6/nablarch-system-development-guide/Nablarchバッチ処理パターン.md"

        fc = derive_file_id(p, "md", "6", repo)

        assert fc is not None
        assert fc.type == "guide"
        assert fc.category == "nablarch-patterns"
        # base = stem with underscores → hyphens, prefixed by category
        assert fc.file_id == "nablarch-patterns-Nablarchバッチ処理パターン"

    def test_unmapped_md_returns_none(self, tmp_path):
        from scripts.common.file_id import derive_file_id

        repo = _repo_root()
        p = tmp_path / "other.md"

        fc = derive_file_id(p, "md", "6", repo)

        assert fc is None


class TestDeriveFileId_XLSX:
    def test_xlsx_exact_filename_category_is_full_id(self):
        from scripts.common.file_id import derive_file_id

        repo = _repo_root()
        # v6 exact mapping — category itself is the file_id (xlsx_exact branch)
        p = repo / ".lw/nab-official/v6/Nablarch機能のセキュリティ対応表.xlsx"

        fc = derive_file_id(p, "xlsx", "6", repo)

        assert fc is not None
        assert fc.type == "check"
        assert fc.category == "security-check"
        assert fc.file_id == "security-check"

    def test_xlsx_pattern_match_uses_stem(self):
        from scripts.common.file_id import derive_file_id

        repo = _repo_root()
        p = repo / ".lw/nab-official/v6/nablarch-6.0.0-releasenote.xlsx"

        fc = derive_file_id(p, "xlsx", "6", repo)

        assert fc is not None
        assert fc.type == "releases"
        assert fc.category == "releases"
        # stem "nablarch-6.0.0-releasenote" has no underscores, category prefix applied
        assert fc.file_id == "releases-nablarch-6.0.0-releasenote"


class TestLoadMappings:
    def test_load_returns_rst_md_xlsx_sections(self):
        from scripts.common.file_id import load_mappings

        m = load_mappings("6", _repo_root())

        assert isinstance(m, dict)
        assert "rst" in m and isinstance(m["rst"], list)
        assert "md" in m and isinstance(m["md"], dict)
        assert "xlsx" in m and isinstance(m["xlsx"], dict)

    def test_missing_version_raises_filenotfound(self, tmp_path):
        from scripts.common.file_id import load_mappings

        with pytest.raises(FileNotFoundError):
            load_mappings("99", tmp_path)


class TestRelForClassify:
    def test_v6_strips_nablarch_document_ja_marker(self):
        from scripts.common.file_id import rel_for_classify

        p = Path("/x/y/.lw/nab-official/v6/nablarch-document/ja/a/b/c.rst")
        assert rel_for_classify(p, "6") == "a/b/c.rst"

    def test_v1x_preserves_marker_except_document(self):
        from scripts.common.file_id import rel_for_classify

        p = Path("/x/.lw/nab-official/v1.4/workflow/foo/bar.rst")
        # non-"document/" markers are preserved in the returned rel
        assert rel_for_classify(p, "1.4") == "workflow/foo/bar.rst"


class TestReExportsFromCreate:
    """Existing create.scan / create.classify must keep their import surface
    so downstream callers don't break.  These re-exports live in
    create/__init__-ish places, but the simplest check is the modules
    themselves still expose the same names (even if they delegate)."""

    def test_scan_load_mappings_delegates_to_common(self):
        from scripts.create.scan import _load_mappings
        from scripts.common.file_id import load_mappings

        assert _load_mappings is load_mappings or _load_mappings.__wrapped__ is load_mappings or \
               _load_mappings.__module__ == "scripts.common.file_id"

    def test_scan_rel_for_classify_delegates_to_common(self):
        from scripts.create.scan import _rel_for_classify
        from scripts.common.file_id import rel_for_classify

        assert _rel_for_classify is rel_for_classify or \
               _rel_for_classify.__module__ == "scripts.common.file_id"

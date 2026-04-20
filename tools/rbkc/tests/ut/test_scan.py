"""Tests for scan.py — source file discovery."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.create.scan import scan_sources, SourceFile


def _make_repo(tmp_path: Path, version: str) -> Path:
    """Create minimal repo structure with .lw/nab-official/."""
    repo = tmp_path / "repo"
    repo.mkdir()
    # v1.x _source_roots iterates v1.x directory; create it to avoid FileNotFoundError
    if version.startswith("1."):
        (repo / f".lw/nab-official/v{version}").mkdir(parents=True, exist_ok=True)
    return repo


def _touch(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()
    return path


def _write_mapping(repo: Path, version: str, data: dict):
    mapping_path = repo / f"tools/rbkc/mappings/v{version}.json"
    mapping_path.parent.mkdir(parents=True, exist_ok=True)
    mapping_path.write_text(json.dumps(data), encoding="utf-8")


# ---------------------------------------------------------------------------
# .xls extension support
# ---------------------------------------------------------------------------

class TestXlsExtension:
    """scan_sources must treat .xls files the same as .xlsx."""

    def test_xls_file_included_in_files_mode(self, tmp_path):
        """.xls file path in explicit files= list → included with fmt='xlsx'."""
        repo = _make_repo(tmp_path, "5")
        xls = _touch(repo / ".lw/nab-official/all-releasenote/nablarch-1.3-all-releasenote/1.3.0/test-detail.xls")
        result = scan_sources("5", repo, files=[str(xls.relative_to(repo))])
        assert len(result) == 1
        assert result[0].format == "xlsx"
        assert result[0].path == xls

    def test_xls_file_discovered_via_pattern(self, tmp_path):
        """.xls file in source root matched by endswith pattern → included."""
        repo = _make_repo(tmp_path, "1.3")
        root = repo / ".lw/nab-official/all-releasenote/nablarch-1.3-all-releasenote"
        xls = _touch(root / "1.3.0" / "nablarch_toolbox-1.3.0-releasenote-detail.xls")
        _write_mapping(repo, "1.3", {
            "rst": [], "md": {}, "xlsx": {},
            "xlsx_patterns": [{"endswith": "-releasenote-detail.xls"}],
        })
        result = scan_sources("1.3", repo)
        paths = [r.path for r in result]
        assert xls in paths
        assert all(r.format == "xlsx" for r in result if r.path == xls)


# ---------------------------------------------------------------------------
# all-releasenote source root inclusion
# ---------------------------------------------------------------------------

class TestAllReleasenoteRoot:
    """all-releasenote directory must be included as a source root."""

    def test_v5_all_releasenote_xlsx_discovered(self, tmp_path):
        """v5 all-releasenote xlsx matched by pattern → included."""
        repo = _make_repo(tmp_path, "5")
        root = repo / ".lw/nab-official/all-releasenote/nablarch-5-all-releasenote"
        xlsx = _touch(root / "nablarch5-releasenote.xlsx")
        _write_mapping(repo, "5", {
            "rst": [], "md": {}, "xlsx": {},
            "xlsx_patterns": [{"endswith": "-releasenote.xlsx"}],
        })
        result = scan_sources("5", repo)
        paths = [r.path for r in result]
        assert xlsx in paths

    def test_v14_all_releasenote_xlsx_discovered(self, tmp_path):
        """v1.4 all-releasenote xlsx matched by pattern → included."""
        repo = _make_repo(tmp_path, "1.4")
        root = repo / ".lw/nab-official/all-releasenote/nablarch-1.4-all-releasenote"
        xlsx = _touch(root / "nablarch-1.4.0-releasenote.xlsx")
        _write_mapping(repo, "1.4", {
            "rst": [], "md": {}, "xlsx": {},
            "xlsx_patterns": [{"endswith": "-releasenote.xlsx"}],
        })
        result = scan_sources("1.4", repo)
        paths = [r.path for r in result]
        assert xlsx in paths

    def test_v13_all_releasenote_xls_discovered(self, tmp_path):
        """v1.3 all-releasenote xls matched by pattern → included."""
        repo = _make_repo(tmp_path, "1.3")
        root = repo / ".lw/nab-official/all-releasenote/nablarch-1.3-all-releasenote"
        xls = _touch(root / "1.3.0" / "nablarch_toolbox-1.3.0-releasenote-detail.xls")
        _write_mapping(repo, "1.3", {
            "rst": [], "md": {}, "xlsx": {},
            "xlsx_patterns": [{"endswith": "-releasenote-detail.xls"}],
        })
        result = scan_sources("1.3", repo)
        paths = [r.path for r in result]
        assert xls in paths

    def test_v12_all_releasenote_xls_discovered(self, tmp_path):
        """v1.2 all-releasenote xls matched by pattern → included."""
        repo = _make_repo(tmp_path, "1.2")
        root = repo / ".lw/nab-official/all-releasenote/nablarch-1.2-all-releasenote"
        xls = _touch(root / "1.2.0" / "nablarch_toolbox-1.2.0-releasenote-detail.xls")
        _write_mapping(repo, "1.2", {
            "rst": [], "md": {}, "xlsx": {},
            "xlsx_patterns": [{"endswith": "-releasenote-detail.xls"}],
        })
        result = scan_sources("1.2", repo)
        paths = [r.path for r in result]
        assert xls in paths

    def test_v6_all_releasenote_xlsx_discovered(self, tmp_path):
        """v6 all-releasenote xlsx matched by pattern → included (v6 uses explicit roots)."""
        repo = _make_repo(tmp_path, "6")
        # v6 _source_roots uses explicit list — must also include all-releasenote
        (repo / ".lw/nab-official/v6/nablarch-document/ja").mkdir(parents=True)
        (repo / ".lw/nab-official/v6/nablarch-system-development-guide").mkdir(parents=True)
        root = repo / ".lw/nab-official/all-releasenote/nablarch-6-all-releasenote"
        xlsx = _touch(root / "nablarch6u99-releasenote.xlsx")
        _write_mapping(repo, "6", {
            "rst": [], "md": {}, "xlsx": {},
            "xlsx_patterns": [{"endswith": "-releasenote.xlsx"}],
        })
        result = scan_sources("6", repo)
        paths = [r.path for r in result]
        assert xlsx in paths

    def test_all_releasenote_not_included_when_no_pattern_matches(self, tmp_path):
        """Files in all-releasenote without matching pattern are excluded."""
        repo = _make_repo(tmp_path, "1.4")
        root = repo / ".lw/nab-official/all-releasenote/nablarch-1.4-all-releasenote"
        xlsx = _touch(root / "nablarch-1.4.0-releasenote.xlsx")
        _write_mapping(repo, "1.4", {
            "rst": [], "md": {}, "xlsx": {},
            "xlsx_patterns": [],  # no patterns
        })
        result = scan_sources("1.4", repo)
        paths = [r.path for r in result]
        assert xlsx not in paths

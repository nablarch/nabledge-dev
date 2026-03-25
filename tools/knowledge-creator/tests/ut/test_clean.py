"""Tests for clean.py: verify catalog.json sources preservation."""
import json
import os
import sys

import pytest

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(TOOL_DIR, "scripts"))


def _make_repo(tmp_path, version="6"):
    """Build a minimal fake repo with cache and log directories."""
    repo = tmp_path / "repo"
    cache_dir = repo / "tools" / "knowledge-creator" / ".cache" / f"v{version}"
    logs_dir = repo / "tools" / "knowledge-creator" / ".logs" / f"v{version}"
    knowledge_dir = repo / ".claude" / "skills" / f"nabledge-{version}" / "knowledge"
    docs_dir = repo / ".claude" / "skills" / f"nabledge-{version}" / "docs"
    for d in [cache_dir, logs_dir, knowledge_dir, docs_dir]:
        d.mkdir(parents=True)
    return str(repo), str(cache_dir)


class TestCleanVersionPreservesSources:
    """clean_version must preserve catalog.json sources after deleting .cache/."""

    def test_sources_preserved_after_clean(self, tmp_path):
        """sources field survives clean_version when catalog.json has sources."""
        from clean import clean_version

        repo, cache_dir = _make_repo(tmp_path)
        catalog_path = os.path.join(cache_dir, "catalog.json")
        sources = [
            {"repo": "https://github.com/nablarch/nablarch-document",
             "branch": "main", "commit": "abc123"},
            {"repo": "https://github.com/Fintan-contents/nablarch-system-development-guide",
             "branch": "main", "commit": "def456"},
        ]
        with open(catalog_path, "w", encoding="utf-8") as f:
            json.dump({"version": "6", "sources": sources, "files": []}, f)

        clean_version(repo, "6")

        assert os.path.exists(catalog_path), "catalog.json should be restored"
        with open(catalog_path, encoding="utf-8") as f:
            catalog = json.load(f)
        assert catalog["sources"] == sources, (
            f"sources should be preserved after clean\n"
            f"expected: {sources}\nactual: {catalog['sources']}"
        )

    def test_empty_sources_not_restored(self, tmp_path):
        """catalog.json with empty sources is not recreated after clean."""
        from clean import clean_version

        repo, cache_dir = _make_repo(tmp_path)
        catalog_path = os.path.join(cache_dir, "catalog.json")
        with open(catalog_path, "w", encoding="utf-8") as f:
            json.dump({"version": "6", "sources": [], "files": []}, f)

        clean_version(repo, "6")

        assert not os.path.exists(catalog_path), (
            "catalog.json should not be restored when sources was empty"
        )

    def test_no_catalog_clean_succeeds(self, tmp_path):
        """clean_version works normally when catalog.json does not exist."""
        from clean import clean_version

        repo, cache_dir = _make_repo(tmp_path)

        clean_version(repo, "6")  # Should not raise

        assert not os.path.exists(os.path.join(cache_dir, "catalog.json"))


class TestCleanStaleCache:
    """Tests for _clean_stale_cache in run.py.

    After Phase A produces a new catalog, stale cache files whose IDs no longer
    exist in the catalog should be deleted. Valid cache files must be preserved.
    """

    def _make_cache_repo(self, tmp_path, version="6"):
        """Build a minimal repo with cache and catalog directories."""
        repo = tmp_path / "repo"
        cache_knowledge = repo / "tools" / "knowledge-creator" / ".cache" / f"v{version}" / "knowledge"
        catalog_dir = repo / "tools" / "knowledge-creator" / ".cache" / f"v{version}"
        for d in [cache_knowledge, catalog_dir]:
            d.mkdir(parents=True, exist_ok=True)
        return str(repo), str(cache_knowledge), str(catalog_dir)

    def _make_ctx(self, repo, version="6"):
        import sys
        TOOL_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sys.path.insert(0, TOOL_DIR)
        from run import Context
        return Context(version=version, repo=repo, concurrency=1, run_id="test")

    def _write_catalog(self, catalog_dir, file_ids):
        catalog_path = os.path.join(catalog_dir, "catalog.json")
        with open(catalog_path, "w") as f:
            json.dump({
                "version": "6",
                "files": [{"id": fid, "source_path": f"path/{fid}.rst",
                           "format": "rst", "filename": f"{fid}.rst",
                           "type": "component", "category": "test",
                           "output_path": f"component/test/{fid}.json",
                           "assets_dir": f"component/test/assets/{fid}/"}
                          for fid in file_ids]
            }, f)

    def _make_cache_file(self, cache_dir, file_id):
        path = os.path.join(cache_dir, "component", "test")
        os.makedirs(path, exist_ok=True)
        fpath = os.path.join(path, f"{file_id}.json")
        with open(fpath, "w") as f:
            json.dump({"id": file_id, "content": "cached"}, f)
        return fpath

    def test_stale_cache_file_deleted(self, tmp_path):
        """カタログにないIDのキャッシュファイルが削除されること。"""
        repo, cache_dir, catalog_dir = self._make_cache_repo(tmp_path)
        ctx = self._make_ctx(repo)

        self._write_catalog(catalog_dir, ["current-id"])
        stale_path = self._make_cache_file(cache_dir, "stale-old-id")

        from run import _clean_stale_cache
        _clean_stale_cache(ctx)

        assert not os.path.exists(stale_path), (
            "Stale cache file (ID not in catalog) should be deleted"
        )

    def test_current_cache_file_preserved(self, tmp_path):
        """カタログに存在するIDのキャッシュファイルは削除されないこと。"""
        repo, cache_dir, catalog_dir = self._make_cache_repo(tmp_path)
        ctx = self._make_ctx(repo)

        self._write_catalog(catalog_dir, ["current-id"])
        current_path = self._make_cache_file(cache_dir, "current-id")

        from run import _clean_stale_cache
        _clean_stale_cache(ctx)

        assert os.path.exists(current_path), (
            "Cache file whose ID exists in catalog should be preserved"
        )

    def test_no_catalog_returns_without_error(self, tmp_path):
        """catalog.jsonがない場合はエラーなく終了すること。"""
        repo, _, _ = self._make_cache_repo(tmp_path)
        ctx = self._make_ctx(repo)

        from run import _clean_stale_cache
        _clean_stale_cache(ctx)  # Should not raise

    def test_mixed_stale_and_current(self, tmp_path):
        """カタログにある/ないIDが混在する場合、ステールのみ削除されること。"""
        repo, cache_dir, catalog_dir = self._make_cache_repo(tmp_path)
        ctx = self._make_ctx(repo)

        self._write_catalog(catalog_dir, ["keep-a", "keep-b"])
        keep_a = self._make_cache_file(cache_dir, "keep-a")
        keep_b = self._make_cache_file(cache_dir, "keep-b")
        stale_1 = self._make_cache_file(cache_dir, "old-id-1")
        stale_2 = self._make_cache_file(cache_dir, "old-id-2")

        from run import _clean_stale_cache
        _clean_stale_cache(ctx)

        assert os.path.exists(keep_a)
        assert os.path.exists(keep_b)
        assert not os.path.exists(stale_1)
        assert not os.path.exists(stale_2)

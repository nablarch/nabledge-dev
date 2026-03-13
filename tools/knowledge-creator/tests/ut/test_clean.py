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

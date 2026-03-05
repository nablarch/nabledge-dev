"""Tests for steps/knowledge_meta.py"""
import os
import json
import subprocess
from datetime import date
import pytest
from steps.knowledge_meta import (
    get_meta_path,
    load_meta,
    get_local_repo_path,
    _get_commit,
    update_knowledge_meta,
)
from steps.common import write_json


class TestGetMetaPath:

    def test_returns_correct_path_for_v6(self, ctx):
        expected = os.path.join(
            ctx.repo,
            ".claude/skills/nabledge-6/plugin/knowledge-creator.json"
        )
        assert get_meta_path(ctx) == expected

    def test_returns_correct_path_for_v5(self, ctx):
        ctx.version = "5"
        expected = os.path.join(
            ctx.repo,
            ".claude/skills/nabledge-5/plugin/knowledge-creator.json"
        )
        assert get_meta_path(ctx) == expected


class TestLoadMeta:

    def test_loads_existing_file(self, ctx):
        meta_path = get_meta_path(ctx)
        os.makedirs(os.path.dirname(meta_path), exist_ok=True)

        test_meta = {
            "generated_at": "2026-01-15",
            "sources": [
                {"repo": "https://github.com/test/repo", "branch": "main", "commit": "abc123"}
            ]
        }
        write_json(meta_path, test_meta)

        loaded = load_meta(ctx)
        assert loaded == test_meta

    def test_returns_empty_dict_when_file_missing(self, ctx):
        assert load_meta(ctx) == {}

    def test_raises_on_malformed_json(self, ctx):
        """Verify that malformed JSON causes an error instead of silent failure."""
        meta_path = get_meta_path(ctx)
        os.makedirs(os.path.dirname(meta_path), exist_ok=True)
        with open(meta_path, 'w') as f:
            f.write("{invalid json")

        with pytest.raises(json.JSONDecodeError):
            load_meta(ctx)


class TestGetLocalRepoPath:

    def test_nablarch_document_v6(self):
        path = get_local_repo_path(
            "https://github.com/nablarch/nablarch-document",
            "6",
            "/home/user/work/nabledge"
        )
        assert path == "/home/user/work/nabledge/.lw/nab-official/v6/nablarch-document"

    def test_fintan_guide_v6(self):
        path = get_local_repo_path(
            "https://github.com/Fintan-contents/nablarch-system-development-guide",
            "6",
            "/home/user/work/nabledge"
        )
        assert path == "/home/user/work/nabledge/.lw/nab-official/v6/nablarch-system-development-guide"

    def test_strips_git_extension(self):
        path = get_local_repo_path(
            "https://github.com/nablarch/nablarch-document.git",
            "6",
            "/home/user/work"
        )
        assert path == "/home/user/work/.lw/nab-official/v6/nablarch-document"

    def test_nablarch_document_v5(self):
        path = get_local_repo_path(
            "https://github.com/nablarch/nablarch-document",
            "5",
            "/home/user/work/nabledge"
        )
        assert path == "/home/user/work/nabledge/.lw/nab-official/v5/nablarch-document"

    def test_handles_trailing_slash(self):
        """Verify trailing slash is properly stripped before extracting repo name."""
        path1 = get_local_repo_path("https://github.com/nablarch/nablarch-document/", "6", "/home/user")
        path2 = get_local_repo_path("https://github.com/nablarch/nablarch-document", "6", "/home/user")
        assert path1 == path2
        assert path1 == "/home/user/.lw/nab-official/v6/nablarch-document"

    def test_handles_git_extension_with_trailing_slash(self):
        """Verify both .git extension and trailing slash are handled correctly."""
        path = get_local_repo_path("https://github.com/nablarch/nablarch-document.git/", "6", "/home/user")
        assert path == "/home/user/.lw/nab-official/v6/nablarch-document"


class TestGetCommit:

    def test_returns_commit_from_git_repo(self, tmp_path):
        # Create a git repository
        repo_dir = tmp_path / "test_repo"
        repo_dir.mkdir()

        subprocess.run(["git", "init"], cwd=repo_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=repo_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_dir, check=True, capture_output=True)

        # Create a file and commit
        (repo_dir / "test.txt").write_text("test content")
        subprocess.run(["git", "add", "test.txt"], cwd=repo_dir, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_dir, check=True, capture_output=True)

        commit = _get_commit(str(repo_dir))

        assert len(commit) == 40  # SHA-1 hash length
        assert commit.isalnum()

    def test_returns_empty_string_for_non_git_directory(self, tmp_path):
        non_repo = tmp_path / "non_repo"
        non_repo.mkdir()

        commit = _get_commit(str(non_repo))
        assert commit == ""


class TestUpdateKnowledgeMeta:

    def test_updates_metadata_with_commits(self, tmp_path):
        """Test real integration without mocking - verifies path resolution logic."""
        # Create test repo directory
        repo_root = tmp_path / "repo"
        repo_root.mkdir()

        # Create meta file with realistic repo URL
        meta_path = repo_root / ".claude" / "skills" / "nabledge-6" / "plugin" / "knowledge-creator.json"
        os.makedirs(os.path.dirname(meta_path), exist_ok=True)

        initial_meta = {
            "generated_at": "",
            "sources": [
                {"repo": "https://github.com/test/test-repo", "branch": "main", "commit": ""}
            ]
        }
        write_json(str(meta_path), initial_meta)

        # Create git repository at the path that get_local_repo_path would resolve
        # This tests the ACTUAL path resolution logic (URL -> repo name extraction)
        repo_dir = repo_root / ".lw" / "nab-official" / "v6" / "test-repo"
        repo_dir.mkdir(parents=True)

        subprocess.run(["git", "init"], cwd=repo_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=repo_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_dir, check=True, capture_output=True)
        (repo_dir / "file.txt").write_text("content")
        subprocess.run(["git", "add", "file.txt"], cwd=repo_dir, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Test"], cwd=repo_dir, check=True, capture_output=True)

        # Create context with real repo root - NO MOCKING
        from run import Context
        ctx = Context(version="6", repo=str(repo_root), concurrency=1)

        # Test the real integration - path resolution + commit retrieval
        update_knowledge_meta(ctx, dry_run=False)

        updated = load_meta(ctx)
        assert updated["generated_at"] == date.today().isoformat()
        assert len(updated["sources"]) == 1
        assert len(updated["sources"][0]["commit"]) == 40
        assert updated["sources"][0]["commit"].isalnum()

    def test_dry_run_does_not_write_file(self, ctx, capsys):
        meta_path = get_meta_path(ctx)
        os.makedirs(os.path.dirname(meta_path), exist_ok=True)

        initial_meta = {
            "generated_at": "",
            "sources": [
                {"repo": "https://github.com/test/repo", "branch": "main", "commit": ""}
            ]
        }
        write_json(meta_path, initial_meta)

        update_knowledge_meta(ctx, dry_run=True)

        # File should not be modified in dry-run
        loaded = load_meta(ctx)
        assert loaded["generated_at"] == ""
        assert loaded["sources"][0]["commit"] == ""

        # Check console output
        captured = capsys.readouterr()
        assert "[dry-run]" in captured.out

    def test_handles_missing_meta_file(self, ctx, capsys):
        # Don't create meta file
        update_knowledge_meta(ctx, dry_run=False)

        captured = capsys.readouterr()
        assert "knowledge-creator.json が見つかりません" in captured.out

    def test_handles_missing_local_repo(self, ctx, capsys):
        meta_path = get_meta_path(ctx)
        os.makedirs(os.path.dirname(meta_path), exist_ok=True)

        initial_meta = {
            "generated_at": "",
            "sources": [
                {"repo": "https://github.com/nonexistent/repo", "branch": "main", "commit": ""}
            ]
        }
        write_json(meta_path, initial_meta)

        update_knowledge_meta(ctx, dry_run=False)

        updated = load_meta(ctx)
        assert updated["generated_at"] == date.today().isoformat()
        assert updated["sources"][0]["commit"] == ""  # Empty when repo not found

        captured = capsys.readouterr()
        assert "コミット取得失敗" in captured.out

    def test_updates_multiple_repos(self, tmp_path):
        """Test integration with multiple source repositories with different names."""
        repo_root = tmp_path / "repo"
        repo_root.mkdir()

        # Create meta file with two different repos
        meta_path = repo_root / ".claude" / "skills" / "nabledge-6" / "plugin" / "knowledge-creator.json"
        os.makedirs(os.path.dirname(meta_path), exist_ok=True)

        initial_meta = {
            "generated_at": "",
            "sources": [
                {"repo": "https://github.com/nablarch/nablarch-document", "branch": "main", "commit": ""},
                {"repo": "https://github.com/Fintan-contents/nablarch-system-development-guide", "branch": "main", "commit": ""}
            ]
        }
        write_json(str(meta_path), initial_meta)

        # Create first git repository
        repo1_dir = repo_root / ".lw" / "nab-official" / "v6" / "nablarch-document"
        repo1_dir.mkdir(parents=True)
        subprocess.run(["git", "init"], cwd=repo1_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=repo1_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo1_dir, check=True, capture_output=True)
        (repo1_dir / "file1.txt").write_text("content1")
        subprocess.run(["git", "add", "file1.txt"], cwd=repo1_dir, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "First repo"], cwd=repo1_dir, check=True, capture_output=True)

        # Create second git repository
        repo2_dir = repo_root / ".lw" / "nab-official" / "v6" / "nablarch-system-development-guide"
        repo2_dir.mkdir(parents=True)
        subprocess.run(["git", "init"], cwd=repo2_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=repo2_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo2_dir, check=True, capture_output=True)
        (repo2_dir / "file2.txt").write_text("content2")
        subprocess.run(["git", "add", "file2.txt"], cwd=repo2_dir, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Second repo"], cwd=repo2_dir, check=True, capture_output=True)

        # Create context and update metadata
        from run import Context
        ctx = Context(version="6", repo=str(repo_root), concurrency=1)
        update_knowledge_meta(ctx, dry_run=False)

        # Verify both repos were updated with different commits
        updated = load_meta(ctx)
        assert updated["generated_at"] == date.today().isoformat()
        assert len(updated["sources"]) == 2

        # Both should have valid commits
        assert len(updated["sources"][0]["commit"]) == 40
        assert len(updated["sources"][1]["commit"]) == 40

        # Commits should be different (different repos)
        assert updated["sources"][0]["commit"] != updated["sources"][1]["commit"]

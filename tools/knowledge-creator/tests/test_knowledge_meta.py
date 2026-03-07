"""Tests for steps/knowledge_meta.py"""
import json
import os
import subprocess
import pytest
from common import load_json, write_json
from knowledge_meta import (
    get_meta_path,
    load_meta,
    get_local_repo_path,
    _get_head_commit,
    detect_changed_files,
    update_knowledge_meta,
)


def _git(args, cwd):
    """Helper to run git commands."""
    return subprocess.run(
        ["git"] + args, cwd=cwd,
        capture_output=True, text=True, check=True
    )


def _create_local_repo(path, branch="main"):
    """Create a local git repo with an initial commit."""
    os.makedirs(path, exist_ok=True)
    _git(["init", "-b", branch], cwd=path)
    _git(["config", "user.email", "test@test.com"], cwd=path)
    _git(["config", "user.name", "test"], cwd=path)
    # Initial commit
    dummy = os.path.join(path, "README.md")
    with open(dummy, "w") as f:
        f.write("init")
    _git(["add", "."], cwd=path)
    _git(["commit", "-m", "initial"], cwd=path)
    return path


def _add_file_and_commit(repo_path, relative_path, content, message="update"):
    """Add or modify a file and commit."""
    full_path = os.path.join(repo_path, relative_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)
    _git(["add", relative_path], cwd=repo_path)
    _git(["commit", "-m", message], cwd=repo_path)


class TestGetLocalRepoPath:

    def test_derives_path_from_url(self):
        path = get_local_repo_path(
            "https://github.com/nablarch/nablarch-document",
            "6", "/repo"
        )
        assert path == "/repo/.lw/nab-official/v6/nablarch-document"

    def test_strips_git_suffix(self):
        path = get_local_repo_path(
            "https://github.com/nablarch/nablarch-document.git",
            "6", "/repo"
        )
        assert path == "/repo/.lw/nab-official/v6/nablarch-document"

    def test_version_5(self):
        path = get_local_repo_path(
            "https://github.com/nablarch/nablarch-document",
            "5", "/repo"
        )
        assert path == "/repo/.lw/nab-official/v5/nablarch-document"

    def test_version_5_system_development_guide(self):
        # nablarch-system-development-guide is listed in v5's knowledge-creator.json
        # and cloned under v5 by setup.sh, same as any other source repo
        path = get_local_repo_path(
            "https://github.com/Fintan-contents/nablarch-system-development-guide",
            "5", "/repo"
        )
        assert path == "/repo/.lw/nab-official/v5/nablarch-system-development-guide"


class TestGetHeadCommit:

    def test_returns_sha(self, tmp_path):
        repo = _create_local_repo(str(tmp_path / "repo"))
        sha = _get_head_commit(repo)
        assert len(sha) == 40
        assert all(c in "0123456789abcdef" for c in sha)

    def test_returns_empty_for_invalid_path(self, tmp_path):
        assert _get_head_commit(str(tmp_path / "nonexistent")) == ""


class TestDetectChangedFiles:
    """E2E test: create real git repos, record commit, make changes, detect."""

    def _setup_meta_and_repo(self, ctx, tmp_path):
        """Setup knowledge-creator.json and a local git repo with source files."""
        # Create local git repo simulating nablarch-document
        repo_name = "nablarch-document"
        local_repo = str(
            tmp_path / "repo" / ".lw" / "nab-official" / "v6" / repo_name
        )
        _create_local_repo(local_repo)

        # Add a source file
        _add_file_and_commit(
            local_repo,
            "ja/application_framework/handlers/sample.rst",
            "Original content",
            "add sample handler doc"
        )
        initial_commit = _get_head_commit(local_repo)

        # Write knowledge-creator.json with this commit
        meta_path = get_meta_path(ctx)
        os.makedirs(os.path.dirname(meta_path), exist_ok=True)
        write_json(meta_path, {
            "generated_at": "2026-01-01",
            "sources": [{
                "repo": f"https://github.com/nablarch/{repo_name}",
                "branch": "main",
                "commit": initial_commit
            }]
        })

        # Write classified.json referencing this source
        write_json(ctx.classified_list_path, {
            "version": "6",
            "generated_at": "2026-01-01T00:00:00Z",
            "files": [{
                "id": "handlers-sample",
                "source_path": f".lw/nab-official/v6/{repo_name}/ja/application_framework/handlers/sample.rst",
                "format": "rst",
                "filename": "sample.rst",
                "type": "component",
                "category": "handlers",
                "output_path": "component/handlers/handlers-sample.json",
                "assets_dir": "component/handlers/assets/handlers-sample/"
            }, {
                "id": "handlers-other",
                "source_path": f".lw/nab-official/v6/{repo_name}/ja/application_framework/handlers/other.rst",
                "format": "rst",
                "filename": "other.rst",
                "type": "component",
                "category": "handlers",
                "output_path": "component/handlers/handlers-other.json",
                "assets_dir": "component/handlers/assets/handlers-other/"
            }]
        })

        return local_repo, initial_commit

    def test_no_changes_returns_empty(self, ctx, tmp_path):
        """Same commit → empty list (no changes)."""
        self._setup_meta_and_repo(ctx, tmp_path)
        result = detect_changed_files(ctx)
        assert result == []

    def test_changed_file_detected(self, ctx, tmp_path):
        """Modified file → detected with correct file_id."""
        local_repo, _ = self._setup_meta_and_repo(ctx, tmp_path)

        # Modify source file and commit
        _add_file_and_commit(
            local_repo,
            "ja/application_framework/handlers/sample.rst",
            "Updated content",
            "update sample handler"
        )

        result = detect_changed_files(ctx)
        assert "handlers-sample" in result
        assert "handlers-other" not in result

    def test_empty_commit_returns_none(self, ctx):
        """Empty commit (first generation) → None (= all files)."""
        meta_path = get_meta_path(ctx)
        os.makedirs(os.path.dirname(meta_path), exist_ok=True)
        write_json(meta_path, {
            "generated_at": "",
            "sources": [{
                "repo": "https://github.com/nablarch/nablarch-document",
                "branch": "main",
                "commit": ""
            }]
        })
        result = detect_changed_files(ctx)
        assert result is None

    def test_missing_meta_returns_none(self, ctx):
        """No knowledge-creator.json → None."""
        result = detect_changed_files(ctx)
        assert result is None

    def test_multiple_files_changed(self, ctx, tmp_path):
        """Multiple files changed → all detected."""
        local_repo, _ = self._setup_meta_and_repo(ctx, tmp_path)

        # Add the other file first (so it exists)
        _add_file_and_commit(
            local_repo,
            "ja/application_framework/handlers/other.rst",
            "Other original",
            "add other doc"
        )

        # Update recorded commit to current
        meta_path = get_meta_path(ctx)
        meta = load_json(meta_path)
        meta["sources"][0]["commit"] = _get_head_commit(local_repo)
        write_json(meta_path, meta)

        # Now modify both files
        _add_file_and_commit(
            local_repo,
            "ja/application_framework/handlers/sample.rst",
            "Updated sample",
            "update sample"
        )
        _add_file_and_commit(
            local_repo,
            "ja/application_framework/handlers/other.rst",
            "Updated other",
            "update other"
        )

        result = detect_changed_files(ctx)
        assert set(result) == {"handlers-sample", "handlers-other"}


class TestUpdateKnowledgeMeta:

    def test_writes_commit_and_date(self, ctx, tmp_path):
        """After update, commit SHA and date are written."""
        # Create local repo
        local_repo = str(
            tmp_path / "repo" / ".lw" / "nab-official" / "v6" / "nablarch-document"
        )
        _create_local_repo(local_repo)
        expected_sha = _get_head_commit(local_repo)

        # Write initial meta
        meta_path = get_meta_path(ctx)
        os.makedirs(os.path.dirname(meta_path), exist_ok=True)
        write_json(meta_path, {
            "generated_at": "",
            "sources": [{
                "repo": "https://github.com/nablarch/nablarch-document",
                "branch": "main",
                "commit": ""
            }]
        })

        update_knowledge_meta(ctx)

        updated = load_json(meta_path)
        assert updated["generated_at"] != ""
        assert updated["sources"][0]["commit"] == expected_sha

    def test_dry_run_does_not_write(self, ctx, tmp_path):
        """Dry run → file unchanged."""
        local_repo = str(
            tmp_path / "repo" / ".lw" / "nab-official" / "v6" / "nablarch-document"
        )
        _create_local_repo(local_repo)

        meta_path = get_meta_path(ctx)
        os.makedirs(os.path.dirname(meta_path), exist_ok=True)
        original = {
            "generated_at": "",
            "sources": [{
                "repo": "https://github.com/nablarch/nablarch-document",
                "branch": "main",
                "commit": ""
            }]
        }
        write_json(meta_path, original)

        update_knowledge_meta(ctx, dry_run=True)

        after = load_json(meta_path)
        assert after["generated_at"] == ""
        assert after["sources"][0]["commit"] == ""

    def test_test_mode_skips_update(self, tmp_path):
        """テストモード時は knowledge-creator.json を更新しない。"""
        from run import Context
        local_repo = str(
            tmp_path / "repo" / ".lw" / "nab-official" / "v6" / "nablarch-document"
        )
        _create_local_repo(local_repo)

        ctx = Context(
            version="6", repo=str(tmp_path / "repo"), concurrency=1,
            test_file="test-files-top3.json"
        )
        meta_path = get_meta_path(ctx)
        os.makedirs(os.path.dirname(meta_path), exist_ok=True)
        original = {
            "generated_at": "",
            "sources": [{
                "repo": "https://github.com/nablarch/nablarch-document",
                "branch": "main",
                "commit": ""
            }]
        }
        write_json(meta_path, original)

        update_knowledge_meta(ctx)

        after = load_json(meta_path)
        assert after["generated_at"] == "", "テストモードでは generated_at を更新してはいけない"
        assert after["sources"][0]["commit"] == "", "テストモードでは commit を更新してはいけない"


class TestEffectiveTargetIsolation:
    """Verify that --regen detection does not leak between versions.

    This tests the design requirement that effective_target is a per-version
    local variable, not a mutation of args.target.
    """

    def test_changed_ids_are_per_version(self, tmp_path):
        """Two versions with different source repos → independent detection."""
        from run import Context

        repo = tmp_path / "repo"
        repo.mkdir()

        # Create v6 local repo with a change
        v6_repo = str(repo / ".lw" / "nab-official" / "v6" / "nablarch-document")
        _create_local_repo(v6_repo)
        _add_file_and_commit(v6_repo, "ja/handlers/a.rst", "original", "init")
        v6_commit = _get_head_commit(v6_repo)
        _add_file_and_commit(v6_repo, "ja/handlers/a.rst", "changed", "update")

        # Create v5 local repo with NO change
        v5_repo = str(repo / ".lw" / "nab-official" / "v5" / "nablarch-document")
        _create_local_repo(v5_repo, branch="v5-main")
        _add_file_and_commit(v5_repo, "ja/handlers/b.rst", "stable", "init")
        v5_commit = _get_head_commit(v5_repo)

        # Setup contexts
        for ver, commit in [("6", v6_commit), ("5", v5_commit)]:
            ctx = Context(version=ver, repo=str(repo), concurrency=1)
            os.makedirs(ctx.log_dir, exist_ok=True)

            meta_path = get_meta_path(ctx)
            os.makedirs(os.path.dirname(meta_path), exist_ok=True)
            write_json(meta_path, {
                "generated_at": "2026-01-01",
                "sources": [{
                    "repo": "https://github.com/nablarch/nablarch-document",
                    "branch": "main" if ver == "6" else "v5-main",
                    "commit": commit
                }]
            })

            write_json(ctx.classified_list_path, {
                "version": ver,
                "generated_at": "2026-01-01T00:00:00Z",
                "files": [{
                    "id": f"handlers-{'a' if ver == '6' else 'b'}",
                    "source_path": f".lw/nab-official/v{ver}/nablarch-document/ja/handlers/{'a' if ver == '6' else 'b'}.rst",
                    "format": "rst", "filename": f"{'a' if ver == '6' else 'b'}.rst",
                    "type": "component", "category": "handlers",
                    "output_path": f"component/handlers/handlers-{'a' if ver == '6' else 'b'}.json",
                    "assets_dir": f"component/handlers/assets/handlers-{'a' if ver == '6' else 'b'}/"
                }]
            })

        # v6 should detect changes
        ctx6 = Context(version="6", repo=str(repo), concurrency=1)
        result6 = detect_changed_files(ctx6)
        assert result6 == ["handlers-a"]

        # v5 should detect NO changes
        ctx5 = Context(version="5", repo=str(repo), concurrency=1)
        result5 = detect_changed_files(ctx5)
        assert result5 == []

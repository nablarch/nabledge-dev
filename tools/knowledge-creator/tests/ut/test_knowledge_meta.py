"""Tests for steps/knowledge_meta.py"""
import json
import os
import subprocess
import pytest
from common import load_json, write_json
import knowledge_meta
from knowledge_meta import (
    get_meta_path,
    load_meta,
    get_local_repo_path,
    get_local_svn_path,
    _get_head_commit,
    _get_svn_revision,
    _svn_auth_args,
    detect_changed_files,
    update_knowledge_meta,
    pull_official_repos,
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

        # Write catalog.json with sources and files (unified)
        meta_path = get_meta_path(ctx)
        os.makedirs(os.path.dirname(meta_path), exist_ok=True)
        write_json(meta_path, {
            "generated_at": "2026-01-01",
            "sources": [{
                "repo": f"https://github.com/nablarch/{repo_name}",
                "branch": "main",
                "commit": initial_commit
            }],
            "version": "6",
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


# ============================================================
# SVN helpers
# ============================================================

def _run_svn(args, cwd=None):
    """Helper to run svn commands."""
    return subprocess.run(
        ["svn"] + args, cwd=cwd,
        capture_output=True, text=True, check=True
    )


def _create_svn_repo(path):
    """Create a local SVN repository."""
    os.makedirs(path, exist_ok=True)
    subprocess.run(["svnadmin", "create", path], check=True, capture_output=True)
    return f"file://{path}"


def _checkout_svn(repo_url, wc_path):
    """Checkout an SVN repository to a working copy."""
    os.makedirs(os.path.dirname(wc_path), exist_ok=True)
    _run_svn(["checkout", repo_url, wc_path])
    return wc_path


def _svn_add_file_and_commit(wc_path, relative_path, content, message="update"):
    """Add or modify a file in an SVN working copy and commit."""
    full_path = os.path.join(wc_path, relative_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    is_new = not os.path.exists(full_path)
    with open(full_path, "w") as f:
        f.write(content)
    if is_new:
        _run_svn(["add", "--parents", relative_path], cwd=wc_path)
    _run_svn(["commit", "-m", message], cwd=wc_path)
    # Sync WC revision counter to match committed revision
    _run_svn(["update"], cwd=wc_path)


# ============================================================
# SVN: get_local_svn_path
# ============================================================

class TestGetLocalSvnPath:

    def test_derives_path_from_url(self):
        path = get_local_svn_path(
            "svn+ssh://svn.example.com/nablarch/1.3_maintain",
            "1.3", "/repo"
        )
        assert path == "/repo/.lw/nab-official/v1.3/1.3_maintain"

    def test_file_protocol_url(self):
        path = get_local_svn_path(
            "file:///tmp/svn_repos/1.4_maintain",
            "1.4", "/repo"
        )
        assert path == "/repo/.lw/nab-official/v1.4/1.4_maintain"

    def test_version_1_2(self):
        path = get_local_svn_path(
            "svn+ssh://svn.example.com/nablarch/1.2_maintain",
            "1.2", "/repo"
        )
        assert path == "/repo/.lw/nab-official/v1.2/1.2_maintain"


# ============================================================
# SVN: _get_svn_revision
# ============================================================

class TestGetSvnRevision:

    def test_returns_revision_after_commit(self, tmp_path):
        repo_url = _create_svn_repo(str(tmp_path / "svn_repo"))
        wc = _checkout_svn(repo_url, str(tmp_path / "wc"))
        _svn_add_file_and_commit(wc, "README.txt", "init", "initial commit")

        rev = _get_svn_revision(wc)
        assert rev != ""
        assert rev.isdigit()

    def test_revision_increases_after_new_commit(self, tmp_path):
        repo_url = _create_svn_repo(str(tmp_path / "svn_repo"))
        wc = _checkout_svn(repo_url, str(tmp_path / "wc"))
        _svn_add_file_and_commit(wc, "README.txt", "init", "first")
        rev1 = _get_svn_revision(wc)
        _svn_add_file_and_commit(wc, "README.txt", "updated", "second")
        rev2 = _get_svn_revision(wc)
        assert int(rev2) > int(rev1)

    def test_returns_empty_for_missing_path(self, tmp_path):
        rev = _get_svn_revision(str(tmp_path / "nonexistent"))
        assert rev == ""


# ============================================================
# SVN: detect_changed_files
# ============================================================

class TestDetectChangedFilesSvn:

    def _setup_svn_meta_and_wc(self, ctx, tmp_path):
        """Setup catalog.json with SVN source and a real SVN working copy."""
        repo_url = _create_svn_repo(str(tmp_path / "svn_repo"))
        wc_name = "nablarch-1x-docs"
        wc_path = str(
            tmp_path / "repo" / ".lw" / "nab-official" / f"v{ctx.version}" / wc_name
        )
        _checkout_svn(repo_url, wc_path)

        # Add a source file and record initial revision
        _svn_add_file_and_commit(
            wc_path,
            "ja/application_framework/handlers/sample.rst",
            "Original content",
            "add sample handler doc"
        )
        initial_rev = _get_svn_revision(wc_path)

        # Use a URL whose last component matches wc_name so get_local_svn_path
        # resolves to the correct working copy path in the test repo.
        svn_source_url = f"file:///dummy/{wc_name}"

        meta_path = get_meta_path(ctx)
        os.makedirs(os.path.dirname(meta_path), exist_ok=True)
        write_json(meta_path, {
            "generated_at": "2026-01-01",
            "sources": [{
                "repo": svn_source_url,
                "type": "svn",
                "commit": initial_rev,
            }],
            "version": ctx.version,
            "files": [{
                "id": "handlers-sample",
                "source_path": f".lw/nab-official/v{ctx.version}/{wc_name}/ja/application_framework/handlers/sample.rst",
                "format": "rst",
                "filename": "sample.rst",
                "type": "component",
                "category": "handlers",
                "output_path": "component/handlers/handlers-sample.json",
                "assets_dir": "component/handlers/assets/handlers-sample/"
            }, {
                "id": "handlers-other",
                "source_path": f".lw/nab-official/v{ctx.version}/{wc_name}/ja/application_framework/handlers/other.rst",
                "format": "rst",
                "filename": "other.rst",
                "type": "component",
                "category": "handlers",
                "output_path": "component/handlers/handlers-other.json",
                "assets_dir": "component/handlers/assets/handlers-other/"
            }]
        })

        return wc_path, initial_rev, wc_name

    def test_no_changes_returns_empty(self, ctx, tmp_path):
        """Same revision → empty list (no changes)."""
        self._setup_svn_meta_and_wc(ctx, tmp_path)
        result = detect_changed_files(ctx)
        assert result == []

    def test_changed_file_detected(self, ctx, tmp_path):
        """Modified SVN file → detected with correct file_id."""
        wc_path, _, wc_name = self._setup_svn_meta_and_wc(ctx, tmp_path)

        # Modify source file and commit
        _svn_add_file_and_commit(
            wc_path,
            "ja/application_framework/handlers/sample.rst",
            "Updated content",
            "update sample handler"
        )

        result = detect_changed_files(ctx)
        assert "handlers-sample" in result
        assert "handlers-other" not in result

    def test_empty_revision_returns_none(self, ctx):
        """Empty commit (first generation) → None (= all files)."""
        meta_path = get_meta_path(ctx)
        os.makedirs(os.path.dirname(meta_path), exist_ok=True)
        write_json(meta_path, {
            "generated_at": "",
            "sources": [{
                "repo": "file:///dummy/1.3_maintain",
                "type": "svn",
                "commit": ""
            }]
        })
        result = detect_changed_files(ctx)
        assert result is None


# ============================================================
# SVN: update_knowledge_meta
# ============================================================

class TestUpdateKnowledgeMetaSvn:

    def test_writes_commit_and_date(self, ctx, tmp_path):
        """After update, SVN commit (revision) and date are written for SVN sources."""
        wc_name = "nablarch-1x-docs"
        wc_path = str(
            tmp_path / "repo" / ".lw" / "nab-official" / f"v{ctx.version}" / wc_name
        )
        repo_url = _create_svn_repo(str(tmp_path / "svn_repo"))
        _checkout_svn(repo_url, wc_path)
        _svn_add_file_and_commit(wc_path, "README.txt", "init", "initial")
        expected_rev = _get_svn_revision(wc_path)

        svn_source_url = f"file:///dummy/{wc_name}"

        # Override ctx.repo to point to our tmp repo root so path derivation works
        from run import Context
        test_ctx = Context(
            version=ctx.version,
            repo=str(tmp_path / "repo"),
            concurrency=1,
            run_id="test-svn"
        )
        os.makedirs(os.path.dirname(get_meta_path(test_ctx)), exist_ok=True)
        write_json(get_meta_path(test_ctx), {
            "generated_at": "",
            "sources": [{
                "repo": svn_source_url,
                "type": "svn",
                "commit": ""
            }]
        })

        update_knowledge_meta(test_ctx)

        updated = load_json(get_meta_path(test_ctx))
        assert updated["generated_at"] != ""
        assert updated["sources"][0]["type"] == "svn"
        assert updated["sources"][0]["commit"] == expected_rev
        assert updated["sources"][0]["commit"] != ""

    def test_git_source_unchanged(self, ctx, tmp_path):
        """Git sources are still handled correctly alongside SVN."""
        git_repo = str(tmp_path / "git_repo")
        _create_local_repo(git_repo)
        expected_sha = _get_head_commit(git_repo)

        wc_name = "nablarch-1x-docs"
        wc_path = str(
            tmp_path / "repo" / ".lw" / "nab-official" / f"v{ctx.version}" / wc_name
        )
        svn_repo_url = _create_svn_repo(str(tmp_path / "svn_repo"))
        _checkout_svn(svn_repo_url, wc_path)
        _svn_add_file_and_commit(wc_path, "README.txt", "init", "initial")
        expected_rev = _get_svn_revision(wc_path)

        git_repo_name = "nablarch-document"
        git_local = str(
            tmp_path / "repo" / ".lw" / "nab-official" / f"v{ctx.version}" / git_repo_name
        )
        os.makedirs(os.path.dirname(git_local), exist_ok=True)
        import shutil
        shutil.copytree(git_repo, git_local)

        svn_source_url = f"file:///dummy/{wc_name}"

        from run import Context
        test_ctx = Context(
            version=ctx.version,
            repo=str(tmp_path / "repo"),
            concurrency=1,
            run_id="test-mixed"
        )
        os.makedirs(os.path.dirname(get_meta_path(test_ctx)), exist_ok=True)
        write_json(get_meta_path(test_ctx), {
            "generated_at": "",
            "sources": [
                {
                    "repo": f"https://github.com/nablarch/{git_repo_name}",
                    "branch": "main",
                    "commit": ""
                },
                {
                    "repo": svn_source_url,
                    "type": "svn",
                    "commit": ""
                }
            ]
        })

        update_knowledge_meta(test_ctx)

        updated = load_json(get_meta_path(test_ctx))
        assert updated["sources"][0].get("commit") == expected_sha
        assert updated["sources"][0].get("type") != "svn"
        assert updated["sources"][1].get("commit") == expected_rev
        assert updated["sources"][1].get("type") == "svn"


class TestPullOfficialReposSvn:

    def test_svn_update_detects_new_revision(self, ctx, tmp_path):
        """svn update pulls latest revision and reports updated=True when changed."""
        from run import Context

        wc_name = "nablarch-1x-docs"
        repo_url = _create_svn_repo(str(tmp_path / "svn_repo"))

        # Upstream working copy: used to commit new changes
        upstream_wc = str(tmp_path / "upstream_wc")
        _checkout_svn(repo_url, upstream_wc)
        _svn_add_file_and_commit(upstream_wc, "README.txt", "init", "initial")

        # Local working copy: the one pull_official_repos will update
        wc_path = str(
            tmp_path / "repo" / ".lw" / "nab-official" / f"v{ctx.version}" / wc_name
        )
        _checkout_svn(repo_url, wc_path)
        before_rev = _get_svn_revision(wc_path)

        # Commit a new change via upstream (local WC is now behind)
        _svn_add_file_and_commit(upstream_wc, "README.txt", "updated", "second commit")

        svn_source_url = f"file:///dummy/{wc_name}"
        test_ctx = Context(
            version=ctx.version,
            repo=str(tmp_path / "repo"),
            concurrency=1,
            run_id="test-pull-svn"
        )
        os.makedirs(os.path.dirname(get_meta_path(test_ctx)), exist_ok=True)
        write_json(get_meta_path(test_ctx), {
            "generated_at": "",
            "sources": [{"repo": svn_source_url, "type": "svn", "commit": before_rev}]
        })

        results = pull_official_repos(test_ctx)

        assert svn_source_url in results
        result = results[svn_source_url]
        assert result["before"] == before_rev
        assert int(result["after"]) > int(result["before"])
        assert result["updated"] is True

    def test_svn_no_update_when_current(self, ctx, tmp_path):
        """svn update reports updated=False when already at latest."""
        from run import Context

        wc_name = "nablarch-1x-docs"
        repo_url = _create_svn_repo(str(tmp_path / "svn_repo"))
        wc_path = str(
            tmp_path / "repo" / ".lw" / "nab-official" / f"v{ctx.version}" / wc_name
        )
        _checkout_svn(repo_url, wc_path)
        _svn_add_file_and_commit(wc_path, "README.txt", "init", "initial")
        current_rev = _get_svn_revision(wc_path)

        svn_source_url = f"file:///dummy/{wc_name}"
        test_ctx = Context(
            version=ctx.version,
            repo=str(tmp_path / "repo"),
            concurrency=1,
            run_id="test-pull-svn-noop"
        )
        os.makedirs(os.path.dirname(get_meta_path(test_ctx)), exist_ok=True)
        write_json(get_meta_path(test_ctx), {
            "generated_at": "",
            "sources": [{"repo": svn_source_url, "type": "svn", "commit": current_rev}]
        })

        results = pull_official_repos(test_ctx)

        result = results[svn_source_url]
        assert result["before"] == current_rev
        assert result["after"] == current_rev
        assert result["updated"] is False


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
            # Write sources and files together in catalog.json
            write_json(meta_path, {
                "generated_at": "2026-01-01",
                "sources": [{
                    "repo": "https://github.com/nablarch/nablarch-document",
                    "branch": "main" if ver == "6" else "v5-main",
                    "commit": commit
                }],
                "version": ver,
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


# ============================================================
# SVN auth args
# ============================================================

class TestSvnAuthArgs:
    """Unit tests for _svn_auth_args() — no SVN binary needed."""

    def test_no_env_vars_returns_empty(self, monkeypatch):
        monkeypatch.delenv("SVN_USERNAME", raising=False)
        monkeypatch.delenv("SVN_PASSWORD", raising=False)
        assert _svn_auth_args() == []

    def test_username_only(self, monkeypatch):
        monkeypatch.setenv("SVN_USERNAME", "alice")
        monkeypatch.delenv("SVN_PASSWORD", raising=False)
        assert _svn_auth_args() == ["--username", "alice", "--non-interactive"]

    def test_password_only(self, monkeypatch):
        monkeypatch.delenv("SVN_USERNAME", raising=False)
        monkeypatch.setenv("SVN_PASSWORD", "s3cr3t")
        assert _svn_auth_args() == ["--password", "s3cr3t", "--no-auth-cache", "--non-interactive"]

    def test_both_username_and_password(self, monkeypatch):
        monkeypatch.setenv("SVN_USERNAME", "alice")
        monkeypatch.setenv("SVN_PASSWORD", "s3cr3t")
        assert _svn_auth_args() == [
            "--username", "alice",
            "--password", "s3cr3t",
            "--no-auth-cache",
            "--non-interactive",
        ]


# ============================================================
# SVN diff failure → full regeneration
# ============================================================

class TestDetectChangedFilesSvnDiffFailure:
    """SVN diff failure (e.g. auth error) must trigger full regeneration, not silent empty list."""

    def _setup_svn_source_meta(self, ctx, tmp_path, wc_name, old_rev="1"):
        """Write catalog.json with an SVN source pointing to a dummy WC dir."""
        wc_path = str(
            tmp_path / "repo" / ".lw" / "nab-official" / f"v{ctx.version}" / wc_name
        )
        os.makedirs(wc_path, exist_ok=True)

        svn_source_url = f"file:///dummy/{wc_name}"
        meta_path = get_meta_path(ctx)
        os.makedirs(os.path.dirname(meta_path), exist_ok=True)
        write_json(meta_path, {
            "generated_at": "2026-01-01",
            "sources": [{
                "repo": svn_source_url,
                "type": "svn",
                "commit": old_rev,
            }],
            "version": ctx.version,
            "files": [],
        })
        return wc_path, svn_source_url

    def _mock_svn_diff_failure(self, args, cwd=None):
        if args[0] == "info":
            return subprocess.CompletedProcess(args, returncode=0, stdout="2\n", stderr="")
        if args[0] == "diff":
            return subprocess.CompletedProcess(
                args, returncode=1, stdout="",
                stderr="svn: E170001: Authentication required for 'SVN repo'"
            )
        return subprocess.CompletedProcess(args, returncode=0, stdout="", stderr="")

    def test_diff_failure_exits(self, ctx, tmp_path, monkeypatch):
        """svn diff --summarize failure → SystemExit(1), not silent [] or None."""
        wc_name = "nablarch-1x-docs"
        self._setup_svn_source_meta(ctx, tmp_path, wc_name, old_rev="1")
        monkeypatch.setattr(knowledge_meta, "_svn", self._mock_svn_diff_failure)

        with pytest.raises(SystemExit) as exc_info:
            detect_changed_files(ctx)
        assert exc_info.value.code == 1

    def test_diff_failure_prints_auth_hint(self, ctx, tmp_path, monkeypatch, capsys):
        """svn diff failure prints an error mentioning SVN_USERNAME/SVN_PASSWORD."""
        wc_name = "nablarch-1x-docs"
        self._setup_svn_source_meta(ctx, tmp_path, wc_name, old_rev="1")
        monkeypatch.setattr(knowledge_meta, "_svn", self._mock_svn_diff_failure)

        with pytest.raises(SystemExit):
            detect_changed_files(ctx)

        captured = capsys.readouterr()
        assert "SVN_USERNAME" in captured.out or "SVN_PASSWORD" in captured.out

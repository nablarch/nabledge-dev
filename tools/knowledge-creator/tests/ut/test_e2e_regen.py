"""End-to-end tests for the --regen flow.

These tests cover the full --regen pipeline:
  pull_official_repos → detect_changed_files → clean affected → generate

Key scenarios:
  1. First-time user (no classified.json or empty commit) → full generation
  2. Source files changed → detect and regenerate only changed files
  3. No source changes → skip generation (return empty list)
"""
import os
import subprocess
import pytest
from common import load_json, write_json
from knowledge_meta import (
    get_meta_path,
    get_local_repo_path,
    pull_official_repos,
    detect_changed_files,
    update_knowledge_meta,
    _get_head_commit,
)


def _git(args, cwd):
    """Helper to run git commands in a local repo."""
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


def _setup_repo_and_meta(tmp_path, version="6", sources=None):
    """Create a test repo with local git clones and knowledge-creator.json.

    Returns:
        (repo_root, local_repo_paths) tuple.
        repo_root: path to the simulated project root
        local_repo_paths: dict mapping repo_name to local clone path
    """
    repo_root = str(tmp_path / "project")
    os.makedirs(repo_root, exist_ok=True)

    local_repos = {}

    if sources is None:
        sources = [
            {
                "name": "nablarch-document",
                "repo": "https://github.com/nablarch/nablarch-document",
                "branch": "main",
                "files": {
                    "ja/application_framework/handlers/sample.rst": "Original content"
                }
            }
        ]

    meta_sources = []
    for src in sources:
        local_path = os.path.join(
            repo_root, f".lw/nab-official/v{version}", src["name"]
        )
        _create_local_repo(local_path)
        for rel_path, content in src.get("files", {}).items():
            _add_file_and_commit(local_path, rel_path, content, "add source file")

        local_repos[src["name"]] = local_path
        meta_sources.append({
            "repo": src["repo"],
            "branch": src["branch"],
            "commit": ""
        })

    # Write knowledge-creator.json with empty commits (first-run state)
    from run import Context
    ctx = Context(version=version, repo=repo_root, concurrency=1)
    os.makedirs(ctx.log_dir, exist_ok=True)
    meta_path = get_meta_path(ctx)
    os.makedirs(os.path.dirname(meta_path), exist_ok=True)
    write_json(meta_path, {
        "generated_at": "",
        "sources": meta_sources
    })

    return repo_root, local_repos, ctx


class TestRegenFirstRun:
    """Tests for first-time --regen user (no prior generation)."""

    def test_first_run_changes_but_no_classified_json_returns_none(self, tmp_path):
        """When source changed but no classified.json exists, returns None (full gen).

        Scenario: user ran --regen after setup but before any generation.
        Meta has a recorded commit (e.g., from a shared initial setup), source
        was updated, but classified.json doesn't exist yet (Phase A never ran).
        detect_changed_files should return None to trigger full generation.
        """
        repo_root, local_repos, ctx = _setup_repo_and_meta(tmp_path)
        repo_name = "nablarch-document"
        local_repo = local_repos[repo_name]

        # Record an old commit in meta (not the current HEAD)
        old_sha = _get_head_commit(local_repo)
        meta_path = get_meta_path(ctx)
        meta = load_json(meta_path)
        meta["generated_at"] = "2026-01-01"
        meta["sources"][0]["commit"] = old_sha
        write_json(meta_path, meta)

        # Simulate source update (HEAD now differs from recorded commit)
        _add_file_and_commit(
            local_repo,
            "ja/application_framework/handlers/sample.rst",
            "Updated content",
            "upstream update"
        )

        # No classified.json exists (user never ran Phase A)
        result = detect_changed_files(ctx)

        # Should return None → trigger full generation
        # (cannot map changed paths without classified.json)
        assert result is None, (
            "Without classified.json to map paths to file_ids, "
            "detect_changed_files should return None to trigger full generation"
        )

    def test_first_run_empty_commit_returns_none(self, tmp_path):
        """When knowledge-creator.json has empty commits, detect returns None (full gen)."""
        repo_root, local_repos, ctx = _setup_repo_and_meta(tmp_path)

        # knowledge-creator.json has empty commits (initial state from setup.sh)
        result = detect_changed_files(ctx)

        # Should return None → full generation
        assert result is None, (
            "Empty commit in knowledge-creator.json should return None "
            "to trigger full generation (same as UC1)"
        )

    def test_first_run_no_meta_returns_none(self, tmp_path):
        """When knowledge-creator.json does not exist at all, returns None."""
        repo_root = str(tmp_path / "project")
        os.makedirs(repo_root, exist_ok=True)
        from run import Context
        ctx = Context(version="6", repo=repo_root, concurrency=1)
        os.makedirs(ctx.log_dir, exist_ok=True)

        result = detect_changed_files(ctx)

        assert result is None, "Missing knowledge-creator.json should return None"


class TestRegenWithChanges:
    """Tests for --regen when source files have changed."""

    def _write_classified(self, ctx, local_repo_path, repo_name, files):
        """Write classified files into catalog.json (preserving existing sources)."""
        classified_files = []
        for file_id, rel_path in files.items():
            classified_files.append({
                "id": file_id,
                "source_path": f".lw/nab-official/v{ctx.version}/{repo_name}/{rel_path}",
                "format": "rst",
                "filename": rel_path.split("/")[-1],
                "type": "component",
                "category": "handlers",
                "output_path": f"component/handlers/{file_id}.json",
                "assets_dir": f"component/handlers/assets/{file_id}/"
            })
        catalog = load_json(ctx.classified_list_path)
        catalog["version"] = ctx.version
        catalog["generated_at"] = "2026-01-01T00:00:00Z"
        catalog["files"] = classified_files
        write_json(ctx.classified_list_path, catalog)

    def _record_commit(self, ctx, local_repos):
        """Record current HEAD commits in knowledge-creator.json (simulate Phase M)."""
        meta_path = get_meta_path(ctx)
        meta = load_json(meta_path)
        for source in meta["sources"]:
            repo_name = source["repo"].rstrip("/").split("/")[-1]
            if repo_name in local_repos:
                source["commit"] = _get_head_commit(local_repos[repo_name])
        meta["generated_at"] = "2026-01-01"
        write_json(meta_path, meta)

    def test_changed_source_file_detected(self, tmp_path):
        """Modified source file → only that source path returned."""
        repo_root, local_repos, ctx = _setup_repo_and_meta(tmp_path)
        repo_name = "nablarch-document"
        local_repo = local_repos[repo_name]

        # Setup classified.json
        self._write_classified(ctx, local_repo, repo_name, {
            "handlers-sample": "ja/application_framework/handlers/sample.rst",
            "handlers-other": "ja/application_framework/handlers/other.rst",
        })

        # Record current commit (simulate previous successful generation)
        self._record_commit(ctx, local_repos)

        # Simulate source change: update one file
        _add_file_and_commit(
            local_repo,
            "ja/application_framework/handlers/sample.rst",
            "Updated content",
            "update sample handler"
        )

        changed = detect_changed_files(ctx)

        expected_path = f".lw/nab-official/v{ctx.version}/{repo_name}/ja/application_framework/handlers/sample.rst"
        other_path = f".lw/nab-official/v{ctx.version}/{repo_name}/ja/application_framework/handlers/other.rst"
        assert changed is not None, "Should detect changes"
        assert expected_path in changed, "Changed file should be detected"
        assert other_path not in changed, "Unchanged file should not be detected"

    def test_multiple_changed_files_all_detected(self, tmp_path):
        """Multiple modified source files → all returned."""
        repo_root, local_repos, ctx = _setup_repo_and_meta(tmp_path)
        repo_name = "nablarch-document"
        local_repo = local_repos[repo_name]

        # Add second file before recording commit
        _add_file_and_commit(
            local_repo,
            "ja/application_framework/handlers/other.rst",
            "Other content",
            "add other handler"
        )

        self._write_classified(ctx, local_repo, repo_name, {
            "handlers-sample": "ja/application_framework/handlers/sample.rst",
            "handlers-other": "ja/application_framework/handlers/other.rst",
        })
        self._record_commit(ctx, local_repos)

        # Modify both files
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

        changed = detect_changed_files(ctx)

        sample_path = f".lw/nab-official/v{ctx.version}/{repo_name}/ja/application_framework/handlers/sample.rst"
        other_path = f".lw/nab-official/v{ctx.version}/{repo_name}/ja/application_framework/handlers/other.rst"
        assert set(changed) == {sample_path, other_path}, (
            "All changed files should be detected"
        )

    def test_no_source_changes_returns_empty_list(self, tmp_path):
        """No source changes since last generation → empty list (skip generation)."""
        repo_root, local_repos, ctx = _setup_repo_and_meta(tmp_path)
        repo_name = "nablarch-document"
        local_repo = local_repos[repo_name]

        self._write_classified(ctx, local_repo, repo_name, {
            "handlers-sample": "ja/application_framework/handlers/sample.rst",
        })
        self._record_commit(ctx, local_repos)

        # No changes since commit was recorded
        changed = detect_changed_files(ctx)

        assert changed == [], (
            "No source changes should return empty list to skip generation"
        )

    def test_split_files_source_path_returned(self, tmp_path):
        """When source file has split parts, the source path is returned once (deduplicated)."""
        repo_root, local_repos, ctx = _setup_repo_and_meta(tmp_path)
        repo_name = "nablarch-document"
        local_repo = local_repos[repo_name]

        # classified.json with split file parts referencing the same source
        source_path = "ja/application_framework/handlers/large.rst"
        classified_files = [
            {
                "id": "handlers-large--section-1",
                "source_path": f".lw/nab-official/v{ctx.version}/{repo_name}/{source_path}",
                "format": "rst",
                "filename": "large.rst",
                "type": "component",
                "category": "handlers",
                "output_path": "component/handlers/handlers-large--section-1.json",
                "assets_dir": "component/handlers/assets/handlers-large--section-1/",
                "split_info": {
                    "is_split": True,
                    "original_id": "handlers-large",
                    "part": 1,
                    "total_parts": 2
                }
            },
            {
                "id": "handlers-large--section-2",
                "source_path": f".lw/nab-official/v{ctx.version}/{repo_name}/{source_path}",
                "format": "rst",
                "filename": "large.rst",
                "type": "component",
                "category": "handlers",
                "output_path": "component/handlers/handlers-large--section-2.json",
                "assets_dir": "component/handlers/assets/handlers-large--section-2/",
                "split_info": {
                    "is_split": True,
                    "original_id": "handlers-large",
                    "part": 2,
                    "total_parts": 2
                }
            }
        ]
        _add_file_and_commit(local_repo, source_path, "Large file content", "add large file")
        catalog = load_json(ctx.classified_list_path)
        catalog["version"] = ctx.version
        catalog["files"] = classified_files
        write_json(ctx.classified_list_path, catalog)
        self._record_commit(ctx, local_repos)

        # Modify the shared source file
        _add_file_and_commit(local_repo, source_path, "Updated large file", "update large file")

        changed = detect_changed_files(ctx)

        # Returns source path (deduplicated), not individual split part IDs
        # Caller resolves to new catalog IDs after Phase A
        expected_source = f".lw/nab-official/v{ctx.version}/{repo_name}/{source_path}"
        assert changed == [expected_source], (
            "Source path should be returned once (deduplicated across split parts)"
        )


class TestRegenPullAndDetect:
    """Tests for pull_official_repos integration with detect_changed_files."""

    def test_pull_updates_local_repo(self, tmp_path):
        """pull_official_repos performs git pull on listed repos."""
        repo_root, local_repos, ctx = _setup_repo_and_meta(tmp_path)
        repo_name = "nablarch-document"
        local_repo = local_repos[repo_name]

        before_sha = _get_head_commit(local_repo)

        # Add a commit to the local repo (simulates remote update since it's the same repo)
        _add_file_and_commit(
            local_repo,
            "ja/application_framework/handlers/new.rst",
            "New content",
            "add new file"
        )
        after_sha = _get_head_commit(local_repo)
        assert before_sha != after_sha, "Test setup: commit should change SHA"

        # pull_official_repos should not raise errors even with local-only repos
        # (git pull on a local repo without remote will warn but not crash)
        results = pull_official_repos(ctx)
        assert repo_name in results or any(
            k.endswith(repo_name) for k in results.keys()
        ), "Result should reference the repo"

    def test_full_regen_flow_first_run(self, tmp_path):
        """Full --regen flow for first-time user: detect returns None → all files."""
        repo_root, local_repos, ctx = _setup_repo_and_meta(tmp_path)

        # First run: meta has empty commits, no classified.json
        changed = detect_changed_files(ctx)

        # Should be None → all files generated (UC1 equivalent)
        assert changed is None, (
            "First-time --regen should return None, triggering full generation "
            "of all files (same behavior as initial run without --regen)"
        )

    def test_full_regen_flow_after_generation(self, tmp_path):
        """Full --regen flow after initial generation: only changed files returned."""
        repo_root, local_repos, ctx = _setup_repo_and_meta(tmp_path)
        repo_name = "nablarch-document"
        local_repo = local_repos[repo_name]

        source_path = "ja/application_framework/handlers/sample.rst"

        # Simulate previous generation: add files to catalog and record commit
        catalog = load_json(ctx.classified_list_path)
        catalog["version"] = ctx.version
        catalog["files"] = [{
            "id": "handlers-sample",
            "source_path": f".lw/nab-official/v{ctx.version}/{repo_name}/{source_path}",
            "format": "rst",
            "filename": "sample.rst",
            "type": "component",
            "category": "handlers",
            "output_path": "component/handlers/handlers-sample.json",
            "assets_dir": "component/handlers/assets/handlers-sample/"
        }]
        write_json(ctx.classified_list_path, catalog)
        meta_path = get_meta_path(ctx)
        meta = load_json(meta_path)
        meta["generated_at"] = "2026-01-01"
        meta["sources"][0]["commit"] = _get_head_commit(local_repo)
        write_json(meta_path, meta)

        # Simulate upstream update: modify source file
        _add_file_and_commit(local_repo, source_path, "Updated content", "upstream update")

        # Run --regen detection
        changed = detect_changed_files(ctx)

        expected_source = f".lw/nab-official/v{ctx.version}/{repo_name}/{source_path}"
        assert changed == [expected_source], (
            "After upstream update, only the changed source path should be returned"
        )

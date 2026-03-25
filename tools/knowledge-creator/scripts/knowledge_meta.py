"""Knowledge meta file manager.

Manages plugin/knowledge-creator.json which records:
- generated_at: ISO datetime when generation completed
- sources: list of source entries, each either:
    {repo, branch, commit} for Git sources, or
    {repo, type, commit} for SVN sources (type="svn")

Provides source change detection by comparing recorded commits
with the current state of local clones/working copies.
"""

import os
import subprocess
from datetime import datetime, timezone, timedelta
from common import load_json, write_json


def get_meta_path(ctx) -> str:
    """Return absolute path to catalog.json."""
    return ctx.classified_list_path


def load_meta(ctx) -> dict:
    """Load catalog.json. Returns empty dict if not found."""
    path = get_meta_path(ctx)
    if not os.path.exists(path):
        return {}
    return load_json(path)


def get_local_repo_path(repo_url: str, version: str, repo_root: str) -> str:
    """Derive local clone path from repo URL and version.

    Mirrors the directory layout used by setup.sh:
      .lw/nab-official/v{version}/{repo_name}

    Each version's knowledge-creator.json lists its source repositories.
    setup.sh reads this file and clones each listed repository under the
    corresponding versioned directory (.lw/nab-official/v{version}/).
    """
    repo_name = repo_url.rstrip("/").split("/")[-1]
    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]
    return os.path.join(repo_root, f".lw/nab-official/v{version}", repo_name)


def _git(args: list, cwd: str) -> subprocess.CompletedProcess:
    """Run a git command and return CompletedProcess."""
    return subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True
    )


def _svn(args: list, cwd: str = None) -> subprocess.CompletedProcess:
    """Run an svn command and return CompletedProcess."""
    return subprocess.run(
        ["svn"] + args,
        cwd=cwd,
        capture_output=True,
        text=True
    )


def _svn_auth_args() -> list:
    """Build SVN auth options from environment variables SVN_USERNAME and SVN_PASSWORD.

    Mirrors the auth option handling in setup-svn.sh.
    Returns empty list if neither variable is set.
    """
    args = []
    username = os.environ.get("SVN_USERNAME", "")
    password = os.environ.get("SVN_PASSWORD", "")
    if username:
        args += ["--username", username]
    if password:
        args += ["--password", password, "--no-auth-cache"]
    if args:
        args += ["--non-interactive"]
    return args


def _get_head_commit(repo_path: str) -> str:
    """Get current HEAD commit SHA of a local git repository."""
    if not os.path.isdir(repo_path):
        return ""
    result = _git(["rev-parse", "HEAD"], cwd=repo_path)
    return result.stdout.strip() if result.returncode == 0 else ""


def _get_svn_revision(wc_path: str) -> str:
    """Get current revision of an SVN working copy."""
    if not os.path.isdir(wc_path):
        return ""
    result = _svn(["info", "--show-item", "revision"], cwd=wc_path)
    return result.stdout.strip() if result.returncode == 0 else ""


def get_local_svn_path(repo_url: str, version: str, repo_root: str) -> str:
    """Derive local SVN working copy path from repo URL and version.

    Mirrors the directory layout used by setup.sh:
      .lw/nab-official/v{version}/{wc_name}

    where wc_name is the last path component of the SVN repo URL.
    """
    wc_name = repo_url.rstrip("/").split("/")[-1]
    return os.path.join(repo_root, f".lw/nab-official/v{version}", wc_name)


def pull_official_repos(ctx) -> dict:
    """Pull all official repositories listed in knowledge-creator.json.

    Supports both Git (git pull) and SVN (svn update) sources.

    Returns:
        dict mapping repo_url to {"before": old_ref, "after": new_ref, "updated": bool}
    """
    meta = load_meta(ctx)
    results = {}

    for source in meta.get("sources", []):
        repo_url = source.get("repo", "")
        source_type = source.get("type", "git")

        if source_type == "svn":
            local_path = get_local_svn_path(repo_url, ctx.version, ctx.repo)

            if not os.path.isdir(local_path):
                print(f"   ⚠️ ローカル作業コピーが見つかりません: {local_path}")
                print(f"      setup.sh を実行してください")
                results[repo_url] = {"before": "", "after": "", "updated": False}
                continue

            before = _get_svn_revision(local_path)

            update = _svn(["update"] + _svn_auth_args(), cwd=local_path)
            if update.returncode != 0:
                print(f"   ⚠️ svn update失敗: {repo_url}")
                results[repo_url] = {"before": before, "after": before, "updated": False}
                continue

            after = _get_svn_revision(local_path)
            updated = before != after
            name = repo_url.rstrip("/").split("/")[-1]
            if updated:
                print(f"   📥 更新あり: {name} r{before} → r{after}")
            else:
                print(f"   ✅ 最新: {name} @ r{after}")
            results[repo_url] = {"before": before, "after": after, "updated": updated}

        else:
            branch = source.get("branch", "main")
            local_path = get_local_repo_path(repo_url, ctx.version, ctx.repo)

            if not os.path.isdir(local_path):
                print(f"   ⚠️ ローカルクローンが見つかりません: {local_path}")
                print(f"      setup.sh を実行してください")
                results[repo_url] = {"before": "", "after": "", "updated": False}
                continue

            before = _get_head_commit(local_path)

            checkout = _git(["checkout", branch], cwd=local_path)
            if checkout.returncode != 0:
                print(f"   ⚠️ checkout失敗: {repo_url} branch={branch}")
                results[repo_url] = {"before": before, "after": before, "updated": False}
                continue

            pull = _git(["pull"], cwd=local_path)
            if pull.returncode != 0:
                print(f"   ⚠️ pull失敗: {repo_url}")
                results[repo_url] = {"before": before, "after": before, "updated": False}
                continue

            after = _get_head_commit(local_path)
            updated = before != after
            if updated:
                print(f"   📥 更新あり: {repo_url.split('/')[-1]} {before[:7]} → {after[:7]}")
            else:
                print(f"   ✅ 最新: {repo_url.split('/')[-1]} @ {after[:7]}")
            results[repo_url] = {"before": before, "after": after, "updated": updated}

    return results


def detect_changed_files(ctx) -> list:
    """Detect file_ids whose source files changed since last generation.

    Compares recorded commit in knowledge-creator.json with current HEAD,
    then maps changed file paths to file_ids via classified.json.

    Returns:
        list of changed file_ids, or None if commit is empty (= first generation).
    """
    meta = load_meta(ctx)
    if not meta or not meta.get("sources"):
        print("   ⚠️ catalog.json が見つかりません（またはソース情報がありません）")
        return None

    # Collect changed file paths from all source repos
    changed_paths = set()
    has_empty_commit = False

    for source in meta.get("sources", []):
        source_type = source.get("type", "git")

        if source_type == "svn":
            repo_url = source.get("repo", "")
            old_rev = source.get("commit", "")

            if not repo_url:
                print("   ⚠️ SVNソースの repo が未設定です")
                continue
            if not old_rev:
                has_empty_commit = True
                continue

            local_path = get_local_svn_path(repo_url, ctx.version, ctx.repo)

            if not os.path.isdir(local_path):
                continue

            current_rev = _get_svn_revision(local_path)
            if current_rev == old_rev:
                continue

            # Get changed files between old revision and current revision
            result = _svn(
                ["diff", "--summarize", f"-r{old_rev}:{current_rev}"] + _svn_auth_args() + [local_path]
            )
            if result.returncode != 0:
                print(f"   ❌ SVN差分取得失敗: {repo_url}")
                print(f"      SVN_USERNAME / SVN_PASSWORD 環境変数を設定してから再実行してください")
                raise SystemExit(1)
            local_norm = os.path.normpath(local_path)
            for line in result.stdout.strip().splitlines():
                if not line.strip():
                    continue
                parts = line.split(None, 1)
                if len(parts) != 2:
                    continue
                _, path = parts
                abs_path = os.path.normpath(path)
                if abs_path.startswith(local_norm):
                    rel = abs_path[len(local_norm):].lstrip(os.sep)
                    changed_paths.add((local_path, rel))
        else:
            repo_url = source.get("repo", "")
            old_commit = source.get("commit", "")
            local_path = get_local_repo_path(repo_url, ctx.version, ctx.repo)

            if not old_commit:
                has_empty_commit = True
                continue

            if not os.path.isdir(local_path):
                continue

            head = _get_head_commit(local_path)
            if head == old_commit:
                continue

            # Get changed files between old commit and HEAD
            result = _git(
                ["diff", "--name-only", old_commit, "HEAD"],
                cwd=local_path
            )
            if result.returncode == 0:
                for line in result.stdout.strip().splitlines():
                    if line:
                        changed_paths.add((local_path, line.strip()))

    if has_empty_commit:
        print("   ⚠️ 初回生成前のため全ファイルが再生成対象です")
        return None

    if not changed_paths:
        return []

    # Map changed paths to file_ids using classified files in catalog.json
    # meta is already loaded; "files" key is added by Phase A
    if "files" not in meta:
        print("   ⚠️ catalog.json に files がありません。先に Phase A を実行してください")
        return None

    changed_ids = []

    for fi in meta["files"]:
        source_path = fi.get("source_path", "")
        # source_path is relative to repo root, e.g.:
        #   .lw/nab-official/v6/nablarch-document/ja/application_framework/...
        # git diff output is relative to the repo clone dir, e.g.:
        #   ja/application_framework/...
        # So we check if source_path ends with the git diff path
        #
        # Note: split files share the same source_path with different file_ids
        # (e.g. handlers-sample--section-1, handlers-sample--section-2).
        # Since we iterate all entries, all split parts are correctly detected.
        abs_source = os.path.join(ctx.repo, source_path)
        for local_repo, diff_path in changed_paths:
            abs_diff = os.path.join(local_repo, diff_path)
            if os.path.normpath(abs_source) == os.path.normpath(abs_diff):
                changed_ids.append(fi["id"])
                break

    return changed_ids


def update_knowledge_meta(ctx):
    """Update plugin/knowledge-creator.json after successful Phase M.

    Reads repo/branch from the existing knowledge-creator.json,
    resolves each to a local clone path, reads the current HEAD commit,
    and writes back generated_at + commits.

    Skipped in test mode to prevent overwriting production metadata.

    Args:
        ctx: Context object (ctx.repo, ctx.version)
    """
    if getattr(ctx, "test_file", None):
        print(f"   ⏭️ テストモードのため catalog.json の更新をスキップ")
        return

    meta_path = get_meta_path(ctx)

    if not os.path.exists(meta_path):
        print(f"   ⚠️ catalog.json が見つかりません: {meta_path}")
        return

    meta = load_json(meta_path)

    updated_sources = []
    for source in meta.get("sources", []):
        source_type = source.get("type", "git")
        repo_url = source.get("repo", "")

        if source_type == "svn":
            local_path = get_local_svn_path(repo_url, ctx.version, ctx.repo) if repo_url else ""
            revision = _get_svn_revision(local_path) if local_path and os.path.isdir(local_path) else ""
            if not revision:
                print(f"   ⚠️ リビジョン取得失敗: {repo_url} (path: {local_path})")
            updated_sources.append({
                "repo": repo_url,
                "type": "svn",
                "commit": revision,
            })
        else:
            branch = source.get("branch", "main")
            local_path = get_local_repo_path(repo_url, ctx.version, ctx.repo)
            commit = _get_head_commit(local_path) if os.path.isdir(local_path) else ""
            if not commit:
                print(f"   ⚠️ コミット取得失敗: {repo_url} (path: {local_path})")
            updated_sources.append({
                "repo": repo_url,
                "branch": branch,
                "commit": commit
            })

    meta["generated_at"] = datetime.now(tz=timezone(timedelta(hours=9))).strftime("%Y-%m-%dT%H:%M:%S+09:00")
    meta["sources"] = updated_sources

    write_json(meta_path, meta)
    print(f"   💾 catalog.json 更新完了: {meta_path}")
    for s in updated_sources:
        if s.get("type") == "svn":
            rev = s.get("commit") or "(取得失敗)"
            print(f"     {s['repo']} @ r{rev}")
        else:
            commit_short = s['commit'][:7] if s['commit'] else '(取得失敗)'
            print(f"     {s['repo']} @ {commit_short}")

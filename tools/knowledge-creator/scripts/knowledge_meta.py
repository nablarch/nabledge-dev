"""Knowledge meta file manager.

Manages plugin/knowledge-creator.json which records:
- generated_at: ISO date when generation completed
- sources: list of {repo, branch, commit} for each official doc repository

Provides source change detection by comparing recorded commits
with current HEAD of local clones.
"""

import os
import subprocess
from datetime import date
from common import load_json, write_json


KNOWLEDGE_META_RELATIVE = ".claude/skills/nabledge-{version}/plugin/knowledge-creator.json"


def get_meta_path(ctx) -> str:
    """Return absolute path to knowledge-creator.json for the given context."""
    return os.path.join(
        ctx.repo,
        KNOWLEDGE_META_RELATIVE.format(version=ctx.version)
    )


def load_meta(ctx) -> dict:
    """Load knowledge-creator.json. Returns empty dict if not found."""
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


def _get_head_commit(repo_path: str) -> str:
    """Get current HEAD commit SHA of a local git repository."""
    if not os.path.isdir(repo_path):
        return ""
    result = _git(["rev-parse", "HEAD"], cwd=repo_path)
    return result.stdout.strip() if result.returncode == 0 else ""


def pull_official_repos(ctx) -> dict:
    """Git pull all official repositories listed in knowledge-creator.json.

    Returns:
        dict mapping repo_url to {"before": old_sha, "after": new_sha, "updated": bool}
    """
    meta = load_meta(ctx)
    results = {}

    for source in meta.get("sources", []):
        repo_url = source.get("repo", "")
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
    if not meta:
        print("   ⚠️ knowledge-creator.json が見つかりません")
        return None

    # Collect changed file paths from all source repos
    changed_paths = set()
    has_empty_commit = False

    for source in meta.get("sources", []):
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

    # Map changed paths to file_ids using classified.json
    classified_path = ctx.classified_list_path
    if not os.path.exists(classified_path):
        print("   ⚠️ classified.json が見つかりません。先に Phase A を実行してください")
        return None

    classified = load_json(classified_path)
    changed_ids = []

    for fi in classified.get("files", []):
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


def update_knowledge_meta(ctx, dry_run: bool = False):
    """Update plugin/knowledge-creator.json after successful Phase M.

    Reads repo/branch from the existing knowledge-creator.json,
    resolves each to a local clone path, reads the current HEAD commit,
    and writes back generated_at + commits.

    Skipped in test mode to prevent overwriting production metadata.

    Args:
        ctx: Context object (ctx.repo, ctx.version)
        dry_run: If True, print what would be written but do not write.
    """
    if getattr(ctx, "test_file", None):
        print(f"   ⏭️ テストモードのため knowledge-creator.json の更新をスキップ")
        return

    meta_path = get_meta_path(ctx)

    if not os.path.exists(meta_path):
        print(f"   ⚠️ knowledge-creator.json が見つかりません: {meta_path}")
        return

    meta = load_json(meta_path)

    updated_sources = []
    for source in meta.get("sources", []):
        repo_url = source.get("repo", "")
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

    updated_meta = {
        "generated_at": date.today().isoformat(),
        "sources": updated_sources
    }

    if dry_run:
        import json
        print(f"   [dry-run] knowledge-creator.json を更新予定:")
        print(f"   {json.dumps(updated_meta, ensure_ascii=False, indent=2)}")
        return

    write_json(meta_path, updated_meta)
    print(f"   💾 knowledge-creator.json 更新完了: {meta_path}")
    for s in updated_sources:
        commit_short = s['commit'][:7] if s['commit'] else '(取得失敗)'
        print(f"     {s['repo']} @ {commit_short}")

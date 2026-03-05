"""Knowledge meta file manager.

Manages plugin/knowledge-creator.json which records:
- generated_at: ISO date when generation completed
- sources: list of {repo, branch, commit} for each official doc repository
"""

import os
import subprocess
from datetime import date
from .common import load_json, write_json


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
    """
    repo_name = repo_url.rstrip("/").split("/")[-1]
    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]
    return os.path.join(repo_root, f".lw/nab-official/v{version}", repo_name)


def _get_commit(repo_path: str) -> str:
    """Get current HEAD commit SHA of a local git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""


def update_knowledge_meta(ctx, dry_run: bool = False):
    """Update plugin/knowledge-creator.json after successful Phase M.

    Reads repo/branch from the existing knowledge-creator.json,
    resolves each to a local clone path, reads the current HEAD commit,
    and writes back generated_at + commits.

    This function must be called only after Phase M completes successfully
    so that generated_at reflects a fully finalized generation.

    Args:
        ctx: Context object (ctx.repo, ctx.version)
        dry_run: If True, print what would be written but do not write.
    """
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
        commit = _get_commit(local_path) if os.path.isdir(local_path) else ""
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

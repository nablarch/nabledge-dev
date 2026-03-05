# 実装タスク: knowledge-creator.json の導入

## 目的

公式ドキュメントリポジトリのどのコミット時点から知識ファイルを生成したかを記録・管理する。
利用者も参照できるよう `plugin/` ディレクトリに配置し、Gitで管理する。
また `setup.sh` のクローン対象も本ファイルから読み取るよう統一し、ソースURLの一元管理を実現する。

---

## 作業内容

以下の4つを順番に実施する。

1. 初期ファイルの作成（2ファイル）
2. `steps/knowledge_meta.py` の新規作成
3. `run.py` の修正
4. `setup.sh` の修正

---

## 作業 1: 初期ファイルの作成

### 1-1. `.claude/skills/nabledge-6/plugin/knowledge-creator.json` を新規作成する

ディレクトリ `.claude/skills/nabledge-6/plugin/` はすでに存在する。

```json
{
  "generated_at": "",
  "sources": [
    {
      "repo": "https://github.com/nablarch/nablarch-document",
      "branch": "main",
      "commit": ""
    },
    {
      "repo": "https://github.com/Fintan-contents/nablarch-system-development-guide",
      "branch": "main",
      "commit": ""
    }
  ]
}
```

### 1-2. `.claude/skills/nabledge-5/plugin/knowledge-creator.json` を新規作成する

ディレクトリ `.claude/skills/nabledge-5/plugin/` は存在しないため、`mkdir -p` で作成してからファイルを置く。

```json
{
  "generated_at": "",
  "sources": [
    {
      "repo": "https://github.com/nablarch/nablarch-document",
      "branch": "v5-main",
      "commit": ""
    }
  ]
}
```

---

## 作業 2: `tools/knowledge-creator/steps/knowledge_meta.py` の新規作成

`tools/knowledge-creator/steps/` ディレクトリに `knowledge_meta.py` を新規作成する。

既存の `source_tracker.py` と同様に `from .common import` の相対importを使う。

```python
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
```

---

## 作業 3: `tools/knowledge-creator/run.py` の修正

Phase M 完了直後に `update_knowledge_meta` を呼び出す1箇所を修正する。

**修正前**（260行目付近）:

```python
        # Phase M (replaces G+F in default flow)
        if "M" in phases:
            logger.info("\n📦Phase M: Merge + Resolve + Finalize")
            logger.info("   └─ Merging, resolving links, generating docs...")
            from steps.phase_m_finalize import PhaseMFinalize
            PhaseMFinalize(ctx, dry_run=args.dry_run).run()

        # Phase G (backward compat: only when explicitly specified without M)
```

**修正後**:

```python
        # Phase M (replaces G+F in default flow)
        if "M" in phases:
            logger.info("\n📦Phase M: Merge + Resolve + Finalize")
            logger.info("   └─ Merging, resolving links, generating docs...")
            from steps.phase_m_finalize import PhaseMFinalize
            PhaseMFinalize(ctx, dry_run=args.dry_run).run()

            logger.info("\n📝 knowledge-creator.json 更新")
            from steps.knowledge_meta import update_knowledge_meta
            update_knowledge_meta(ctx, dry_run=args.dry_run)

        # Phase G (backward compat: only when explicitly specified without M)
```

**呼び出しタイミングの根拠**:
- Phase M は Merge → Resolve → Finalize（index生成含む）まで完了した状態であり、知識ファイルが完全に確定した時点
- Phase B 完了後は C/D/E ループで内容が変わる可能性があるため不適切
- `--phase BCDE`（M省略）では更新されない。これは意図通り

---

## 作業 4: `setup.sh` の修正

クローン対象のリポジトリURLとブランチを `knowledge-creator.json` から読み取るよう変更する。

`setup.sh` の以下の範囲をまるごと置き換える。`clone_or_update_repo` 関数定義は変更しない。

**修正前**（339行目付近、`clone_or_update_repo` 関数定義の直後から `# Final summary` の直前まで）:

```bash
# Clone Nablarch 6 repositories (main branch)
print_status info "Setting up Nablarch 6 repositories..."
clone_or_update_repo "https://github.com/nablarch/nablarch-document.git" "$NAB_OFFICIAL_V6_DIR" "main"
clone_or_update_repo "https://github.com/nablarch/nablarch-single-module-archetype.git" "$NAB_OFFICIAL_V6_DIR" "main"
clone_or_update_repo "https://github.com/Fintan-contents/nablarch-system-development-guide.git" "$NAB_OFFICIAL_V6_DIR" "main"

# Clone Nablarch 5 repositories (v5-main branch)
print_status info "Setting up Nablarch 5 repositories..."
clone_or_update_repo "https://github.com/nablarch/nablarch-document.git" "$NAB_OFFICIAL_V5_DIR" "v5-main"
clone_or_update_repo "https://github.com/nablarch/nablarch-single-module-archetype.git" "$NAB_OFFICIAL_V5_DIR" "v5-main"
# Note: nablarch-system-development-guide not cloned for v5 (no v5 version exists)
```

**修正後**:

```bash
# Clone Nablarch official repositories from knowledge-creator.json
clone_repos_from_meta() {
    local version="$1"
    local target_dir="$2"
    local meta_file=".claude/skills/nabledge-${version}/plugin/knowledge-creator.json"

    if [ ! -f "$meta_file" ]; then
        print_status warning "knowledge-creator.json not found: $meta_file (skip)"
        return
    fi

    print_status info "Setting up Nablarch ${version} repositories from ${meta_file}..."

    local count
    count=$(jq '.sources | length' "$meta_file")

    for i in $(seq 0 $((count - 1))); do
        local repo_url branch
        repo_url=$(jq -r ".sources[$i].repo" "$meta_file")
        branch=$(jq -r ".sources[$i].branch" "$meta_file")
        clone_or_update_repo "${repo_url%.git}.git" "$target_dir" "$branch"
    done
}

clone_repos_from_meta "6" "$NAB_OFFICIAL_V6_DIR"
clone_repos_from_meta "5" "$NAB_OFFICIAL_V5_DIR"
```

**変更の意図**:
- クローン対象の正典を `knowledge-creator.json` に一元化
- `nablarch-single-module-archetype` は静的解析で代替するため `knowledge-creator.json` に含めておらず、自動的にクローン対象から外れる
- `nabledge-5/plugin/knowledge-creator.json` が存在しない間は `clone_repos_from_meta "5"` は警告を出してスキップする
- `jq` はセクション2（本関数より前）でインストール済みのため利用可能

---

## 更新されるケース・されないケース

| コマンド | Phase M 実行 | knowledge-creator.json 更新 |
|---|---|---|
| `nc.sh gen 6` | ✅ | ✅ |
| `nc.sh regen 6` | ✅ | ✅ |
| `nc.sh fix 6` | ✅ | ✅（`generated_at` のみ変わる、コミットは同じ） |
| `--phase BCDE`（M省略） | ❌ | ❌ |
| `--dry-run` | ✅（dry） | ✅（dry、書き込みなし） |

---

## 検証手順

### 手動確認

1. リポジトリをクリーンな状態でクローン
2. `plugin/knowledge-creator.json` が初期状態（`generated_at: ""`）で存在することを確認
3. `./setup.sh` を実行し、`knowledge-creator.json` から読み取ったリポジトリがクローンされることを確認
4. `nc.sh gen 6 --dry-run` を実行し、knowledge-creator.json の更新予定内容がログに出力されることを確認
5. `nc.sh gen 6 --test test-files-top3.json` を実行
6. `plugin/knowledge-creator.json` の内容を確認:
   - `generated_at` に本日日付が入っていること
   - `sources[].commit` に40桁のSHAが入っていること
   - 実際のローカルリポジトリのHEADと一致すること

### 確認コマンド

```bash
# knowledge-creator.json の内容確認
cat .claude/skills/nabledge-6/plugin/knowledge-creator.json

# 実際のコミットと照合
git -C .lw/nab-official/v6/nablarch-document rev-parse HEAD
git -C .lw/nab-official/v6/nablarch-system-development-guide rev-parse HEAD
```

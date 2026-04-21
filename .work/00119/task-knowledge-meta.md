# 実装タスク: ソース変更追随の仕組み導入

## 目的

公式ドキュメントリポジトリのどのコミット時点から知識ファイルを生成したかを記録し、
その情報をもとにソース変更を検知して、変更があったファイルだけを再生成する仕組みを導入する。

現状の `source_tracker.py` はローカルの `.logs/` にハッシュを保存するため、
別のメンバー・別のマシン・CI環境では変更検知が機能しない。
Git管理される `knowledge-creator.json` にコミットSHAを記録し、
`git diff` でファイル単位の変更検知を行う方式に置き換える。

---

## 設計

### knowledge-creator.json

`plugin/` ディレクトリに配置し、Gitで管理する。

```json
{
  "generated_at": "",
  "sources": [
    {
      "repo": "https://github.com/nablarch/nablarch-document",
      "branch": "main",
      "commit": ""
    }
  ]
}
```

- `generated_at`: Phase M 完了日（ISO date）
- `sources[].commit`: 生成時の公式リポジトリHEADコミットSHA
- `commit` が空 = 初回未生成状態

### 変更検知フロー（UC3 `regen`）

```
nc.sh regen 6
  1. 公式リポを git pull（最新化）
  2. knowledge-creator.json の記録済みコミット vs HEAD を比較
  3. コミット同一 → 「更新なし」で終了
  4. コミット異なる → git diff --name-only <old> HEAD で変更ファイル一覧取得
  5. classified.json の source_path と突き合わせて対象 file_id を特定
  6. 対象の Phase B/D 成果物をクリーン
  7. Phase BCDEM を対象 file_id に対して実行
  8. Phase M 完了後、knowledge-creator.json にHEADコミットを書き戻し
```

### UC一覧と変更検知の関係

| UC | コマンド | 動作 | コミット比較 | knowledge-creator.json 更新 |
|---|---|---|---|---|
| UC1 | `gen` | 全クリーン→全生成 | しない（全件） | Phase M後に書き戻し |
| UC2 | `gen --resume` | output存在でスキップ | しない（中断再開） | Phase M後に書き戻し |
| UC3 | `regen` | git pull→差分検知→該当のみ再生成 | **する** | Phase M後に書き戻し |
| UC4 | `regen --target` | 指定ファイルのみ再生成 | しない（明示指定） | Phase M後に書き戻し |
| UC5 | `fix` | 全件再検証・修正 | しない（品質改善） | Phase M後に書き戻し |
| UC6 | `fix --target` | 指定ファイル再検証・修正 | しない（品質改善） | Phase M後に書き戻し |

---

## 作業内容

以下の8つを順番に実施する。

1. 初期ファイルの作成（2ファイル）
2. `steps/knowledge_meta.py` の新規作成
3. `run.py` の修正
4. `nc.sh` の確認（コード変更なし）
5. `source_tracker.py` の廃止
6. `setup.sh` の修正
7. E2Eテストの追加
8. README の刷新

---

## 作業 1: 初期ファイルの作成

### 1-1. `.claude/skills/nabledge-6/plugin/knowledge-creator.json` を新規作成

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

### 1-2. `.claude/skills/nabledge-5/plugin/knowledge-creator.json` を新規作成

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
3つの責務を持つ:

- A) メタ情報の読み書き（load / update）
- B) 公式リポの git pull
- C) 変更ファイル検知（git diff → file_id 逆引き）

```python
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
```

---

## 作業 3: `run.py` の修正

4箇所を修正する。修正の要点は以下の2つ:

- `args.target` を直接書き換えず、ループ内ローカル変数 `effective_target` を使う
  （`args.target` はコマンドライン引数で全バージョン共通。`--version all` 時に v6 の結果が v5 に漏れるのを防ぐ）
- `effective_target` を Phase B / Phase D の両方に伝搬させる

### 3-1. `effective_target` の導入と `--regen` ハンドラの置き換え

**修正前**（181行目〜210行目）:

```python
        # --clean-phase: remove artifacts before run
        if args.clean_phase:
            from steps.cleaner import clean_phase_artifacts
            clean_phase_artifacts(ctx, args.clean_phase,
                                  target_ids=args.target, yes=args.yes)

        # --regen: detect source changes and clean affected artifacts
        if args.regen:
            from steps.source_tracker import detect_and_clean_changed
            detect_and_clean_changed(ctx, yes=args.yes)

        # Phase A
        if "A" in phases:
            logger.info("\n📋Phase A: Prepare")
            logger.info("   └─ Scanning documentation sources...")
            from steps.step1_list_sources import Step1ListSources
            from steps.step2_classify import Step2Classify
            sources = Step1ListSources(ctx, dry_run=args.dry_run).run()
            Step2Classify(ctx, dry_run=args.dry_run, sources_data=sources).run()

        # Phase B
        if "B" in phases:
            logger.info("\n🤖Phase B: Generate")
            logger.info("   └─ Converting documentation to knowledge files...")
            from steps.phase_b_generate import PhaseBGenerate
            PhaseBGenerate(ctx, dry_run=args.dry_run).run(target_ids=args.target)

            if not args.dry_run and os.path.exists(ctx.classified_list_path):
                from steps.source_tracker import save_hashes
                save_hashes(ctx)
```

**修正後**:

```python
        # effective_target: per-version target list
        # --target from CLI is the default; --regen may override per version
        effective_target = args.target

        # --clean-phase: remove artifacts before run
        if args.clean_phase:
            from steps.cleaner import clean_phase_artifacts
            clean_phase_artifacts(ctx, args.clean_phase,
                                  target_ids=effective_target, yes=args.yes)

        # --regen: pull official repos, detect source changes, clean affected
        # Note: This runs BEFORE Phase A. detect_changed_files reads the
        # PREVIOUS run's classified.json (from .logs/) to map git diff paths
        # to file_ids. If classified.json does not exist (first run), it
        # returns None → all files will be generated (same as UC1).
        if args.regen:
            from steps.knowledge_meta import pull_official_repos, detect_changed_files
            logger.info("\n📥 公式リポジトリを更新中...")
            pull_official_repos(ctx)

            logger.info("\n🔍 ソース変更を検知中...")
            changed = detect_changed_files(ctx)

            if changed is not None and len(changed) == 0:
                logger.info("   ✨ ソース変更なし")
                # Phase M の update_knowledge_meta を通らずに終了する（意図通り）
                continue

            if changed is not None:
                logger.info(f"   🔄 変更検知: {len(changed)} ファイル")
                for fid in changed[:10]:
                    logger.info(f"     - {fid}")
                if len(changed) > 10:
                    logger.info(f"     ... 他 {len(changed) - 10} ファイル")
                from steps.cleaner import clean_phase_artifacts
                clean_phase_artifacts(ctx, "BD", target_ids=changed, yes=args.yes)
                effective_target = changed
            # changed is None → 初回生成扱い、effective_target = None のまま全件実行

        # Phase A
        if "A" in phases:
            logger.info("\n📋Phase A: Prepare")
            logger.info("   └─ Scanning documentation sources...")
            from steps.step1_list_sources import Step1ListSources
            from steps.step2_classify import Step2Classify
            sources = Step1ListSources(ctx, dry_run=args.dry_run).run()
            Step2Classify(ctx, dry_run=args.dry_run, sources_data=sources).run()

        # Phase B
        if "B" in phases:
            logger.info("\n🤖Phase B: Generate")
            logger.info("   └─ Converting documentation to knowledge files...")
            from steps.phase_b_generate import PhaseBGenerate
            PhaseBGenerate(ctx, dry_run=args.dry_run).run(target_ids=effective_target)
```

**変更点のまとめ**:
- `effective_target = args.target` をループ先頭で初期化
- `--regen` で `changed` を検知したら `effective_target = changed` に代入（`args.target` は不変）
- `--clean-phase` と Phase B の `target_ids` を `effective_target` に差し替え
- `save_hashes` 呼び出しを削除

### 3-2. Phase D の `args.target` 参照を `effective_target` に差し替え

**修正前**（227行目付近）:

```python
            if "D" in phases:
                logger.info("\n🔍Phase D: Content Check")
                logger.info("   └─ Comparing knowledge files with source docs...")
                from steps.phase_d_content_check import PhaseDContentCheck
                pass_ids = c_result.get("pass_ids") if c_result else None
                # Intersect with --target if specified
                if args.target and pass_ids is not None:
                    target_set = set(args.target)
                    effective_ids = [fid for fid in pass_ids if fid in target_set]
                elif args.target:
                    effective_ids = args.target
                else:
                    effective_ids = pass_ids
```

**修正後**:

```python
            if "D" in phases:
                logger.info("\n🔍Phase D: Content Check")
                logger.info("   └─ Comparing knowledge files with source docs...")
                from steps.phase_d_content_check import PhaseDContentCheck
                pass_ids = c_result.get("pass_ids") if c_result else None
                # Intersect with effective_target if specified
                if effective_target and pass_ids is not None:
                    target_set = set(effective_target)
                    effective_ids = [fid for fid in pass_ids if fid in target_set]
                elif effective_target:
                    effective_ids = effective_target
                else:
                    effective_ids = pass_ids
```

### 3-3. Phase M 完了後に `update_knowledge_meta` を呼び出す

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

---

## 作業 4: `nc.sh` の修正

コード変更は不要。現状の nc.sh の UC3 は `--regen` を `run.py` に渡しており、
`run.py` 側の作業3で対応済み。

**動作確認ポイント**:
- UC3 は `--phase` 未指定 → `phases = "ABCDEM"`
- Phase A は全件スキャン（`classified.json` の生成に必要）
- Phase B / D は `effective_target` により変更ファイルのみに絞られる
- Phase M は全件対象（merge/resolve/index生成は全体で行う必要がある）

---

## 作業 5: `source_tracker.py` の廃止

### 5-1. `steps/source_tracker.py` を削除

```bash
git rm tools/knowledge-creator/steps/source_tracker.py
```

### 5-2. `tests/test_source_tracker.py` を削除

```bash
git rm tools/knowledge-creator/tests/test_source_tracker.py
```

### 5-3. 他ファイルからの参照を確認・除去

`source_tracker` を import している箇所は `run.py` の2箇所のみ。
作業3-1（`save_hashes` 削除、`detect_and_clean_changed` 置き換え）で対応済み。

確認コマンド:
```bash
grep -r "source_tracker" tools/knowledge-creator/ --include="*.py"
# → 何も出力されないこと
```

**既存テストへの影響**:
- `test_source_tracker.py` は作業5-2で削除するため問題なし
- `test_nc_sh.py` は nc.sh のコマンドルーティングのみテストしており、`source_tracker` への参照なし
- `test_run_phases.py` は全Phaseクラスをmockしており、`source_tracker` の遅延importは到達しないため影響なし
- その他のテスト（`test_pipeline.py`, `test_e2e_split.py` 等）に `source_tracker` への参照なし

---

## 作業 6: `setup.sh` の修正

クローン対象のリポジトリURLとブランチを `knowledge-creator.json` から読み取るよう変更する。
`clone_or_update_repo` 関数定義は変更しない。

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

**注意**: `nablarch-single-module-archetype` は `knowledge-creator.json` に含めていないため、自動的にクローン対象から外れる。

---

## 作業 7: E2Eテストの追加

`tests/test_knowledge_meta.py` を新規作成する。
テスト用にローカルgitリポジトリを作成し、コミット比較と変更検知をテストする。

```python
"""Tests for steps/knowledge_meta.py"""
import json
import os
import subprocess
import pytest
from steps.common import load_json, write_json
from steps.knowledge_meta import (
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
```

---

## 作業 8: README の刷新

`tools/knowledge-creator/README.md` を以下の3セクション構成で書き直す。
既存の README から再利用できる内容（Phase 詳細テーブル、Mermaid フローチャート、オプションテーブル）は
そのまま移植し、新たに追加する内容を以下に示す。

### 追加・変更する内容

1. **UC一覧テーブル**（以下をそのまま使う）:

| UC | コマンド | 用途 | 何が起きるか |
|---|---|---|---|
| UC1 | `nc.sh gen 6` | 初回の全件生成 | 全クリーン → Phase A〜M を順次実行 |
| UC2 | `nc.sh gen 6 --resume` | 中断からの再開 | 生成済みファイルをスキップして続行 |
| UC3 | `nc.sh regen 6` | 公式ドキュメント更新への追随 | git pull → コミット比較 → 変更ファイルのみ再生成 |
| UC4 | `nc.sh regen 6 --target FILE_ID` | 特定ファイルの再生成 | 指定ファイルをクリーン → 再生成 |
| UC5 | `nc.sh fix 6` | 品質改善（全件） | Phase C→D→E→M で再検証・修正 |
| UC6 | `nc.sh fix 6 --target FILE_ID` | 品質改善（指定ファイル） | 指定ファイルのみ再検証・修正 |

2. **ソース変更追随の仕組み**（新規セクション）:
   - `knowledge-creator.json` の役割とフォーマット
   - UC3 実行時の8ステップフロー（本ドキュメントの「設計 > 変更検知フロー」を転記）
   - `setup.sh` 実行でクローン対象も `knowledge-creator.json` から読み取ること

3. **開発ガイド**（新規セクション）:
   - テスト実行コマンド
   - テストファイル一覧テーブル（`test_knowledge_meta.py` を追加）
   - ディレクトリ構成に `plugin/knowledge-creator.json` の位置を追記

### 構成

```
# Knowledge Creator
（1行説明）

## セットアップ
（setup.sh の手順、必要なもの）

## 運用ガイド
### UC一覧（上記テーブル）
### ソース変更追随の仕組み（新規）
### Phase 詳細（既存のテーブル＋Mermaid移植）
### オプション一覧（既存テーブル移植）
### テストモード（既存の実行方法移植）

## 開発ガイド
### テスト実行（新規）
### テストの種類（新規）
### ディレクトリ構成（既存＋knowledge-creator.json追記）
```

---

## 検証手順

### 自動テスト

```bash
cd tools/knowledge-creator
python -m pytest tests/test_knowledge_meta.py -v
```

### 手動確認

1. リポジトリをクリーンな状態でクローン
2. `plugin/knowledge-creator.json` が初期状態（`generated_at: ""`, `commit: ""`）で存在することを確認
3. `./setup.sh` を実行し、`knowledge-creator.json` から読み取ったリポジトリがクローンされることを確認
4. `nc.sh gen 6 --dry-run` を実行し、`knowledge-creator.json` の更新予定内容がログに出力されることを確認
5. `nc.sh gen 6 --test test-files-top3.json` を実行
6. `plugin/knowledge-creator.json` の内容を確認:
   - `generated_at` に本日日付が入っていること
   - `sources[].commit` に40桁のSHAが入っていること
7. `nc.sh regen 6 --test test-files-top3.json` を実行し、「ソース変更なし」と表示されることを確認
8. 公式リポの任意のファイルを手動変更 → `nc.sh regen 6` で該当ファイルのみ再生成されることを確認

### 確認コマンド

```bash
# knowledge-creator.json の内容確認
cat .claude/skills/nabledge-6/plugin/knowledge-creator.json

# 実際のコミットと照合
git -C .lw/nab-official/v6/nablarch-document rev-parse HEAD
git -C .lw/nab-official/v6/nablarch-system-development-guide rev-parse HEAD

# source_tracker.py の参照が残っていないことを確認
grep -r "source_tracker" tools/knowledge-creator/ --include="*.py"
```

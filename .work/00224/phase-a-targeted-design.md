# Phase A 対象限定設計

**関連**: PR #224 作業記録
**日付**: 2026-03-26

## 問題

`kc regen --target X` 実行時、Phase A が**全ソースファイルを再分類**してしまう。

- #230 の split logic 変更で v5 カタログが 331 → 540 エントリに変化
- `_clean_stale_cache` が 214 個の旧キャッシュファイルを削除
- Phase B は 1 ファイルしか生成せず Phase M が壊れた状態で実行
- 結果: `.claude/skills/nabledge-5/` の 800+ ファイルが破損

## 設計方針

**Phase A の対象をコマンドの意図に合わせて限定する**

| コマンド | Phase A 現在 | Phase A あるべき |
|---------|------------|----------------|
| `gen` | 全ファイル | 全ファイル（変更なし）|
| `gen --resume` | 全ファイル | **スキップ**（既存カタログ再利用）|
| `regen --target X` | 全ファイル | **X のソースファイルのみ再分類** |
| `regen`（差分） | 全ファイル | **変更ソースファイルのみ再分類** |
| `fix` | 実行なし | 実行なし（変更なし）|

## 実装方針

### 1. `gen --resume`: Phase A スキップ

```python
# kc.sh の --resume フラグを run.py に渡す
# _run_pipeline で Phase A をスキップ

def kc_gen(ctx, resume=False):
    if resume and os.path.exists(ctx.classified_list_path):
        _run_pipeline(ctx, _make_args(ctx, phase="BCDEMV"))  # Phase A なし
    else:
        _run_pipeline(ctx, _make_args(ctx))  # 通常通り全フェーズ
```

### 2. `regen --target` / `regen`（差分）: 部分的 Phase A

**新関数 `_partial_phase_a(ctx, source_paths)`**:

```python
def _partial_phase_a(ctx, source_paths):
    """指定ソースファイルのみカタログを再分類・更新する。"""
    catalog = load_json(ctx.classified_list_path)

    # 対象ソースの旧エントリを保存（stale 削除用）
    old_entries = [f for f in catalog["files"]
                   if f["source_path"] in source_paths]

    # 対象ソースのみ再分類
    sources = [{"path": sp, ...} for sp in source_paths]
    new_entries = Step2Classify(ctx, sources_data=sources).run(return_only=True)

    # カタログ更新: 旧エントリ削除 → 新エントリ挿入
    remaining = [f for f in catalog["files"]
                 if f["source_path"] not in source_paths]
    catalog["files"] = remaining + new_entries
    write_json(ctx.classified_list_path, catalog)

    # stale cleanup: 旧エントリのキャッシュのみ削除
    _clean_stale_cache_for_entries(ctx, old_entries, new_entries)
```

**新関数 `_clean_stale_cache_for_entries(ctx, old_entries, new_entries)`**:

```python
def _clean_stale_cache_for_entries(ctx, old_entries, new_entries):
    """対象ソースに関連する旧キャッシュファイルのみ削除する。"""
    new_ids = {e["id"] for e in new_entries}
    for entry in old_entries:
        if entry["id"] not in new_ids:
            cache_path = f"{ctx.knowledge_cache_dir}/{entry['output_path']}"
            if os.path.exists(cache_path):
                os.remove(cache_path)
```

### 3. `_run_pipeline` の変更

```python
# Phase A
if "A" in phases:
    if args.resume and os.path.exists(ctx.classified_list_path):
        # gen --resume: 既存カタログ再利用
        pass
    elif effective_target or (args.regen and changed_source_paths):
        # regen --target / regen（差分）: 対象ソースのみ再分類
        source_paths = _resolve_target_source_paths(
            ctx, effective_target, changed_source_paths
        )
        _partial_phase_a(ctx, source_paths)
    else:
        # gen: 全件（変更なし）
        sources = Step1ListSources(ctx).run()
        Step2Classify(ctx, sources_data=sources).run()
        _clean_stale_cache(ctx)  # 全件のみ full cleanup
```

### 4. `Step2Classify` への `return_only` 引数追加

現在 `Step2Classify.run()` はカタログを上書き保存する。
部分更新では「分類結果のみ返す（保存しない）」モードが必要。

```python
class Step2Classify:
    def run(self, return_only=False):
        entries = self._classify()
        if not return_only:
            self._save_catalog(entries)  # 全件の場合のみ保存
        return entries
```

## 影響範囲

- `scripts/run.py`: `_run_pipeline`, `kc_gen`, `kc_regen_target`, 新関数追加
- `scripts/step2_classify.py`: `return_only` 引数追加
- `kc.sh`: `--resume` フラグを `run.py` に渡す
- `tests/e2e/test_e2e.py`: `regen --target` テストで「他のキャッシュが維持される」アサーション追加

## テスト追加方針

```python
def test_regen_target_preserves_other_cache():
    """regen --target 1ファイルで、他の既存キャッシュが削除されないことを確認"""
    # 事前: N ファイルのキャッシュを配置
    setup_full_cache(ctx, N)
    before_count = count_cache_files(ctx)

    kc_regen_target(ctx, ["blank-project-FirstStepContainer"])

    after_count = count_cache_files(ctx)
    # 対象ソースの旧エントリ数だけ減り、新エントリ数だけ増える
    # 他のキャッシュは変化しない
    assert after_count >= before_count - len(old_entries_for_target)
```

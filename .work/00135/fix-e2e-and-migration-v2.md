# タスク: E2E テスト修正・マイグレーション修正

## 前提

ブランチ `120-generate-all-nabledge6-knowledge-files` の最新コミット `e858893` に対する修正。

## 禁止事項

- モンキーパッチ（`モジュール.関数名 = 別の関数` による差し替え）は使わない。引数で渡す。
- Phase クラスを直接呼ばない。run.py の main() を経由する。
- タスクドキュメントに記載のないファイルを変更しない。
- 各 Step の検証コマンドの assert が全てパスしてから次の Step に進む。

## 作業手順

1. generate_expected.py の RecursionError 修正
2. test_cache_separation.py を run.py main() 経由に書き直し
3. テスト実行 → 5件パス確認
4. マイグレーション: catalog.json 復元
5. マイグレーション: cache knowledge を split 状態に変換
6. 整合性検証
7. コミット・プッシュ

---

## Step 1: generate_expected.py の RecursionError 修正

### 変更ファイル

`tests/generate_expected.py` のみ。

### 変更内容

`compute_merged_files` 関数（L498）の引数に `knowledge_fn` を追加する。関数内の `mock_phase_b_knowledge` 呼び出し 4箇所を全て `knowledge_fn` に置き換える。

**変更前（L498）:**
```python
def compute_merged_files(catalog_entries: list) -> dict:
```

**変更後:**
```python
def compute_merged_files(catalog_entries: list, knowledge_fn=None) -> dict:
    if knowledge_fn is None:
        knowledge_fn = mock_phase_b_knowledge
```

**関数内の置き換え（4箇所）:**
- L519: `first_knowledge = mock_phase_b_knowledge(parts[0]['id'], parts[0])` → `first_knowledge = knowledge_fn(parts[0]['id'], parts[0])`
- L531: `pk = mock_phase_b_knowledge(p['id'], p)` → `pk = knowledge_fn(p['id'], p)`
- L543: `pk = mock_phase_b_knowledge(p['id'], p)` → `pk = knowledge_fn(p['id'], p)`
- L556: `pk = mock_phase_b_knowledge(p['id'], p)` → `pk = knowledge_fn(p['id'], p)`
- L571: `k = mock_phase_b_knowledge(e['id'], e)` → `k = knowledge_fn(e['id'], e)`

### 検証

```bash
cd tools/knowledge-creator
python -c "
from tests.generate_expected import compute_merged_files, classify_all, list_sources, mock_phase_b_knowledge, mock_phase_e_knowledge
import os
sources = list_sources(os.path.abspath('../..'), '6')
entries = classify_all(sources, os.path.abspath('../..'))
# Phase B版（正常動作すること）
m1 = compute_merged_files(entries)
print(f'merged_b: {len(m1)} files')
# Phase E版（RecursionErrorにならないこと）
m2 = compute_merged_files(entries, knowledge_fn=mock_phase_e_knowledge)
print(f'merged_e: {len(m2)} files')
assert len(m1) == len(m2)
print('OK: no RecursionError')
"
```

---

## Step 2: test_cache_separation.py を run.py main() 経由に書き直し

### 変更ファイル

`tests/test_cache_separation.py` のみ。全体を書き直す。

### 要件

1. 全テストで `run.py` の `main()` 関数を呼ぶ。Phase クラスを直接呼ばない。
2. `TestContext` で全出力を `.logs/{run_id}/` にリダイレクトする（現状維持）。
3. `_make_cc_mock()` で CC mock を作り、counter で呼び出し回数を記録する（現状維持）。
4. `generate_expected.py` から期待値を生成し、全出力ファイルを `==` で完全一致比較する。
5. 各 Step 完了後の assert はコメントではなく `assert` 文で書く。

### _run_main 関数

以下の関数を `test_cache_separation.py` に定義する。既存の `test_run_phases.py` L94-128 と同じパターンだが、TestContext と counter 付き CC mock を使う点が異なる。

```python
def _run_main(ctx, mock_fn, phases=None, target=None, clean_phase=None):
    """run.py main() を CC mock 付きで実行する。

    ctx は TestContext インスタンス。
    mock_fn は _make_cc_mock() の戻り値。
    """
    from unittest.mock import patch, MagicMock

    args = MagicMock()
    args.version = "6"
    args.phase = phases          # None = "ABCDEM"
    args.max_rounds = ctx.max_rounds
    args.concurrency = ctx.concurrency
    args.dry_run = False
    args.test = None
    args.run_id = ctx.run_id
    args.yes = True
    args.regen = False
    args.target = target         # list of base_names, or None
    args.clean_phase = clean_phase
    args.verbose = False

    original_abspath = os.path.abspath

    def patched_abspath(path):
        result = original_abspath(path)
        if result == original_abspath(os.path.join(TOOL_DIR, '..', '..')):
            return ctx.repo
        return result

    with patch("sys.argv", ["run.py", "--version", "6"]), \
         patch("argparse.ArgumentParser.parse_args", return_value=args), \
         patch("os.path.abspath", side_effect=patched_abspath), \
         patch("run.Context", lambda **kwargs: ctx), \
         patch("phase_b_generate._default_run_claude", mock_fn), \
         patch("phase_d_content_check._default_run_claude", mock_fn), \
         patch("phase_e_fix._default_run_claude", mock_fn), \
         patch("phase_f_finalize._default_run_claude", mock_fn):
        import run as run_module
        run_module.main()
```

注意: `patch("run.Context", lambda **kwargs: ctx)` で main() 内の Context 生成を TestContext インスタンスに差し替える。main() は `Context(version=v, repo=repo_root, ...)` と呼ぶので、lambda で受けて ctx を返す。

### expected fixture の修正（L244-247）

**変更前:**
```python
orig_fn = ge.mock_phase_b_knowledge
ge.mock_phase_b_knowledge = ge.mock_phase_e_knowledge
expected_merged_fixed = compute_merged_files(catalog_entries)
ge.mock_phase_b_knowledge = orig_fn
```

**変更後:**
```python
expected_merged_fixed = compute_merged_files(catalog_entries, knowledge_fn=ge.mock_phase_e_knowledge)
```

### 各テストの書き換え

全5テストを以下のパターンに統一する:

```python
def test_xxx(self, expected):
    ctx = _make_ctx(max_rounds=2)
    counter = {"B": [], "D": [], "E": [], "F": []}
    mock = _make_cc_mock(
        expected["expected_knowledge_cache"],
        expected["expected_fixed_cache"],
        counter,
    )
    try:
        # setup（必要に応じて _copy_state 等）
        ...

        # 実行: run.py main() 経由
        _run_main(ctx, mock, phases=..., target=..., clean_phase=...)

        # assert: 全出力ファイルを期待値と == で比較
        ...
    finally:
        if os.path.exists(ctx.log_dir):
            shutil.rmtree(ctx.log_dir)
```

**test_gen**: `_run_main(ctx, mock)`（phases=None = ABCDEM）
**test_gen_resume**: knowledge_cache_dir に1件事前配置後、`_run_main(ctx, mock)`
**test_regen_target**: gen_state コピー後、`_run_main(ctx, mock, phases="ABCDEM", target=[24 base_names], clean_phase="BD")`
**test_fix**: gen_state コピー後、`_run_main(ctx, mock, phases="CDEM")`
**test_fix_target**: gen_state コピー後、`_run_main(ctx, mock, phases="CDEM", target=[24 base_names], clean_phase="D")`

アサート部分は現状のコードを維持する（catalog 完全一致、knowledge_cache 完全一致、merged knowledge 完全一致、counter 回数チェック、catalog split 状態チェック）。

### gen_state fixture の修正

gen_state fixture（L352-385）も `_run_main` 経由に変更:

```python
@pytest.fixture(scope="session")
def gen_state(expected):
    ctx = _make_ctx(run_id=f"gen-state-{uuid.uuid4().hex[:8]}", max_rounds=2)
    counter = {"B": [], "D": [], "E": [], "F": []}
    mock = _make_cc_mock(
        expected["expected_knowledge_cache"],
        expected["expected_fixed_cache"],
        counter,
    )

    _run_main(ctx, mock)  # phases=None = ABCDEM

    yield {"ctx": ctx, "counter": counter}

    if os.path.exists(ctx.log_dir):
        shutil.rmtree(ctx.log_dir)
```

### 検証

```bash
cd tools/knowledge-creator
python -m pytest tests/test_cache_separation.py -v
```

5テスト全てパスすること。

```bash
python -m pytest tests/ -v
```

既存テスト含め全件パスすること。

---

## Step 3: マイグレーション: catalog.json 復元

### 実行

```bash
cd tools/knowledge-creator
python -c "
import sys, os
sys.path.insert(0, 'scripts')
from run import Context
from step1_list_sources import Step1ListSources
from step2_classify import Step2Classify

ctx = Context(version='6', repo=os.path.abspath('../..'), concurrency=1, run_id='migrate')
os.makedirs(ctx.log_dir, exist_ok=True)
sources = Step1ListSources(ctx).run()
Step2Classify(ctx, sources_data=sources).run()
"
```

### 検証（全 assert がパスすること）

```bash
cd tools/knowledge-creator
python -c "
import json
from collections import Counter
d = json.load(open('.cache/v6/catalog.json'))
ids = [f['id'] for f in d['files']]
assert len(ids) == 421, f'Expected 421, got {len(ids)}'
assert len(ids) == len(set(ids)), f'Duplicate IDs: {[k for k,v in Counter(ids).items() if v>1]}'
assert all('base_name' in f for f in d['files']), 'Missing base_name'
split_count = sum(1 for f in d['files'] if 'split_info' in f)
assert split_count == 296, f'Expected 296 split entries, got {split_count}'
print(f'catalog: OK (421 entries, 296 split, 0 duplicates)')
"
```

---

## Step 4: マイグレーション: cache knowledge を split 状態に変換

### 変更前の状態

`.cache/v6/knowledge/` に 331 merged ファイル（`.claude/skills/nabledge-6/knowledge/` のコピー）。

### 変更後の期待状態

`.cache/v6/knowledge/` に 417 split ファイル（421 - 4 LOSER）。

### スクリプト作成

`tools/knowledge-creator/scripts/migrate_to_split_cache.py` を以下の内容で作成する。

```python
#!/usr/bin/env python3
"""Migrate merged knowledge cache to split state.

Reads:
- .cache/v6/catalog.json (split state, from Step 3)
- .claude/skills/nabledge-6/knowledge/ (merged knowledge, 331 files)

Writes:
- .cache/v6/knowledge/ (split knowledge, 417 files)

Skips:
- LOSER files (4 files from ID dedup whose content was overwritten)
"""
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(__file__))
from common import load_json, write_json


def main():
    repo = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    catalog_path = os.path.join(repo, 'tools/knowledge-creator/.cache/v6/catalog.json')
    merged_dir = os.path.join(repo, '.claude/skills/nabledge-6/knowledge')
    cache_dir = os.path.join(repo, 'tools/knowledge-creator/.cache/v6/knowledge')

    catalog = load_json(catalog_path)
    entries = catalog['files']

    # Clear existing cache
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)

    # Group split entries
    split_groups = {}
    non_split = []
    for e in entries:
        if 'split_info' in e and e['split_info'].get('is_split'):
            oid = e['split_info']['original_id']
            split_groups.setdefault(oid, []).append(e)
        else:
            non_split.append(e)

    created = 0
    skipped = []

    # Non-split: copy merged knowledge with id change
    for e in non_split:
        merged_path = os.path.join(merged_dir, e['output_path'])
        if not os.path.exists(merged_path):
            skipped.append(e['id'])
            continue
        knowledge = load_json(merged_path)
        knowledge['id'] = e['id']
        cache_path = os.path.join(cache_dir, e['output_path'])
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        write_json(cache_path, knowledge)
        created += 1

    # Split groups: split merged knowledge into parts
    for oid, parts in split_groups.items():
        parts.sort(key=lambda p: p['split_info']['part'])

        # Find merged file
        type_ = parts[0]['type']
        category = parts[0]['category']
        merged_path = os.path.join(merged_dir, type_, category, f'{oid}.json')
        if not os.path.exists(merged_path):
            for p in parts:
                skipped.append(p['id'])
            continue

        merged = load_json(merged_path)
        merged_index = merged.get('index', [])
        merged_sections = merged.get('sections', {})

        # Distribute index/sections to parts based on section_range.sections count
        idx_pos = 0
        for part in parts:
            sr = part.get('section_range', {})
            n_sections = len([s for s in sr.get('sections', []) if s])
            if n_sections == 0:
                n_sections = 1  # fallback

            # Take n_sections from merged_index
            part_index = merged_index[idx_pos:idx_pos + n_sections]
            part_sections = {}
            for ie in part_index:
                sid = ie['id']
                if sid in merged_sections:
                    content = merged_sections[sid]
                    # Replace asset paths: assets/{oid}/ -> assets/{part_id}/
                    content = content.replace(f'assets/{oid}/', f'assets/{part["id"]}/')
                    part_sections[sid] = content

            part_knowledge = {
                'id': part['id'],
                'title': merged.get('title', ''),
                'no_knowledge_content': merged.get('no_knowledge_content', False),
                'official_doc_urls': merged.get('official_doc_urls', []),
                'index': part_index,
                'sections': part_sections,
            }

            cache_path = os.path.join(cache_dir, part['output_path'])
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            write_json(cache_path, part_knowledge)
            created += 1
            idx_pos += n_sections

    print(f'Created: {created} split knowledge files')
    print(f'Skipped (LOSER/missing): {len(skipped)} files')
    if skipped:
        print('Skipped IDs:')
        for s in skipped:
            print(f'  {s}')


if __name__ == '__main__':
    main()
```

### 実行

```bash
cd tools/knowledge-creator
python scripts/migrate_to_split_cache.py
```

### 検証（全 assert がパスすること）

```bash
cd tools/knowledge-creator
python -c "
import json, os

# cache file count
cache_count = sum(1 for r, d, f in os.walk('.cache/v6/knowledge') for x in f if x.endswith('.json'))
assert cache_count >= 410, f'Expected ~417 cache files, got {cache_count}'
print(f'cache files: {cache_count}')

# Section count match: cache total == nabledge-6 total
cache_sec = 0
for root, _, files in os.walk('.cache/v6/knowledge'):
    for f in files:
        if f.endswith('.json'):
            d = json.load(open(os.path.join(root, f)))
            cache_sec += len(d.get('sections', {}))

kb_sec = 0
for root, _, files in os.walk('../../.claude/skills/nabledge-6/knowledge'):
    for f in files:
        if f.endswith('.json'):
            d = json.load(open(os.path.join(root, f)))
            kb_sec += len(d.get('sections', {}))

print(f'cache sections: {cache_sec}')
print(f'nabledge-6 sections: {kb_sec}')
assert cache_sec == kb_sec, f'Section count mismatch: cache={cache_sec} vs kb={kb_sec}'
print('sections: OK')

# Every catalog entry (except LOSERs) has a cache file
catalog = json.load(open('.cache/v6/catalog.json'))
missing = []
for e in catalog['files']:
    p = os.path.join('.cache/v6/knowledge', e['output_path'])
    if not os.path.exists(p):
        missing.append(e['id'])
print(f'missing cache files: {len(missing)}')
assert len(missing) <= 10, f'Too many missing: {missing}'
if missing:
    print('Missing (expected LOSERs):')
    for m in missing:
        print(f'  {m}')
print('migration: OK')
"
```

---

## Step 5: 最終検証

全ての assert がパスすること:

```bash
cd tools/knowledge-creator

# 1. テスト
python -m pytest tests/test_cache_separation.py -v
python -m pytest tests/ -v

# 2. catalog
python -c "
import json
from collections import Counter
d = json.load(open('.cache/v6/catalog.json'))
ids = [f['id'] for f in d['files']]
assert len(ids) == 421
assert len(ids) == len(set(ids))
assert all('base_name' in f for f in d['files'])
print('catalog: OK')
"

# 3. nabledge-6 knowledge (変更なし)
python -c "
import os
count = sum(1 for r,d,f in os.walk('../../.claude/skills/nabledge-6/knowledge') for x in f if x.endswith('.json'))
assert count == 331, f'Expected 331, got {count}'
print(f'nabledge-6: {count} files OK')
"
```

---

## Step 6: コミット・プッシュ

```
fix: E2E test recursion error, main() integration, and migration

- generate_expected.py: compute_merged_files に knowledge_fn 引数追加（RecursionError 修正）
- test_cache_separation.py: run.py main() 経由で全フローをテスト
- catalog.json: Phase A 再実行で 421 エントリの split 状態に復元
- .cache/v6/knowledge/: merged 331 → split ~417 に逆マージ変換
- migrate_to_split_cache.py: マイグレーションスクリプト追加
```

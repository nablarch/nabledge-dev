# タスク: マイグレーション修正 + テストの本番影響バグ修正

## 前提

ブランチ `120-generate-all-nabledge6-knowledge-files` の最新コミット `25bae73` に対する修正。

## 禁止事項

- タスクドキュメントに記載のないファイルを変更しない。
- スクリプトを独自に作成しない。このドキュメントに記載されたコマンドをそのまま実行する。
- 各 Step の検証の assert が全てパスしてから次の Step に進む。assert が失敗したら作業を止めて報告する。

## 変更対象ファイル

| ファイル | 変更内容 |
|---------|---------|
| `tools/knowledge-creator/tests/test_test_mode.py` | RealContext に classified_list_path を追加（本番 catalog 上書きバグ修正） |
| `tools/knowledge-creator/.cache/v6/catalog.json` | Phase A 再実行で 421 エントリに復元 |
| `tools/knowledge-creator/.cache/v6/knowledge/` 配下 | clear → split 状態で再生成 |

上記以外のファイルは変更しない。

---

## Step 1: test_test_mode.py の本番 catalog 上書きバグを修正

`tests/test_test_mode.py` の `real_ctx` fixture 内の `RealContext` クラスに `classified_list_path` プロパティを追加する。

### 変更内容

L29-33 を以下に変更する:

**変更前:**
```python
    class RealContext(Context):
        @property
        def log_dir(self):
            return str(log_base / f"v{self.version}")
```

**変更後:**
```python
    class RealContext(Context):
        @property
        def log_dir(self):
            return str(log_base / f"v{self.version}")

        @property
        def classified_list_path(self):
            return os.path.join(self.log_dir, 'catalog.json')
```

### Step 1 検証

```bash
cd tools/knowledge-creator

# catalog を復元
python -c "
import sys, os
sys.path.insert(0, 'scripts')
from run import Context
from step1_list_sources import Step1ListSources
from step2_classify import Step2Classify
repo = os.path.abspath('../..')
ctx = Context(version='6', repo=repo, concurrency=1, run_id='verify-fix')
os.makedirs(ctx.log_dir, exist_ok=True)
Step2Classify(ctx, sources_data=Step1ListSources(ctx).run()).run()
" 2>&1 | tail -1

# test_test_mode.py 実行後も catalog が 421 のままであること
python -c "import json; assert len(json.load(open('.cache/v6/catalog.json'))['files']) == 421; print('before: 421')"
python -m pytest tests/test_test_mode.py -q --tb=line
python -c "
import json
n = len(json.load(open('.cache/v6/catalog.json'))['files'])
assert n == 421, f'FAIL: catalog has {n} entries after test_test_mode.py (expected 421, test is overwriting production catalog)'
print(f'after: {n} — Step 1 OK')
"
```

---

## Step 2: catalog.json を 421 エントリに復元

```bash
cd tools/knowledge-creator
python -c "
import sys, os
sys.path.insert(0, 'scripts')
from run import Context
from step1_list_sources import Step1ListSources
from step2_classify import Step2Classify

repo = os.path.abspath('../..')
ctx = Context(version='6', repo=repo, concurrency=1, run_id='migrate-catalog')
os.makedirs(ctx.log_dir, exist_ok=True)
sources = Step1ListSources(ctx).run()
Step2Classify(ctx, sources_data=sources).run()
print('Done')
"
```

### Step 2 検証

```bash
python -c "
import json
from collections import Counter
d = json.load(open('.cache/v6/catalog.json'))
ids = [f['id'] for f in d['files']]
assert len(ids) == 421, f'FAIL: {len(ids)}'
assert len(ids) == len(set(ids)), f'FAIL: duplicates'
assert all('base_name' in f for f in d['files']), 'FAIL: missing base_name'
split_count = sum(1 for f in d['files'] if 'split_info' in f)
assert split_count == 296, f'FAIL: split={split_count}'
print(f'Step 2 OK: {len(ids)} entries ({split_count} split, {len(ids)-split_count} non-split)')
"
```

---

## Step 3: cache knowledge を clear して split 状態で再生成

以下のコマンドをそのまま実行する:

```bash
python -c "
import json, os, shutil

repo = os.path.abspath('../..')
cache_dir = '.cache/v6/knowledge'
merged_dir = os.path.join(repo, '.claude/skills/nabledge-6/knowledge')
catalog_path = '.cache/v6/catalog.json'
trace_dir = '.cache/v6/traces'

# cache を完全に削除して再作成
if os.path.exists(cache_dir):
    shutil.rmtree(cache_dir)
    print(f'Deleted: {cache_dir}')
os.makedirs(cache_dir, exist_ok=True)

with open(catalog_path, encoding='utf-8') as f:
    catalog = json.load(f)
entries = catalog['files']
print(f'Catalog: {len(entries)} entries')

# split group と non-split を分類
split_groups = {}
non_split = []
for e in entries:
    if 'split_info' in e and e['split_info'].get('is_split'):
        oid = e['split_info']['original_id']
        split_groups.setdefault(oid, []).append(e)
    else:
        non_split.append(e)

for parts in split_groups.values():
    parts.sort(key=lambda p: p['split_info']['part'])

split_oids = set(split_groups.keys())
print(f'Split groups: {len(split_groups)}, Non-split: {len(non_split)}')

def load_trace(oid):
    path = os.path.join(trace_dir, f'{oid}.json')
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    return None

def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

created = 0
skipped = []

# non-split ファイル処理
# split group の oid と同じ ID の non-split はスキップ
# （merged knowledge は split group のソースから生成されたもので、この non-split のソースとは異なる）
for e in non_split:
    if e['id'] in split_oids:
        skipped.append(e['id'])
        continue
    merged_path = os.path.join(merged_dir, e['output_path'])
    if not os.path.exists(merged_path):
        skipped.append(e['id'])
        continue
    with open(merged_path, encoding='utf-8') as f:
        knowledge = json.load(f)
    knowledge['id'] = e['id']
    write_json(os.path.join(cache_dir, e['output_path']), knowledge)
    created += 1

# split group 処理
for oid, parts in split_groups.items():
    type_ = parts[0]['type']
    category = parts[0]['category']
    merged_path = os.path.join(merged_dir, type_, category, f'{oid}.json')
    if not os.path.exists(merged_path):
        for p in parts:
            skipped.append(p['id'])
        continue

    with open(merged_path, encoding='utf-8') as f:
        merged = json.load(f)

    merged_index = merged.get('index', [])
    merged_sections = merged.get('sections', {})

    # trace から source_heading -> section_id のマッピングを取得
    trace = load_trace(oid)
    heading_to_sid = {}
    if trace and 'sections' in trace:
        for ts in trace['sections']:
            heading_to_sid[ts.get('source_heading', '')] = ts['section_id']

    # 各 part に section を振り分け
    part_assignments = {p['id']: [] for p in parts}
    assigned_sids = set()

    for part in parts:
        for heading in part.get('section_range', {}).get('sections', []):
            if heading in heading_to_sid:
                sid = heading_to_sid[heading]
                if sid not in assigned_sids:
                    part_assignments[part['id']].append(sid)
                    assigned_sids.add(sid)

    # 未割り当て section を part 1 に追加
    # merged_index と merged_sections の両方をカバー（index にないが sections にある section 対策）
    # merged_sections に存在するもののみ（trace にあるが knowledge にない section を除外）
    first_part_id = parts[0]['id']
    all_merged_sids = set(ie['id'] for ie in merged_index) | set(merged_sections.keys())
    for sid in all_merged_sids:
        if sid not in assigned_sids and sid in merged_sections:
            part_assignments[first_part_id].append(sid)
            assigned_sids.add(sid)

    # 各 part の knowledge JSON を生成
    for part in parts:
        pid = part['id']
        sids = part_assignments[pid]
        part_index = [ie for ie in merged_index if ie['id'] in sids]
        sid_order = [ie['id'] for ie in merged_index]
        part_index.sort(key=lambda ie: sid_order.index(ie['id']) if ie['id'] in sid_order else 999)
        part_sections = {}
        for sid in sids:
            if sid in merged_sections:
                part_sections[sid] = merged_sections[sid].replace(f'assets/{oid}/', f'assets/{pid}/')
        write_json(os.path.join(cache_dir, part['output_path']), {
            'id': pid, 'title': merged.get('title', ''),
            'no_knowledge_content': merged.get('no_knowledge_content', False),
            'official_doc_urls': merged.get('official_doc_urls', []),
            'index': part_index, 'sections': part_sections,
        })
        created += 1

print(f'')
print(f'Created: {created} files')
print(f'Skipped: {len(skipped)} files')
if skipped:
    print(f'Skipped IDs:')
    for s in skipped:
        print(f'  {s}')
"
```

### Step 3 検証

```bash
python -c "
import json, os

cache_count = sum(1 for r,d,f in os.walk('.cache/v6/knowledge') for x in f if x.endswith('.json'))
assert 400 <= cache_count <= 421, f'FAIL: cache files={cache_count}'
print(f'cache files: {cache_count}')

catalog = json.load(open('.cache/v6/catalog.json'))
catalog_ids = {f['id'] for f in catalog['files']}
cache_ids = set()
for root, dirs, files in os.walk('.cache/v6/knowledge'):
    for f in files:
        if f.endswith('.json'):
            cache_ids.add(f.replace('.json', ''))
extra = cache_ids - catalog_ids
assert len(extra) == 0, f'FAIL: extra files: {list(extra)[:5]}'
print(f'No extra files in cache: OK')

cache_sec = sum(len(json.load(open(os.path.join(r,f))).get('sections',{})) for r,_,fs in os.walk('.cache/v6/knowledge') for f in fs if f.endswith('.json'))
kb_sec = sum(len(json.load(open(os.path.join(r,f))).get('sections',{})) for r,_,fs in os.walk('../../.claude/skills/nabledge-6/knowledge') for f in fs if f.endswith('.json'))
deficit = kb_sec - cache_sec
assert 0 <= deficit <= 10, f'FAIL: deficit={deficit} (cache={cache_sec}, kb={kb_sec})'
print(f'sections: cache={cache_sec}, kb={kb_sec}, LOSER deficit={deficit}: OK')

missing = [e['id'] for e in catalog['files'] if not os.path.exists(os.path.join('.cache/v6/knowledge', e['output_path']))]
assert len(missing) <= 15, f'FAIL: too many missing: {len(missing)}'
print(f'Missing cache files: {len(missing)} (expected 11 = 7 LOSER + 4 overlap)')

print(f'Step 3 OK')
"
```

---

## Step 4: 最終検証

```bash
# 全テスト実行
python -m pytest tests/ -q --tb=line

# テスト後も catalog が 421 のままであること
python -c "
import json, os
d = json.load(open('.cache/v6/catalog.json'))
assert len(d['files']) == 421, f'FAIL: catalog={len(d[\"files\"])} after tests'
cache = sum(1 for r,_,fs in os.walk('.cache/v6/knowledge') for f in fs if f.endswith('.json'))
assert 400 <= cache <= 421
kb = sum(1 for r,_,fs in os.walk('../../.claude/skills/nabledge-6/knowledge') for f in fs if f.endswith('.json'))
assert kb == 331
print(f'catalog: {len(d[\"files\"])}, cache: {cache}, kb: {kb}')
print(f'All OK')
"
```

---

## Step 5: コミット・プッシュ

```bash
cd ../..
git add tools/knowledge-creator/tests/test_test_mode.py
git add tools/knowledge-creator/.cache/v6/catalog.json
git add tools/knowledge-creator/.cache/v6/knowledge/
git status
```

`git status` で以下を確認:
- `tests/test_test_mode.py` が modified
- `.cache/v6/catalog.json` が modified
- `.cache/v6/knowledge/` 配下に追加・削除あり
- 上記以外に変更がないこと

確認後:
```bash
git commit -m "fix: test_test_mode production catalog overwrite + migration

- test_test_mode.py: RealContext に classified_list_path 追加
  (テスト実行で本番 .cache/v6/catalog.json を上書きするバグを修正)
- catalog.json: Phase A 再実行で 421 エントリの split 状態に復元
- .cache/v6/knowledge/: merged+split 混在状態を clear し、
  split-only 410 ファイルとして再生成
  (11 files skipped: 7 dedup LOSER + 4 non-split/split-oid overlap)"

git push origin 120-generate-all-nabledge6-knowledge-files
```

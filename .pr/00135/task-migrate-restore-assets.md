# タスク: キャッシュの欠損assetsを復元するマイグレーション

## 目的

migration時に失われたキャッシュのassetファイル（画像等）をソースリポジトリからコピーで復元する。

## 背景

初回gen（20260307T162831）でPhase Bが正しくコピーしたassetsが、cache分離リファクタリング（`a5ec170`）のmigrationで知識JSONのみコピーされassetsディレクトリが失われた。Phase C S15で34ファイル・76参照が不合格。

動作確認済み: 305ファイルコピー後にS15 failures: 0を確認済み。

## 手順

### 1. マイグレーション実行

`tools/knowledge-creator/`で以下を実行する。

```python
import json, os, re, shutil

catalog = json.load(open('.cache/v6/catalog.json'))
repo = os.path.abspath('../..')
cache_dir = f'{repo}/tools/knowledge-creator/.cache/v6'

copied = 0
skipped = 0

for entry in catalog['files']:
    if entry['format'] != 'rst':
        continue
    source_path = f'{repo}/{entry["source_path"]}'
    if not os.path.exists(source_path):
        continue
    try:
        content = open(source_path, encoding='utf-8').read()
    except Exception:
        continue

    sr = entry.get('section_range')
    if sr:
        lines = content.splitlines()
        content = '\n'.join(lines[sr['start_line']:sr['end_line']])

    source_dir = os.path.dirname(source_path)
    assets_dir = f'{cache_dir}/knowledge/{entry["assets_dir"]}'

    refs = []
    for ref in re.findall(r'\.\.\s+(?:image|figure)::\s+(.+)', content):
        refs.append(ref.strip())
    for ref in re.findall(r':download:`[^<]*<([^>]+)>`', content):
        refs.append(ref.strip())

    for ref in refs:
        src = os.path.join(source_dir, ref)
        dst = os.path.join(assets_dir, os.path.basename(ref))
        if not os.path.exists(src) or os.path.exists(dst):
            if os.path.exists(dst):
                skipped += 1
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        copied += 1

print(f'Copied: {copied}')
print(f'Already exists: {skipped}')
```

期待される出力: `Copied: 305`, `Already exists: 27`

### 2. Phase C S15の検証

```python
import sys, os
sys.path.insert(0, 'scripts')
from run import Context
from phase_c_structure_check import PhaseCStructureCheck
ctx = Context(version='6', repo=os.path.abspath('../..'), concurrency=1, run_id='verify')
result = PhaseCStructureCheck(ctx).run()
s15 = {fid: errs for fid, errs in result.get('errors', {}).items() if any('S15' in e for e in errs)}
print(f'S15 failures: {len(s15)}')
```

期待される出力: `S15 failures: 0`

### 3. コミット

コピーされたassetsファイル群をコミットする。

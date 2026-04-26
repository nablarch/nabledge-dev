# タスク: V3/V7 verify_integrity FAIL修正

## 状況

`150-fix-phase-c-failures` ブランチの verify_integrity.py で2件のFAILが残っている。

| チェック | 問題 | 根本原因 |
|---|---|---|
| V3 | docs MDの1件のassetリンクが変換されていない | `_convert_asset_paths`の正規表現がalt text内の`[no]`で壊れる |
| V7 | index.toonとJSONのタイトル不一致1件 | `check_v7`のカンマ変換方向が逆 |

## 前提

- ブランチ: `150-fix-phase-c-failures`
- 作業ディレクトリ: `tools/knowledge-creator/`
- 現状: `python -m pytest tests/ut/ -q` → 154 passed, 7 skipped
- 現状: `python scripts/verify_integrity.py` → 15 OK, 2 WARN, 2 FAIL

## Task 1: V3修正 — _convert_asset_pathsの正規表現

### 根本原因

`scripts/phase_f_finalize.py` の `_convert_asset_paths` 内の正規表現:

```python
'image': re.compile(r'!\[([^\]]*)\]\(assets/' + re.escape(file_id) + r'/([^)]+)\)')
```

`[^\]]*` は `]` 以外の文字にマッチするが、alt textに `[no]` のようなネストされた角括弧があると、`[no]` の中の `]` で閉じてしまいマッチが失敗する。

実際に変換できていないケース（docs MD L312）:
```
![パラメータなしの場合（[no]列のみの例）](assets/testing-framework-...-02-RequestUnitTest/dummy_request_param.png)
```

### 修正

**ファイル**: `scripts/phase_f_finalize.py`

L348-351付近の正規表現を `[^\]]*` から `.*?` に変更:

変更前:
```python
        if file_id not in self._pattern_cache:
            self._pattern_cache[file_id] = {
                'image': re.compile(r'!\[([^\]]*)\]\(assets/' + re.escape(file_id) + r'/([^)]+)\)'),
                'link': re.compile(r'(?<!\!)\[([^\]]*)\]\(assets/' + re.escape(file_id) + r'/([^)]+)\)')
            }
```

変更後:
```python
        if file_id not in self._pattern_cache:
            # Use .*? for alt text to handle nested brackets like ![text with [no] inside](...)
            self._pattern_cache[file_id] = {
                'image': re.compile(r'!\[(.*?)\]\(assets/' + re.escape(file_id) + r'/([^)]+)\)'),
                'link': re.compile(r'(?<!\!)\[(.*?)\]\(assets/' + re.escape(file_id) + r'/([^)]+)\)')
            }
```

### 検証

```bash
cd tools/knowledge-creator

# 正規表現が [no] を含むalt textにマッチすることを確認
python3 -c "
import re
file_id = 'testing-framework-guide-development-guide-05-UnitTestGuide-02-RequestUnitTest'
pattern = re.compile(r'!\[(.*?)\]\(assets/' + re.escape(file_id) + r'/([^)]+)\)')
test = '![パラメータなしの場合（[no]列のみの例）](assets/' + file_id + '/dummy_request_param.png)'
m = pattern.search(test)
assert m is not None, 'Pattern did not match'
assert m.group(2) == 'dummy_request_param.png', f'Got: {m.group(2)}'
print('OK')
"
```

---

## Task 2: V7修正 — verify_integrity.pyのカンマ変換方向

### 根本原因

`scripts/verify_integrity.py` の `check_v7_index_toon` (L100付近):

```python
expected_title = parts[0].replace("、", ",")
actual_title = data.get("title", "")
```

`_build_index_toon` はタイトル書き出し時に `title.replace(",", "、")` でASCIIカンマをJapaneseカンマに変換する。verify側で読み戻す時に `replace("、", ",")` と逆方向に変換しているため、元々Japaneseカンマ `、` を含むタイトルがASCIIカンマ `,` に変わってしまい不一致になる。

実際のケース:
- JSON title: `処理方式、環境に依存する設定の管理方法` （Japaneseカンマ）
- toon title: `処理方式、環境に依存する設定の管理方法` （同じ）
- verify変換後: `処理方式,環境に依存する設定の管理方法` （ASCIIカンマに誤変換）→ 不一致

### 修正

**ファイル**: `scripts/verify_integrity.py`

L99-103付近を変更:

変更前:
```python
        data = load_json(json_path)
        expected_title = parts[0].replace("、", ",")
        actual_title = data.get("title", "")
        if expected_title != actual_title:
            fails.append(f"  title mismatch for {path}: '{expected_title}' != '{actual_title}'")
```

変更後:
```python
        data = load_json(json_path)
        # _build_index_toon writes: title.replace(",", "、")
        # So to compare, apply the same normalization to JSON title
        toon_title = parts[0]
        actual_title = data.get("title", "").replace(",", "、")
        if toon_title != actual_title:
            fails.append(f"  title mismatch for {path}: '{toon_title}' != '{actual_title}'")
```

### 検証

```bash
cd tools/knowledge-creator

# カンマ変換が正しいことを確認
python3 -c "
toon_title = '処理方式、環境に依存する設定の管理方法'
json_title = '処理方式、環境に依存する設定の管理方法'
actual = json_title.replace(',', '、')
assert toon_title == actual, f'{toon_title} != {actual}'
print('OK')
"
```

---

## Task 3: Phase M再実行

V3修正でdocs MDのassetパス変換が変わるため、出力を再生成する。

```bash
cd tools/knowledge-creator
python3 -c "
import sys, os
sys.path.insert(0, 'scripts')
from run import Context
from phase_m_finalize import PhaseMFinalize
ctx = Context(version='6', repo=os.path.abspath('../..'), concurrency=1, run_id='v3v7fix')
PhaseMFinalize(ctx).run()
"
```

### 検証

```bash
cd tools/knowledge-creator

# V3が修正されたことを確認: 問題のassetパスが変換されている
python3 -c "
md = open('../../.claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-guide-development-guide-05-UnitTestGuide-02-RequestUnitTest.md').read()
assert 'assets/testing-framework-guide' not in md.split('knowledge/')[-1] if 'knowledge/' in md else True
# L312付近に ../../../knowledge/ プレフィックスがあることを確認
import re
refs = re.findall(r'!\[.*?\]\((assets/[^)]+)\)', md)
assert len(refs) == 0, f'{len(refs)} unconverted asset refs remain: {refs[:3]}'
print('OK: all asset refs converted')
"
```

---

## Task 4: 最終検証

```bash
cd tools/knowledge-creator

echo "=== UT ===" && python -m pytest tests/ut/ -q

echo "=== Integrity ===" && python scripts/verify_integrity.py

echo "=== Counts ===" && python3 -c "
import glob, json
s = len([p for p in glob.glob('../../.claude/skills/nabledge-6/knowledge/**/*.json', recursive=True) if '/assets/' not in p])
d = len(glob.glob('../../.claude/skills/nabledge-6/docs/**/*.md', recursive=True))
n = sum(1 for l in open('../../.claude/skills/nabledge-6/knowledge/index.toon').read().splitlines() if 'not yet created' in l)
print(f'Skill:{s} Docs:{d} NotYet:{n}')
assert s >= 300 and d >= 250 and n == 0
print('ALL OK')
"
```

### 期待結果

- UT: 154+ passed, 0 failed
- verify_integrity.py: **0 FAIL**, 15 OK, 2 WARN
  - V10/V11 WARN: ソースRSTに存在しない架空ラベルへのAI生成参照（186件）。Phase Bの生成品質問題であり別Issueで対応。
- Skill JSON: >=300, Docs MD: >=250, not_yet_created: 0

### コミット

```
fix: V3 nested bracket regex in _convert_asset_paths, V7 comma comparison in verify_integrity

V3: _convert_asset_paths regex [^\]]* could not handle alt text
containing nested brackets like [no]. Changed to .*? pattern.

V7: check_v7_index_toon was converting 、→, (wrong direction).
Changed to normalize JSON title with ,→、 (same as _build_index_toon).

Part of #150
```

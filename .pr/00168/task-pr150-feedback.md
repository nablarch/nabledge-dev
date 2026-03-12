# タスク: PR #150 レビューフィードバック対応

## 対応一覧

| # | 問題 | 深刻度 | 対応 |
|---|---|---|---|
| 1 | conftest.pyにPhase Gの古いコメント | 軽微 | コメント修正 |
| 2 | `_make_cross_file_link`のos.path.relpathがWindowsで`\`を返す | 中 | `.replace('\\', '/')` 追加 |
| 3 | doc_mapの部分パスマッチで3件の誤リンク＋1件未解決 | 高 | 参照元source_pathからの相対パス解決に変更 |
| 4 | PRのClosesリストに#151が含まれるが未対応 | 中 | コミットメッセージから#151を外す |

### #3の詳細

doc_mapが「部分パスのsetdefault先着優先」でマッチするため、同名ファイルが複数ディレクトリにある場合に誤ったファイルにリンクされる。

**誤リンク3件:**

| 参照元 | `:doc:`パス | 現在（誤） | 正解 |
|---|---|---|---|
| `web-application-architecture--s1` | `application_design` | `nablarch-batch-application_design` | `web-application-application_design` |
| `testing-framework-real` | `./batch` | `testing-framework-batch-02_RequestUnitTest` | `testing-framework-batch-03_DealUnitTest` |
| `testing-framework-RequestUnitTest_batch--s1` | `../05_UnitTestGuide/02_RequestUnitTest/batch` | `testing-framework-batch-02_RequestUnitTest` | `testing-framework-batch` |

**未解決1件:**

`libraries-permission_check--s1`の`:doc:`role_check``。同一effective_id（`libraries-permission_check`）にnon-split版（`libraries/`ディレクトリ）とsplit版（`libraries/authorization/`ディレクトリ）の2つのsource_dirがあり、`setdefault`でnon-split版が先に登録されるため、split版のディレクトリから`:doc:`role_check``を解決できない。

**解決策:** `file_source_dir`をeffective_id→単一dirではなく、effective_id→dir listに変更し、resolve_doc内で全候補を試す。70/70件全て解決されることを確認済み。

multi-dirケースは以下の4 effective_idのみ:

| effective_id | dirs |
|---|---|
| `libraries-permission_check` | `libraries/`, `libraries/authorization/` |
| `testing-framework-delayed_receive` | `02_RequestUnitTest/`, `03_DealUnitTest/` |
| `testing-framework-delayed_send` | `02_RequestUnitTest/`, `03_DealUnitTest/` |
| `testing-framework-real` | `02_RequestUnitTest/`, `03_DealUnitTest/` |

## 前提

- ブランチ: `150-fix-phase-c-failures`
- 作業ディレクトリ: `tools/knowledge-creator/`
- 現状テスト: 154 passed, 7 skipped
- **実行順**: Task 1 → 2 → 3 → 4 → 5 → 6（順序厳守）

---

## Task 1: conftest.pyのstaleコメント修正

**ファイル**: `tests/ut/conftest.py` L98

変更前:
```python
    # classified.json (required by Phase G for doc index building)
```

変更後:
```python
    # classified.json (required by Phase F for doc/index generation)
```

---

## Task 2: os.path.relpathのWindows安全対策

**ファイル**: `scripts/phase_f_finalize.py`

`_make_cross_file_link` メソッド内のL227とL235の2箇所を変更。

L227 変更前:
```python
            rel = os.path.relpath(to_path, from_dir)
            return f"{rel}{anchor}"
        else:
```

L227 変更後:
```python
            rel = os.path.relpath(to_path, from_dir).replace('\\', '/')
            return f"{rel}{anchor}"
        else:
```

L235 変更前:
```python
            rel = os.path.relpath(to_path, from_dir)
            return f"{rel}{anchor}"
```

L235 変更後:
```python
            rel = os.path.relpath(to_path, from_dir).replace('\\', '/')
            return f"{rel}{anchor}"
```

---

## Task 3: doc_mapを参照元相対パス解決に変更

### Step 3-1: `__init__`に`file_source_dirs`を追加

**ファイル**: `scripts/phase_f_finalize.py`

`__init__`メソッド内、`self.file_type_category = {}`の後に追加:

```python
        self.file_source_dirs = {}  # effective_id -> [source_dir, ...] (for :doc: resolution)
```

### Step 3-2: `_build_link_maps`のdoc_map構築を変更

L63-74付近を変更。

変更前:
```python
            # Build doc_map from source_path (only once per effective_id)
            source_path = fi.get("source_path", "")
            if source_path and not effective_id_data[effective_id]["source_path"].strip():
                effective_id_data[effective_id]["source_path"] = source_path

            rst_path = re.sub(r'\.(rst|md|xlsx?)$', '', source_path) if source_path else ""
            if rst_path:
                self.doc_map.setdefault(rst_path, effective_id)
                parts = rst_path.split("/")
                for i in range(1, len(parts)):
                    partial = "/".join(parts[i:])
                    self.doc_map.setdefault(partial, effective_id)
```

変更後:
```python
            # Build doc_map: full source_path (without extension) -> effective_id
            source_path = fi.get("source_path", "")
            if source_path and not effective_id_data[effective_id]["source_path"].strip():
                effective_id_data[effective_id]["source_path"] = source_path

            rst_path = re.sub(r'\.(rst|md|xlsx?)$', '', source_path) if source_path else ""
            if rst_path:
                self.doc_map[rst_path] = effective_id
                # Store all source directories for this effective_id
                # (some files have multiple source dirs due to split across directories)
                source_dir = os.path.dirname(source_path)
                if effective_id not in self.file_source_dirs:
                    self.file_source_dirs[effective_id] = [source_dir]
                elif source_dir not in self.file_source_dirs[effective_id]:
                    self.file_source_dirs[effective_id].append(source_dir)
```

### Step 3-3: `resolve_doc`クロージャを変更

`_resolve_rst_links`内の`resolve_doc`（L158-179付近）を全置換。

変更前:
```python
        def resolve_doc(m):
            full = m.group(0)
            with_text = re.match(r':doc:`([^<>`]+?)\s*<([^>`]+)>`', full)
            plain = re.match(r':doc:`([^`>]+)`', full)
            if with_text:
                display_text = with_text.group(1).strip()
                doc_path = with_text.group(2).strip()
            elif plain:
                doc_path = plain.group(1).strip()
                display_text = None
            else:
                return full

            # Normalize: strip leading ./ and ../
            norm = re.sub(r'^(\.\.?/)+', '', doc_path)
            target_file_id = self.doc_map.get(doc_path) or self.doc_map.get(norm)
            if not target_file_id:
                return full  # unresolved

            text = display_text if display_text else doc_path
            link = self._make_cross_file_link(current_file_id, target_file_id, None, output_type)
            return f"[{text}]({link})"
```

変更後:
```python
        def resolve_doc(m):
            full = m.group(0)
            with_text = re.match(r':doc:`([^<>`]+?)\s*<([^>`]+)>`', full)
            plain = re.match(r':doc:`([^`>]+)`', full)
            if with_text:
                display_text = with_text.group(1).strip()
                doc_path = with_text.group(2).strip()
            elif plain:
                doc_path = plain.group(1).strip()
                display_text = None
            else:
                return full

            # Resolve relative to the source file's directory
            target_file_id = None
            for source_dir in self.file_source_dirs.get(current_file_id, []):
                target_full = os.path.normpath(
                    os.path.join(source_dir, doc_path)
                )
                target_file_id = self.doc_map.get(target_full)
                if target_file_id:
                    break

            if not target_file_id:
                return full  # unresolved

            text = display_text if display_text else doc_path
            link = self._make_cross_file_link(current_file_id, target_file_id, None, output_type)
            return f"[{text}]({link})"
```

### Step 3-4: テスト更新

**ファイル**: `tests/ut/test_phase_f_links.py`

`_make_pf`メソッド内にあるdoc_mapとfile_source_dirsのテストデータを更新する必要がある。

現在の`_make_pf` (L167-183付近):
```python
    def _make_pf(self, ctx):
        from phase_f_finalize import PhaseFFinalize
        pf = PhaseFFinalize(ctx, dry_run=True)
        pf.label_map = {
            "internal_label": ("current-file", "s1"),
            "external_label": ("other-file", "s2"),
            "external_no_section": ("other-file", None),
            "external_label-hyphen": ("other-file", "s2"),
        }
        pf.doc_map = {
            "path/to/other": "other-file",
        }
        pf.file_type_category = {
            "current-file": ("component", "handlers"),
            "other-file": ("component", "adapters"),
        }
        return pf
```

変更後:
```python
    def _make_pf(self, ctx):
        from phase_f_finalize import PhaseFFinalize
        pf = PhaseFFinalize(ctx, dry_run=True)
        pf.label_map = {
            "internal_label": ("current-file", "s1"),
            "external_label": ("other-file", "s2"),
            "external_no_section": ("other-file", None),
            "external_label-hyphen": ("other-file", "s2"),
        }
        pf.doc_map = {
            "src/component/handlers/path/to/other": "other-file",
        }
        pf.file_type_category = {
            "current-file": ("component", "handlers"),
            "other-file": ("component", "adapters"),
        }
        pf.file_source_dirs = {
            "current-file": ["src/component/handlers"],
            "other-file": ["src/component/adapters"],
        }
        return pf
```

doc_mapのキーをフルパスに変更し、file_source_dirsを追加。`resolve_doc`は`file_source_dirs["current-file"]`→`["src/component/handlers"]`を使い、`os.path.normpath("src/component/handlers/path/to/other")`→`"src/component/handlers/path/to/other"`でdoc_mapからマッチする。

### 検証

```bash
cd tools/knowledge-creator

# 1. UTが通ること
python -m pytest tests/ut/ -q --tb=short

# 2. 70件全件解決の確認
python3 -c "
import sys, os, json, re, glob
sys.path.insert(0, 'scripts')
from phase_f_finalize import PhaseFFinalize
from run import Context
from common import load_json

ctx = Context(version='6', repo=os.path.abspath('../..'), concurrency=1, run_id='test')
split_catalog = load_json(ctx.classified_list_path)
pf = PhaseFFinalize(ctx, dry_run=True, catalog_for_links=split_catalog)
pf._build_link_maps()

# 全 :doc: 参照をresolve_docで解決
cache_dir = '.cache/v6/knowledge'
ok = 0; ng = 0
catalog = load_json(ctx.classified_list_path)
for p in glob.glob(f'{cache_dir}/**/*.json', recursive=True):
    if '/assets/' in p: continue
    data = load_json(p)
    fid = data.get('id','')
    eid = fid
    for fi in catalog['files']:
        if fi['id'] == fid:
            si = fi.get('split_info',{})
            eid = si.get('original_id', fid)
            break
    for sid, content in data.get('sections',{}).items():
        for m in re.finditer(r':doc:\x60[^\x60]+\x60', content):
            original = m.group(0)
            resolved = pf._resolve_rst_links(original, eid, 'skill_json')
            if ':doc:' in resolved:
                ng += 1
                print(f'  UNRESOLVED: {fid} {original}')
            else:
                ok += 1
print(f':doc: refs: {ok} resolved, {ng} unresolved')
assert ng == 0, f'{ng} unresolved'
print('OK')
"
```

---

## Task 4: Phase M再実行

```bash
cd tools/knowledge-creator
python3 -c "
import sys, os
sys.path.insert(0, 'scripts')
from run import Context
from phase_m_finalize import PhaseMFinalize
ctx = Context(version='6', repo=os.path.abspath('../..'), concurrency=1, run_id='docfix')
PhaseMFinalize(ctx).run()
"
```

### 検証

```bash
cd tools/knowledge-creator

# 1. 誤リンク3件が修正されたことを確認
python3 -c "
import json, os, re
skill_dir = '../../.claude/skills/nabledge-6/knowledge'
p = f'{skill_dir}/processing-pattern/web-application/web-application-architecture.json'
data = json.load(open(p))
for sid, content in data.get('sections', {}).items():
    for m in re.finditer(r'\[([^\]]*)\]\(([^)]+application_design[^)]*\.json)', content):
        link = m.group(2)
        assert 'web-application' in link, f'Wrong: {link}'
        print(f'application_design: {link} OK')
        break
"

# 2. V6 cross-file全件チェック
python3 -c "
import glob, json, os, re
skill_dir = '../../.claude/skills/nabledge-6/knowledge'
broken = 0; total = 0
for p in glob.glob(f'{skill_dir}/**/*.json', recursive=True):
    if '/assets/' in p: continue
    data = json.load(open(p))
    json_dir = os.path.dirname(p)
    for sid, content in data.get('sections', {}).items():
        for m in re.finditer(r'\[([^\]]*)\]\(([^)]+\.json)(?:#([^)]*))?\)', content):
            tf = m.group(2)
            if tf.startswith('http'): continue
            total += 1
            if not os.path.exists(os.path.normpath(os.path.join(json_dir, tf))):
                broken += 1
                print(f'  BROKEN: {data.get(\"id\",\"\")} -> {tf}')
print(f'V6: {total} total, {broken} broken')
assert broken == 0
print('OK')
"

# 3. ファイル数・integrity
python scripts/verify_integrity.py
python3 -c "
import glob
s = len([p for p in glob.glob('../../.claude/skills/nabledge-6/knowledge/**/*.json', recursive=True) if '/assets/' not in p])
d = len(glob.glob('../../.claude/skills/nabledge-6/docs/**/*.md', recursive=True))
n = sum(1 for l in open('../../.claude/skills/nabledge-6/knowledge/index.toon').read().splitlines() if 'not yet created' in l)
print(f'Skill:{s} Docs:{d} NotYet:{n}')
assert s >= 300 and d >= 250 and n == 0
print('OK')
"
```

---

## Task 5: #151をコミットメッセージから外す

コミット `acf408e` のメッセージ末尾 `Part of #150, #149, #151` から `, #151` を削除する。

```bash
GIT_SEQUENCE_EDITOR="sed -i 's/^pick acf408e/reword acf408e/'" git rebase -i acf408e^
```

rebaseのエディタが開いたら、メッセージの `Part of #150, #149, #151` を `Part of #150, #149` に変更して保存。

コンフリクトが発生した場合は `git rebase --abort` して、この Task は一旦スキップする（手動対応を依頼する）。

```bash
git push --force-with-lease origin 150-fix-phase-c-failures
```

---

## Task 6: 最終検証

```bash
cd tools/knowledge-creator
echo "=== UT ===" && python -m pytest tests/ut/ -q
echo "=== Integrity ===" && python scripts/verify_integrity.py
echo "=== Counts ===" && python3 -c "
import glob
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
- verify_integrity.py: 0 FAIL, 15 OK, 2 WARN（V10/V11は架空ラベル）
- Skill JSON: >=300, Docs MD: >=250, not_yet_created: 0

### コミット

```
fix: resolve :doc: links relative to source file path, Windows-safe relpath

- Replace doc_map partial-path matching with source-relative full-path resolution
  Fixes 3 wrong :doc: links + 1 unresolved (multi-dir effective_id)
- file_source_dirs stores all source directories per effective_id
- Add .replace('\\', '/') to os.path.relpath in _make_cross_file_link
- Fix stale Phase G comment in conftest.py

Part of #150
```

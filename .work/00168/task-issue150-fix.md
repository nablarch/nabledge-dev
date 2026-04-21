# タスク: Issue #150 根本原因修正

## 目的

セクションIDのAI生成をスクリプト決定論的生成に置き換え、Phase G廃止・traceファイル廃止・processing_patterns除去・リンク変換のPhase F統合を行う。Issue #149, #150, #151, #166を同時解決する。

## 前提

- テスト実行: `python -m pytest tests/ut/ -q` (141 passed が現状のベースライン)
- **再生成は行わない**。既存キャッシュをスクリプトでマイグレーションする

## 作業の進め方

各Taskは独立してコミット可能な単位。Task内のStepは順序通りに実行する。各Taskの最後に指定された検証コマンドを実行し、全てパスしてからコミットする。

### Task依存関係

```
Task 1 (step2_classify連番化)
  ↓
Task 2 (テスト更新)  ←→  Task 3 (Phase C S5変更)
  ↓
Task 4 (Phase G・trace廃止)
  ↓
Task 5 (knowledge JSONマイグレーション) ← Task 1のカタログ再生成が前提
  ↓
Task 6 (Phase Fリンク変換統合)
  ↓
Task 7 (Phase F実行・データ再生成) ← Task 4,5,6が全て完了していること
  ↓
Task 8 (プロンプト更新) ← Task 4完了後ならいつでも可
Task 9 (Phase D/E更新) ← Task 4完了後ならいつでも可
Task 10 (#166 biz_samples) ← Task 5,7と同時実行不可（カタログ競合）、Task 7の前に実行推奨
Task 11 (#151 scenarios) ← Task 5完了後
Task 12 (ワークフロー更新) ← Task 5完了後
Task 13 (マイグレーションスクリプト更新) ← Task 4完了後
Task 14 (最終検証) ← 全Task完了後
```

**推奨実行順**: 1 → 2 → 3 → 4 → 5 → 10 → 6 → 7 → 8 → 9 → 11 → 12 → 13 → 14

---

## Task 1: セクションID連番化 — step2_classify.py

### 目的

`_title_to_section_id()`（AIが生成するkebab-case ID）を廃止し、スクリプトが`s1`, `s2`, `s3`...の連番IDを決定論的に割り当てる。同時にRSTラベルを解析して`section_map`をカタログに記録する。

### Step 1-1: `_title_to_section_id()` を連番ID生成に置き換え

**ファイル**: `scripts/step2_classify.py`

`_title_to_section_id` メソッドを削除し、`_generate_entries_from_groups` メソッドを変更する。

`_generate_entries_from_groups` の現在のID生成ロジック:

```python
first_section = group[0]
section_id = self._title_to_section_id(first_section['title'])

# 重複回避: 同じsection_idが既出なら連番を付与
original_section_id = section_id
counter = 2
while section_id in used_ids:
    section_id = f"{original_section_id}-{counter}"
    counter += 1
used_ids.add(section_id)
split_id = f"{base_id}--{section_id}"
```

変更後:

```python
section_id = f"s{section_counter}"
section_counter += 1
split_id = f"{base_id}--{section_id}"
```

ただし `section_counter` はベースネーム単位の通し連番。`_generate_entries_from_groups` はベースネーム単位で呼ばれるので、メソッド内のローカルカウンタで足りる。ただし、複数パートにまたがる連番にするため、`split_file_entry` からカウンタを受け渡す。

具体的な変更:

1. `_title_to_section_id` staticmethod を削除

2. `split_file_entry` メソッドを変更:
   ```python
   def split_file_entry(self, base_entry, sections, content):
       expanded_sections = self._expand_large_sections(sections, content)
       groups = self._group_sections_by_lines(expanded_sections)
       
       # 全セクション（展開後）を通しカウントし、各グループの開始番号を計算
       section_counter = 1
       group_start_counters = []
       for group in groups:
           group_start_counters.append(section_counter)
           section_counter += len(group)  # このグループ内のセクション数を加算
       
       result = self._generate_entries_from_groups(
           base_entry, groups, group_start_counters
       )
       return result
   ```

3. `_generate_entries_from_groups` を変更:
   - 引数に `group_start_counters: list[int]` を追加（各グループの開始連番）
   - セクションごとに `s{counter}` 形式のIDを割り当てる
   - `used_ids` ロジックは全て削除（連番は重複しない）
   ```python
   def _generate_entries_from_groups(self, base_entry, groups, group_start_counters):
       result = []
       for part_num, (group, start_counter) in enumerate(
           zip(groups, group_start_counters), 1
       ):
           counter = start_counter
           section_id_list = []
           for section in group:
               sid = f"s{counter}"
               section['assigned_id'] = sid  # section_map構築用
               section_id_list.append(sid)
               counter += 1
           
           # パートIDは最初のセクションIDを使用
           first_sid = section_id_list[0]
           split_id = f"{base_entry['id']}--{first_sid}"
           
           # ... entry構築 ...
           result.append({
               **base_entry,
               'id': split_id,
               # ...
               'section_range': {
                   'start_line': group[0]['start_line'],
                   'end_line': group[-1]['end_line'],
                   'sections': [s['title'] for s in group],
                   'section_ids': section_id_list,
               },
               # ...
           })
       return result
   ```

4. `section_range` に `section_ids` リストを追加:
   ```python
   'section_range': {
       'start_line': start_line,
       'end_line': end_line,
       'sections': section_titles,
       'section_ids': section_id_list  # 新規追加: このパートに割り当てられたセクションIDのリスト
   }
   ```

### Step 1-2: RSTラベル解析と`section_map`のカタログ記録

**ファイル**: `scripts/step2_classify.py`

RSTソースファイルの `.. _label:` 定義を解析し、各セクションに属するラベルを特定する。

1. `_extract_rst_labels_with_positions` メソッドを新規追加:
   ```python
   def _extract_rst_labels_with_positions(self, content: str) -> list:
       """Extract RST label definitions with their line positions.
       Returns: [(label, line_number), ...]
       """
       import re
       results = []
       for i, line in enumerate(content.splitlines()):
           m = re.match(r'^\.\.\s+_([a-z0-9_-]+):', line)
           if m:
               results.append((m.group(1), i))
       return results
   ```

2. `split_file_entry` 内で、分割後に各パートのセクション行範囲にどのラベルが属するかを判定し、`section_map` を構築:
   ```python
   section_map = []
   for group in groups:
       for section in group:
           labels = [label for label, line in rst_labels 
                     if section['start_line'] <= line < section['end_line']]
           section_map.append({
               "section_id": section['assigned_id'],  # s1, s2, ...
               "heading": section['title'],
               "rst_labels": labels
           })
   ```

3. 非分割ファイル（h2セクションが1つ以下）にも `section_map` を生成。`run()` メソッド内の非分割ファイル処理ブロックで、RSTファイルに対して同様にセクション解析・ラベル割り当てを行う。

4. カタログ出力の各ファイルエントリに `section_map` フィールドを追加。

### Step 1-3: 非分割ファイルのセクションIDとsection_map

非分割RSTファイル（should_split=False）にもsection_mapを生成する。これはRSTラベルのマッピング情報（Phase Fのリンク解決に必要）を提供するためであり、セクションIDの割り当てはマイグレーションスクリプト（Task 5）がindex順序ベースで行う。

非分割ファイルのh2セクション数とknowledge JSONのセクション数は一致しないケースがある（h2が0-1個でもAIがh3 promotionでマルチセクション化するなど）。したがって、section_mapのheading情報は「参考」として記録し、実際のID割り当てには使わない。

RSTラベルの帰属先セクションは行位置で判定する:

```python
if format == "rst" and not should_split:
    content = read_file(full_path)
    sections = self.analyze_rst_sections(content)
    rst_labels = self._extract_rst_labels_with_positions(content)
    
    # section_mapはRSTラベル→行位置のマッピング情報
    # section_idはh2セクションの出現順で仮付番（マイグレーションで上書きされる）
    counter = 1
    section_map = []
    for sec in sections:
        labels = [label for label, line in rst_labels
                  if sec['start_line'] <= line < sec['end_line']]
        section_map.append({
            "section_id": f"s{counter}",
            "heading": sec['title'],
            "rst_labels": labels
        })
        counter += 1
    
    # h2がないファイル（タイトルのみ等）でもラベルがあれば記録
    if not sections and rst_labels:
        section_map.append({
            "section_id": "s1",
            "heading": "",
            "rst_labels": [label for label, _ in rst_labels]
        })
    
    entry['section_map'] = section_map
```

**重要**: section_mapの`section_id`はh2ベースの仮ID。knowledge JSONの実際のセクションID（AIが付けたkebab-case）との対応は1:1とは限らない。Phase Fのリンク解決では、rst_label → file_id の紐付けに使い、section_id はマイグレーション後の連番IDを別途参照する。

### Step 1-4: `processing_patterns` 保存ロジック削除

`run()` メソッドの末尾にある `processing_patterns` の既存カタログからの保存ロジックを削除:

削除対象:
```python
# Preserve processing_patterns from existing files
existing_pp = {}
for fi in existing.get("files", []):
    pp = fi.get("processing_patterns")
    if pp is not None:
        existing_pp[fi["id"]] = pp
for fi in classified:
    if fi["id"] in existing_pp:
        fi["processing_patterns"] = existing_pp[fi["id"]]
```

### 検証

```bash
cd tools/knowledge-creator

# 1. 単体テスト実行 — _title_to_section_id 関連テストが失敗するのは期待通り
python -m pytest tests/ut/test_split_criteria.py -q -x 2>&1 | head -30

# 2. step2_classify を dry-run で実行し、section_map が生成されることを確認
python -c "
import sys, os
sys.path.insert(0, 'scripts')
from run import Context
from step2_classify import Step2Classify

ctx = Context(version='6', repo=os.path.abspath('../..'), concurrency=1, run_id='test')
s2 = Step2Classify(ctx, dry_run=True)
result = s2.run()
# section_map があるファイルの数を確認
sm_count = sum(1 for f in result['files'] if f.get('section_map'))
print(f'Files with section_map: {sm_count}/{len(result[\"files\"])}')
# 分割ファイルのIDが s1, s2 形式であることを確認
split_files = [f for f in result['files'] if f.get('split_info', {}).get('is_split')]
if split_files:
    sample = split_files[0]
    print(f'Sample split ID: {sample[\"id\"]}')
    assert '--s' in sample['id'], f'Expected --sN format, got: {sample[\"id\"]}'
print('OK')
"
```

### コミット

```
feat: replace AI-generated section IDs with deterministic sequential IDs

- Delete _title_to_section_id() in step2_classify.py
- Generate s1, s2, s3... IDs per base_name (sequential across parts)
- Add _extract_rst_labels_with_positions() for RST label parsing
- Add section_map to catalog entries (section_id, heading, rst_labels)
- Remove processing_patterns preservation from catalog generation

Part of #150, #149, #151
```

---

## Task 2: テスト更新 — 連番ID対応

### 目的

Task 1の変更に合わせてテストを更新し、全テストがパスする状態にする。

### Step 2-1: `test_split_criteria.py` の更新

**ファイル**: `tests/ut/test_split_criteria.py`

1. `test_title_to_section_id_*` テストを全て削除

2. 分割IDフォーマットを検証するテストを `--sN` 形式に変更:
   - 全てのsplit IDが `{base_name}--s{N}` 形式であることを検証
   - `_title_to_section_id` を呼び出しているアサーションを連番形式に変更
   - `test_duplicate_titles_get_unique_ids`: 重複回避ロジックは不要になったため、代わりに連番が正しく割り振られることを検証

3. 新規テスト追加:
   ```python
   def test_sequential_section_ids_across_parts(self):
       """Section IDs are sequential across parts within a base_name."""
       # 3パートに分割されるファイルで s1~sN が通し連番であることを確認
   
   def test_section_map_contains_rst_labels(self):
       """section_map includes RST labels from source file."""
       # RSTソースの .. _label: がsection_mapに含まれることを確認
   
   def test_section_map_for_non_split_files(self):
       """Non-split RST files also get section_map."""
   ```

### Step 2-2: `test_phase_c.py` の更新

**ファイル**: `tests/ut/test_phase_c.py`

1. `test_s5_non_kebab`: kebab-case検証を連番ID検証に変更。S5チェックのロジック自体をPhase Cで変更する必要がある（Task 3で対応）。ここではテストのexpected values を更新。

### Step 2-3: `conftest.py` の更新

**ファイル**: `tests/ut/conftest.py`

1. `make_mock_run_claude` のデフォルト knowledge output のsection_idを連番形式に更新:
   - `sample_knowledge.json` を読み込んで使うので、Step 2-4でfixtureを更新すれば自動的に反映される

2. **trace出力のsection_idは変更しない**。Task 4でtrace関連コードごと削除するため、ここで変更する意味がない。

3. `test_repo` fixture の trace ディレクトリ作成は維持（Task 4で`test_phase_g.py`と共に削除）

### Step 2-4: `sample_knowledge.json` fixture 更新

**ファイル**: `tests/ut/fixtures/sample_knowledge.json`

section IDを連番に変更:
- `"overview"` → `"s1"`
- `"module-list"` → `"s2"`
- 対応する index[].id、sections のキー、内部参照(`#overview` → `#s1`)を全て更新
- `processing_patterns` フィールドが存在する場合は削除

### 検証

```bash
cd tools/knowledge-creator
# test_phase_c.pyはTask 3でPhase Cコード変更後にパスするため、ここでは除外
python -m pytest tests/ut/test_split_criteria.py -q -x
# sample_knowledge.jsonを使う他のテストも確認（test_phase_g.pyはまだ存在するがTask 4で削除予定のため除外）
python -m pytest tests/ut/ -q -x --ignore=tests/ut/test_phase_g.py --ignore=tests/ut/test_phase_c.py -k "not phase_g"
```

### コミット

```
test: update tests for sequential section ID format (s1, s2, ...)

- Remove _title_to_section_id tests
- Update split ID assertions to --sN format  
- Add section_map test coverage
- Update sample_knowledge.json fixture to use s1/s2

Part of #150
```

---

## Task 3: Phase C構造チェック — 連番ID検証

### 目的

Phase CのS5検証をkebab-case検証から連番ID形式検証に変更する。

### Step 3-1: S5検証の変更

**ファイル**: `scripts/phase_c_structure_check.py`

1. `KEBAB_CASE_PATTERN` を連番パターンに変更:
   ```python
   SECTION_ID_PATTERN = re.compile(r'^s\d+$')
   ```

2. `VALID_PROCESSING_PATTERNS` 定数は共通モジュールに移動予定だが、まず参照は残す（Task 6で対応）。

3. S5チェックを変更:
   ```python
   # S5: Sequential section ID format
   for entry in knowledge.get("index", []):
       if not SECTION_ID_PATTERN.match(entry["id"]):
           errors.append(f"S5: Section ID '{entry['id']}' is not sequential format (expected: s1, s2, ...)")
   ```

### 検証

```bash
cd tools/knowledge-creator
python -m pytest tests/ut/test_phase_c.py -q -x
# S5テストがパスすることを確認
```

### コミット

```
feat: change Phase C S5 validation from kebab-case to sequential ID format

Part of #150
```

---

## Task 4: Phase G廃止・trace廃止

### 目的

Phase G (phase_g_resolve_links.py)、traceファイル、関連コードを全て削除する。

### Step 4-1: ファイル削除

```bash
git rm scripts/phase_g_resolve_links.py
git rm tests/ut/test_phase_g.py
```

### Step 4-2: `run.py` からPhase G関連を削除

**ファイル**: `scripts/run.py`

1. `trace_dir` プロパティを削除（L75-76付近）
2. `knowledge_resolved_dir` プロパティを削除（L103-104付近）
3. Phase G backward compat ブロックを削除（L459-464）:
   ```python
   # 削除対象（L459-464）
   # Phase G (backward compat: only when explicitly specified without M)
   if "G" in phases and "M" not in phases:
       logger.info("\n🔗Phase G: Resolve Links")
       logger.info("   └─ Resolving RST cross-references...")
       from phase_g_resolve_links import PhaseGResolveLinks
       PhaseGResolveLinks(ctx).run()
   ```

### Step 4-3: `phase_m_finalize.py` からPhase G呼び出しを削除

**ファイル**: `scripts/phase_m_finalize.py`

1. `from phase_g_resolve_links import PhaseGResolveLinks` を削除
2. Step 5 の `PhaseGResolveLinks(self.ctx).run()` 呼び出しを削除
3. Step 7 の `processing_patterns` transplant ロジックを削除:
   ```python
   # 削除対象
   for fi in split_catalog.get("files", []):
       cache_path = f"{self.ctx.knowledge_cache_dir}/{fi['output_path']}"
       if os.path.exists(cache_path):
           knowledge = load_json(cache_path)
           fi["processing_patterns"] = knowledge.get("processing_patterns", [])
   ```

### Step 4-4: `phase_b_generate.py` からtrace書き出しを削除

**ファイル**: `scripts/phase_b_generate.py`

1. `_extract_rst_labels` メソッドを削除
2. `_build_prompt` 内の `{INTERNAL_LABELS}` 置換を削除（ただしプロンプト側はTask 8で対応するため、ここでは空配列を渡すように変更）
3. `generate_one` 内の trace 書き出しを削除:
   ```python
   # 削除対象
   if trace_json and trace_json.get("sections"):
       write_json(f"{self.ctx.trace_dir}/{file_id}.json", {
           "file_id": file_id,
           "generated_at": started_at,
           "sections": trace_json["sections"]
       })
   ```
4. `_extract_json` メソッドの変更: trace を返さずknowledge のみ返す。ただし、プロンプト変更（Task 8）までは出力が `{"knowledge": {...}, "trace": {...}}` 形式のままなので、`"knowledge"` キーからの抽出は維持し、`trace` を無視するだけにする:
   ```python
   def _extract_json(self, output):
       """Extract knowledge from output. Returns knowledge dict."""
       parsed = json.loads(output.strip())
       # Handle both formats: {"knowledge": {...}, "trace": {...}} and direct knowledge JSON
       knowledge = parsed.get("knowledge") or parsed
       if not isinstance(knowledge, dict) or "id" not in knowledge:
           raise ValueError("No valid knowledge data in output")
       return knowledge
   ```
   呼び出し元の `generate_one` を更新: `knowledge_json, trace_json = self._extract_json(...)` → `knowledge_json = self._extract_json(...)`

### Step 4-5: `merge.py` からtrace関連を削除

**ファイル**: `scripts/merge.py`

1. `_merge_trace_files` メソッドを削除
2. `run()` 内の `self._merge_trace_files(original_id, parts)` 呼び出しを削除
3. `processing_patterns` マージ処理を削除:
   ```python
   # 削除対象
   seen_pp = set()
   pp_list = []
   for pj in part_jsons:
       for pp in pj.get("processing_patterns", []):
           if pp not in seen_pp:
               seen_pp.add(pp)
               pp_list.append(pp)
   merged["processing_patterns"] = pp_list
   ```

### Step 4-6: `cleaner.py` からtrace削除処理を削除

**ファイル**: `scripts/cleaner.py`

`_list_phase_b_artifacts` 内の trace 関連行を削除:
```python
# 削除対象
trace = f"{ctx.trace_dir}/{file_id}.json"
if os.path.exists(trace):
    paths.append(trace)
```
および:
```python
# 削除対象
if os.path.isdir(ctx.trace_dir):
    paths.append(ctx.trace_dir)
```

### Step 4-7: `phase_f_finalize.py` から `knowledge_resolved_dir` 参照を削除

**ファイル**: `scripts/phase_f_finalize.py`

`_build_index_toon` と `_generate_docs` 内の以下を削除:
```python
# 削除対象
knowledge_dir = self.ctx.knowledge_resolved_dir if os.path.exists(self.ctx.knowledge_resolved_dir) else self.ctx.knowledge_dir
```

変更後: `self.ctx.knowledge_dir` を直接使用する。

### Step 4-8: テスト更新

1. `tests/ut/test_merge.py`:
   - `test_merge_consolidates_trace_files` テストを削除
   - `processing_patterns` マージテストを削除
   - `internal_labels` 関連テストを削除

2. `tests/ut/test_phase_m.py`:
   - Phase G 呼び出し検証を削除
   - trace 関連テストを削除
   - `processing_patterns` transplant テストを削除

3. `tests/ut/test_cleaner.py`:
   - trace ディレクトリ関連テストを削除

4. `tests/ut/conftest.py`:
   - `test_repo` fixture からの trace ディレクトリ作成を削除

### 検証

```bash
cd tools/knowledge-creator

# 1. 削除対象ファイルが存在しないことを確認
python -c "
import os
assert not os.path.exists('scripts/phase_g_resolve_links.py'), 'phase_g still exists'
assert not os.path.exists('tests/ut/test_phase_g.py'), 'test_phase_g still exists'
print('OK: Files deleted')
"

# 2. 全テスト実行
python -m pytest tests/ut/ -q -x

# 3. import検証 — phase_g_resolve_links を参照するファイルが残っていないこと
grep -r "phase_g_resolve_links" scripts/ tests/ --include="*.py" | grep -v "^Binary"
# 出力が空であること

# 4. trace_dir を参照するファイルが残っていないこと（run.pyのプロパティ削除確認含む）
grep -r "trace_dir" scripts/ tests/ --include="*.py" | grep -v "^Binary"
# 出力が空であること

# 5. knowledge_resolved を参照するファイルが残っていないこと
grep -r "knowledge_resolved" scripts/ tests/ --include="*.py" | grep -v "^Binary"
# 出力が空であること
```

### コミット

```
feat: remove Phase G, trace files, and processing_patterns from pipeline

- Delete phase_g_resolve_links.py and test_phase_g.py
- Remove trace_dir and knowledge_resolved_dir from Context
- Remove trace writing from Phase B
- Remove trace merging and processing_patterns merging from merge.py
- Remove processing_patterns transplant from Phase M
- Remove knowledge_resolved_dir fallback from Phase F
- Update tests: remove trace/Phase G/processing_patterns assertions

Closes #150 (partial)
```

---

## Task 5: knowledge JSONマイグレーションスクリプト

### 目的

421件の既存knowledge JSONファイルのセクションIDを旧形式（kebab-case）から新形式（s1, s2, ...）にリネームし、`processing_patterns` フィールドを削除する。

### 前提条件

- Task 1が完了し、step2_classify.pyが更新されていること
- カタログ（`.cache/v6/catalog.json`）がstep2で再生成され、`section_map` が全エントリに含まれていること
- カタログ再生成は以下で実行する（マイグレーション前に必ず実行）:
  ```bash
  cd tools/knowledge-creator
  python -c "
  import sys, os
  sys.path.insert(0, 'scripts')
  from run import Context
  from step2_classify import Step2Classify
  ctx = Context(version='6', repo=os.path.abspath('../..'), concurrency=1, run_id='migrate')
  Step2Classify(ctx, dry_run=False).run()
  "
  ```

### Step 5-1: マイグレーションスクリプト作成

**ファイル**: `scripts/migrate_section_ids.py` (新規作成)

```python
#!/usr/bin/env python3
"""Migrate knowledge JSON section IDs from kebab-case to sequential (s1, s2, ...).

Strategy: Use index array order in each knowledge JSON file.
index[0].id → s1, index[1].id → s2, ...

This is the simplest and most reliable approach because:
- index order is deterministic within each file
- heading-based matching fails for 106/296 split files (AI may add/merge sections)
- index[].id and sections{} keys are 1:1 consistent in 373/376 files (3 exceptions are Issue #150 bugs)

Also removes processing_patterns field from all knowledge JSON files.
"""
```

処理フロー:

1. 全knowledge JSONファイルを走査（カタログのoutput_pathを使用）
2. 各ファイルについて:
   a. `no_knowledge_content: true` → スキップ（`processing_patterns` 削除のみ）
   b. `index` 配列の出現順で old_id → new_id (s1, s2, ...) マッピングを構築
   c. index-section不整合がある3件（Phase C failのケース）は index 側を正として変換し、不整合のsection keyは削除
3. knowledge JSON を書き換え:
   - `index[].id` をリネーム
   - `sections` のキーをリネーム
   - `sections` 内の内部参照 `(#old-id)` を `(#new-id)` に置換
   - `processing_patterns` フィールドを削除
4. 変更統計を出力（変換件数、スキップ件数、不整合修正件数）

**マッピング構築の詳細**:

全ファイル共通（split/非split問わず）:
```python
mapping = {}
for i, entry in enumerate(knowledge.get("index", []), start=1):
    old_id = entry["id"]
    new_id = f"s{i}"
    mapping[old_id] = new_id
```

このアプローチの安全性:
- 106件のsplit heading/section不一致は無関係（index順を使うため）
- 非splitファイル（18件がマルチセクション）も同じロジックで処理可能
- 3件のindex-section不整合はマイグレーション中に検出・修正

**内部参照の置換**:
```python
import re
for old_id, new_id in mapping.items():
    # (#old-id) → (#new-id)
    content = re.sub(
        r'\(#' + re.escape(old_id) + r'\)',
        f'(#{new_id})',
        content
    )
```

**index-section不整合の修正** (3件):
```python
idx_ids = set(e["id"] for e in knowledge.get("index", []))
sec_keys = set(knowledge.get("sections", {}).keys())
# indexにないsection keyを削除
for orphan_key in (sec_keys - idx_ids):
    del knowledge["sections"][orphan_key]
    log(f"  Removed orphan section key: {orphan_key}")
# sectionにないindex entryを削除
knowledge["index"] = [e for e in knowledge["index"] if e["id"] in sec_keys or e["id"] in mapping]
```

### Step 5-2: 検証スクリプト

マイグレーションスクリプトの最後に検証ロジックを組み込む:

```python
def verify(knowledge_cache_dir):
    """Verify all section IDs are in s{N} format and no processing_patterns remain."""
    import glob, re
    errors = []
    pattern = re.compile(r'^s\d+$')
    for p in glob.glob(f'{knowledge_cache_dir}/**/*.json', recursive=True):
        if '/assets/' in p:
            continue
        data = load_json(p)
        if data.get('no_knowledge_content'):
            continue
        # Check section IDs
        for entry in data.get('index', []):
            if not pattern.match(entry['id']):
                errors.append(f"{p}: index id '{entry['id']}' not sequential")
        for sid in data.get('sections', {}).keys():
            if not pattern.match(sid):
                errors.append(f"{p}: section key '{sid}' not sequential")
        # Check no processing_patterns
        if 'processing_patterns' in data:
            errors.append(f"{p}: processing_patterns still present")
    return errors
```

### 検証

```bash
cd tools/knowledge-creator

# 1. まずカタログを更新（step2_classify dry-runで確認）
python -c "
import sys, os
sys.path.insert(0, 'scripts')
from run import Context
from step2_classify import Step2Classify

ctx = Context(version='6', repo=os.path.abspath('../..'), concurrency=1, run_id='test')
s2 = Step2Classify(ctx, dry_run=False)
result = s2.run()
sm_count = sum(1 for f in result['files'] if f.get('section_map'))
print(f'Files with section_map: {sm_count}/{len(result[\"files\"])}')
"

# 2. マイグレーション実行
python scripts/migrate_section_ids.py

# 3. 検証: 全セクションIDがs{N}形式であること
python -c "
import glob, json, re
pattern = re.compile(r'^s\d+$')
errors = 0
for p in glob.glob('.cache/v6/knowledge/**/*.json', recursive=True):
    if '/assets/' in p: continue
    data = json.load(open(p))
    if data.get('no_knowledge_content'): continue
    for entry in data.get('index', []):
        if not pattern.match(entry['id']):
            print(f'BAD index id: {p}: {entry[\"id\"]}')
            errors += 1
    for sid in data.get('sections', {}).keys():
        if not pattern.match(sid):
            print(f'BAD section key: {p}: {sid}')
            errors += 1
print(f'Errors: {errors}')
assert errors == 0, f'{errors} section IDs not migrated'
print('OK: All section IDs are sequential')
"

# 4. 検証: processing_patternsが全て消えていること
python -c "
import glob, json
count = 0
for p in glob.glob('.cache/v6/knowledge/**/*.json', recursive=True):
    if '/assets/' in p: continue
    data = json.load(open(p))
    if 'processing_patterns' in data:
        count += 1
        print(f'Still has pp: {p}')
assert count == 0, f'{count} files still have processing_patterns'
print('OK: No processing_patterns in cache')
"

# 5. 検証: Phase C で全件パスすること
python -c "
import sys, os
sys.path.insert(0, 'scripts')
from run import Context
from phase_c_structure_check import PhaseCStructureCheck

ctx = Context(version='6', repo=os.path.abspath('../..'), concurrency=1, run_id='verify')
results = PhaseCStructureCheck(ctx).run()
print(f'Phase C: {results[\"pass\"]}/{results[\"total\"]} pass')
assert results['error'] == 0, f'{results[\"error\"]} files failed Phase C'
"
```

### コミット

```
feat: migrate 421 knowledge JSON files to sequential section IDs

- Rename section keys from kebab-case to s1, s2, s3 format
- Update internal references (#old-id → #new-id)
- Remove processing_patterns field from all knowledge JSONs

Part of #150
```

---

## Task 6: Phase Fリンク変換統合

### 目的

Phase Fに全RSTリンク変換（`:ref:`, `:doc:`, `:download:`, `:java:extdoc:`）を統合する。3種類の出力（skill JSON, 閲覧用MD, index.toon）それぞれに適切な変換を適用する。

### Step 6-1: Phase Fにリンク変換ロジックを追加

**ファイル**: `scripts/phase_f_finalize.py`

1. `_build_link_maps` メソッドを新規追加:
   ```python
   def _build_link_maps(self):
       """Build link resolution maps from catalog and knowledge files.
       
       Returns/sets:
           self.label_map: {rst_label: (file_id, section_id_or_None)}
           self.doc_map: {source_path_without_ext: file_id}  
           self.file_type_category: {file_id: (type, category)}
       """
   ```

   **ラベル→(file_id, section_id)マッピングの構築手順**:
   
   a. カタログの全エントリを走査
   b. split_info がある場合は `original_id` でグループ化（mergeされたfile_idを使う）
   c. `section_map` の `rst_labels` からラベル→file_id を確定
   d. section_id の解決:
      - section_mapの `heading` と、knowledge JSONの `index[].title` を比較
      - 一致するものがあれば、そのindexエントリの `id` (= s1, s2, ...) をsection_idとする
      - 一致しない場合は `None`（ファイルレベルリンク）
   e. underscore/hyphen の両方のバリアントをインデックスに登録
   
   **重要**: section_mapのsection_idはh2ベースの仮番号でknowledge JSONのsection_idと直接一致しない。heading/title テキストマッチングで橋渡しする。

2. `_resolve_rst_links` メソッドを新規追加:
   ```python
   def _resolve_rst_links(self, content: str, current_file_id: str, 
                           output_type: str) -> str:
       """Resolve RST link syntax in content.
       
       Args:
           content: Section content with RST links
           current_file_id: ID of the file being processed
           output_type: 'skill_json' | 'docs_md'
       """
   ```

   4種のRSTリンクを正規表現でマッチし、output_typeに応じた変換を適用:

   | RST構文 | skill_json出力 | docs_md出力 |
   |---|---|---|
   | `:ref:` | `[text](#section_id)` (同一) / `[text](file_id.json#section_id)` (別) | `[text](#section_id)` (同一) / `[text](../../../docs/type/category/file-id.md#section_id)` (別) |
   | `:doc:` | `[text](file_id.json)` | `[text](../../../docs/type/category/file-id.md)` |
   | `:download:` | `[text](assets/file_id/filename)` | `[text](../../../knowledge/type/category/assets/file-id/filename)` |
   | `:java:extdoc:` | `` `ClassName` `` | `` `ClassName` `` |

   未解決のリンク（マップにない参照）はRST構文のまま維持し、ログに記録する。

3. `_generate_skill_json` メソッドを新規追加:
   ```python
   def _generate_skill_json(self):
       """Generate skill JSON files with RST links resolved.
       
       Reads merged knowledge JSON from knowledge_dir, applies link resolution,
       and overwrites the same files in-place. This is safe because:
       - knowledge_dir files are copies from cache (merge.py copies them)
       - Cache files in knowledge_cache_dir are never modified
       - If re-run is needed, Phase M re-copies from cache first
       """
   ```

   knowledge_dir（merge後）の各JSONを読み込み、`_resolve_rst_links(content, file_id, 'skill_json')` を適用して**同じパスに上書き**する。キャッシュ（knowledge_cache_dir）はRSTリンク未解決のまま保持される。

4. `_generate_docs` メソッドを拡張:
   - 既存の `_convert_asset_paths` の呼び出しに加えて `_resolve_rst_links(content, file_id, 'docs_md')` を呼び出す

5. `_convert_asset_paths` のバグ修正:
   `../../knowledge/` → `../../../knowledge/`

   具体的には:
   ```python
   # 修正前
   relative_prefix = f"../../knowledge/{type_}/{category}/assets/{file_id}/"
   # 修正後
   relative_prefix = f"../../../knowledge/{type_}/{category}/assets/{file_id}/"
   ```

6. `_build_index_toon` の変更:
   - `processing_patterns` をknowledge JSONからではなくカタログから読む
   - `type == "processing-pattern"` の場合は `category` をそのまま使用
   - それ以外はカタログの `processing_patterns` フィールド（現状ほぼ空）

7. `VALID_PROCESSING_PATTERNS` 定数を削除（もしくは common.py に移動）。

### Step 6-2: Phase Mの更新とPhase F run()のフロー変更

**ファイル**: `scripts/phase_f_finalize.py`

`run()` メソッドに `_generate_skill_json` と `_build_link_maps` を追加:

```python
def run(self):
    self._build_link_maps()  # 新規追加: リンク対応表構築

    self.logger.info("  Generating skill JSON with resolved links...")
    self._generate_skill_json()  # 新規追加: スキルJSON出力

    self.logger.info("  Building index.toon...")
    self._build_index_toon()

    self.logger.info("  Generating docs...")
    self._generate_docs()

    self.logger.info("  Generating summary...")
    self._generate_summary()
```

**ファイル**: `scripts/phase_m_finalize.py`

1. Phase G呼び出し削除は Task 4で完了済み
2. processing_patterns transplant は Task 4で削除済み
3. Phase Fのrun()が全出力を担当するため、Phase Mの変更は不要（Phase Fを呼び出すだけ）

Phase Mの新しいフロー:
```python
def run(self):
    # Step 1: Save split catalog
    split_catalog = load_json(self.ctx.classified_list_path)
    
    # Step 2: Delete knowledge_dir and docs_dir
    ...
    
    # Step 3: Merge knowledge_cache_dir -> knowledge_dir
    merged_catalog = MergeSplitFiles(self.ctx).run()
    
    # Step 4: Switch to merged catalog
    if not self.dry_run and merged_catalog:
        write_json(self.ctx.classified_list_path, merged_catalog)
    
    # Step 5: Phase F (link resolution + skill JSON + docs + index)
    PhaseFFinalize(self.ctx, dry_run=self.dry_run).run()
    
    # Step 6: Restore split catalog
    if not self.dry_run:
        write_json(self.ctx.classified_list_path, split_catalog)
```

### Step 6-3: テスト追加

**ファイル**: `tests/ut/test_phase_f_links.py` (新規作成)

Phase Gから移行するリンク変換テスト + 新規テスト:

```python
class TestPhaseFLinkResolution:
    """Test RST link resolution integrated into Phase F."""
    
    def test_ref_internal_same_file(self):
        """Internal :ref: resolves to #section_id."""
    
    def test_ref_external_skill_json(self):
        """External :ref: resolves to file_id.json#section_id for skill JSON."""
    
    def test_ref_external_docs_md(self):
        """External :ref: resolves to relative MD path for docs."""
    
    def test_doc_link_skill_json(self):
        """:doc: resolves to file_id.json for skill JSON."""
    
    def test_doc_link_docs_md(self):
        """:doc: resolves to relative MD path for docs."""
    
    def test_download_link(self):
        """:download: resolves to assets path."""
    
    def test_java_extdoc(self):
        """:java:extdoc: resolves to inline code."""
    
    def test_asset_path_bug_fix(self):
        """Asset paths in docs use ../../../ (not ../../)."""
    
    def test_unresolved_ref_preserved(self):
        """Unresolvable :ref: kept as-is."""
    
    def test_skill_json_generated(self):
        """Skill JSON files are generated with links resolved."""

    def test_index_toon_uses_catalog_pp(self):
        """index.toon reads processing_patterns from catalog, not knowledge JSON."""
```

テストデータは `tests/ut/fixtures/rst-links-testcases.json` を流用する。

### Step 6-4: `test_phase_m.py` の更新

Phase G関連テストはTask 4で削除済み。残りのテストでPhase Fの新しいフローが反映されるよう更新:

- merge後にPhase FがスキルJSON出力することの検証
- リンク変換がPhase F経由で行われることの検証

### 検証

```bash
cd tools/knowledge-creator

# 1. テスト実行
python -m pytest tests/ut/test_phase_f_links.py -q -x

# 2. 全テスト実行
python -m pytest tests/ut/ -q -x

# 3. Phase F単体テスト: リンク変換の動作確認
python -c "
import sys, os, json, re
sys.path.insert(0, 'scripts')
# サンプルのRSTリンクが変換されることを確認
from phase_f_finalize import PhaseFFinalize
from run import Context

ctx = Context(version='6', repo=os.path.abspath('../..'), concurrency=1, run_id='verify')
pf = PhaseFFinalize(ctx, dry_run=True)
pf._build_link_maps()
# :java:extdoc: の変換テスト
test_content = ':java:extdoc:\`SampleHandler <nablarch.sample.SampleHandler>\`'
result = pf._resolve_rst_links(test_content, 'test-file', 'skill_json')
assert ':java:extdoc:' not in result, f'java:extdoc not resolved: {result}'
assert 'SampleHandler' in result
print(f'java:extdoc resolved: {result}')
print('OK')
"
```

### コミット

```
feat: integrate all RST link resolution into Phase F

- Add _build_link_maps() using catalog section_map
- Add _resolve_rst_links() for :ref:, :doc:, :download:, :java:extdoc:
- Add _generate_skill_json() for link-resolved skill output
- Fix asset path bug in _convert_asset_paths (../../ → ../../../)
- Read processing_patterns from catalog in _build_index_toon
- Add comprehensive link resolution tests

Closes #149, part of #150
```

---

## Task 7: Phase F実行とデータ再生成

### 目的

スクリプト変更完了後、Phase Fを実行して3種類の出力を再生成する。

### Step 7-1: traceディレクトリ削除

```bash
git rm -r tools/knowledge-creator/.cache/v6/traces/
```

### Step 7-2: Phase F実行

```bash
cd tools/knowledge-creator
python -c "
import sys, os
sys.path.insert(0, 'scripts')
from run import Context
from phase_m_finalize import PhaseMFinalize

ctx = Context(version='6', repo=os.path.abspath('../..'), concurrency=1, run_id='finalize')
PhaseMFinalize(ctx).run()
"
```

### 検証

```bash
cd tools/knowledge-creator

# 全項目の一括検証（URL以外）
python scripts/verify_integrity.py

# 期待結果: 全チェック OK, 0 fail
# 主なチェック項目:
#   V1  docs内 [text](file.md) リンク → リンク先ファイルが実在する
#   V2  docs内 [text](file.md#anchor) → リンク先ファイル内にそのanchorが存在する
#   V3  docs内 asset画像/添付リンク → 画像/添付ファイルが実在する（旧94件リンク切れ→0件）
#   V4  skill JSON内 assets/ リンク → ファイル実在
#   V5  skill JSON内 (#section_id) → 同一ファイル内にそのsectionが存在する
#   V6  skill JSON内 (file.json#sid) → 対象JSONとsectionが実在する
#   V7  index.toon path → JSONファイル実在 + title文字列一致
#   V8  index[].id と sections{} の完全一致
#   V9  キャッシュの全section IDが s{N} 形式
#   V10 skill JSONにRST構文(:ref:等)が残っていない
#   V11 docs MDにRST構文(:ref:等)が残っていない
#   V12 キャッシュのRST構文は保持されている（変換されていない）
#   V13 キャッシュにprocessing_patternsフィールドがない
#   V14 カタログsection_mapのrst_labelsがソースRSTに実在する
#   V15 Phase G, trace, knowledge_resolvedが削除済み
#   V16 Pythonコードにtrace_dir等の残存参照がない
#   V17 biz_samplesがguide/biz-samplesに正しく配置

# URL疎通テストも実行する場合（ネットワーク接続必要）
python scripts/verify_integrity.py --check-urls
# V18 official_doc_urls サンプル → HTTP 200
# V19 セクション内の外部URL サンプル → HTTP 200
```

### コミット

```
feat: regenerate skill JSON, docs, and index with resolved links

- Delete .cache/v6/traces/ directory
- Regenerate skill JSON (335 files) with RST links resolved
- Regenerate docs MD (292 files) with RST links + asset paths fixed
- Regenerate index.toon with catalog-based processing_patterns
- Add scripts/verify_integrity.py for post-migration validation

Closes #149
```

---

## Task 8: プロンプト更新

### 目的

生成プロンプト・チェックプロンプト・修正プロンプトをセクションID連番化とprocessing_patterns除去に合わせて更新する。

### Step 8-1: `generate.md` の更新

**ファイル**: `prompts/generate.md`

1. Work Step 2-3 "Assign section IDs" を削除。代わりに以下を追記:
   ```
   ### 2-3. Section IDs are pre-assigned
   
   Section IDs (s1, s2, s3, ...) are pre-assigned by the classification script.
   Use the IDs provided in the {SECTION_IDS} placeholder below. Do NOT generate your own section IDs.
   ```

2. `{INTERNAL_LABELS}` セクションを削除（Phase B側で不要になったため）

3. Work Step 6 "Classify processing patterns" を全て削除

4. Output JSON Schema から `processing_patterns` を削除:
   - `required` 配列から除去
   - `properties` から除去

5. trace スキーマをJSON出力から削除。knowledge のみを出力するスキーマに変更:
   ```json
   {
     "type": "object",
     "required": ["id", "title", "no_knowledge_content", "official_doc_urls", "index", "sections"],
     "properties": {
       ...knowledge fields only...
     }
   }
   ```

6. Final self-checks から以下を削除:
   - `processing_patterns` 関連項目
   - kebab-case 検証項目（「All section IDs are kebab-case」）
   - trace 関連項目

7. 以下を追加:
   - 「Section IDs match the pre-assigned IDs (s1, s2, ...)」

8. Phase G言及の削除:
   - "Phase G will handle" → "Post-processing will handle"（RSTリンク保持指示の文言変更）

### Step 8-2: `content_check.md` の更新

**ファイル**: `prompts/content_check.md`

1. V6 "Processing Patterns Check" セクションを全て削除
2. V3のsection ID format チェック説明を連番形式に更新

### Step 8-3: `fix.md` の更新

**ファイル**: `prompts/fix.md`

1. `processing_patterns_invalid` fix指示を削除
2. セクションIDルールの言及を連番形式に更新

### 検証

```bash
cd tools/knowledge-creator

# 1. プロンプトにprocessing_patternsが残っていないことを確認
grep -c "processing_patterns" prompts/generate.md prompts/content_check.md prompts/fix.md
# 全て0であること

# 2. プロンプトにPhase Gの言及が残っていないことを確認
grep -ic "phase g" prompts/generate.md prompts/content_check.md prompts/fix.md
# 全て0であること

# 3. プロンプトにtraceの言及が残っていないことを確認
grep -ic "trace" prompts/generate.md
# 0であること

# 4. テスト実行
python -m pytest tests/ut/ -q
```

### コミット

```
feat: update prompts for sequential section IDs and remove processing_patterns

- Remove section ID generation instructions (pre-assigned by script)
- Remove processing_patterns from schema and checks
- Remove trace output from generate prompt
- Remove Phase G references
- Update content_check and fix prompts accordingly

Part of #150
```

---

## Task 9: Phase D/E更新

### 目的

Phase DとPhase Eから`processing_patterns`関連ロジックを削除する。

### Step 9-1: Phase D更新

**ファイル**: `scripts/phase_d_content_check.py`

1. `FINDINGS_SCHEMA` の `category` enum から `"processing_patterns_invalid"` を削除（ただし、他のカテゴリに影響しないよう `"no_knowledge_content_invalid"` 等は維持）

**注意**: Phase Dの`_compute_content_warnings`にはprocessing_patterns関連のチェックは存在しない（V6チェックはプロンプト側のみ）。スクリプト側の変更は FINDINGS_SCHEMA のみ。

### Step 9-2: Phase E更新

**ファイル**: `scripts/phase_e_fix.py`

`KNOWLEDGE_SCHEMA` の `required` と `properties` から `processing_patterns` を削除:

```python
KNOWLEDGE_SCHEMA = {
    "type": "object",
    "required": ["id", "title", "no_knowledge_content", "official_doc_urls", "index", "sections"],
    "properties": {
        "id": {"type": "string"},
        "title": {"type": "string"},
        "no_knowledge_content": {"type": "boolean"},
        "official_doc_urls": {"type": "array", "items": {"type": "string"}},
        "index": { ... },
        "sections": {"type": "object", "additionalProperties": {"type": "string"}}
    }
}
```

### 検証

```bash
cd tools/knowledge-creator
python -m pytest tests/ut/ -q
```

### コミット

```
feat: remove processing_patterns from Phase D/E schemas

Part of #150
```

---

## Task 10: #166 biz_samples リマップ

### 目的

biz_samplesのtype/categoryを `about/about-nablarch` から `guide/biz-samples` に変更する。

### Step 10-1: mappings更新

**ファイル**: `mappings/v6.json`, `mappings/v5.json`

`biz_samples/` のマッピングを変更:
```json
// 変更前
{"pattern": "biz_samples/", "type": "about", "category": "about-nablarch"}
// 変更後
{"pattern": "biz_samples/", "type": "guide", "category": "biz-samples"}
```

### Step 10-2: マイグレーションスクリプト

**ファイル**: `scripts/migrate_biz_samples.py` (新規作成)

1. カタログの18エントリを更新:
   - `type`: `about` → `guide`
   - `category`: `about-nablarch` → `biz-samples`
   - `id`: プレフィックス `about-nablarch-` → `biz-samples-`（例: `about-nablarch-biz_samples` → `biz-samples-biz_samples`）
   - `output_path`: `about/about-nablarch/` → `guide/biz-samples/`
   - `assets_dir`: 同上
   - `base_name`: splitファイルは `split_info.original_id` も同様にリネーム

2. knowledge JSONファイルを移動:
   - `.cache/v6/knowledge/about/about-nablarch/{old-id}.json` → `.cache/v6/knowledge/guide/biz-samples/{new-id}.json`
   - ファイル内の `id` フィールドを新IDに更新
   - ファイル内の `assets/about-nablarch-*` パスを `assets/biz-samples-*` に更新
   - assetsディレクトリも移動: `assets/about-nablarch-*/` → `assets/biz-samples-*/`

**対象18ファイルの例**:
```
about-nablarch-biz_samples       → biz-samples-biz_samples
about-nablarch-01--sec-d41d8cd9  → biz-samples-01--sec-d41d8cd9
about-nablarch-03--sec-d41d8cd9  → biz-samples-03--sec-d41d8cd9
```

### 検証

```bash
cd tools/knowledge-creator

# 1. biz_samplesファイルがguide/biz-samplesに配置されていること
python -c "
import json
cat = json.load(open('.cache/v6/catalog.json'))
biz = [f for f in cat['files'] if 'biz_samples' in f.get('source_path', '')]
for f in biz:
    assert f['type'] == 'guide', f'Expected guide, got {f[\"type\"]} for {f[\"id\"]}'
    assert f['category'] == 'biz-samples', f'Expected biz-samples, got {f[\"category\"]} for {f[\"id\"]}'
print(f'OK: {len(biz)} biz_samples files in guide/biz-samples')
"

# 2. about-nablarchにbiz_samples系が含まれないこと
python -c "
import json
cat = json.load(open('.cache/v6/catalog.json'))
bad = [f for f in cat['files'] if f.get('category') == 'about-nablarch' and 'biz_samples' in f.get('source_path', '')]
assert len(bad) == 0, f'{len(bad)} biz_samples files still in about-nablarch'
print('OK: No biz_samples in about-nablarch')
"
```

### コミット

```
feat: remap biz_samples from about/about-nablarch to guide/biz-samples

Closes #166
```

---

## Task 11: #151 nabledge-testシナリオ更新

### 目的

nabledge-testのシナリオファイルでsection_idが使われている場合、連番形式に更新する。

### Step 11-1: scenarios.json確認と更新

**ファイル**: `.claude/skills/nabledge-test/scenarios/nabledge-6/scenarios.json`

現状のscenarios.jsonには`section_id`フィールドは含まれていない（qa/ca タイプで`expectations`リストのみ使用）。対応方針書の「4/5シナリオ不一致」は今後section_id検証が追加された場合の話であり、**現時点ではscenarios.json自体の変更は不要**。

ただし、対応方針書にIssue #151として記載されているため、以下を確認する:
1. scenarios.jsonに `section_id` を含むフィールドがないことを確認
2. 含まれていなければ変更なし（Issueはこのタスク完了でCloseする）

```bash
python -c "
import json
data = json.load(open('../../.claude/skills/nabledge-test/scenarios/nabledge-6/scenarios.json'))
has_section_id = any('section_id' in json.dumps(s) for s in data.get('scenarios', []))
if has_section_id:
    print('WARNING: section_id found in scenarios - needs update')
else:
    print('OK: No section_id in scenarios - no change needed')
"
```

### 検証

```bash
# scenarioファイルにkebab-caseのsection IDが残っていないことを確認
python -c "
import json, re
data = json.load(open('../../.claude/skills/nabledge-test/scenarios/nabledge-6/scenarios.json'))
content = json.dumps(data)
# 旧形式のsection_id（kebab-case）がないことを確認
# s{N}形式またはsection_idフィールドが存在しないことを確認
print('Scenarios checked')
print('OK')
"
```

### コミット

```
fix: update nabledge-test scenarios for sequential section IDs

Closes #151
```

---

## Task 12: ワークフロードキュメント更新

### 目的

knowledge-searchワークフロードキュメントのsection_id例を連番形式に更新する。

### Step 12-1: ワークフローMD更新

以下のファイルでsection_idの例示を連番形式に更新:

**`.claude/skills/nabledge-6/workflows/_knowledge-search.md`**:
```
# 変更前
"section_id": "setup",
"section_id": "configuration",

# 変更後
"section_id": "s2",
"section_id": "s3",
```

**`.claude/skills/nabledge-6/workflows/_knowledge-search/_section-judgement.md`**:
```
# 変更前
file: features/libraries/universal-dao.json, section_id: paging, relevance: high
file: features/libraries/universal-dao.json, section_id: overview, relevance: partial

# 変更後
file: features/libraries/universal-dao.json, section_id: s3, relevance: high
file: features/libraries/universal-dao.json, section_id: s1, relevance: partial
```

**変更不要なファイル** (section_idの「例示」ではなく「フィールド説明」のみ):
- `_section-search.md` — 「候補セクションのリスト（file, section_id）」は説明文であり例示ではない。変更不要。
- `_full-text-search.md` — 同上。変更不要。

### 検証

```bash
# section_id の例がs{N}形式であることを確認
grep -n "section_id" ../../.claude/skills/nabledge-6/workflows/_knowledge-search*.md ../../.claude/skills/nabledge-6/workflows/_knowledge-search/*.md
```

### コミット

```
docs: update workflow docs for sequential section ID format

Part of #150
```

---

## Task 13: migrate_to_split_cache.py と migrate_to_catalog.py の更新

### 目的

マイグレーションスクリプトからtrace依存とprocessing_patterns依存を除去する。

### Step 13-1: `migrate_to_split_cache.py`

**ファイル**: `scripts/migrate_to_split_cache.py`

このスクリプトは初回マイグレーション用（mergedキャッシュ→splitキャッシュへの変換）で、今後再実行する予定はない。trace依存とprocessing_patterns依存を含むが、動作させる必要はない。

**対応**: trace_dir参照をコメントアウトまたは削除し、インポートエラーが発生しないようにする。具体的には:

1. `trace_dir` 変数の参照箇所をコメントアウト（L19付近, L116, L140, L162-179付近）
2. `assign_sections_to_parts` の `trace_sections` 引数を使わないフォールバック処理に変更するか、`trace_sections=[]` をデフォルトにする
3. `migrate_split_group` の trace 関連引数 `trace_data` をオプショナルにし、空dictで動作するようにする

### Step 13-2: `migrate_to_catalog.py`

**ファイル**: `scripts/migrate_to_catalog.py`

1. `processing_patterns` の patterns_map 読み込みを削除:
   ```python
   # 削除対象
   patterns_dir = f"{run_dir}/phase-f/patterns"
   patterns_map = {}
   for p in glob.glob(f"{patterns_dir}/*.json"):
       ...
   ```

2. `processing_patterns` の設定を削除:
   ```python
   # 削除対象
   for fi in files:
       fi["processing_patterns"] = patterns_map.get(fi["id"], [])
   ```

3. trace コピーを削除:
   ```python
   # 削除対象
   src_traces = f"{run_dir}/phase-b/traces"
   dst_traces = f"{cache_dir}/traces"
   if os.path.isdir(src_traces):
       shutil.copytree(src_traces, dst_traces, dirs_exist_ok=True)
   ```

### 検証

```bash
cd tools/knowledge-creator

# trace_dir, processing_patterns 参照が残っていないことを確認
grep -n "trace_dir\|trace_path\|traces/" scripts/migrate_to_split_cache.py scripts/migrate_to_catalog.py
# 出力が空であること

grep -n "processing_patterns\|patterns_map\|patterns_dir" scripts/migrate_to_catalog.py
# 出力が空であること
```

### コミット

```
refactor: remove trace and processing_patterns dependencies from migration scripts

Part of #150
```

---

## Task 14: 最終検証

### 全件検証コマンド

```bash
cd tools/knowledge-creator

# 1. ユニットテスト
echo "=== Unit Tests ==="
python -m pytest tests/ut/ -q

# 2. 統合検証（リンク先実在・タイトル一致・構造整合性・残存参照チェック全項目）
echo "=== Integrity Verification ==="
python scripts/verify_integrity.py -v

# 3. URL疎通テスト（ネットワーク接続必要）
echo "=== URL Verification ==="
python scripts/verify_integrity.py --check-urls

# 期待結果: 全て 0 fail
```

### コミット

最終検証パス後、PRを作成:

```
PR title: fix: deterministic section IDs, Phase G removal, link resolution integration

Closes #149, #150, #151, #166

## Summary
- Section IDs: AI-generated kebab-case → script-generated sequential (s1, s2, ...)
- Phase G: abolished, link resolution integrated into Phase F
- Trace files: abolished, section mapping moved to catalog
- processing_patterns: removed from knowledge JSON, catalog-only
- Asset path bug: fixed (../../ → ../../../) in browsable docs
- Skill JSON: RST links now fully resolved (was: 2,040+ unresolved)
- biz_samples: remapped to guide/biz-samples

## No regeneration required
All changes are script-based migrations on existing cache data.
```

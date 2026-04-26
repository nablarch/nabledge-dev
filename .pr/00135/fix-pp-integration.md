# タスク: processing_patterns を Phase B/D/E に統合、Phase F から CC 削除

## 前提

ブランチ `120-generate-all-nabledge6-knowledge-files` に対する修正。

## 問題

1. Phase F（パターン分類）が独立した CC 呼び出しで全量実行される。fix --target で対象を絞っても全量 CC が動く。
2. processing_patterns は knowledge JSON にない。catalog.json にだけ保存されている。Phase D/E でチェック・修正されない。

## 方針

- Phase B: knowledge 生成時に processing_patterns を同時に分類し、knowledge JSON に含める
- Phase D: processing_patterns が正しいかチェックする項目を追加
- Phase E: processing_patterns の問題を修正する項目を追加
- Phase F: CC 呼び出しを削除。index.toon / docs / summary 生成のみ（knowledge JSON の processing_patterns を読む）

## 禁止事項

- タスクドキュメントに記載のないファイルを変更しない。
- 記載されたコードをそのまま使う。
- 各 Step の検証がパスしてから次の Step に進む。失敗したら止めて報告する。

## 変更対象ファイル

| ファイル | 変更内容 |
|---------|---------|
| `prompts/generate.md` | processing_patterns の分類指示と JSON schema に追加 |
| `prompts/content_check.md` | V6: processing_patterns チェック追加 |
| `prompts/fix.md` | processing_patterns_invalid の修正指示追加 |
| `scripts/phase_f_finalize.py` | CC 呼び出し削除。knowledge JSON から pp を読む |
| `scripts/phase_m_finalize.py` | pp 移植ロジック削除（不要になる） |
| `tests/test_cache_separation.py` | target を 1/3 に変更、Phase F CC 期待値を 0 に修正 |
| `README.md` | Phase F の説明更新 |
| `prompts/classify_patterns.md` | 削除（Phase F で使わなくなる） |

---

## Step 1: テスト修正（RED 確認）

`tests/test_cache_separation.py` を修正する。

### 1-1. expected fixture の target を 1/3 に変更

L300-318 の `persistent_error_base_names` ブロックを以下に置き換える:

**変更前:**
```python
    persistent_error_base_names = [
        "adapters-doma_adaptor", "adapters-redisstore_lettuce_adaptor",
        "blank-project-CustomizeDB", "blank-project-setup_ContainerWeb",
        "cloud-native-aws_distributed_tracing", "db-messaging-multiple_process",
        "handlers-SessionStoreHandler", "handlers-csrf_token_verification_handler",
        "handlers-thread_context_handler", "java-static-analysis-java_static_analysis",
        "libraries-bean_validation", "libraries-database",
        "libraries-failure_log", "libraries-log",
        "libraries-service_availability", "libraries-tag",
        "libraries-tag_reference", "mom-messaging-feature_details",
        "nablarch-batch-architecture", "restful-web-service-architecture",
        "testing-framework-02_entityUnitTestWithNablarchValidation",
        "testing-framework-batch",
        "testing-framework-guide-development-guide-05-UnitTestGuide-02-RequestUnitTest",
        "toolbox-NablarchOpenApiGenerator",
    ]
    split_ids_24 = []
    for bn in persistent_error_base_names:
        matched = [e["id"] for e in catalog_entries if e.get("base_name") == bn]
        split_ids_24.extend(matched)
```

**変更後:**
```python
    # 1/3 target: sorted base_names の先頭 1/3
    all_base_names = sorted(set(e.get('base_name', e['id']) for e in catalog_entries))
    target_base_names = all_base_names[:len(all_base_names) // 3]
    target_split_ids = []
    for bn in target_base_names:
        matched = [e["id"] for e in catalog_entries if e.get("base_name") == bn]
        target_split_ids.extend(matched)
```

### 1-2. params dict を更新

```python
# 変更前:
"split_ids_24": split_ids_24,
"split_ids_24_count": len(split_ids_24),

# 変更後:
"target_base_names": target_base_names,
"target_split_ids": target_split_ids,
"target_split_ids_count": len(target_split_ids),
```

### 1-3. test_regen_target と test_fix_target のローカル変数を更新

両テスト内のハードコードされた `persistent_error_base_names` リスト（2箇所）を以下に置き換え:
```python
target_base_names = params["target_base_names"]
```

params からの取得:
```python
# 変更前:
split_ids_24 = params["split_ids_24"]
target_count = params["split_ids_24_count"]

# 変更後:
target_split_ids = params["target_split_ids"]
target_count = params["target_split_ids_count"]
```

`_run_main` の target 引数: `persistent_error_base_names` → `target_base_names`

テスト本体の `split_ids_24` 参照を全て `target_split_ids` に置換。

### 1-4. 全5テストの Phase F CC 期待値を 0 に修正

Phase F から CC 呼び出しがなくなるので、全テストで F=0。

```python
# test_gen, test_gen_resume, test_regen_target, test_fix, test_fix_target 全て:
# 変更前:
assert len(counter["F"]) == params["F_TARGET"]
# または他の F 期待値

# 変更後:
assert len(counter["F"]) == 0, (
    f"counter['F'] expected 0 (no CC in Phase F), got {len(counter['F'])}"
)
```

### 1-5. CC mock の Phase B 応答に processing_patterns を追加

`_make_cc_mock` 内の Phase B 応答で、knowledge に `processing_patterns` を追加する:

```python
        if "trace" in schema_str:
            # Phase B: generate knowledge + trace
            counter["B"].append(file_id)
            knowledge = expected_knowledge_cache[file_id]
```

この `knowledge` には既に `expected_knowledge_cache` から値が来る。`generate_expected.py` の `mock_phase_b_knowledge` にも `processing_patterns` を追加する必要がある:

`tests/generate_expected.py` の `mock_phase_b_knowledge` 関数の return dict に追加:

```python
    return {
        "id": file_id,
        "title": f"Title for {file_id}",
        "no_knowledge_content": False,
        "official_doc_urls": [...],
        "processing_patterns": [],  # 追加
        "index": [...],
        "sections": {...},
    }
```

`mock_phase_e_knowledge` も同様（`mock_phase_b_knowledge` を呼ぶので自動的に含まれる）。

### Step 1 検証（RED 確認）

```bash
cd tools/knowledge-creator
python -m pytest tests/test_cache_separation.py -v --tb=line
```

期待結果:
- test_gen: FAILED（Phase F CC が 256 回呼ばれる、期待は 0）
- test_gen_resume: FAILED（同上）
- test_regen_target: FAILED（同上）
- test_fix: FAILED（同上）
- test_fix_target: FAILED（同上）

5件全て FAILED を確認してから Step 2 に進む。

---

## Step 2: プロンプト修正

### 2-1. prompts/generate.md

Step 7 の JSON schema の knowledge.properties に `processing_patterns` を追加する。`sections` の直後に追加:

```json
        "processing_patterns": {
          "type": "array",
          "description": "Relevant Nablarch processing patterns. Empty array if none apply.",
          "items": {
            "type": "string",
            "enum": [
              "nablarch-batch", "jakarta-batch", "restful-web-service",
              "http-messaging", "web-application", "mom-messaging", "db-messaging"
            ]
          }
        }
```

knowledge.required にも `"processing_patterns"` を追加:
```json
"required": ["id", "title", "no_knowledge_content", "official_doc_urls", "index", "sections", "processing_patterns"],
```

generate.md の Work Step 6 の前（Step 5 の後）に以下の Work Step を追加:

```markdown
## Work Step 6: Classify processing patterns

Determine which Nablarch processing patterns are relevant to this content.

### Valid patterns

| Pattern | Match if content mentions... |
|---|---|
| nablarch-batch | Nablarchバッチ, 都度起動, 常駐型, BatchAction, DataReader, nablarch.fw.action.BatchAction |
| jakarta-batch | Jakarta Batch, JSR 352, jBatch, Batchlet, Chunk, javax.batch |
| restful-web-service | RESTful, JAX-RS, REST API, @Produces, @Consumes, JaxRsMethodBinder |
| http-messaging | HTTPメッセージング, HTTP受信, メッセージ同期応答, HttpMessagingRequestParsingHandler |
| web-application | Webアプリケーション, サーブレット, JSP, HttpRequest, セッション管理 |
| mom-messaging | MOMメッセージング, MQ, キュー, 非同期メッセージ, MomMessagingAction |
| db-messaging | DB連携メッセージング, テーブルキュー, 電文, DatabaseRecordReader |

### Rules

1. Include a pattern only if the content explicitly mentions it.
2. Generic libraries used across patterns → include ONLY patterns explicitly mentioned. Do NOT assume all apply.
3. If no pattern is mentioned → empty array `[]`.
4. If FILE_TYPE is `processing-pattern` → include FILE_CATEGORY as the pattern.
```

既存の Step 6（URL extraction）を Step 7 に、Step 7（Assemble JSON）を Step 8 にリナンバーする。

Final self-checks に追加:
```
- [ ] `processing_patterns` is an array (empty `[]` if no patterns apply)
```

### 2-2. prompts/content_check.md

Validation Checklist の末尾（V5 の後）に追加:

```markdown
### V6: Processing Patterns Check (severity: minor)

Check that `processing_patterns` in the knowledge file is correct:

1. If `processing_patterns` field is missing → report: category "processing_patterns_invalid", description "processing_patterns field is missing"
2. For each pattern in the array, confirm the content actually mentions that pattern (use the indicators table from generate.md Step 6).
3. If content mentions a pattern not in the array → report as finding.
4. If FILE_TYPE is `processing-pattern`, confirm `processing_patterns` includes FILE_CATEGORY.

For each issue found, record:
"PROCESSING_PATTERNS_INVALID: {description}"
```

### 2-3. prompts/fix.md

Instructions のリストに追加:

```markdown
- **processing_patterns_invalid**: Fix the processing_patterns array. Add missing patterns, remove incorrect ones, or add the field if missing. Valid values: nablarch-batch, jakarta-batch, restful-web-service, http-messaging, web-application, mom-messaging, db-messaging. If FILE_TYPE is `processing-pattern`, include FILE_CATEGORY.
```

### Step 2 検証

プロンプトの変更はテストに影響しない（CC はモック）。構文を確認:

```bash
python -c "
import json
# generate.md の JSON schema が valid JSON かチェック
content = open('prompts/generate.md').read()
# schema 部分を抽出
start = content.find('{', content.find('### Output JSON Schema'))
end = content.rfind('}', 0, content.find('### Final self-checks')) + 1
schema = content[start:end]
parsed = json.loads(schema)
assert 'processing_patterns' in parsed['properties']['knowledge']['properties']
assert 'processing_patterns' in parsed['properties']['knowledge']['required']
print('generate.md schema: OK')
"
```

---

## Step 3: スクリプト修正（GREEN にする）

### 3-1. phase_f_finalize.py: CC 呼び出し削除

`_build_index_toon` メソッドを修正。CC で分類する代わりに knowledge JSON の `processing_patterns` を読む。

**変更前（L121-179）の `_build_index_toon` 内:**
```python
            if fi["type"] == "processing-pattern":
                patterns = fi["category"]
            else:
                to_classify.append((fi, knowledge))
                patterns = None
```

**変更後:**
```python
            if fi["type"] == "processing-pattern":
                patterns = fi["category"]
            else:
                pp = knowledge.get("processing_patterns", [])
                patterns = " ".join(pp) if isinstance(pp, list) else (pp or "")
```

`to_classify` のブロック全体（L155-168: ThreadPoolExecutor で CC を並列実行する部分）を削除。

`_save_pp_to_catalog` の呼び出し（L172-179: pp_map を作って catalog に保存する部分）も削除。

`__init__` から以下を削除:
- `self._pp_cache = self._load_pp_cache()`
- `_load_pp_cache` メソッド全体
- `_classify_patterns` メソッド全体
- `_save_pp_to_catalog` メソッド全体

`__init__` から以下も削除（不要になる）:
- `self.prompt_template = read_file(...)` （classify_patterns.md の読み込み）
- `from concurrent.futures import ThreadPoolExecutor, as_completed` が不要になったら import も削除

### 3-2. phase_m_finalize.py: pp 移植ロジック削除

Step 7 の pp 移植（split_catalog への processing_patterns 書き戻し）は不要になる。knowledge JSON に pp が入っているので、Phase F は knowledge から読む。ただし catalog.json の processing_patterns フィールドは index.toon 生成では使わなくなるが、既存の互換性のために残す。

Step 7 の処理を簡略化:

**変更前（L68-82）:**
```python
        # Step 7: Transplant processing_patterns from merged catalog back to
        # split catalog, then restore split catalog
        if not self.dry_run:
            merged_data = load_json(self.ctx.classified_list_path)
            merged_pp = {}
            for fi in merged_data.get("files", []):
                pp = fi.get("processing_patterns")
                if pp is not None:
                    merged_pp[fi["id"]] = pp
            for fi in split_catalog.get("files", []):
                base = fi.get("base_name", fi["id"])
                if base in merged_pp:
                    fi["processing_patterns"] = merged_pp[base]
            write_json(self.ctx.classified_list_path, split_catalog)
```

**変更後:**
```python
        # Step 7: Restore split catalog
        if not self.dry_run:
            write_json(self.ctx.classified_list_path, split_catalog)
```

### 3-3. prompts/classify_patterns.md を削除

```bash
git rm prompts/classify_patterns.md
```

### Step 3 検証（GREEN 確認）

```bash
python -m pytest tests/test_cache_separation.py -v --tb=line
```

期待結果: 5件全て PASSED。

```bash
python -m pytest tests/ -q --tb=line
```

期待結果: 全テスト PASSED。

---

## Step 4: README 更新

`README.md` の Phase 一覧表を更新:

**変更前:**
```
| **M: Finalization** | 分割ファイル統合 → RSTリンク解決 → インデックス・ドキュメント生成 | Hybrid | No |
```

**変更後:**
```
| **M: Finalization** | 分割ファイル統合 → RSTリンク解決 → インデックス・ドキュメント生成 | Script | No |
```

Mermaid フロー図の Phase M ラベルから Phase F 関連の記述があれば「Generate Docs & Index」に簡略化。

Phase 一覧表に「Phase F の CC 呼び出しなし」を明記するか、Phase F の行を削除して Phase M の説明に統合:

```
| **B: Generation** | ソース → knowledge JSON 生成（processing_patterns 分類含む） | AI | Yes |
```

### Step 4 検証

README の記述が実装と一致していることを目視確認。

---

## Step 5: コミット・プッシュ

```bash
cd ../..
git add tools/knowledge-creator/prompts/generate.md
git add tools/knowledge-creator/prompts/content_check.md
git add tools/knowledge-creator/prompts/fix.md
git rm tools/knowledge-creator/prompts/classify_patterns.md
git add tools/knowledge-creator/scripts/phase_f_finalize.py
git add tools/knowledge-creator/scripts/phase_m_finalize.py
git add tools/knowledge-creator/tests/test_cache_separation.py
git add tools/knowledge-creator/tests/generate_expected.py
git add tools/knowledge-creator/README.md
git status
```

上記ファイルのみ変更されていることを確認。

```bash
git commit -m "refactor: integrate processing_patterns into Phase B/D/E, remove CC from Phase F

- generate.md: add processing_patterns classification as Work Step 6,
  add field to knowledge JSON schema
- content_check.md: add V6 processing_patterns check
- fix.md: add processing_patterns_invalid fix instruction
- phase_f_finalize.py: remove CC calls, read pp from knowledge JSON
- phase_m_finalize.py: simplify Step 7 (pp transplant no longer needed)
- classify_patterns.md: deleted (no longer used)
- test_cache_separation.py: all tests assert Phase F CC = 0,
  target tests use 1/3 of base_names
- generate_expected.py: mock knowledge includes processing_patterns"

git push origin 120-generate-all-nabledge6-knowledge-files
```

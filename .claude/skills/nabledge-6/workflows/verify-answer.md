# Verify Answer Workflow

Verifies that all Nablarch-specific claims in the answer are supported by the source pages, and that no required content is missing from the answer.

## Input

- `{answer_text}`: Generated answer string.
- `{selected_sections}`: Array of section pointers in `{"file": "...", "section_id": "...", "relevance": "..."}` format. Used only to identify which pages to read.

## Output

```json
{"result": "PASS"}
```

or

```json
{"result": "FAIL", "issues": ["<unsupported claim or missing item description>", ...]}
```

---

## Step 1: Read pages

Extract the unique `file` values from `{selected_sections}`. For each unique file path, read the full page file at `knowledge/{file}`. Save all page contents as `page_contents`.

## Step 2: Verify claims

Check that all Nablarch-specific claims in `{answer_text}` are supported by `page_contents`.

**Extract these claim categories** (Nablarch-specific claims):

| Category | Examples |
|----------|---------|
| API names | "UniversalDao.deferメソッド", "@InjectForm アノテーション" |
| Class names | "DatabaseRecordReader", "BatchAction" |
| Configuration method | "web-component-configuration.xmlに設定", "コンポーネント定義ファイルに記述" |
| Behavior spec | "遅延ロードはDB接続をストリーミングする", "バリデーションエラー時にステータスコード400を返す" |
| Constraints | "closeしないとリソースリーク", "Formのプロパティは全てString型" |
| Parameters | "-requestPathで指定", "SQLID" |

**Do NOT extract** (general knowledge):

| Category | Examples |
|----------|---------|
| General Java | "Beanクラスを作成する", "try-with-resourcesを使う" |
| General programming | "バリデーションを実行する", "エラーメッセージを表示する" |
| Flow description | "まず〜して、次に〜する" |
| General web concepts | "HTTPリクエスト", "JSONレスポンス" |

For each extracted claim, judge in order:
1. Directly stated in page content → supported
2. Direct paraphrase of page content (paraphrase/abbreviation/synonym) → supported
3. Attribute/behavior/constraint not explicitly stated → unsupported

Boundary rule: Inference is valid only for direct paraphrases. Attributes, behaviors, or constraints not explicitly stated are unsupported even if technically plausible.

## Step 3: Check for missing MUST content

Check whether `page_contents` contains information that directly answers the question but is absent from `{answer_text}`.

Specifically: if a page section contains a concrete implementation method, required configuration, or explicit constraint that is directly relevant to the question AND is not reflected in the answer in any form, flag it as a missing item.

Do NOT flag:
- Background or conceptual content
- Content the answer correctly omitted as out of scope
- Content that is present in the answer in paraphrased form

## Step 4: Return result

If any claim from Step 2 is unsupported OR any missing item found in Step 3:
```json
{"result": "FAIL", "issues": ["<unsupported claim or missing item description>", ...]}
```

Otherwise:
```json
{"result": "PASS"}
```

# Verify Answer Workflow

Verifies that all Nablarch-specific claims in the answer are supported by the sections.

## Input

- `{answer_text}`: Generated answer string.
- `{selected_sections}`: Array of section pointers used to generate the answer.

## Output

```json
{"result": "PASS"}
```

or

```json
{"result": "FAIL", "issues": ["claim1", "claim2"]}
```

---

## Step 1: Verify answer

Check that all Nablarch-specific claims in `{answer_text}` are supported by the content of `{selected_sections}`.

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
1. Directly stated in section content → supported
2. Direct paraphrase of section content (paraphrase/abbreviation/synonym) → supported
3. Attribute/behavior/constraint not explicitly stated → unsupported

Boundary rule: Inference is valid only for direct paraphrases. Attributes, behaviors, or constraints not explicitly stated are unsupported even if technically plausible.

If any claim is unsupported, return `{"result": "FAIL", "issues": ["<claim1>", "<claim2>", ...]}` listing all unsupported claims.

Otherwise return `{"result": "PASS"}`.

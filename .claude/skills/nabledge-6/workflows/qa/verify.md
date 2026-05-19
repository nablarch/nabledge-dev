# Verify Workflow

Verifies that all Nablarch-specific claims in the answer are supported by knowledge sections.

## Input

- `{answer}`: Answer text to verify
- `{pointer_json}`: Pointer JSON used to generate the answer

## Output

Verified answer text (possibly with a warning appended if hallucination detected)

## Steps

### Step 1: Read section content

**Tool**: Bash

From `{pointer_json}.results`, select sections to read:
- All sections (up to 15)
- `"high"` first, then `"partial"`

If `pointer_json.results` is empty, set `sections_content = ""` and proceed to Step 2.

Otherwise, build the argument list: for each selected result, `"{file}:{section_id}"`.

Run:
```bash
bash scripts/read-sections.sh "file1.json:s1" "file2.json:s3" ...
```

Save the output as `sections_content`.

### Step 2: Verify claims

**Tool**: In-memory (LLM generation)

Call LLM with the following prompt, substituting the variables:

---
You are a Nablarch framework claim verifier. Verify that all Nablarch-specific claims in the answer text are supported by the knowledge sections.

**Answer text**: {answer}

**Knowledge sections**: {sections_content}

Steps:
1. Extract all Nablarch-specific claims from the answer text. For each claim, record the verbatim quote from the answer.
2. For each claim, verify whether it is supported by the knowledge section content.
3. If even one claim is unsupported, set result to FAIL; otherwise PASS.
4. Output JSON in the format below.

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

**Verification criteria** — for each claim, judge in order:

1. Directly stated in section content → supported: true, evidence: section reference (file.json:sN format)
2. Direct paraphrase of section content (paraphrase/abbreviation/synonym) → supported: true, evidence: section reference (file.json:sN format)
3. Attribute/behavior/constraint not explicitly stated in section content → supported: false, evidence: "" (empty string)

Boundary rule: Inference is valid only for direct paraphrases of section content. Attributes, behaviors, or constraints not explicitly stated are supported: false even if technically plausible.

Output JSON:
```json
{
  "result": "PASS or FAIL",
  "claims": [
    {"claim": "...", "supported": true, "evidence": "file.json:sN"},
    {"claim": "...", "supported": false, "evidence": ""}
  ],
  "issues": [
    {"claim": "unsupported claim text", "quote": "verbatim quote from answer text"}
  ]
}
```
`issues` is empty array on PASS.
---

Parse the JSON response. Extract:
- `result`: `"PASS"` or `"FAIL"`
- `issues`: list of unsupported claims (empty if PASS)

### Step 3: Return verified answer

**If `result == "PASS"`**: Return the original answer text unchanged.

**If `result == "FAIL"`**: Append a warning to the answer:

```
---
⚠️ 検証: 以下の主張は知識ファイルで裏付けが取れていません:
- {issue.claim}
```

Return the modified answer text.

# QA Workflow

Question-answering workflow. Searches Nablarch knowledge and responds in Japanese.

## Input

User's question (natural Japanese text)

## Output

Answer in Japanese (Markdown)

---

## Step 1: Classify question

From the question, determine `processing_type` and `purpose` independently.

### Determine processing_type

**Check A — Verbatim keyword match (no inference)**

Scan the question for keywords below. Match verbatim only; do not infer from business context.

Group 1 — Official names/abbreviations of processing types:
- ウェブアプリケーション, Webアプリ, Web画面
- RESTfulウェブサービス, REST API, RESTful, REST
- Nablarchバッチ, バッチアプリケーション (only "Nablarchバッチ" or "バッチアプリ")
- Jakartaバッチ
- テーブルをキューとして使ったメッセージング
- HTTPメッセージング
- MOMメッセージング

Group 2 — Technical terms that exist in exactly one processing type:
- JSP, HIDDENストア, セッション変数, セッションストア, CSRF → ウェブアプリケーション
- リソースクラス, JAX-RS → RESTfulウェブサービス
- requestPath (as a batch startup argument) → Nablarchバッチ
- ItemReader, ItemWriter, Chunk → Jakartaバッチ

- Match → exactly one type → `processing_type = <that type>`
- Match → multiple types → `processing_type = UNCLEAR`
- No match → proceed to Check B

**Check B — Cross-functional feature check**

Check whether the question topic is one of:
- Testing framework
- Internationalization (i18n)
- Logging configuration
- Common utilities (date/time, code value management, etc.)

Note: Common concepts (transactions, validation, DB access, SQL) are NOT cross-functional if their configuration/implementation differs per processing type.

- Topic is cross-functional → `processing_type = null`
- Topic is not cross-functional → `processing_type = UNCLEAR`

### Determine purpose

Scan the question for signal keywords:

| Signal keywords | Purpose |
|---|---|
| 「仕組み」「とは」「動作」「理解」「概要」 | 仕組み・動作を理解したい |
| 「エラー」「例外」「不具合」「原因」「調査」 | 不具合・エラーを調査したい |
| 「テスト」「テストコード」「テストケース」 | テストを書きたい |
| 「バージョンアップ」「移行」「マイグレーション」「アップグレード」 | バージョンアップしたい |
| 「サンプル」「パターン」「例を見たい」「参考」 | 実装パターン・サンプルを参考にしたい |
| 「セキュリティ」「脆弱性」「認証」「認可」 | セキュリティ対応したい |

- Match found → `purpose = <that category>`
- No match → `purpose = UNCLEAR`

### Result

If both `processing_type` and `purpose` are determined (not UNCLEAR) → build `hearing_answer` and proceed to Step 3:
```
hearing_answer = { "processing_type": "<type or null>", "purpose": "<category>" }
```

If either is UNCLEAR → proceed to Step 2.

---

## Step 2: Ask user if needed

If both `processing_type` and `purpose` are already determined in Step 1, skip to the build step below.

Otherwise, ask only about what is UNCLEAR.

**If both processing_type and purpose are UNCLEAR**, output both questions together in one message:

```
いくつか確認させてください。

どの処理方式で実装しますか？
1. ウェブアプリケーション
2. RESTfulウェブサービス
3. Nablarchバッチ
4. Jakartaバッチ
5. テーブルをキューとして使ったメッセージング
6. HTTPメッセージング
7. MOMメッセージング
8. その他（処理方式に依存しない）

何を目的としていますか？
1. 実装したい
2. 仕組み・動作を理解したい
3. 不具合・エラーを調査したい
4. テストを書きたい
5. バージョンアップしたい
6. 実装パターン・サンプルを参考にしたい
7. セキュリティ対応したい
8. その他
```

**If only processing_type is UNCLEAR**, output:

```
どの処理方式で実装しますか？

1. ウェブアプリケーション
2. RESTfulウェブサービス
3. Nablarchバッチ
4. Jakartaバッチ
5. テーブルをキューとして使ったメッセージング
6. HTTPメッセージング
7. MOMメッセージング
8. その他（処理方式に依存しない）
```

**If only purpose is UNCLEAR**, output:

```
何を目的としていますか？

1. 実装したい
2. 仕組み・動作を理解したい
3. 不具合・エラーを調査したい
4. テストを書きたい
5. バージョンアップしたい
6. 実装パターン・サンプルを参考にしたい
7. セキュリティ対応したい
8. その他
```

Wait for the user's response. Then build `hearing_answer`:
- `processing_type`: from Step 1 or user's selection (「その他」or 8 → null)
- `purpose`: from Step 1 or user's selection (「その他」or 8 → 実装したい)

Proceed to Step 3.

---

## Step 3: Semantic search

Execute `workflows/semantic-search.md` with:
- `{question}` = user's question
- `{hearing_answer}` = formatted hearing string from Step 2:
  - If `processing_type` is not null: `"処理方式: {processing_type}\n目的: {purpose}"`
  - If `processing_type` is null: `"目的: {purpose}"`

Save the returned `results` array as `selected_sections`.

---

## Step 4: Read section content

From `selected_sections`, select sections to read:
1. All `high` sections first
2. Then `partial` sections to fill remaining slots
3. Maximum 10 sections total

Build the argument list: for each selected section, `"{file}:{section_id}"`.

```bash
bash scripts/read-sections.sh "file1.json:s1" "file2.json:s3" ...
```

Save the output as `sections_content`.

If `selected_sections` is empty, set `sections_content = ""`.

---

## Step 5: Generate answer

If `sections_content` is empty, output immediately:
```
この情報は知識ファイルに含まれていません。
```
and stop.

Otherwise, generate a Japanese answer based solely on the knowledge sections.

**Question**: user's question

**Hearing answer**: formatted hearing string from Step 2

**Knowledge sections**: `sections_content`

1. Read all knowledge sections.
2. Identify the information that directly answers the question.
3. Write the answer in the format below.

**Answer format**:

**結論**: Direct answer to the question (1–2 sentences)
- Do not parrot back the question
- Include specific method names, class names, and approaches

**根拠**: Code examples, configuration examples, or spec information that backs the conclusion
- Show code/config examples in code blocks
- Priority: implementation example > configuration example > API spec > conceptual explanation
- If using multiple sections, organize along the implementation flow
- Quote code examples from sections verbatim (do not modify)

**注意点**: Constraints, resource management, common mistakes
- Omit this section if nothing applies

参照: Only sections actually cited in the answer (file.json:sN format, omit category path)

**Rules**:
- Base the answer only on the knowledge sections. Do not fill gaps with inference.
- General Java/programming knowledge (try-catch, Bean, getter/setter, etc.) may be used.
- Stay within 500 tokens (up to 800 for complex questions).
- If hearing_answer identified a processing type, choose the approach matching that type.
- For gaps in section content, state explicitly: "この情報は知識ファイルの対象範囲外です". Do not infer.

Save as `answer_text`.

---

## Step 6: Verify answer

Check that all Nablarch-specific claims in `answer_text` are supported by `sections_content`.

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

If any claim is unsupported, set `verify_result = FAIL` and record `issues` (list of unsupported claims). Otherwise `verify_result = PASS`.

---

## Step 7: Handle verify result

**If PASS**: Set `final_answer = answer_text`.

**If FAIL**: Re-run Step 5 once with the additional constraint: do not include any of the `issues` claims in the answer. Save the result as `final_answer`.

---

## Step 8: Output

Output `final_answer` to the user.

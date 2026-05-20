# QA Workflow

Question-answering workflow. Searches Nablarch knowledge and responds in Japanese.

## Input

User's question (natural Japanese text)

## Output

Answer in Japanese (Markdown)

---

## Step 1: Classify question — skip or ask?

Read the user's question and determine whether the processing type can be identified without asking.

**Step A: Scan for explicit keywords**

Check whether the question contains any keyword from the lists below verbatim. Do not infer from business context — only match listed keywords exactly.

Group 1 (official names or abbreviations of processing types):
- ウェブアプリケーション, Webアプリ, Web画面
- RESTfulウェブサービス, REST API, RESTful, REST
- Nablarchバッチ, バッチアプリケーション (only in the form "Nablarchバッチ" or "バッチアプリ")
- Jakartaバッチ
- テーブルをキューとして使ったメッセージング
- HTTPメッセージング
- MOMメッセージング

Group 2 (technical terms that exist in exactly one processing type):
- JSP, HIDDENストア, セッション変数, セッションストア, CSRF → ウェブアプリケーション
- リソースクラス, JAX-RS → RESTfulウェブサービス
- requestPath (in the context of a batch startup argument) → Nablarchバッチ
- ItemReader, ItemWriter, Chunk → Jakartaバッチ

**Step B: Match**
- Keyword found → points to exactly one processing type → **skip** (that processing type)
- Keyword found → points to multiple processing types → **ask**
- No keyword found → proceed to Step C

**Step C: Cross-functional check**

Check whether the question topic is one of the following cross-functional features:
- Testing framework
- Internationalization (i18n)
- Logging configuration
- Common utilities (date/time, code value management, etc.)

If yes → **skip** (processing_type = null)

Note: Common concepts (transactions, validation, DB access, SQL, etc.) are NOT cross-functional if their configuration/implementation differs per processing type.

**Step D: Default**

If neither Step B nor Step C produced "skip" → **ask**

**Step E: Infer purpose**

Always infer `purpose` from the question (never ask the user). Select one from the 7 fixed categories:

1. 実装したい
2. 仕組み・動作を理解したい
3. 不具合・エラーを調査したい
4. テストを書きたい
5. バージョンアップしたい
6. 実装パターン・サンプルを参考にしたい
7. セキュリティ対応したい

Signal keywords:
- 「仕組み」「とは」「動作」「理解」「概要」→ 仕組み・動作を理解したい
- 「エラー」「例外」「不具合」「原因」「調査」→ 不具合・エラーを調査したい
- 「テスト」「テストコード」「テストケース」→ テストを書きたい
- 「バージョンアップ」「移行」「マイグレーション」「アップグレード」→ バージョンアップしたい
- 「サンプル」「パターン」「例を見たい」「参考」→ 実装パターン・サンプルを参考にしたい
- 「セキュリティ」「脆弱性」「認証」「認可」→ セキュリティ対応したい
- (no signal matches) → **実装したい** (default)

Build `hearing_answer`:
- skip: `{ "processing_type": "<type from the list above, or null>", "purpose": "<one of the 7 categories>" }`
  - processing_type: null for cross-functional
- ask: `hearing_answer = null` (purpose will be set in Step 2)

---

## Step 2: Ask user if needed

**If skip**: Use `hearing_answer` from Step 1. Proceed to Step 3.

**If ask**: Use AskUserQuestion:
- Question: "どの処理方式で実装しますか？"
- Options:
  - ウェブアプリケーション
  - RESTfulウェブサービス
  - Nablarchバッチ
  - Jakartaバッチ
  - テーブルをキューとして使ったメッセージング
  - HTTPメッセージング
  - MOMメッセージング

Then build `hearing_answer` from the user's selection:
1. Use the selected processing type as `processing_type`.
2. Infer `purpose` from the original question using the same signal keywords from Step 1E (default: 実装したい).

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

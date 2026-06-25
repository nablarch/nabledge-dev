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

Judge which processing type the question belongs to. Use the names and technical terms below as reference:

Processing types:
- ウェブアプリケーション
- RESTfulウェブサービス
- Nablarchバッチ
- Jakartaバッチ
- テーブルをキューとして使ったメッセージング
- HTTPメッセージング
- MOMメッセージング

Judgment:
- Question clearly belongs to one processing type → `processing_type = <that type>`
- Question is cross-functional (testing framework, i18n, logging, common utilities) → `processing_type = null`
- Otherwise → `processing_type = UNCLEAR`

Note: Common concepts (transactions, validation, DB access, SQL) are NOT cross-functional if their configuration/implementation differs per processing type.

### Determine purpose

Judge the purpose from the question. Reference categories:

Purpose categories:
- 実装したい
- 仕組み・動作を理解したい
- 不具合・エラーを調査したい
- テストを書きたい
- バージョンアップしたい
- セキュリティ対応したい

- Purpose is clear from the question → `purpose = <that category>`
- Cannot determine from the question → `purpose = UNCLEAR`

### Result

If both `processing_type` and `purpose` are determined (not UNCLEAR) → proceed to Step 3.

If either is UNCLEAR → proceed to Step 2.

---

## Step 2: Ask user if needed

If both `processing_type` and `purpose` are already determined in Step 1, skip to the build step below.

Otherwise, ask only about what is UNCLEAR.

**If both processing_type and purpose are UNCLEAR**, output both questions together in one message:

```
いくつか確認させてください。

どの処理方式の質問ですか？
1. ウェブアプリケーション
2. RESTfulウェブサービス
3. Nablarchバッチ
4. Jakartaバッチ
5. テーブルをキューとして使ったメッセージング
6. HTTPメッセージング
7. MOMメッセージング
8. その他（処理方式に依存しない）

質問の目的は？
1. 実装したい
2. 仕組み・動作を理解したい
3. 不具合・エラーを調査したい
4. テストを書きたい
5. バージョンアップしたい
6. セキュリティ対応したい
7. その他
```

**If only processing_type is UNCLEAR**, output:

```
どの処理方式の質問ですか？

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
質問の目的は？

1. 実装したい
2. 仕組み・動作を理解したい
3. 不具合・エラーを調査したい
4. テストを書きたい
5. バージョンアップしたい
6. セキュリティ対応したい
7. その他
```

Wait for the user's response. Then set:
- `processing_type`: from Step 1 or user's selection (「その他」or 8 → null)
- `purpose`: from Step 1 or user's selection (「その他」or 8 → 実装したい)

Proceed to Step 3.

---

## Step 3: BM25 pre-search

Attempt a fast BM25-ranked search before semantic search. If BM25 returns a verified answer, skip semantic search entirely.

### Step 3-1: Extract BM25-effective terms

From the user's question, extract terms that will **narrow the result set** in BM25 search — terms specific enough to appear in only a small number of knowledge files.

**Criterion**: Extract a term if it is a concrete identifier (class name, annotation name, method name, configuration file name, SQL ID, component name) that appears verbatim in the Nablarch knowledge base. The test is: "Would a keyword match on this term return a small, focused set of pages?"

**Source rule**: Take terms **as they appear in the question** — do not infer synonyms, related terms, or paraphrases. The only permitted modification is correcting an obvious typo or misspelling (e.g. `UniversalDoa` → `UniversalDao`) so the term matches the knowledge base.

**Extract** (concrete identifiers, low document frequency):
`UniversalDao`, `@InjectForm`, `batchUpdate`, `SqlPStatement`, `web-component-configuration.xml`, `SQLID`, `RoutesMapping`, `BatchAction`, etc.

**Do NOT extract** (broad terms, high document frequency — would match too many pages and dilute scores):
- Abstract concepts: `バリデーション`, `トランザクション`, `Handler`, `Action`
- General Java: `List`, `String`, `try-catch`, `Exception`
- Natural language filler: `使い方`, `方法`, `について`
- Do NOT add synonyms, related identifiers, or guessed class names not present in the question.

Save the extracted terms as `bm25_terms` (list of strings).

**If `bm25_terms` is empty** (no narrow-enough terms found), skip immediately to Step 4 (semantic search).

---

### Step 3-2: BM25 search

Execute the BM25 search script with the extracted terms:

```bash
bash scripts/bm25-search.sh <term1> [term2] ...
```

Replace `<term1>`, `[term2]` etc. with the terms from `bm25_terms`.

The script outputs a JSON array. Each element is a section hit with a BM25 score:

```json
[
  {
    "file": "component/libraries/universal-dao.json",
    "section_id": "s3",
    "section_title": "batchUpdateメソッドの使い方",
    "score": 12.45
  },
  ...
]
```

**If the output array is empty** (`[]`), set `bm25_sections = []` and skip to Step 4 (semantic search).

**If the script exits non-zero** for any reason (index build failure, missing dependency, unexpected error), treat the result as empty and skip to Step 4 (semantic search).

Otherwise, save the array as `bm25_raw`. Take the top 20 entries by score.

Convert to the `selected_sections` format:

```json
[
  {"file": "component/libraries/universal-dao.json", "section_id": "s3", "relevance": "high"}
]
```

Save as `bm25_sections`.

---

### Step 3-3: Read section content

From `bm25_sections`, build the argument list: for each section, `"{file}:{section_id}"`.

```bash
bash scripts/read-sections.sh "file1.json:s1" "file2.json:s3" ...
```

Save the output as `bm25_content`.

**If `bm25_content` is empty or contains only `FILE_NOT_FOUND` / `SECTION_NOT_FOUND` entries**, skip to Step 4 (semantic search).

---

### Step 3-4: Generate answer from BM25 hits

Generate the answer using **exactly the same format, constraints, and rules as Step 6** (answer generation). Substitute `bm25_content` for `sections_content`. Save as `bm25_answer_text`.

- If `processing_type` is not null, focus on approaches that match that type.
- For any gap in the sections, write "この情報は知識ファイルの対象範囲外です" — do not infer.

---

### Step 3-5: Verify BM25 answer

Apply the same verification procedure as Step 7 (hallucination check), using `bm25_answer_text` as the answer and `bm25_content` as the sections.

Check that all Nablarch-specific claims in `bm25_answer_text` are supported by `bm25_content`. Use the same claim categories and boundary rules as Step 7.

If any claim is unsupported, set `bm25_verify = FAIL`. Otherwise set `bm25_verify = PASS`.

---

### Step 3-6: Handle BM25 verify result

**If `bm25_verify = PASS`**:

Set `final_answer = bm25_answer_text`.

Skip Steps 4–8. Go directly to Step 9 (Output).

**If `bm25_verify = FAIL`**:

Discard `bm25_answer_text`. Proceed to Step 4 (semantic search) with no modifications.

---

## Step 4: Semantic search

Execute `workflows/semantic-search.md` with:
- `{question}` = user's question with hearing result appended:
  - If `processing_type` is not null: `"{user's question}（処理方式: {processing_type}）（目的: {purpose}）"`
  - If `processing_type` is null: `"{user's question}（目的: {purpose}）"`

Save the returned `selected_sections` array as `selected_sections`.

---

## Step 5: Read section content

From `selected_sections`, select sections to read:
1. All `high` sections first (body sections and Javadoc together)
2. Then `partial` sections to fill remaining slots
3. Maximum 20 entries total, counting body sections and Javadoc together

Build the argument list: for each selected section, `"{file}:{section_id}"`.

```bash
bash scripts/read-sections.sh "file1.json:s1" "file2.json:s3" ...
```

Save the output as `sections_content`.

If `selected_sections` is empty, set `sections_content = ""`.

---

## Step 6: Generate answer

If `sections_content` is empty, output immediately:
```
この情報は知識ファイルに含まれていません。
```
and stop.

Otherwise, generate a Japanese answer following the steps below.

1. Read all sections in `sections_content`.
2. If `processing_type` is not null, focus on approaches that match that type.
3. Identify the information that directly answers the question. For any gap in the sections, write "この情報は知識ファイルの対象範囲外です" — do not infer.
4. Write the answer in the format below. Stay within 500 tokens (up to 800 for complex questions).

**Answer format**:

**結論**: Direct answer to the question (1–2 sentences)
- Include specific method names, class names, and approaches
- Do not parrot back the question

**根拠**: Code examples, configuration examples, or spec information that backs the conclusion
- Show code/config examples in code blocks
- Priority: implementation example > configuration example > API spec > conceptual explanation
- If using multiple sections, organize along the implementation flow
- Quote code examples from sections verbatim (do not modify)

**注意点**: Constraints, resource management, common mistakes
- Omit this section if nothing applies

参照: Only sections actually cited in the answer (file.json:sN format, omit category path)

Note: General Java/programming knowledge (try-catch, Bean, getter/setter, etc.) may be used alongside knowledge sections.

Save as `answer_text`.

---

## Step 7: Verify answer

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

## Step 8: Handle verify result

**If PASS**: Set `final_answer = answer_text`.

**If FAIL**: Re-run Step 6 once with the additional constraint: do not include any of the `issues` claims in the answer. Save the result as `final_answer`.

---

## Step 9: Output

Output `final_answer` to the user.

# Full-Text Search Workflow

BM25 pre-search: attempts a fast keyword-based search and returns either a verified answer or a fallback signal.

## Input

- `{question}`: User's question text.
- `{processing_type}`: Processing type determined in qa.md Step 1 (may be null).

## Output

One of two results:

```json
{"status": "complete", "final_answer": "<answer text>"}
```
BM25 produced a verified answer. The caller should use `final_answer` as-is and skip semantic search.

```json
{"status": "fallback"}
```
BM25 found nothing useful or verification failed. The caller should proceed to semantic search.

---

## Step 1: Extract BM25-effective terms

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

**If `bm25_terms` is empty** (no narrow-enough terms found), return `{"status": "fallback"}` immediately.

---

## Step 2: BM25 search

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

**If the output array is empty** (`[]`), return `{"status": "fallback"}`.

**If the script exits non-zero** for any reason (index build failure, missing dependency, unexpected error), return `{"status": "fallback"}`.

Otherwise, save the array as `bm25_raw`. Take the top 20 entries by score.

Convert to the `selected_sections` format:

```json
[
  {"file": "component/libraries/universal-dao.json", "section_id": "s3", "relevance": "high"}
]
```

Save as `bm25_sections`.

---

## Step 3: Read section content

From `bm25_sections`, build the argument list: for each section, `"{file}:{section_id}"`.

```bash
bash scripts/read-sections.sh "file1.json:s1" "file2.json:s3" ...
```

Save the output as `bm25_content`.

**If `bm25_content` is empty or contains only `FILE_NOT_FOUND` / `SECTION_NOT_FOUND` entries**, return `{"status": "fallback"}`.

---

## Step 4: Generate answer from BM25 hits

Generate a Japanese answer from `bm25_content`. Use the same answer format as qa.md Step 6:

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

Additional constraints:
- If `processing_type` is not null, focus on approaches that match that type.
- For any gap in the sections, write "この情報は知識ファイルの対象範囲外です" — do not infer.
- Stay within 500 tokens (up to 800 for complex questions).

Save as `bm25_answer_text`.

---

## Step 5: Verify BM25 answer

Check that all Nablarch-specific claims in `bm25_answer_text` are supported by `bm25_content`.

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

If any claim is unsupported, set `bm25_verify = FAIL`. Otherwise set `bm25_verify = PASS`.

---

## Step 6: Handle verify result

**If `bm25_verify = PASS`**:

Return `{"status": "complete", "final_answer": "<bm25_answer_text>"}`.

**If `bm25_verify = FAIL`**:

Return `{"status": "fallback"}`.

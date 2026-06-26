# Full-Text Search Workflow

BM25 keyword search. Returns matching sections.

## Input

- `{question}`: User's question text.

## Output

```json
{"selected_sections": [...]}
```

or

```json
{"selected_sections": []}
```

Empty array when no BM25 terms found, script returns no hits, or script exits non-zero.

---

## Step 1: Extract BM25 search terms using page title lookup

Read the FTS hints file to get the current page title list:

```bash
cat scripts/fts-hints.md
```

Use this list as a translation table to map the question's concepts to Nablarch-specific terms.

**Process**:

1. Read the question and identify its topic (e.g., "バリデーション", "セッション", "DB操作", "ファイル入出力").
2. Scan the page title list and find titles whose terms relate to that topic.
3. From the matching titles, extract BM25 search terms:
   - Use hyphen-separated parts of the title (e.g., `libraries-bean-validation` → `bean-validation`)
   - Or the full filename (e.g., `handlers-SessionStoreHandler` → `SessionStoreHandler`)
4. Also include any concrete identifiers that appear **verbatim** in the question (class name, annotation, method name, configuration file name).

**Do NOT extract** broad words from the question:
- Abstract concepts: `バリデーション`, `トランザクション`, `ハンドラ`, `データ変換`
- General Java terms: `List`, `String`, `Exception`, `try-catch`
- Natural language filler: `使い方`, `方法`, `について`, `実装`

**Examples**:

| Question | Matching titles | BM25 terms to use |
|---|---|---|
| RESTのバリデーション実装を教えて | `libraries-bean-validation`, `handlers-jaxrs-bean-validation-handler` | `bean-validation`, `jaxrs-bean-validation` |
| セッションのストア選択基準を知りたい | `libraries-session-store`, `handlers-SessionStoreHandler` | `session-store`, `SessionStoreHandler` |
| UniversalDaoで検索する方法 | `libraries-universal-dao` (and verbatim: `UniversalDao`) | `universal-dao`, `UniversalDao` |
| ファイル入出力の実装方法 | `libraries-data-format`, `libraries-data-bind`, `libraries-data-io-functional-comparison` | `data-format`, `data-bind` |

Save the extracted terms as `bm25_terms` (list of strings).

**If `bm25_terms` is empty** (no relevant titles found and no verbatim identifiers in the question), return `{"selected_sections": []}` immediately.

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

**If the output array is empty** (`[]`), return `{"selected_sections": []}`.

**If the script exits non-zero** for any reason (index build failure, missing dependency, unexpected error), return `{"selected_sections": []}`.

Otherwise, save the array as `bm25_raw`. Take the top 20 entries by score.

Convert to the `selected_sections` format:

```json
[
  {"file": "component/libraries/universal-dao.json", "section_id": "s3", "relevance": "high"}
]
```

All BM25 hits use `"relevance": "high"`.

Return:

```json
{"selected_sections": [...]}
```

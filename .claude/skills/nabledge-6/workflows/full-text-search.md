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

**If `bm25_terms` is empty** (no narrow-enough terms found), return `{"selected_sections": []}` immediately.

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

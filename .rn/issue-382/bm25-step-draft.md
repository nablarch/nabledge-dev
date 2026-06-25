# BM25 Pre-Search — Research & Draft

## Section 1: Library Comparison

| Library | License | Latest version | Last release | Python min | Install size (approx) | Notes |
|---------|---------|---------------|--------------|------------|----------------------|-------|
| **rank-bm25** | Apache 2.0 | 0.2.2 | Feb 2022 | unspecified (py3) | ~8.5 KB + numpy | Pure Python + numpy. No index persistence — re-indexes on every call. Maintainer's own README flags it as unsuitable for large-scale use. ~2 QPS. Effectively unmaintained (4+ years). |
| **bm25s** | MIT | 0.3.9 | May 2026 | Python 3.8 | ~100 KB + numpy | Pure Python + numpy sparse matrices. Supports index save/load (build once, reload fast). Memory-mapped loading available. ~573 QPS. Actively maintained with multiple 2026 releases. |
| **Whoosh** | BSD 2-clause | 2.7.4 | Apr 2016 | unspecified | ~468 KB, no deps | Pure Python, zero dependencies. Last release 2016 (10 years); Python 3.12+ compatibility uncertain. Requires an on-disk index directory. Effectively a dead project. |

### Recommendation: **bm25s**

bm25s is the only actively maintained library of the three (multiple releases in 2026), and its index save/load feature is critical for on-demand bash-script invocation over ~50,000–200,000 sections — build the index once on first run, reload it in milliseconds on subsequent calls. Its sole mandatory dependency is numpy, which is already present in most Python environments used by nabledge's target users.

---

## Section 1b: Index Lifecycle

**When the index is built**: On first invocation of `bm25-search.sh`, the script builds the BM25 index from `knowledge/*.json` and saves it to a fixed path (e.g. `scripts/.bm25-index/`). Subsequent calls reload the saved index without rebuilding.

**When to rebuild**: After `rbkc.sh create` regenerates the knowledge files, the index becomes stale. The script detects staleness by comparing the index mtime to the newest JSON mtime and rebuilds automatically — no manual intervention is needed.

**User setup impact**: `pip install bm25s` must be added to the skill's setup script (`tools/setup/setup-6-cc.sh` and equivalent files for other versions). No additional manual step is needed at query time; index management is handled entirely by `bm25-search.sh`.

---

## Section 2: BM25 Step Draft

> **Renumbering note**: This draft shows only the new BM25 step. The existing Steps 3–8 in `qa.md` will be renumbered to Steps 4–9 during implementation (task #3). Any internal cross-references within those existing steps (e.g. "go to Step 3", "Step 7") will be updated at that time.

The following step is intended to be inserted into `qa.md` **between Step 2 (hear processing_type/purpose) and the current Step 3 (semantic search)**. The current Step 3 through Step 8 numbering shifts by one after insertion; this draft uses the new numbering (Step 3 = BM25, Step 4 = former Step 3, …, Step 9 = former Step 8).

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

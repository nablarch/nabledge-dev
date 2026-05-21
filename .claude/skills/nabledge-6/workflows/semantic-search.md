# Semantic Search Workflow

Searches knowledge files and returns relevant sections for the question.

## Input

- `{question}`: User's question.

## Output

Pointer JSON:
```json
{
  "selected_sections": [
    {"file": "processing-pattern/nablarch-batch/page.json", "section_id": "s1", "relevance": "high"},
    {"file": "component/libraries/universal-dao.json", "section_id": "s3", "relevance": "partial"}
  ]
}
```

---

## Step 1: Read index.md

Read `knowledge/index.md` (relative to skill root). Save content as `index_content`.

---

## Step 2: Select pages

Read the question. Identify in one sentence what the user wants to know. If the question contains `（処理方式: X）`, use that as the processing type context.

If the question contains `（目的: X）`, use the following priority categories when ordering pages:

| 目的 | Priority categories |
|------|-------------------|
| 実装したい | processing-pattern/*, component/libraries |
| 仕組み・動作を理解したい | component/handlers, component/libraries, about/about-nablarch |
| 不具合・エラーを調査したい | component/handlers, component/libraries, processing-pattern/* |
| テストを書きたい | development-tools/testing-framework, component/libraries |
| バージョンアップしたい | about/migration, releases/releases, about/release-notes |
| 実装パターン・サンプルを参考にしたい | guide/nablarch-patterns, guide/biz-samples, processing-pattern/* |
| セキュリティ対応したい | check/security-check, component/handlers, processing-pattern/* |

For each page in the index, judge whether it contains information needed to answer the question:
- Select pages that directly correspond to the question's operation target
- Select pages for features that solve the question's technical problem
- Select pages for the processing type in the question
- Do NOT select pages for a different processing type than the question

When ordering selected pages, place pages in priority categories first.

Select up to 10 pages, ordered by confidence (highest first). If more than 10 candidates exist, select the 10 most direct matches. If fewer than 3 high-confidence pages exist, do not pad to 10.

If no pages match, return `{"selected_sections": []}` immediately.

Save the selected page paths (relative to knowledge/) as `selected_pages`.

---

## Step 3: Select sections

For each path in `selected_pages` (up to 10):
1. Read `knowledge/{path}`
2. For each section, judge relevance:
   - **high**: Information in this section is required to answer the question (e.g., section directly corresponding to the question's operation target, section containing the implementation method that solves the technical problem)
   - **partial**: Supplements information missing from high sections — background knowledge or related configuration needed when implementing the high section's content
   - **out of scope**: Neither of the above

Select all high sections first, then fill remaining slots (up to 30 total) with partial sections.

Do NOT include as partial:
- Information already inferable from high section content
- Concept definitions only, with no implementation details
- Content that just explains the same information as a high section from a different angle

Do NOT select:
- Sections with only general overview and no specific information
- Module lists, revision histories, and other boilerplate

Return:
```json
{
  "selected_sections": [
    {"file": "<path relative to knowledge/>", "section_id": "sN", "relevance": "high|partial"}
  ]
}
```

Results sorted by relevance descending (high → partial).

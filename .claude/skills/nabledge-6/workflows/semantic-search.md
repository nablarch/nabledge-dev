# Semantic Search Workflow

2-stage semantic search: Stage 1 selects pages from index.md, Stage 2 selects sections from knowledge JSONs.

## Input

- `{question}`: User's question. May contain hearing result appended as `（処理方式: X）（目的: Y）`.

## Output

Pointer JSON:
```json
{
  "results": [
    {"file": "processing-pattern/nablarch-batch/page.json", "section_id": "s1", "relevance": "high"},
    {"file": "component/libraries/universal-dao.json", "section_id": "s3", "relevance": "partial"}
  ]
}
```

---

## Step 1: Read index.md

Read `knowledge/index.md` (relative to skill root). Save content as `index_content`.

---

## Step 2: Stage 1 — Page selection

Read the question. Identify in one sentence what the user wants to know. If the question contains `（処理方式: X）`, use that as the processing type context.

For each page in the index, judge whether it contains information needed to answer the question:
- Select pages that directly correspond to the question's operation target
- Select pages for features that solve the question's technical problem
- Select pages for the processing type in the question
- Do NOT select pages for a different processing type than the question

Select up to 10 pages, ordered by confidence (highest first). If more than 10 candidates exist, select the 10 most direct matches. If fewer than 3 high-confidence pages exist, do not pad to 10.

If no pages match, return `{"results": []}` immediately.

Save the selected page paths (relative to knowledge/) as `selected_pages`.

---

## Step 3: Stage 2 — Section selection

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
  "results": [
    {"file": "<path relative to knowledge/>", "section_id": "sN", "relevance": "high|partial"}
  ]
}
```

Results sorted by relevance descending (high → partial).

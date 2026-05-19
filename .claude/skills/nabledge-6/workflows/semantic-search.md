# Semantic Search Workflow

2-stage semantic search: Stage 1 selects pages from index.md, Stage 2 selects sections from knowledge JSONs.

## Input

- `{question}`: User's question
- `{hearing_answer}`: Formatted hearing result ("処理方式: X\nやりたいこと: Y") or "なし"

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

## Steps

### Step 1: Read index.md

**Tool**: Read

Read `knowledge/index.md` (relative to skill root).

Save content as `index_content`.

### Step 2: Stage 1 — Page selection

**Tool**: In-memory (LLM generation)

Call LLM with the following prompt, substituting the variables:

---
You are a knowledge base search system. Select the pages (knowledge files) from the index that contain information needed to answer the user's question.

**Question**: {question}

**Hearing answer**: {hearing_answer}

**Index**:
```
{index_content}
```

Steps:
1. Read the question and hearing answer. Identify in one sentence what the user wants to know.
2. Read each page's title and section list in the index to find pages that contain information needed to answer the question.
3. Narrow down candidates by these criteria:
   - Select pages that directly correspond to the question's operation target
   - Select pages for features that solve the question's technical problem
   - Select pages for the processing type needed by the question's context (e.g., REST API question → RESTful web service pages)
   - Select pages related to the processing type identified in the hearing answer
4. Select up to 10 pages, ordered by confidence (highest first).
5. If more than 10 candidates exist, analyze the cause and select the 10 most direct matches.
6. If fewer than 3 high-confidence pages exist, do not pad to 10. Note this in `trace.low_confidence_note` (one sentence explaining why matches are limited).

Do NOT select:
- Pages related to but not directly addressing the question
- Pages for a different processing type than the question (e.g., web UI pages for a REST API question)

Output JSON with a `files` array (each entry: `path`, `reason`) and a `trace` field:
- `trace.user_intent`: the user's intent identified in step 1 (one sentence)
- `trace.excluded`: pages considered but not selected (only pages actually considered; each entry: `path`, `reason`)
---

Parse the JSON response. Extract the `files` array — each entry has:
- `path`: path relative to knowledge directory (e.g., `processing-pattern/nablarch-batch/page.json`)
- `reason`: selection rationale

If `files` is empty, return `{"results": []}` immediately.

### Step 3: Stage 2 — Section selection

**Tool**: In-memory (LLM generation)

For each path in the Stage 1 `files` array (up to 10):
1. Prepend `knowledge/` to the path to get the file path relative to skill root (e.g., `knowledge/processing-pattern/nablarch-batch/page.json`)
2. Read the knowledge JSON file using the Read tool
3. Format the file content as:
   ```
   ## {path}
   タイトル: {data.title}

   ### {section.id}: {section.title}

   {section.content}

   (repeat for all sections in the file)
   ```

Concatenate all formatted file contents as `{files_content}`.

Call LLM with the following prompt, substituting the variables:

---
You are a knowledge base search system. Read the full text of candidate pages and select sections relevant to the user's question.

**Question**: {question}

**Hearing answer**: {hearing_answer}

**Candidate page contents**:
{files_content}

Steps:
1. Read the body of each section in each page.
2. Judge each section's relevance by these criteria:
   - **high**: Information in this section is required to answer the question (e.g., section directly corresponding to the question's operation target, section containing implementation method that solves the technical problem)
   - **partial**: Supplements information missing from high sections. Background knowledge or related configuration needed when implementing the high section's content.
   - **out of scope**: Neither of the above
3. Select all high sections first.
4. Fill remaining slots (30 − high count) with partial sections.
5. Maximum 30 sections total.

Do NOT include as partial:
- Information already inferable from high section content
- Concept definitions only, with no implementation details
- Content that just explains the same information as a high section from a different angle

Do NOT select:
- Sections with only general overview and no specific information
- Module lists, revision histories, and other boilerplate
- Sections related to but not directly addressing the question

Output JSON with a `results` array and a `trace` field:
- Each result entry: `file` (path relative to knowledge/), `section_id`, `relevance` ("high"/"partial"), `reason` (one line)
- Sort results by relevance descending (high → partial)
- `trace.excluded`: sections considered but not selected (sections with some relevance to the question that did not meet high/partial criteria; each entry: `file`, `section_id`, `reason`)
- Omit clearly irrelevant sections (module lists, revision histories, topics completely unrelated to the question) from trace.excluded
- If no matching sections exist, set results to an empty array
---

Parse the JSON response. Extract the `results` array — each entry has:
- `file`: knowledge JSON path relative to knowledge/ (e.g., `processing-pattern/nablarch-batch/page.json`)
- `section_id`: section identifier (e.g., `s1`)
- `relevance`: `"high"` or `"partial"`

### Step 4: Return pointer JSON

Return:
```json
{
  "results": [/* results array from Step 3 */]
}
```

Results are already sorted by relevance descending (high → partial) by Stage 2.

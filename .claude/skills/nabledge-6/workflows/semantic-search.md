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

**Tool**: Read + In-memory (LLM generation)

Read `assets/semantic-search-stage1.md`.

Replace the following variables in the prompt text and call LLM to generate a response:
- `{question}` → the input question
- `{hearing_answer}` → the hearing result string
- `{index_content}` → full content of index.md from Step 1

Parse the JSON response. Extract the `files` array — each entry has:
- `path`: path relative to knowledge directory (e.g., `processing-pattern/nablarch-batch/page.json`)
- `reason`: selection rationale

If `files` is empty, return `{"results": []}` immediately.

### Step 3: Stage 2 — Section selection

**Tool**: Read + In-memory (LLM generation)

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

Read `assets/semantic-search-stage2.md`.

Replace the following variables and call LLM:
- `{question}` → the input question
- `{hearing_answer}` → the hearing result string
- `{files_content}` → the concatenated file contents from above

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

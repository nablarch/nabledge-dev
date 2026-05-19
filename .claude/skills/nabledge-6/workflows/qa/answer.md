# Answer Generation Workflow

Generates a Japanese answer from the search results.

## Input

- `{question}`: User's question
- `{hearing_answer_str}`: Formatted hearing result string
- `{pointer_json}`: Combined pointer JSON from semantic + keyword search

## Output

Answer text in Japanese (Markdown)

## Steps

### Step 1: Read section content

**Tool**: Bash

From `{pointer_json}.results`, select sections to read in this order:
1. All `"high"` relevance sections first
2. Then `"partial"` relevance sections to fill remaining slots
3. Maximum: 10 sections total

Build the argument list: for each selected result, `"{file}:{section_id}"`.

Run:
```bash
bash scripts/read-sections.sh "file1.json:s1" "file2.json:s3" ...
```

Save the output as `sections_content`.

If no results exist, skip to Step 3.

### Step 2: Generate answer

**Tool**: Read + In-memory (LLM generation)

Read `workflows/qa/answer-prompt.md`.

Replace the following variables and call LLM:
- `{question}` → the user's question
- `{hearing_answer}` → `{hearing_answer_str}`
- `{sections_content}` → output from Step 1

Parse the JSON response. Extract `answer` field (Markdown text).

### Step 3: Return answer

If no sections were found in Step 1, return:
```
この情報は知識ファイルに含まれていません。
```

Otherwise, return the `answer` text from Step 2.

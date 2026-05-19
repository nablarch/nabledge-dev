# QA Workflow

Question-answering workflow. Searches Nablarch knowledge and responds in Japanese.

## Input

User's question (natural Japanese text)

## Output

Answer in Japanese (Markdown)

## Steps

### Step 1: Hearing

**Tool**: workflows/qa/hearing.md

Execute `workflows/qa/hearing.md` with the user's question.

This workflow:
- Classifies whether hearing is needed
- Asks the user if needed (via AskUserQuestion)
- Returns `hearing_answer_str` (formatted string for downstream use)

Save the formatted hearing string as `hearing_answer_str`.

### Step 2: Semantic search

**Tool**: workflows/semantic-search.md

Execute `workflows/semantic-search.md` with:
- `{question}` = user's question
- `{hearing_answer}` = `hearing_answer_str`

Save as `semantic_results` (pointer JSON).

### Step 3: Read section content

**Tool**: Bash

From `semantic_results.results`, select sections to read:
1. All `"high"` relevance sections first
2. Then `"partial"` relevance sections to fill remaining slots
3. Maximum: 10 sections total

Build the argument list: for each selected result, `"{file}:{section_id}"`.

Run:
```bash
bash scripts/read-sections.sh "file1.json:s1" "file2.json:s3" ...
```

Save the output as `sections_content`.

If no results exist, set `sections_content = ""`.

### Step 4: Generate answer

**Tool**: workflows/qa/answer.md

Execute `workflows/qa/answer.md` with:
- `{question}` = user's question
- `{hearing_answer}` = `hearing_answer_str`
- `{sections_content}` = `sections_content`

Save result as `answer_text`.

### Step 5: Verify answer

**Tool**: workflows/qa/verify.md

Execute `workflows/qa/verify.md` with:
- `{answer}` = `answer_text`
- `{sections_content}` = `sections_content`

Save result as `verify_result` (JSON with `result`, `claims`, `issues`).

### Step 6: Handle verify result

**If `verify_result.result == "PASS"`**:
- Set `final_answer` = `answer_text`

**If `verify_result.result == "FAIL"`**:
- Re-execute `workflows/qa/answer.md` with (once only):
  - `{question}` = user's question
  - `{hearing_answer}` = `hearing_answer_str`
  - `{sections_content}` = `sections_content`
  - `{exclusions}` = `verify_result.issues` (list of unsupported claims to avoid)
- Save result as `final_answer`

### Step 7: Output

Output `final_answer` to the user.

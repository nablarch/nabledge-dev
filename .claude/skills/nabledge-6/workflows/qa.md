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

### Step 3: Generate answer

**Tool**: workflows/qa/answer.md

Execute `workflows/qa/answer.md` with:
- `{question}` = user's question
- `{hearing_answer_str}` = hearing result string
- `{pointer_json}` = `semantic_results`

Save result as `answer_text`.

### Step 4: Verify answer

**Tool**: workflows/qa/verify.md

Execute `workflows/qa/verify.md` with:
- `{answer}` = `answer_text`
- `{pointer_json}` = `semantic_results`

Save result as `verify_result` (JSON with `result`, `claims`, `issues`).

### Step 5: Handle verify result

**If `verify_result.result == "PASS"`**:
- Set `final_answer` = `answer_text`

**If `verify_result.result == "FAIL"`**:
- Re-execute `workflows/qa/answer.md` with:
  - `{question}` = user's question
  - `{hearing_answer_str}` = hearing result string
  - `{pointer_json}` = `semantic_results`
  - `{exclusions}` = `verify_result.issues` (list of unsupported claims to avoid)
- Save result as `final_answer`

### Step 6: Output

Output `final_answer` to the user.

# QA Workflow

Question-answering workflow. Searches Nablarch knowledge and responds in Japanese.

## Input

User's question (natural Japanese text)

## Output

Answer in Japanese (Markdown)

## Steps

### Step 0: Check for pre-supplied hearing context

Check whether the prompt contains a `## コンテキスト（ヒアリング結果）` section (supplied by the caller).

**If present**:
- Extract `処理方式:` and `目的:` values from that section
- If `処理方式:` is absent, empty, or `None`, set `hearing_answer_str` = `"やりたいこと: {goal}"`
- Otherwise set `hearing_answer_str` = `"処理方式: {processing_type}\nやりたいこと: {goal}"`
- Set `hearing_status` = `"skipped"`, `hearing_questions` = `[]`
- Skip Step 1 and proceed to Step 2

**If not present**:
- Proceed to Step 1

### Step 1: Hearing

**Tool**: workflows/qa/hearing.md

Execute `workflows/qa/hearing.md` with the user's question.

This workflow:
- Classifies whether hearing is needed
- Asks the user if needed (via AskUserQuestion)
- Returns hearing result including `status` (`"skipped"` or `"asked"`) and `questions` (list of asked question strings)

Save the formatted hearing string as `hearing_answer_str`.
Save `hearing_result.status` as `hearing_status` and `hearing_result.questions` as `hearing_questions`.

### Step 2: Semantic search

**Tool**: workflows/semantic-search.md

Execute `workflows/semantic-search.md` with:
- `{question}` = user's question
- `{hearing_answer}` = `hearing_answer_str`

Save as `semantic_results` (pointer JSON).

### Step 3: Keyword search

**Tool**: workflows/keyword-search.md

Execute `workflows/keyword-search.md` with:
- `{question}` = user's question
- `{hearing_answer}` = `hearing_answer_str`

Save as `keyword_results` (pointer JSON).

### Step 4: Merge results

Combine `semantic_results.results` and `keyword_results.results`:
1. Concatenate the two result lists
2. Deduplicate by `(file, section_id)` — when duplicated, keep the entry with higher relevance (`"high"` beats `"partial"`)
3. Sort: `"high"` entries first, then `"partial"`

Save as `merged_pointer_json`.

### Step 5: Generate answer

**Tool**: workflows/qa/answer.md

Execute `workflows/qa/answer.md` with:
- `{question}` = user's question
- `{hearing_answer_str}` = hearing result string
- `{pointer_json}` = `merged_pointer_json`

Save result as `answer_text`.

### Step 6: Verify answer

**Tool**: workflows/qa/verify.md

Execute `workflows/qa/verify.md` with:
- `{answer}` = `answer_text`
- `{pointer_json}` = `merged_pointer_json`

Save result as `final_answer`.

### Step 7: Output

Output `final_answer` to the user.

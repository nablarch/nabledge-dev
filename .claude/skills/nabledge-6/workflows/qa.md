# QA Workflow

Question-answering workflow. Searches Nablarch knowledge and responds in Japanese.

## Input

User's question (natural Japanese text)

## Output

Answer in Japanese (Markdown)

And benchmark markers (required when running in benchmark mode):
```
<<<BENCHMARK_HEARING>>>
{"status": "skipped" or "asked", "questions": [...]}
<<<END_BENCHMARK_HEARING>>>

<<<BENCHMARK_SEARCH>>>
{"section_ids": ["file.json:s1", ...]}
<<<END_BENCHMARK_SEARCH>>>

<<<BENCHMARK_ANSWER>>>
[answer text]
<<<END_BENCHMARK_ANSWER>>>
```

## Steps

### Step 0: Detect pre-injected hearing context

Check whether the prompt contains a `## コンテキスト（ヒアリング結果）` section.

**If present (benchmark runner pre-injection)**:
- Extract `処理方式:` and `目的:` values from that section
- If processing type is empty or the literal string `None`, set `hearing_answer_str` = `"やりたいこと: {goal}"`
- Otherwise set `hearing_answer_str` = `"処理方式: {processing_type}\nやりたいこと: {goal}"`
- Output benchmark hearing marker now:
  ```
  <<<BENCHMARK_HEARING>>>
  {"status": "skipped", "questions": []}
  <<<END_BENCHMARK_HEARING>>>
  ```
- Skip Step 1 and proceed to Step 2

**If not present (normal user invocation)**:
- Proceed to Step 1

### Step 1: Hearing

**Tool**: workflows/qa/hearing.md

Execute `workflows/qa/hearing.md` with the user's question.

This workflow:
- Classifies whether hearing is needed
- Asks the user if needed (via AskUserQuestion)
- Outputs the `<<<BENCHMARK_HEARING>>>` marker
- Returns hearing result

Save the formatted hearing string as `hearing_answer_str`.

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

Output benchmark search marker:
```
<<<BENCHMARK_SEARCH>>>
{"section_ids": ["file.json:s1", "file.json:s3", ...]}
<<<END_BENCHMARK_SEARCH>>>
```

Where `section_ids` is the list of `"file:section_id"` strings from `merged_pointer_json.results`.

If `merged_pointer_json.results` is empty, output `{"section_ids": []}`.

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

Then output benchmark answer marker:
```
<<<BENCHMARK_ANSWER>>>
{final_answer}
<<<END_BENCHMARK_ANSWER>>>
```

# Hearing Workflow

Determines whether to ask the user for their Nablarch processing type or skip based on the question content.

## Input

User's question (natural Japanese text)

## Output

Hearing result:
```json
{
  "classification": "skip",
  "hearing_answer": {
    "processing_type": "Nablarchバッチ",
    "goal": "Nablarchバッチアプリケーションを-requestPathオプションで起動する"
  }
}
```

And benchmark marker output (required):
```
<<<BENCHMARK_HEARING>>>
{"status": "skipped" or "asked", "questions": ["question text"]}
<<<END_BENCHMARK_HEARING>>>
```

## Steps

### Step 1: Extract processing types from index.md

**Tool**: Read

Read `knowledge/index.md`.

Extract all H2 headings of the form `## processing-pattern/{slug}`. Map each slug to a display name:
- `web-application` → ウェブアプリケーション
- `restful-web-service` → RESTfulウェブサービス
- `nablarch-batch` → Nablarchバッチ
- `jakarta-batch` → Jakartaバッチ
- `db-messaging` → テーブルをキューとして使ったメッセージング
- `http-messaging` → HTTPメッセージング
- `mom-messaging` → MOMメッセージング

Format as a bullet list (e.g., `- Nablarchバッチ\n- ウェブアプリケーション`). Save as `processing_types`.

### Step 2: Classify question

**Tool**: Read + In-memory (LLM generation)

Read `assets/hearing-classify.md`.

Replace the following variables and call LLM:
- `{question}` → the user's question
- `{processing_types}` → the formatted list from Step 1

Parse the JSON response. Extract:
- `classification`: `"skip"` or `"ask"`
- `hearing_answer`: object with `processing_type` and `goal`, or null

### Step 3: Ask user if needed

**Branch on classification**:

**If `"skip"`**: Use `hearing_answer` from Step 2 directly. Set `asked_question = null`.

**If `"ask"`**: Use AskUserQuestion to ask the user:
- Question text: "どの処理方式で実装しますか？"
- Options: list of processing types extracted in Step 1 (one option per type)

Read `assets/hearing-extract.md`.

Replace variables and call LLM:
- `{question}` → the user's question
- `{user_response}` → the processing type the user selected

Parse the JSON response. Use `hearing_answer` from the response.

Set `asked_question = "どの処理方式で実装しますか？"`.

### Step 4: Output benchmark marker

Output in this format (substitute values as specified):

```
<<<BENCHMARK_HEARING>>>
{"status": "{STATUS}", "questions": {QUESTIONS}}
<<<END_BENCHMARK_HEARING>>>
```

Where:
- `{STATUS}`: `"skipped"` if classification was `"skip"`, `"asked"` if it was `"ask"`
- `{QUESTIONS}`: `[]` if skipped, `["どの処理方式で実装しますか？"]` if asked

### Step 5: Return hearing result

Return as an in-memory object (passed to the calling workflow):
```json
{
  "classification": "skip" or "ask",
  "hearing_answer": {
    "processing_type": "...",
    "goal": "..."
  }
}
```

Format `hearing_answer` as a string for use in other prompts:
- If `processing_type` is not null: `"処理方式: {processing_type}\nやりたいこと: {goal}"`
- If `processing_type` is null: `"やりたいこと: {goal}"`
- If no hearing was done: `"なし"`

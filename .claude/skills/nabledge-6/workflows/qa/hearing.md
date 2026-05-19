# Hearing Workflow

Determines whether to ask the user for their Nablarch processing type or skip based on the question content.

## Input

User's question (natural Japanese text)

## Output

Formatted hearing answer string for use in downstream prompts:
- If `processing_type` is not null: `"処理方式: {processing_type}\nやりたいこと: {goal}"`
- If `processing_type` is null: `"やりたいこと: {goal}"`

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

**Tool**: In-memory (LLM generation)

Call LLM with the following prompt, substituting the variables:

---
You are a Nablarch knowledge search system. Read the user's question and determine whether the processing type required for the answer can be identified without asking.

**Question**: {question}

**Available processing types**: {processing_types}

Follow these steps:

**Step A: Scan for explicit keywords**

Check whether the question contains any keyword from the lists below verbatim. Do not infer from business context or use cases — only match listed keywords exactly.

Group 1 (official names or abbreviations of processing types):
- ウェブアプリケーション, Webアプリ, Web画面
- RESTfulウェブサービス, REST API, RESTful, REST
- Nablarchバッチ, バッチアプリケーション (only in the form "Nablarchバッチ" or "バッチアプリ")
- Jakartaバッチ
- テーブルをキューとして使ったメッセージング
- HTTPメッセージング
- MOMメッセージング

Group 2 (technical terms that exist in exactly one processing type):
- JSP, HIDDENストア, セッション変数, セッションストア, CSRF → ウェブアプリケーション
- リソースクラス, JAX-RS → RESTfulウェブサービス
- requestPath (in the context of a batch startup argument) → Nablarchバッチ
- ItemReader, ItemWriter, Chunk → Jakartaバッチ

**Step B: Match**
- If a keyword was found:
  - Points to exactly one processing type → **skip** (that processing type)
  - Points to multiple different processing types → **ask**
- If no keyword found → proceed to Step C

**Step C: Cross-functional check**

Check whether the question topic is one of the following cross-functional features:
- Testing framework
- Internationalization (i18n)
- Logging configuration
- Common utilities (date/time, code value management, etc.)

If yes → **skip** (processing_type = null)
If no → **ask**

Note: Common concepts (transactions, validation, DB access, SQL, etc.) are NOT cross-functional if their configuration/implementation differs per processing type.

**Step D: Default**

If neither Step B nor Step C produced "skip" → **ask**

**Build hearing_answer**:
- For skip: extract processing_type (choose from the available list; null for cross-functional) and goal (one sentence verb phrase describing the user's specific objective; use processing-type-specific operation names; do not add information not in the original question)
- For ask: hearing_answer = null

Output JSON:

skip case:
```json
{
  "classification": "skip",
  "hearing_answer": {
    "processing_type": "ウェブアプリケーション",
    "goal": "入力画面のフォームでバリデーションする"
  },
  "trace": {
    "reason": "質問に「Web画面」が明示されている",
    "matched_keywords": ["Web画面"],
    "candidates": []
  }
}
```

ask case:
```json
{
  "classification": "ask",
  "hearing_answer": null,
  "trace": {
    "reason": "入力チェックはWeb/REST APIの両方で異なる実装があるが、質問に処理方式が明示されていない",
    "matched_keywords": [],
    "candidates": ["ウェブアプリケーション", "RESTfulウェブサービス", "Nablarchバッチ", "Jakartaバッチ"]
  }
}
```

cross-functional skip case:
```json
{
  "classification": "skip",
  "hearing_answer": {
    "processing_type": null,
    "goal": "Bean ValidationのFormクラスをテストする"
  },
  "trace": {
    "reason": "テスティングフレームワークは処理方式に依存しない横断的機能",
    "matched_keywords": [],
    "candidates": []
  }
}
```
---

Parse the JSON response. Extract:
- `classification`: `"skip"` or `"ask"`
- `hearing_answer`: object with `processing_type` and `goal`, or null

### Step 3: Ask user if needed

**Branch on classification**:

**If `"skip"`**: Use `hearing_answer` from Step 2 directly. Set `asked_question = null`.

**If `"ask"`**: Use AskUserQuestion to ask the user:
- Question text: "どの処理方式で実装しますか？"
- Options: list of processing types extracted in Step 1 (one option per type)

Call LLM with the following prompt, substituting the variables:

---
You are a Nablarch knowledge search system. Build a hearing_answer from the user's question and their selected processing type.

**Question**: {question}

**User's selected processing type**: {user_response}

Steps:
1. Identify what the user wants to know from the question.
2. Use the selected processing type as processing_type.
3. Concretize the question's key point in the context of that processing type. Write goal as one verb phrase:
   - End with a verb phrase ("〜する", "〜したい", "〜を知りたい")
   - Include processing-type-specific operation names ("画面", "レスポンス", "ジョブ", etc.)
   - Do not add information not present in the original question

Output JSON:
```json
{
  "hearing_answer": {
    "processing_type": "ウェブアプリケーション",
    "goal": "入力画面のフォームでバリデーションする"
  },
  "trace": {
    "user_intent": "入力チェックの実装方法を知りたい",
    "goal_derivation": "「入力チェック」をWeb文脈で「入力画面のフォームでバリデーションする」に具体化"
  }
}
```
---

Parse the JSON response. Use `hearing_answer` from the response.

Set `asked_question = "どの処理方式で実装しますか？"`.

### Step 4: Return hearing result

Return the formatted hearing answer string:
- If `processing_type` is not null: `"処理方式: {processing_type}\nやりたいこと: {goal}"`
- If `processing_type` is null: `"やりたいこと: {goal}"`

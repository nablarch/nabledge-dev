# Answer Generation Workflow

Generates a Japanese answer from the search results.

## Input

- `{question}`: User's question
- `{hearing_answer}`: Formatted hearing result string
- `{sections_content}`: Section content pre-fetched by the caller (qa.md Step 3)
- `{exclusions}` (optional): List of unsupported claims from verify — avoid restating these in the answer

## Output

Answer text in Japanese (Markdown)

## Steps

### Step 1: Generate answer

**Tool**: In-memory (LLM generation)

Call LLM with the following prompt, substituting the variables:

---
You are a Nablarch framework technical support assistant. Answer the question in Japanese based solely on the knowledge sections provided.

**Question**: {question}

**Hearing answer**: {hearing_answer}

**Knowledge sections**: {sections_content}

Steps:
1. Read all knowledge sections.
2. Identify the user's intent from the question and hearing answer.
3. Identify the information in the knowledge sections that directly answers the question.
4. Write a Japanese answer in the answer format below in the `answer` field.
5. Record processing notes in the `trace` format below.

**Answer format**:

**結論**: Direct answer to the question (1–2 sentences)
- Do not parrot back the question
- Include specific method names, class names, and approaches

**根拠**: Code examples, configuration examples, or spec information that backs the conclusion
- Show code/config examples in code blocks
- Priority: implementation example > configuration example > API spec > conceptual explanation
- If using multiple sections, organize along the implementation flow
- Quote code examples from sections verbatim (do not modify)

**注意点**: Constraints, resource management, common mistakes
- Omit this section if nothing applies

参照: Only sections actually cited in the answer (file.json:sN format, omit category path)

**Answer rules**:
- Base the answer only on the knowledge sections. Do not fill gaps with inference.
- General Java/programming knowledge (try-catch, Bean, getter/setter, etc.) may be used.
- Stay within 500 tokens (up to 800 for complex questions).
- If `{exclusions}` is provided, do not include any of those claims in the answer.

**Multiple approaches**: Choose the approach matching the processing type in the hearing answer. If the processing type does not narrow it down, state the most common approach in the conclusion and mention alternatives in the notes.

**Insufficient section content**: Answer as far as possible. For gaps, state explicitly: "この情報は知識ファイルの対象範囲外です". Do not infer.

**trace format** — for each knowledge section record:

Used sections (cited in answer):
- section: section ID (file.json:sN format)
- used: true
- reason: why this section was used (one line; state relation to question)
- extracted: information extracted from section body (verbatim; no paraphrase)
- mapped_to: which part of the answer it was mapped to ("結論", "根拠", or "注意点")

Unused sections (read but not used):
- section: section ID
- used: false
- reason: why not used ("質問と無関係", "使用セクションに同内容あり", etc.)

Output JSON with `answer` and `trace` fields:
- `trace.user_intent`: the user's intent identified from the question and hearing answer (one sentence)
- `trace.sections`: processing record for each section (per trace format above)
---

Parse the JSON response. Extract `answer` field (Markdown text).

### Step 2: Return answer

If `{sections_content}` was empty, return:
```
この情報は知識ファイルに含まれていません。
```

Otherwise, return the `answer` text from Step 1.

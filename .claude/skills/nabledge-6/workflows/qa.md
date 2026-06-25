# QA Workflow

Question-answering workflow. Searches Nablarch knowledge and responds in Japanese.

## Input

User's question (natural Japanese text)

## Output

Answer in Japanese (Markdown)

---

## Step 1

Execute `workflows/hearing.md`:
- `{question}` = user's question

Save result as `processing_type`, `purpose`.

---

## Step 2

Execute `workflows/full-text-search.md`:
- `{question}` = user's question

Save result's `selected_sections` as `bm25_sections`.

---

## Step 3

Execute `workflows/check-answerable.md`:
- `{question}` = user's question
- `{sections}` = bm25_sections

If result is `"OK"`, proceed to Step 5.

If result is `"NG"`, proceed to Step 4.

---

## Step 4

Execute `workflows/semantic-search.md`:
- `{question}` = user's question
- `{processing_type}` = processing_type
- `{purpose}` = purpose

Save result's `selected_sections` as `sem_sections`.

If `sem_sections` is empty, output:
```
この情報は知識ファイルに含まれていません。
```
and stop.

Set `bm25_sections` = `sem_sections` and proceed to Step 5.

---

## Step 5

Execute `workflows/generate-answer.md`:
- `{question}` = user's question
- `{processing_type}` = processing_type
- `{selected_sections}` = bm25_sections

Save result as `answer_text`.

---

## Step 6

Execute `workflows/verify-answer.md`:
- `{question}` = user's question
- `{answer_text}` = answer_text
- `{selected_sections}` = bm25_sections

If result is `"PASS"`, proceed to Step 7.

If result is `"FAIL"`, execute `workflows/generate-answer.md` once more:
- `{question}` = user's question
- `{processing_type}` = processing_type
- `{selected_sections}` = bm25_sections
- `{findings}` = verify result issues

Save the result as `answer_text`. Proceed to Step 7.

---

## Step 7

Output `answer_text`.

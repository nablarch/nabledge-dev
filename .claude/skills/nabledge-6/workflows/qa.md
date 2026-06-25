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

Save `selected_sections` as `bm25_sections`.

---

## Step 3

If `bm25_sections` is empty, skip to Step 5.

Execute `workflows/generate-answer.md`:
- `{question}` = user's question
- `{processing_type}` = processing_type
- `{selected_sections}` = bm25_sections

Save result as `answer_text`.

Execute `workflows/verify-answer.md`:
- `{question}` = user's question
- `{answer_text}` = answer_text
- `{selected_sections}` = bm25_sections

If result is `"PASS"`, set `final_answer = answer_text` and skip to Step 7.

If result is `"FAIL"`, proceed to Step 4.

---

## Step 4

(BM25 verify failed — fall through to semantic search)

---

## Step 5

Execute `workflows/semantic-search.md`:
- `{question}` = user's question
- `{processing_type}` = processing_type
- `{purpose}` = purpose

Save `selected_sections` as `sem_sections`.

If `sem_sections` is empty, output:
```
この情報は知識ファイルに含まれていません。
```
and stop.

---

## Step 6

Execute `workflows/generate-answer.md`:
- `{question}` = user's question
- `{processing_type}` = processing_type
- `{selected_sections}` = sem_sections

Save result as `answer_text`.

Execute `workflows/verify-answer.md`:
- `{question}` = user's question
- `{answer_text}` = answer_text
- `{selected_sections}` = sem_sections

If result is `"PASS"`, set `final_answer = answer_text` and proceed to Step 7.

If result is `"FAIL"`, execute `workflows/generate-answer.md`:
- `{question}` = user's question
- `{processing_type}` = processing_type
- `{selected_sections}` = sem_sections
- `{excluded_claims}` = verify result issues

Set `final_answer` to the result.

---

## Step 7

Output `final_answer`.

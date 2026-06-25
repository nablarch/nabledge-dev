Follow the workflow and additional instructions below, then answer the question.

## Workflow
{workflow}

### Additional instructions

**Step 1**: Skip. The question already contains the hearing result (`（処理方式: X）（目的: Y）`). Start from Step 2.

**Step 2**: While executing full-text-search.md, record the BM25 terms extracted and the sections found.

**Step 3**: While executing check-answerable.md, record whether the result is OK or NG.

**Step 4**: If semantic-search.md ran (check-answerable result was NG), record the sections found. If it did not run, record `ran: false` and `selected_sections: []`.

**Step 7**: Output the following lines in this exact order:
1. The line `### Answer` (plain text, verbatim)
2. final_answer
3. The line `<<<WORKFLOW_DETAILS_JSON>>>` (plain text, verbatim — do not rename, wrap in HTML tags, or omit)
4. A ```json code block containing the JSON below
5. The line `<<<END_WORKFLOW_DETAILS>>>` (plain text, verbatim — do not rename, wrap in HTML tags, or omit)

Do not use HTML `<details>` elements. Output the three delimiter lines as plain text, character-for-character identical to what is shown above.

<<<WORKFLOW_DETAILS_JSON>>>
```json
{
  "step2": {
    "bm25_terms": ["<term>", "..."],
    "bm25_sections": [
      {"file": "<file path>", "section_id": "<sN>", "relevance": "<high|partial>"}
    ]
  },
  "step3": {
    "check_answerable_result": "<OK|NG>"
  },
  "step4": {
    "ran": false,
    "selected_sections": []
  },
  "step5": {
    "sections_used": [
      {"file": "<file path>", "section_id": "<sN>"}
    ]
  },
  "step6": {
    "verify_result": "<PASS|FAIL>",
    "regenerated": false
  }
}
```
<<<END_WORKFLOW_DETAILS>>>

## Question
{question}

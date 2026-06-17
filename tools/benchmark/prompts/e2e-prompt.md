Follow the workflow and additional instructions below, then answer the question.

## Workflow
{workflow}

### Additional instructions

**Step 1 and Step 2**: Skip both steps. The question already contains the hearing result (`（処理方式: X）（目的: Y）`). Start from Step 3.

**Step 3**: While executing semantic-search.md, for each page record why it was selected or skipped, and record its `source`. For each section record why it was selected (high/partial) or skipped.

`source` indicates which phase selected this page: `"index"` if only Phase A (index.md) selected it, `"classes"` if only Phase B (classes.md) selected it, `"both"` if both phases selected it. This must reflect the actual phase membership from Phase C merge (index_pages / class_pages), not a guess.

**Step 4**: Save the section IDs passed to read-sections.sh as `read_sections`.

**Step 8**: Output the following lines in this exact order:
1. The line `### Answer` (plain text, verbatim)
2. final_answer
3. The line `<<<WORKFLOW_DETAILS_JSON>>>` (plain text, verbatim — do not rename, wrap in HTML tags, or omit)
4. A ```json code block containing the JSON below
5. The line `<<<END_WORKFLOW_DETAILS>>>` (plain text, verbatim — do not rename, wrap in HTML tags, or omit)

Do not use HTML `<details>` elements. Output the three delimiter lines as plain text, character-for-character identical to what is shown above.

<<<WORKFLOW_DETAILS_JSON>>>
```json
{
  "step3": {
    "selected_pages": [
      {"path": "<page path relative to knowledge/>", "source": "<index|classes|both>", "reason": "<one sentence: why this page was selected>"}
    ],
    "excluded_pages": [
      {"path": "<page path relative to knowledge/>", "reason": "<one sentence: why this page was skipped>"}
    ],
    "selected_sections": [
      {"file": "<file path>", "section_id": "<sN>", "relevance": "<high|partial>", "reason": "<one sentence: why this section was selected>"}
    ],
    "excluded_sections": [
      {"file": "<file path>", "section_id": "<sN>", "reason": "<one sentence: why this section was skipped>"}
    ]
  },
  "step4": {
    "read_sections": [
      "<file.json:sN>"
    ]
  },
  "step8": {
    "answer_sections": {
      "used": [
        {"ref": "<file.json:sN>", "reason": "<one sentence: why this section was used in the answer>"}
      ],
      "unused": [
        {"ref": "<file.json:sN>", "reason": "<one sentence: why this section was read but not used in the answer>"}
      ]
    }
  }
}
```
<<<END_WORKFLOW_DETAILS>>>

## Question
{question}

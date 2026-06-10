Follow the workflow below, but only execute Steps 1, 2a, 2b, and 2c. Stop after Step 2c.

## Workflow
{workflow}

### Additional instructions

**Steps to execute**: Steps 1, 2a, 2b, and 2c only. Do NOT execute Step 3 or beyond.

After completing Step 2c, output the following lines in this exact order:
1. The line `### Answer` (plain text, verbatim)
2. (empty — no answer to show)
3. The line `<<<WORKFLOW_DETAILS_JSON>>>` (plain text, verbatim)
4. A ```json code block containing the JSON below
5. The line `<<<END_WORKFLOW_DETAILS>>>` (plain text, verbatim)

Do not use HTML `<details>` elements.

<<<WORKFLOW_DETAILS_JSON>>>
```json
{
  "step3": {
    "selected_pages": [
      {"path": "<page path relative to knowledge/>", "reason": "<one sentence: why this page was selected>"}
    ],
    "excluded_pages": [
      {"path": "<page path relative to knowledge/>", "reason": "<one sentence: why this page was skipped or excluded by dedup>"}
    ],
    "selected_sections": [],
    "excluded_sections": []
  },
  "step4": {
    "read_sections": []
  },
  "step8": {
    "answer_sections": {
      "used": [],
      "unused": []
    }
  }
}
```
<<<END_WORKFLOW_DETAILS>>>

Note: `selected_pages` must contain ALL pages in `selected_pages` (the merged result from Step 2c). `excluded_pages` contains pages that were candidates in either route but were removed by dedup or not selected.

## Question
{question}

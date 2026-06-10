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
    "index_strong": [
      {"path": "<page path relative to knowledge/>", "reason": "<one sentence>"}
    ],
    "classes_strong": [
      {"path": "<page path relative to knowledge/>", "reason": "<one sentence>"}
    ],
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

Note:
- `index_strong`: all pages rated 強い by the index route (Step 2a)
- `classes_strong`: all pages rated 強い by the classes route (Step 2b)
- `selected_pages`: the merged result from Step 2c (deduped union of index_strong + classes_strong). Must contain ALL pages in `selected_pages`.
- `excluded_pages`: pages rated 弱い or skip in both routes (not in selected_pages)

## Question
{question}

Follow the workflow and additional instructions below, then answer the question.

## Workflow
{workflow}

### Additional instructions

**Step 1 and Step 2**: Skip both steps. The question already contains the hearing result (`（処理方式: X）（目的: Y）`). Start from Step 3.

**Step 3**: While executing semantic-search.md, for each page record why it was selected or skipped. For each section record why it was selected (high/partial) or skipped.

**Step 4**: Save the section IDs passed to read-sections.sh as `read_sections`.

**Step 8**: After outputting final_answer, output the following.

### Workflow Details
```json
{
  "step3": {
    "selected_pages": [
      {"path": "<page path relative to knowledge/>", "reason": "<one sentence: why this page was selected>"}
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

## Question
{question}

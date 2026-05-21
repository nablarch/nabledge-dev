Follow the workflow and additional instructions below, then answer the question.

## Workflow
{workflow}

### Additional instructions

**Step 1 and Step 2**: Skip both steps. The question already contains the hearing result (`（処理方式: X）（目的: Y）`). Start from Step 3.

**Step 3**: While executing semantic-search.md, save the selected page paths as `selected_pages` and the full `results` array as `selected_sections`.

**Step 4**: Save the section IDs passed to read-sections.sh as `read_sections`.

**Step 8**: After outputting final_answer, output the following.

### Workflow Details
```json
{
  "step3": {
    "selected_pages": [
      "<page path relative to knowledge/>"
    ],
    "selected_sections": [
      {"file": "<file path>", "section_id": "<sN>", "relevance": "<high|partial>"}
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

Follow the workflow and additional instructions below, then answer the question.

## Workflow
{workflow}

### Additional instructions

**Step 1 and Step 2**: Skip both steps. The question already contains the hearing result (`（処理方式: X）（目的: Y）`). Start from Step 3.

**Step 3**: While executing semantic-search.md:
- After Stage 1: save the selected page paths as `selected_pages`.
- After Stage 2: save the full `results` array as `stage2_sections`.

**Step 4**: Save the section IDs passed to read-sections.sh as `read_sections`.

**Step 8**: After outputting final_answer, output the following.

### Workflow Details
```json
{
  "selected_pages": [
    "<page path relative to knowledge/>"
  ],
  "stage2_sections": [
    {"file": "<file path>", "section_id": "<sN>", "relevance": "<high|partial>"}
  ],
  "read_sections": [
    "<file.json:sN>"
  ],
  "answer_sections": {
    "used": [
      {"ref": "<file.json:sN>", "reason": "<one sentence: why this section was used in the answer>"}
    ],
    "unused": [
      {"ref": "<file.json:sN>", "reason": "<one sentence: why this section was read but not used in the answer>"}
    ]
  }
}
```

## Question
{question}

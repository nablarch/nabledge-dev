Follow the workflow and additional instructions below, then answer the question.

## Workflow
{workflow}

### Additional instructions

**Step 1 and Step 2**: If the question contains `処理方式:` and `目的:`, hearing_answer is already determined. Skip Step 1 and Step 2 and start from Step 3.

**Step 3**: Save the full `results` array returned by semantic-search.md as `stage2_sections`.

**Step 4**: Save the section IDs passed to read-sections.sh as `read_sections`.

**Step 8**: After outputting final_answer, output the following.

### Workflow Details
```json
{
  "hearing": {
    "processing_type": "<processing type from `処理方式:` in the question text. null if cross-functional>",
    "purpose": "<purpose from `目的:` in the question text>"
  },
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

Follow the workflow below and answer the question.

## Workflow
{workflow}

### Additional instructions

If the question contains `処理方式:` and `目的:`, hearing_answer is already determined. Skip Step 1 and Step 2 and start from Step 3.

After outputting final_answer in Step 8, output the following.

### Workflow Details
```json
{
  "hearing": {
    "processing_type": "<processing type determined in Step 1, or taken from `処理方式:` in the question text. null if cross-functional>",
    "purpose": "<purpose determined in Step 1, or taken from `目的:` in the question text>"
  },
  "stage2_sections": [
    {"file": "<file path>", "section_id": "<sN>", "relevance": "<high|partial>"}
  ],
  "read_sections": [
    "<section ID passed to read-sections.sh in Step 4 (file.json:sN format)>"
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

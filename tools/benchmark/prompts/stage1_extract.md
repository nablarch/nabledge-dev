# Stage 1: Keyword Extraction

Extract 3-10 search keywords (Japanese or English) from the user's question.

## Rules

- Output ONLY the structured JSON defined by the schema.
- No tool calls needed — this is a pure extraction task.
- Keywords should be concise terms (single words or short compounds) useful for full-text search against a knowledge base about the Nablarch framework.
- Include both Japanese terms the user wrote and any likely technical synonyms.

## Question

{{question}}

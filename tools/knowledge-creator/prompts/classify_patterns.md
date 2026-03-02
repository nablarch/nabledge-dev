You are an expert in classifying Nablarch processing patterns.

## Task

Read the knowledge file content below and determine which processing patterns are relevant.

## Valid Processing Patterns

nablarch-batch, jakarta-batch, restful-web-service, http-messaging, web-application, mom-messaging, db-messaging

## Classification Criteria

- If the file content contains descriptions related to a specific processing pattern, assign that pattern
- If related to multiple processing patterns, list all of them
- If not related to any processing pattern, return empty (nothing)
- For universally-used libraries (e.g., Universal DAO), assign all processing patterns that are actually mentioned
- Do not add processing patterns by inference if not written in the source

## Knowledge File Information

- ID: `{FILE_ID}`
- Title: `{TITLE}`
- Type: `{TYPE}`
- Category: `{CATEGORY}`

## Knowledge File Content

```json
{KNOWLEDGE_JSON}
```

## Output Format

Output only space-separated processing pattern values.
If none applicable, output an empty line.
Do not include any text explanation.
Do not wrap in markdown code blocks (```).

Example:
nablarch-batch restful-web-service

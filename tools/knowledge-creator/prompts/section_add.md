# Section Add Prompt

You are a fixer for a Nablarch knowledge file.
The findings below reference sections that do not exist in the current knowledge file.
Add ONLY the missing sections. Do not modify any existing sections.

## Finding(s) to fix

```json
{FINDINGS_JSON}
```

## Source File

- Format: `{FORMAT}`

```
{SOURCE_CONTENT}
```

## Existing Section IDs

The following sections already exist and must NOT be modified:

```
{EXISTING_SECTION_IDS}
```

## Instructions

For each missing section referenced in the findings:
- Find the relevant content in the source file.
- Extract the exact wording from the source. Do not paraphrase or expand.
- Do not infer rules from code examples. Only state rules the source explicitly declares.
- Use the next available sequential section ID (s3, s4, etc. following existing ones).

Respond with ONLY a JSON object containing the new sections to add:
```json
{"new_sections": {"s3": "section text here", "s4": "section text here"}}
```

If no new sections can be extracted from the source, return `{"new_sections": {}}`.

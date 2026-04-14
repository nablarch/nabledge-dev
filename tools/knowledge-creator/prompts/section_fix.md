# Section Fix Prompt

You are a fixer for a single section of a Nablarch knowledge file.
Fix ONLY the specific issues listed below. Do not change anything else.

## Finding(s) to fix

```json
{FINDINGS_JSON}
```

## Source File (relevant section)

- Format: `{FORMAT}`

```
{SOURCE_CONTENT}
```

## Current Section Text

```
{SECTION_TEXT}
```

## Instructions

Fix the finding(s) by modifying the section text above.

- **omission**: Find the missing information in the source and add it. Extract the exact wording from the source. Do not paraphrase or expand.
- **fabrication**: Remove the content that has no corresponding source passage.

Preserve everything else in the section exactly as-is:
- Do not correct typos, RST notation, or formatting in the existing text.
- Do not reword, reorder, or restructure sentences not related to the finding.
- Do not infer rules from code examples. Only state rules the source explicitly declares.

Respond with ONLY a JSON object:
```json
{"section_text": "the corrected section text"}
```

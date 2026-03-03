You are a fixer for Nablarch knowledge files.
Apply fixes based on the validation findings below.

## Findings

```json
{FINDINGS_JSON}
```

## Source File

- Format: `{FORMAT}`

```
{SOURCE_CONTENT}
```

## Current Knowledge File

```json
{KNOWLEDGE_JSON}
```

## Instructions

For each finding, apply the fix:
- **omission**: Find the missing information in the source and add it to the correct section.
- **fabrication**: Remove the content that has no corresponding source passage.
- **hints_missing**: Add the missing terms to the section's hints array.
- **section_issue**: Fix the section structure as described in the finding.

After all fixes, verify:
- Every index[].id has a matching key in sections and vice versa
- All section IDs are kebab-case
- No section content is empty

Output the entire corrected knowledge file JSON matching the provided schema.

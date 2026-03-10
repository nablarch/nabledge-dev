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
- **no_knowledge_content_invalid**: The file was incorrectly marked as `no_knowledge_content: true` but the source has Layer A/B content. Set `no_knowledge_content: false`, then extract all Layer A/B content from the source into proper sections following the same rules as generate.md Steps 2-6. Build index[] and sections{} normally.
- **processing_patterns_invalid**: Fix the processing_patterns array. Add missing patterns, remove incorrect ones, or add the field if missing. Valid values: nablarch-batch, jakarta-batch, restful-web-service, http-messaging, web-application, mom-messaging, db-messaging. If FILE_TYPE is `processing-pattern`, include FILE_CATEGORY.

After all fixes, verify:
- Every index[].id has a matching key in sections and vice versa
- All section IDs are kebab-case
- No section content is empty

Respond with the entire corrected knowledge file as JSON matching the schema defined in generate.md (knowledge file structure with index[], sections{}, source{}, assets{} fields).

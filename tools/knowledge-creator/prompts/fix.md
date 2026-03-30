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

After all fixes, verify:
- Every index[].id has a matching key in sections and vice versa
- Section IDs follow sequential format: `s1`, `s2`, `s3`, ...
- No section content is empty

Respond with the entire corrected knowledge file as JSON matching the schema defined in generate.md (knowledge file structure with index[], sections{}, source{}, assets{} fields).

---

## Constraints — Read carefully before editing

### E-1: Fix only what findings specify

Modify only the sections, hints, or fields that are directly referenced in the findings above.
Do NOT change any section, hint, or field that has no associated finding.
Do NOT improve, clean up, or reformulate sections that are not mentioned.

### E-2: Extract omission content verbatim from source

When fixing an **omission** finding:
- Locate the passage in the source indicated by `source_evidence`.
- Copy the information faithfully from that passage. Do not paraphrase, generalize, or expand beyond what is written.
- Do not add information that is not contained in that specific source passage.
- Do not infer constraints, rules, or behaviors not explicitly stated in the source.

Decision rule: "Can I point to a specific sentence or phrase in the source for each distinct claim or fact I add?" If NO for any claim → do not include it. You may combine information from multiple source sentences into one statement if each individual claim maps to a specific source passage.

### E-3: Preserve source notation exactly

Copy source text exactly as written — including apparent typos, non-standard notation, intentional formatting, special characters, and RST syntax.
Do NOT "correct" typos or normalize notation. The source is authoritative.

Examples of notation to preserve as-is:
```
:ref:`label`
:java:extdoc:`ClassName<fully.qualified.ClassName>`
```
Also preserve non-standard identifiers or casing in the original source, and intentional unconventional formatting.

### E-4: Do not corrupt adjacent text

When editing content within a section, copy all existing content outside the edited location exactly as it appears in the current knowledge file. Do NOT restructure, reorder, rewrite, or otherwise alter parts of the section that are not part of the fix.

Scope: "edited location" means the specific sentence, list item, or code block identified by the finding. All other content in the same section — including adjacent sentences, surrounding list items, and unrelated paragraphs — must be preserved verbatim.

### E-5: Do not fabricate rules from patterns

Do NOT generalize implicit patterns into explicit rules. Only include rules, constraints, or conditions that are explicitly stated in the source.
If the source shows examples of a pattern without stating a rule, do not add a rule for it.

If a pattern is consistent across many examples but no rule is stated, you may describe what the examples show using phrasing like "Examples in the source all follow the form X" — but do not phrase it as a rule or constraint that must be followed.

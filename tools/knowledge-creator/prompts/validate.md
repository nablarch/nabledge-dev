You are an expert in validating and improving Nablarch knowledge files.
Compare the generated knowledge file with the source file to validate both structure and content, and fix any issues.

## ⚠️ Completion Condition (MUST follow)

The completion condition for knowledge file improvement is **zero validation errors from the structure validation script**.

You **MUST** execute the following process:

1. Fix the knowledge file (refer to validation perspectives below)
2. Save the fixed JSON to `{OUTPUT_PATH}`
3. Run structure validation script:
   ```bash
   python tools/knowledge-creator/validate_single.py {OUTPUT_PATH} {SOURCE_PATH} {FORMAT}
   ```
4. Check exit code:
   - **Exit code 0**: ✅ Validation passed → Complete
   - **Exit code 1**: ❌ Errors found → Read error messages, fix them, and return to step 1
5. **Repeat up to 20 times** (only if errors remain after 20 attempts, output the final version at that point)

**IMPORTANT**: You must NOT complete until validation passes.

---

## Source File

```
{SOURCE_CONTENT}
```

## Knowledge File

```json
{KNOWLEDGE_JSON}
```

---

## Validation Perspectives

Validate and fix from the following perspectives:

**B1. Information Omissions (Most Important)**

Check if the knowledge file contains the following information from the source:
- Specifications (configuration items, default values, types, constraints, behavior specs)
- Notes and warnings (content of important, warning, tip, note directives)
- Design philosophy, recommended patterns
- Code examples, configuration examples
- Class names, interface names, annotation names

**Fix method:** Extract missing information from source and add to relevant sections

**B2. Information Fabrication**

Check if the knowledge file contains information NOT written in the source:
- Inferred default values, constraints, behavior specs
- Added explanations not in source
- Added code examples not in source

**Fix method:** Remove information not in source

**B3. Section Splitting Validity**

- For RST: Split by h2? If text under h2 exceeds 2000 characters, split by h3?
- For MD: Split by ##?
- Are h3 and below included in parent sections?
- Each section must have at least 50 characters of content (empty or extremely short sections are NG)

**Fix method:** Adjust section splitting or add content to short sections

**B4. Search Hints Quality**

- Do section hints include class names, property names, functional keywords?
- Are any hints missing?
- Minimum standard: Technical terms appearing in sections (class names, annotation names, property names) must be included

**Fix method:** Add missing keywords to hints

---

## Output Format

After fixes are complete, output in the following JSON format. Do not include any text other than JSON.

Output **the entire fixed knowledge file** (same JSON Schema as original knowledge file).

```json
{
  "id": "...",
  "title": "...",
  "official_doc_urls": [...],
  "index": [...],
  "sections": {...}
}
```

---

## Important Notes

- If issues remain after 20 attempts, output the final version at that point
- Fixes must be based on source file content
- Do not add information by inference or general knowledge

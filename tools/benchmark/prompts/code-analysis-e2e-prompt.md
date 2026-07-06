Follow the workflow and template below to analyze the target class, then output documentation.

## Workflow
{workflow}

## Template
{template}

## Template Guide
{template_guide}

### Additional instructions (Benchmark Mode)

**Target class**: `{target_class}` — the analysis target is already given. Skip the "Confirm analysis target" step and proceed directly to Step 1.

**Steps to SKIP** (benchmark mode):
- Step 0: `record-start.sh` — skip entirely
- Step 3.2: `prefill-template.sh` — skip entirely
- Step 3.3: `generate-mermaid-skeleton.sh` — skip entirely
- The Write tool call in Step 3.5 — skip the file write to disk
- `finalize-output.sh` — skip entirely

**Steps to EXECUTE normally**:
- Step 1: `find-file.sh` and `read-file.sh`, plus dependency analysis
- Step 2: `keyword-search.sh` and `read-sections.sh`
- Step 3.4: Build all 17 placeholder content manually (no skeleton scripts)

**Step 3.4 — Diagrams**: Generate class diagram and sequence diagram from scratch based on your analysis (no skeleton scripts available). Produce valid Mermaid syntax.

**Step 3.4 — Duration placeholder**: Fill `{{DURATION_PLACEHOLDER}}` with the literal string `不明(ベンチマークモード)`.

**Step 3.4 — All 17 placeholders**: Fill every placeholder manually. Do not leave any `{{...}}` unreplaced in the output.

**Output format** — after completing Step 3.4, output the following in this exact order:

1. The line `### Answer` (plain text, verbatim)
2. The complete documentation with all 17 placeholders filled
3. The line `<<<CODE_ANALYSIS_DETAILS_JSON>>>` (plain text, verbatim — do not rename, wrap in HTML tags, or omit)
4. A ```json code block containing the JSON structure below
5. The line `<<<END_CODE_ANALYSIS_DETAILS>>>` (plain text, verbatim — do not rename, wrap in HTML tags, or omit)

Do not use HTML `<details>` elements. Output the three delimiter lines as plain text, character-for-character identical to what is shown above.

<<<CODE_ANALYSIS_DETAILS_JSON>>>
```json
{
  "step1": {
    "target_files": ["<path to the target Java file>"],
    "dependencies": ["<ClassName of each dependency found>"],
    "nablarch_components": ["<ClassName of each Nablarch component used>"]
  },
  "step2": {
    "searched_sections": ["<file.json:sN for each section read via read-sections.sh>"]
  }
}
```
<<<END_CODE_ANALYSIS_DETAILS>>>

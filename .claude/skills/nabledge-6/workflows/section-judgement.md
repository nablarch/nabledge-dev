# Section Judgement Workflow

Judge relevance of candidate sections by reading content.

## Input

JSON with candidate sections from keyword-search workflow (conforms to `schemas/section-scoring.json`)

## Output

Answer to user's query using relevant knowledge only

## Steps

### Step 1: Read Section Content

For each candidate section:

```bash
jq -r '.sections[<section_id>]' <file_path>
```

Extract only the specified section content. Do not read entire file.

Stop after reading 10 sections or finding 5 High-relevance sections, whichever comes first.

### Step 2: Judge Relevance

For each section read, judge relevance based ONLY on section content:

**High (2)**: Section directly addresses goal AND contains actionable information (methods, examples, configuration)

**Partial (1)**: Section provides prerequisite knowledge, related functionality, or context

**None (0)**: Section addresses different topic

When in doubt between High and Partial, choose Partial.

### Step 3: Filter and Answer

Filter out None (0) relevance sections.

Sort by relevance: High (2) first, then Partial (1).

**If no High-relevance found**:
- Use Partial sections if available
- Add note: "関連する情報は限られています"

**If all sections are None**:
- Output: "この情報は知識ファイルに含まれていません"
- List related entries from index.toon
- DO NOT answer from external knowledge

**Answer format**:
- Extract information from High and Partial sections ONLY
- Structure answer with:
  - 結論 (Conclusion): Direct answer
  - 根拠 (Evidence): 1 code example from knowledge files
  - 注意点 (Considerations): Important points or limitations
- Target length: 500 tokens (simple), 800 tokens (complex)
- Cite sources: `<file>:<section>` format

## Validation

Validate final answer against:
- Uses ONLY information from knowledge files
- Cites sources correctly
- Does not supplement with external knowledge

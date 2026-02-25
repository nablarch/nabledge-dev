# Section Judgement Workflow

Judge relevance of candidate sections by reading content.

## Input

JSON with candidate sections from keyword-search workflow (conforms to `schemas/section-scoring.json`)

## Output

JSON with relevant sections (High and Partial only) for knowledge-search workflow

## Steps

### Step 1: Read Section Content

For each candidate section:

```bash
jq -r '.sections[<section_id>]' <file_path>
```

Extract only the specified section content. Do not read entire file.

### Step 2: Judge Relevance

Stop after reading 10 sections or finding 5 High-relevance sections, whichever comes first.

For each section read, judge relevance based ONLY on section content:

**High (2)**: Section directly addresses goal AND contains actionable information (methods, examples, configuration)

**Partial (1)**: Section provides prerequisite knowledge, related functionality, or context

**None (0)**: Section addresses different topic

When in doubt between High and Partial, choose Partial.

### Step 3: Filter and Output

Filter out None (0) relevance sections.

Sort by relevance: High (2) first, then Partial (1).

Output JSON with filtered and sorted sections for the knowledge-search workflow to use.

## Validation

Validate output JSON:
- Contains filtered sections with relevance ≥ 1
- Sorted by relevance (High first, then Partial)
- Ready for knowledge-search workflow to generate answer

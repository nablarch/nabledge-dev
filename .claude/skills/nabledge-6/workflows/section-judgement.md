# Section Judgement Workflow

Judge relevance of candidate sections by reading content and comparing against user request.

## Overview

**Who executes**: Claude Code (you)

**Input**:
- User's request (natural language)
- Candidates list from keyword-search workflow

**Input format**:
```json
{
  "candidates": [
    {
      "file_path": "features/libraries/universal-dao.json",
      "section": "paging",
      "matched_hints": ["ページング", "per", "page"]
    }
  ]
}
```

**Output**: Filtered sections with relevance scores

**Tools you will use**:
- Bash tool with jq: Batch extract specific sections from JSON files
- None (mental): Judge relevance based on content

**Expected tool calls**: 2-3 calls (reduced from 5-10 via batch extraction by file)

**Expected output**: 5-15 sections with High/Partial relevance

**Output format**:
```json
{
  "sections": [
    {
      "file_path": "features/libraries/universal-dao.json",
      "section": "paging",
      "matched_hints": ["ページング", "per", "page"],
      "relevance": 2,
      "judgement": "High - pagination API and examples"
    }
  ],
  "summary": {
    "high_count": 1,
    "partial_count": 0,
    "none_count": 0,
    "total_tokens": "~500"
  }
}
```

**Purpose**:
1. Read section content from knowledge files
2. Judge relevance: High (2, directly answers), Partial (1, supporting context), None (0, not relevant)
3. Filter out None
4. Return relevant knowledge

**Process**:
1. Read candidate section content
2. Judge relevance
3. Assign score: High (2), Partial (1), None (0)
4. Filter out None, keep High and Partial
5. Sort by relevance (High first)

## Judgement process

### Step 1: Read candidate sections and judge relevance

**Tools**: Bash with jq

**Action**: Batch extract all candidate sections to reduce tool calls, then judge relevance.

**Batch extraction script**:
```bash
# Group candidates by file to minimize jq calls
declare -A file_sections

for file in "${!file_sections[@]}"; do
  sections="${file_sections[$file]}"
  for section in $sections; do
    content=$(jq -r --arg sec "$section" '.sections[$sec] // empty' "$file" 2>/dev/null)
    if [ -n "$content" ]; then
      echo "===FILE: $file"
      echo "===SECTION: $section"
      echo "$content"
      echo "===END==="
    fi
  done
done
```

**Efficiency**:
- Extract all sections from same file in one jq call
- Use `// empty` to skip missing sections
- Structured output with delimiters
- Stop after 5-10 sections if critical

**Judge relevance**:

1. Read extracted section content
2. Judge relevance based ONLY on section content

**Relevance criteria**:

**High (2)**: Section directly addresses goal AND contains actionable information (methods, examples, configuration)
- Example: User wants pagination → Section has per(), page() methods with examples → High

**Partial (1)**: Section provides prerequisite knowledge, related functionality, or context
- Example: User wants pagination → Section explains UniversalDao basics → Partial

**None (0)**: Section addresses different topic
- Example: User wants pagination → Section about logging → None

**Rule**: When in doubt between High and Partial, choose Partial.

**Efficiency**: Stop after finding 5+ High-relevance sections.

### Step 2: Sort, filter, and return results

**Action**:

1. Add relevance score and judgement to each candidate
2. Filter out None (0)
3. Sort by relevance: High (2) first, then Partial (1)
4. Limit to 10-15 sections
5. Return results:

```json
{
  "sections": [
    {
      "file_path": "features/libraries/universal-dao.json",
      "section": "paging",
      "relevance": 2,
      "judgement": "High - pagination API and examples"
    }
  ],
  "summary": {
    "high_count": 1,
    "partial_count": 0,
    "none_count": 2
  }
}
```

**Answer the user**: Extract information from returned sections ONLY (no external knowledge). Cite sources.

## Error handling

**No High-relevance found**: Return top 5-10 Partial sections with note "関連する情報は限られています".

**All None relevance**: State "この情報は知識ファイルに含まれていません", show related entries from index.toon. DO NOT use LLM training data.

## Best practices

- Base judgements ONLY on knowledge file content
- Only assign High (2) if section directly enables goal
- Judge based on content, not section IDs/titles
- Use "この情報は知識ファイルに含まれていません" when knowledge is absent
- Include judgement field with brief reasoning

## Example execution

**Request**: "ページングを実装したい"

**Input**: 4 candidates (universal-dao/paging, universal-dao/search, universal-dao/overview, database-access/query)

**Step 1**: Read each section and judge:
- universal-dao/paging: High (2) - has per(), page() methods with examples
- universal-dao/search: None (0) - not pagination-specific
- universal-dao/overview: Partial (1) - DAO basics for context
- database-access/query: None (0) - underlying mechanism, not needed

**Step 2**: Filter None, sort by relevance, return 2 sections (High + Partial) with judgement reasons

## Integration

Called by keyword-search workflow. Input: candidates list. Output: scored sections with High/Partial relevance.

# Knowledge Search Workflow

Answer user questions using Nablarch 6 knowledge base.

## Input

User's query (natural language)

## Output

Japanese answer with knowledge base citations

## Overview

This workflow orchestrates keyword-search and section-judgement workflows to find relevant knowledge, then generates a comprehensive answer.

## Steps

### Step 1: Execute Keyword Search

**Workflow**: `workflows/keyword-search.md`

**Action**: Execute keyword-search workflow to find candidate sections.

1. Read `workflows/keyword-search.md`
2. Follow the workflow steps:
   - Extract L1/L2 keywords from query
   - Match files in index.toon using semantic matching
   - Extract and score section hints
   - Return candidate sections (relevance ≥ 2)

**Output**: JSON with candidate sections from keyword-search workflow

### Step 2: Execute Section Judgement

**Workflow**: `workflows/section-judgement.md`

**Action**: Execute section-judgement workflow to filter relevant sections.

1. Read `workflows/section-judgement.md`
2. Follow the workflow steps:
   - Read section content from candidate sections
   - Judge relevance (High/Partial/None)
   - Filter and sort (keep High and Partial only)

**Output**: JSON with relevant sections (High and Partial relevance)

### Step 3: Generate Answer

**Action**: Synthesize answer from relevant sections.

1. **Read section content**:
   ```bash
   jq -r '.sections[<section_id>]' <file_path>
   ```

2. **Analyze sections**:
   - Identify main concepts
   - Extract code examples
   - Note configuration requirements
   - Identify best practices and cautions

3. **Structure answer** in Japanese:

```markdown
## 概要
<High-relevance sections summary>

## 実装方法
<Step-by-step instructions from sections>

## コード例
<Code examples from sections>

## 重要なポイント
- ✅ <Must-do items>
- ⚠️ <Cautions>
- 💡 <Tips>

## 参考
- <Knowledge file citations with section IDs>
```

4. **Validation**:
   - Answer uses ONLY information from knowledge files
   - All statements are supported by section content
   - Code examples are copied directly (not modified)
   - Citations include file path and section ID

**Output**: Formatted answer in Japanese

## Error Handling

**No candidate sections found** (Step 1 returns empty):
- Message: "この情報は知識ファイルに含まれていません"
- List extracted keywords
- Show available categories from index.toon

**No relevant sections after judgement** (Step 2 returns empty):
- Message: "該当するセクションが見つかりませんでした"
- List candidate sections that were checked
- Suggest broadening search terms

## Important Notes

**Knowledge-only constraint**:
- Use ONLY information from knowledge files
- DO NOT supplement with external knowledge or LLM training data
- If information is missing, explicitly state: "この情報は知識ファイルに含まれていません"

**Citation format**:
- Format: `[ファイル名](knowledge/path/to/file.json#section-id)`
- Example: `[UniversalDao](knowledge/features/libraries.json#universal-dao-overview)`

**Tool call efficiency**:
- Total tool calls: ~5-10 calls
  - Step 1 (Keyword Search): 2-3 calls (Read index.toon, extract sections with jq)
  - Step 2 (Section Judgement): 1-3 calls (Read section content with jq)
  - Step 3 (Answer Generation): 1-2 calls (Read final sections, generate answer)
- Agent performs semantic analysis in memory without additional tool calls
- Scripts are only used for mechanical extraction (jq for JSON parsing)

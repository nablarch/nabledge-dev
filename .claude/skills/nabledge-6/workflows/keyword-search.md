# Keyword Search Workflow

This workflow searches the knowledge index (index.toon) using keyword matching to find relevant files and sections.

## Table of Contents

- [Overview](#overview)
- [Search process](#search-process)
  - [Step 1: Extract keywords and match against index](#step-1-extract-keywords-and-match-against-index)
  - [Step 2: Extract candidate sections](#step-2-extract-candidate-sections)
  - [Step 3: Judge relevance and return results](#step-3-judge-relevance-and-return-results)
- [Error handling](#error-handling)
- [Example execution](#example-execution)
- [Notes](#notes)

## Overview

**Who executes**: Claude Code (you)

**Input**: User's request (natural language)

**Output**: Candidates list for section-judgement workflow

**Strategy**: Technical axis - match keywords from the request against search hints in index.toon

**Tools you will use**:
- Read tool: Read knowledge/index.toon
- Grep tool (optional): Search for keywords in index.toon
- Bash tool with jq: Extract .index from knowledge files

**Expected tool calls**: 10-15 calls

**Expected output**: 20-30 candidate sections

## Search process

### Step 1: Extract keywords and match against index

**Tools**: Read tool

**Action**: Extract keywords from the user request at three levels, then read index.toon and match keywords against hints.

**Keyword extraction at 3 levels**:

1. **Technical domain** (技術領域): データベース, バッチ, ハンドラ, Web, REST, テスト, etc.
2. **Technical component** (技術要素): DAO, JDBC, JPA, Bean Validation, JSON, XML, etc.
3. **Functional** (機能): ページング, 検索, 登録, 更新, 削除, 接続, コミット, etc.

**Example**: Request "ページングを実装したい"
- Technical domain: ["データベース", "database"]
- Technical component: ["DAO", "UniversalDao", "O/Rマッパー"]
- Functional: ["ページング", "paging", "per", "page", "limit", "offset"]

**Critical**: Include Japanese and English terms, abbreviations, and related concepts at all levels.

**Matching process**:

1. Read knowledge/index.toon (93 entries, format: `Title, hint1 hint2 ..., path.json`)
2. For each entry, match your extracted keywords against hints:
   - **Use Level 1 (Technical domain) + Level 2 (Technical component) keywords only**
   - Level 3 (Functional) keywords are NOT used in this step
   - Case-insensitive matching
   - Partial matching allowed (e.g., "ページ" matches "ページング")
   - Count matched hints per entry
3. Sort files by matched hint count (descending)
4. Select top 10-15 files with ≥1 matched hint

**Output**: List of candidate files with their matched hints counts.

### Step 2: Extract candidate sections

**Tools**: Bash with jq

**Action**: For each of the 10-15 selected files:

1. Extract only the `.index` field using jq:
   ```bash
   jq '.index' knowledge/features/libraries/universal-dao.json
   ```
2. Match your keywords against section hints:
   - **Use Level 2 (Technical component) + Level 3 (Functional) keywords**
   - Level 1 (Technical domain) keywords are NOT used in this step
   - Level 2 is reused from Step 1 (acts as a bridge between file and section selection)
   - Case-insensitive matching, partial matching allowed
   - Count matched hints per section
3. Keep sections with ≥1 matched hint
4. Stop when you have 20-30 candidate sections total

**Output**: List of candidates with file_path, section_id, and matched_hints.

### Step 3: Judge relevance and return results

**Action**: Pass the candidates list to section-judgement workflow (workflows/section-judgement.md):

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

Section-judgement will:
- Read actual section content
- Judge relevance (High=2, Partial=1, None=0)
- Filter out None-relevance sections
- Return 5-15 relevant sections with scores

Use the returned sections to answer the user's question (knowledge files only).

## Error handling

**No keyword matches**: Inform user, list extracted keywords, show available categories from index.toon.

**Too many candidates (>30)**: Select files with 2+ matched hints, limit to top 15 files and 30 sections.

**Section-judgement returns no results**: State "この情報は知識ファイルに含まれていません", show available knowledge from index.toon. DO NOT answer from LLM training data.

## Example execution

**Request**: "ページングを実装したい"

**Extract keywords at 3 levels**:
- Level 1 (Technical domain): ["データベース", "database"]
- Level 2 (Technical component): ["DAO", "UniversalDao", "O/Rマッパー"]
- Level 3 (Functional): ["ページング", "paging", "per", "page", "limit", "offset"]

**Step 1**: Match against index.toon using L1+L2 → universal-dao.json (matched: データベース, DAO), database-access.json (matched: データベース)
**Step 2**: Extract sections using L2+L3 → universal-dao/paging (matched: DAO, ページング, per, page), universal-dao/overview (matched: DAO)
**Step 3**: Section-judgement → Only universal-dao/paging judged as High (2), others filtered as None
**Result**: 1 section with pagination API and examples

## Notes

- Technical axis search (keyword matching) complements intent-search (purpose-oriented search)
- Uses Read tool for index.toon and Bash+jq for extracting section indexes
- Final relevance scoring happens in section-judgement workflow
- Expected output: 5-15 relevant sections filtered by section-judgement

**Keyword level usage strategy**:
- **Level 2 acts as a bridge**: Used in both file selection (Step 1) and section selection (Step 2)
- **File selection (index.toon)**: L1 (broad technical domain) + L2 (specific technology) → narrows down to 10-15 files
- **Section selection (.index)**: L2 (specific technology) + L3 (specific function) → narrows down to 20-30 sections
- This two-stage filtering with L2 overlap ensures high precision while maintaining recall

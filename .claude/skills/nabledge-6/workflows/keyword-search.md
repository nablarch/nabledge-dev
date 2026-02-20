# Keyword Search Workflow

This workflow searches the unified knowledge index (index.toon) using keyword matching to find relevant sections directly.

## Table of Contents

- [Overview](#overview)
- [Search process](#search-process)
  - [Step 1: Extract keywords and score sections](#step-1-extract-keywords-and-score-sections)
  - [Step 2: Judge relevance and return results](#step-2-judge-relevance-and-return-results)
- [Error handling](#error-handling)
- [Example execution](#example-execution)
- [Notes](#notes)

## Overview

**Who executes**: Claude Code (you)

**Input**: User's request (natural language)

**Output**: Candidates list for section-judgement workflow

**Strategy**: Technical axis - match keywords from the request against search hints in the unified section-level index (index.toon)

**Tools you will use**:
- Read tool: Read knowledge/index.toon (147 section-level entries)
- Grep tool (optional): Search for keywords in index.toon

**Expected tool calls**: 2-5 calls

**Expected output**: 20-30 candidate sections

## Search process

### Step 1: Extract keywords and score sections

**Tools**: Read tool

**Action**: Extract keywords from the user request at three levels, then read index.toon and score sections directly using matched keywords.

**Keyword extraction at 3 levels**:

1. **Technical domain** (技術領域): データベース, バッチ, ハンドラ, Web, REST, テスト, etc.
2. **Technical component** (技術要素): DAO, JDBC, JPA, Bean Validation, JSON, XML, etc.
3. **Functional** (機能): ページング, 検索, 登録, 更新, 削除, 接続, コミット, etc.

**Example**: Request "ページングを実装したい"
- Technical domain: ["データベース", "database"]
- Technical component: ["DAO", "UniversalDao", "O/Rマッパー"]
- Functional: ["ページング", "paging", "per", "page", "limit", "offset"]

**Critical**: Include Japanese and English terms, abbreviations, and related concepts at all levels.

**Scoring process**:

1. Read knowledge/index.toon (147 entries, format: `Title, hint1 hint2 ..., path.json#section_id`)
2. For each section entry, match your extracted keywords against hints using this **scoring strategy**:
   - L2 (Technical component) keyword match: **+2 points** per hint
   - L3 (Functional) keyword match: **+2 points** per hint
   - L1 (Technical domain) keyword match: **+1 point** per hint
   - Case-insensitive matching
   - Partial matching allowed (e.g., "ページ" matches "ページング")
   - Sum up all matched hint scores for each section
3. Sort sections by total score (descending)
4. Select top 20-30 sections with score ≥2

**Rationale**:
- **L2 (Technical component) and L3 (Functional)** are weighted equally at +2 points because they directly identify the specific technology and function being asked about
- **L1 (Technical domain)** is weighted lower at +1 point because it provides broad context but is less specific for section-level matching
- Since we're working directly at section level (not file level first), L2 and L3 keywords are the primary discriminators

**Output**: List of candidate sections with file_path, section_id, score, and matched_hints breakdown.

### Step 2: Judge relevance and return results

**Action**: Pass the candidates list to section-judgement workflow (workflows/section-judgement.md):

```json
{
  "candidates": [
    {
      "file_path": "features/libraries/universal-dao.json",
      "section": "paging",
      "score": 8,
      "matched_hints": [
        {"hint": "データベース", "level": "L1", "points": 1},
        {"hint": "DAO", "level": "L2", "points": 2},
        {"hint": "ページング", "level": "L3", "points": 2},
        {"hint": "per", "level": "L3", "points": 2},
        {"hint": "page", "level": "L3", "points": 1}
      ]
    }
  ]
}
```

**Note**: The detailed score breakdown is optional for section-judgement. A simplified format with just `matched_hints: ["データベース", "DAO", "ページング", "per", "page"]` is also acceptable.

Section-judgement will:
- Read actual section content
- Judge relevance (High=2, Partial=1, None=0)
- Filter out None-relevance sections
- Return 5-15 relevant sections with scores

Use the returned sections to answer the user's question (knowledge files only).

## Error handling

**No keyword matches**: Inform user, list extracted keywords, show available categories from index.toon.

**Too many candidates (>30)**: Raise threshold to score ≥3, or limit to top 30 sections by score.

**Section-judgement returns no results**: State "この情報は知識ファイルに含まれていません", show available knowledge from index.toon. DO NOT answer from LLM training data.

## Example execution

**Request**: "ページングを実装したい"

**Extract keywords at 3 levels**:
- Level 1 (Technical domain): ["データベース", "database"]
- Level 2 (Technical component): ["DAO", "UniversalDao", "O/Rマッパー"]
- Level 3 (Functional): ["ページング", "paging", "per", "page", "limit", "offset"]

**Step 1**: Score sections directly from index.toon
- universal-dao.json#paging: score=8 (データベース[L1]:1 + DAO[L2]:2 + ページング[L3]:2 + per[L3]:2 + page[L3]:1)
- database-access.json#paging: score=6 (データベース[L1]:1 + ページング[L3]:2 + offset[L3]:2 + limit[L3]:1)
- universal-dao.json#overview: score=4 (DAO[L2]:2 + O/Rマッパー[L2]:2)
- universal-dao.json#crud: score=2 (DAO[L2]:2)
- Top candidates selected: paging (universal-dao, score=8), paging (database-access, score=6), overview (score=4), crud (score=2)

**Step 2**: Section-judgement → universal-dao/paging judged as High (2), database-access/paging as Partial (1), overview as Partial (1), crud as None (0)

**Result**: 1 primary section (universal-dao/paging) with pagination API and examples, 2 supporting sections

## Notes

- Single-stage section-level scoring using unified index.toon (147 entries)
- Technical axis search (keyword matching) complements intent-search (purpose-oriented search)
- Uses Read tool for index.toon only - no need for jq extraction from individual files
- Final relevance scoring happens in section-judgement workflow
- Expected output: 5-15 relevant sections filtered by section-judgement

**Scoring strategy rationale**:

| Keyword Level | Weight | Rationale |
|---------------|--------|-----------|
| **L1 (Technical domain)** | +1 | Provides broad context but is less specific for section-level matching. Lower weight avoids over-matching on generic domain terms. |
| **L2 (Technical component)** | +2 | Primary discriminator - identifies specific technology/component being asked about. High weight ensures technical precision. |
| **L3 (Functional)** | +2 | Primary discriminator - identifies specific function/operation being asked about. Equal to L2 since both are essential for section-level precision. |

**Why weighted scoring?**:
- **Deterministic**: Same input always produces same scores (no ambiguous judgment)
- **Flexible**: Handles edge cases (L1-only matches get lower scores but aren't excluded)
- **Debuggable**: Score breakdown makes it clear why sections were selected
- **Single-stage efficiency**: Direct section-level scoring eliminates intermediate file selection step

**Threshold settings**:
- Section selection: ≥2 points ensures at least one L2 or L3 match (or two L1 matches)
- This threshold balances precision (avoiding irrelevant sections) with recall (capturing all potentially relevant sections)

# Keyword Search Workflow

Search the knowledge index using keyword matching to find relevant sections.

## Overview

**Executor**: Claude Code (you)

**Input**: User's request (natural language)

**Output**: Candidate sections for section-judgement workflow

**Strategy**: Match keywords from the request against search hints in index.toon

**Tools**:
- Read: Access knowledge/index.toon
- Grep: Search keywords in index.toon
- Bash with jq: Extract section indexes and score sections
- Task: Agent-based section relevance scoring

**Expected tool calls**: 4-6 calls total

**Expected output**: 5-15 relevant sections

## Search Process

### Step 1: Extract Keywords and Match Files

**Extract keywords at two levels**:

1. **L1 (Technical components)**: DAO, JDBC, JPA, Bean Validation, JSON, XML, etc.
2. **L2 (Functional terms)**: ページング, 検索, 登録, 更新, 削除, 接続, コミット, etc.

Include Japanese and English terms, abbreviations, and related concepts for both levels.

**Example**: Request "ページングを実装したい"
- L1: ["DAO", "UniversalDao", "O/Rマッパー", "JDBC"]
- L2: ["ページング", "paging", "per", "page", "limit", "offset"]

**Match keywords against index.toon**:

1. Read knowledge/index.toon
2. Match extracted keywords against hints
3. Score each file:
   - L1 keyword match: +2 points per hint
   - L2 keyword match: +1 point per hint
   - Case-insensitive matching
   - Partial matching (e.g., "ページ" matches "ページング")
4. Sort files by score (descending)
5. Select files with score ≥2
6. Limit to top 10-15 files

**Output format**:
```
File: features/libraries/universal-dao.json, Score: 7, Hints: DAO, O/Rマッパー, ページング
File: features/database/database-access.json, Score: 4, Hints: JDBC, データベース
```

### Step 2: Extract Section Hints (Bash)

**Use bash with jq to extract section hints mechanically**.

Create bash script:
```bash
# Read selected files and extract .index field for each section
for file in <file_paths_from_step1>; do
  jq -r --arg file "$file" \
    '.index | to_entries[] | "\($file)|\(.key)|\(.value.hints | join(","))"' \
    "$file" 2>/dev/null
done
```

**Output format** (one line per section):
```
features/libraries/universal-dao.json|paging|DAO,ページング,per,page,limit,offset
features/libraries/universal-dao.json|overview|DAO,O/Rマッパー,CRUD
features/database/database-access.json|connection|JDBC,接続,Connection
```

Save this output to temporary file for next step.

### Step 3: Agent Judges Relevance (Task Agent)

**Launch Task agent to score section relevance**.

Create JSON input file following `.claude/skills/skill-creator/references/scoring-schema.json`:

```json
{
  "sections": [
    {
      "file_path": "features/libraries/universal-dao.json",
      "section_id": "paging",
      "hints": ["DAO", "ページング", "per", "page", "limit", "offset"],
      "relevance_score": 0,
      "reasoning": ""
    }
  ],
  "query_context": {
    "user_query": "ページングを実装したい",
    "extracted_keywords": {
      "l1": ["DAO", "UniversalDao", "O/Rマッパー"],
      "l2": ["ページング", "paging", "per", "page", "limit", "offset"]
    }
  }
}
```

**Task agent instructions**:

```
Score section relevance for keyword search.

INPUT: JSON file with sections (relevance_score=0, reasoning="")

TASK:
1. Read JSON input file
2. Judge relevance to user_query:
   - Keyword overlap between hints and extracted_keywords
   - Technical component match (L1 keywords in hints)
   - Functional term match (L2 keywords in hints)
3. Assign relevance_score:
   - 3 (high): Multiple L1+L2 matches, directly answers query
   - 2 (medium): Some L1 or L2 matches, partially relevant
   - 1 (low): Weak keyword overlap, tangentially related
   - 0 (not relevant): No meaningful keyword overlap
4. Write brief reasoning (1-2 sentences)
5. Write updated JSON to output file

RULES:
- Score based on keyword overlap only (do not read section content)
- Use hints and extracted_keywords
- Only score 3 if section directly addresses query
- Write valid JSON matching scoring-schema.json format
```

**Agent output**: Updated JSON file with relevance_score and reasoning filled in.

### Step 4: Sort and Filter Results (Bash)

**Use bash with jq to sort and filter mechanically**.

Create bash script:
```bash
# Read agent-scored JSON and filter/sort sections
jq -r '.sections[] | select(.relevance_score >= 2) | "\(.relevance_score)|\(.file_path)|\(.section_id)"' \
  <agent_output_file> | \
  sort -t'|' -k1 -rn | \
  head -20
```

**Output format**:
```
3|features/libraries/universal-dao.json|paging
2|features/libraries/universal-dao.json|overview
2|features/database/database-access.json|connection
```

Select sections with relevance_score ≥2 and limit to top 20 candidates.

### Step 5: Pass to Section-Judgement Workflow

**Format candidates for section-judgement**:

```json
{
  "candidates": [
    {
      "file_path": "features/libraries/universal-dao.json",
      "section": "paging",
      "score": 3,
      "matched_hints": ["DAO", "ページング", "per", "page"]
    }
  ]
}
```

Section-judgement workflow will:
- Read actual section content
- Judge relevance (High=2, Partial=1, None=0)
- Filter out None-relevance sections
- Return 5-15 relevant sections with scores

Use returned sections to answer user's question from knowledge files only.

## Error Handling

**No keyword matches**:
1. Output message: "キーワードがマッチしませんでした"
2. List extracted keywords
3. Show available categories from index.toon

**Too many candidates (>20 after agent scoring)**:
1. Increase file score threshold to ≥3
2. Limit to top 10 files
3. Re-run section extraction and scoring

**Section-judgement returns no results**:
1. Output message: "この情報は知識ファイルに含まれていません"
2. List available knowledge categories from index.toon
3. Do not answer from LLM training data

## Example Execution

**Request**: "ページングを実装したい"

**Step 1: Extract keywords**
- L1: ["DAO", "UniversalDao", "O/Rマッパー"]
- L2: ["ページング", "paging", "per", "page", "limit", "offset"]

**Step 1: Match files**
- universal-dao.json: score=7 (DAO[L1]:2 + O/Rマッパー[L1]:2 + ページング[L2]:1 + paging[L2]:1 + per[L2]:1)
- database-access.json: score=2 (JDBC[L1]:2)
- Selected: universal-dao.json, database-access.json

**Step 2: Extract sections (bash)**
```
features/libraries/universal-dao.json|paging|DAO,ページング,per,page,limit,offset
features/libraries/universal-dao.json|overview|DAO,O/Rマッパー,CRUD
features/libraries/universal-dao.json|crud|DAO,登録,更新,削除
features/database/database-access.json|connection|JDBC,接続,Connection
```

**Step 3: Agent scores relevance**
```json
{
  "sections": [
    {
      "file_path": "features/libraries/universal-dao.json",
      "section_id": "paging",
      "hints": ["DAO", "ページング", "per", "page", "limit", "offset"],
      "relevance_score": 3,
      "reasoning": "Matches L1 keyword DAO and multiple L2 paging keywords, directly addresses query"
    },
    {
      "file_path": "features/libraries/universal-dao.json",
      "section_id": "overview",
      "hints": ["DAO", "O/Rマッパー", "CRUD"],
      "relevance_score": 2,
      "reasoning": "Matches L1 keywords but lacks L2 paging keywords, provides context"
    },
    {
      "file_path": "features/libraries/universal-dao.json",
      "section_id": "crud",
      "hints": ["DAO", "登録", "更新", "削除"],
      "relevance_score": 1,
      "reasoning": "Matches L1 keyword DAO but no L2 paging keywords, tangentially related"
    },
    {
      "file_path": "features/database/database-access.json",
      "section_id": "connection",
      "hints": ["JDBC", "接続", "Connection"],
      "relevance_score": 1,
      "reasoning": "No L2 paging keywords, only L1 component match, not directly relevant"
    }
  ]
}
```

**Step 4: Sort and filter (bash)**
```
3|features/libraries/universal-dao.json|paging
2|features/libraries/universal-dao.json|overview
```

**Step 5: Pass to section-judgement**
- Candidates: paging (score=3), overview (score=2)
- Section-judgement reads content and returns paging as High relevance

**Result**: 1 primary section (paging) with pagination API and examples

## Notes

**L1 and L2 levels**:
- L1 (technical components): Identify specific technology (DAO, JDBC, JPA)
- L2 (functional terms): Identify specific function (ページング, 検索, 登録)

**3-step section scoring**:
- Step 2 (bash): Extract hints mechanically
- Step 3 (agent): Judge relevance with AI
- Step 4 (bash): Sort by scores mechanically

**Scoring weights**:
- File selection: L1=+2, L2=+1
- Section selection: Agent assigns 0-3 based on keyword overlap
- Threshold: relevance_score ≥2 for final candidates

**Performance**:
- Total tool calls: 4-6
- Expected output: 5-15 relevant sections after section-judgement

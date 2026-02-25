# Keyword Search Workflow

Search knowledge base using keyword matching.

## Input

User's query (natural language)

## Output

JSON with candidate sections for section-judgement workflow

## Steps

### Step 1: Extract Keywords

Extract keywords at two levels from user's query:

- **L1 (Technical components)**: DAO, JDBC, UniversalDao, ValidationUtil, DataReader, etc.
- **L2 (Functional terms)**: ページング, 検索, 登録, 更新, 削除, 接続, etc.

Include Japanese, English, abbreviations, and related concepts.

**Example**:
- Query: "ページングを実装したい"
- L1: ["DAO", "UniversalDao", "O/Rマッパー"]
- L2: ["ページング", "paging", "per", "page", "limit", "offset"]

Create JSON:
```json
{
  "query": "ページングを実装したい",
  "keywords": {
    "l1": ["DAO", "UniversalDao", "O/Rマッパー"],
    "l2": ["ページング", "paging", "per", "page", "limit", "offset"]
  }
}
```

### Step 2: Match Files

Execute script to match files and score relevance:

```bash
echo '<json_from_step1>' | .claude/skills/nabledge-6/scripts/extract-file-hints.sh
```

**Script behavior**:
- Reads `knowledge/index.toon`
- Scores each file: L1 keyword match = +2, L2 keyword match = +1
- Sorts by score (descending)
- Filters files with score ≥ 2
- Outputs JSON (conforms to `schemas/file-scoring.json`)

### Step 3: Extract Section Hints

Execute script to extract section hints from selected files:

```bash
echo '<json_from_step2>' | .claude/skills/nabledge-6/scripts/extract-section-hints.sh
```

**Script behavior**:
- Reads `.index` field from each selected file
- Extracts section IDs and hints
- Outputs JSON with sections array (conforms to `schemas/section-scoring.json`)
- Sets `relevance: 0` and `reasoning: ""` for agent scoring

### Step 4: Score Section Relevance

Read JSON from Step 3. For each section, judge relevance based on:
- Keyword overlap between section hints and extracted keywords
- Technical component match (L1 keywords in hints)
- Functional term match (L2 keywords in hints)

Assign relevance score:
- **3 (high)**: Multiple L1+L2 matches, directly answers query
- **2 (medium)**: Some L1 or L2 matches, partially relevant
- **1 (low)**: Weak keyword overlap, tangentially related
- **0 (not relevant)**: No meaningful keyword overlap

Write reasoning (1-2 sentences) for each score.

Update JSON with scores and reasoning. Validate against `schemas/section-scoring.json`.

### Step 5: Sort and Filter

Execute script to sort by relevance and filter:

```bash
echo '<json_from_step4>' | .claude/skills/nabledge-6/scripts/sort-sections.sh
```

**Script behavior**:
- Sorts sections by relevance (descending)
- Filters sections with relevance ≥ 2
- Outputs JSON for section-judgement workflow

Pass output to section-judgement workflow.

## Error Handling

**No keyword matches** (Step 2 returns empty files array):
- Output message: "キーワードがマッチしませんでした"
- List extracted keywords
- Show available categories from index.toon

**No sections after filtering** (Step 5 returns empty sections array):
- Output message: "該当するセクションが見つかりませんでした"
- Continue to section-judgement workflow with empty input

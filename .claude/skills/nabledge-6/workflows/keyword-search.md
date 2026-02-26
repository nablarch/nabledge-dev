# Keyword Search Workflow

Search knowledge base files using keyword matching and return candidate sections.

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

**Tool**: Read

**Action**: Read index.toon and semantically match files based on keywords.

**Agent reads and extracts semantically** - Do NOT use scripts for matching. Agent must use semantic understanding to handle notation variations (表記揺れ) and flexible matching.

1. **Read knowledge/index.toon**:
   ```bash
   # Agent reads using Read tool
   Read tool: .claude/skills/nabledge-6/knowledge/index.toon
   ```
   - Format: `Title, hint1 hint2 ..., path.json`
   - All entries from index.toon
   - Each line: entry title, search hints, file path

2. **Extract all entries**:
   - Parse each line to extract: title, hints, path
   - Build list of all entries

3. **Semantically match entries** (Agent judgment, not script):
   - For each entry, judge if hints semantically match L1/L2 keywords
   - **Prioritize flexible matching**:
     - Japanese/English variations (e.g., "ページング" matches "paging")
     - Abbreviations (e.g., "DAO" matches "UniversalDao")
     - Related terms (e.g., "検索" matches "search", "retrieve", "find")
     - Synonyms and conceptually related terms
   - **Use semantic understanding**, not just exact string matching
   - Consider intent and meaning, not just character matching

4. **Score files** (Agent calculates):
   - L1 keyword match: +2 points per matched hint
   - L2 keyword match: +1 point per matched hint
   - Sum scores for each file
   - Sort by score (descending)

5. **Select top 10 files**:
   - Keep files with score ≥ 2
   - Select top 10 files

**Output format** (structured for next step):
```json
{
  "query": "original query",
  "files": [
    {"path": "knowledge/features/file1.json", "score": 5, "title": "File Title"},
    {"path": "knowledge/features/file2.json", "score": 3, "title": "Another Title"}
  ]
}
```

This structured format enables section extraction in next step.

**Why agent-based matching**:
- Handles notation variations (表記揺れ) automatically
- Flexible semantic understanding
- Adapts to different query phrasings
- Scripts can only do 100% mechanical tasks

### Step 3: Extract Section Hints

**Tool**: Read, Bash with jq

**Action**: Extract section hints from selected files:

1. **For each selected file**, extract `.index` field:
   ```bash
   jq -r '.index' <file_path>
   ```

2. **Collect sections**:
   - Section ID
   - Section hints (for matching)
   - File path

3. **Output**: JSON array with sections (for Step 4 scoring)

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

**Action**: Sort and filter scored sections:

1. **Sort** by relevance score (descending)
2. **Filter** sections with relevance ≥ 2
3. **Output** JSON with candidate sections for section-judgement workflow

Return output to caller.

## Error Handling

**No keyword matches** (Step 2 returns empty files array):
- Output message: "キーワードがマッチしませんでした"
- List extracted keywords
- Show available categories from index.toon

**No sections after filtering** (Step 5 returns empty sections array):
- Output message: "該当するセクションが見つかりませんでした"
- Return empty candidate list to caller

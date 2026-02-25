# Knowledge Search Workflow

Search knowledge base and answer user's query using relevant knowledge only.

## Input

User's query (natural language)

## Output

Answer to user's query using relevant knowledge from knowledge files

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

**Action**: Read index.toon and semantically match files based on keywords:

1. **Read knowledge/index.toon**
   - Format: `Title, hint1 hint2 ..., path.json` (全エントリー)
   - Each line contains entry title, search hints, and file path

2. **Extract matching entries**:
   - For each entry, check if hints semantically match L1/L2 keywords
   - Consider Japanese/English variations and related terms
   - Use flexible matching (not just exact string match)
   - Extract L1 and L2 hints separately

3. **Score files**:
   - L1 keyword match: +2 points per hint
   - L2 keyword match: +1 point per hint
   - Sum scores for each file
   - Sort by score (descending)

4. **Select top candidates**:
   - Keep files with score ≥ 2
   - Select top 10 files

**Output**: List of candidate files with scores

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

Update JSON with scores and reasoning.

### Step 5: Sort and Filter

**Action**: Sort and filter scored sections:

1. **Sort** by relevance score (descending)
2. **Filter** sections with relevance ≥ 2
3. **Select top candidates**: Keep top 20-30 sections

**Output**: JSON with candidate sections

### Step 6: Read Section Content

**Tool**: Bash with jq

**Action**: For each candidate section (up to 10 sections or until finding 5 high-relevance sections):

```bash
jq -r '.sections[<section_id>]' <file_path>
```

Extract only the specified section content. Do not read entire file.

### Step 7: Judge Final Relevance

For each section read, judge relevance based ONLY on actual section content:

**High (2)**: Section directly addresses goal AND contains actionable information (methods, examples, configuration)

**Partial (1)**: Section provides prerequisite knowledge, related functionality, or context

**None (0)**: Section addresses different topic

When in doubt between High and Partial, choose Partial.

**Stop condition**: After reading 10 sections OR finding 5 High-relevance sections, whichever comes first.

### Step 8: Generate Answer

**Action**: Based on High and Partial relevance sections:

1. **Synthesize answer**:
   - Use ONLY information from High/Partial sections
   - Structure answer with clear sections
   - Include code examples if available
   - Cite source sections

2. **Output format** (Japanese):
```markdown
## 回答

[Main answer content synthesized from knowledge sections]

### コード例

[Code examples if available]

### 参考情報

- [File path:section] - [Brief description]
- [File path:section] - [Brief description]
```

3. **If no High sections found**:
```markdown
## 回答

この情報は知識ファイルに含まれていません。

### 関連する情報

以下の情報が見つかりました:
- [Related entry from index.toon]
- [Related entry from index.toon]
```

## Error Handling

**No keyword matches** (Step 2 returns empty files array):
- Output message: "キーワードがマッチしませんでした"
- List extracted keywords
- Show available categories from index.toon

**No sections after filtering** (Step 5 returns empty sections array):
- Output message: "該当するセクションが見つかりませんでした"
- List related available knowledge from index.toon

**No High relevance sections** (Step 7 finds no High sections):
- Output Partial relevance information if available
- Otherwise output "knowledge not found" message

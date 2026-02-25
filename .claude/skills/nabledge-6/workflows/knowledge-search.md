# Knowledge Search Workflow

Search knowledge base and answer user's query using relevant knowledge only.

## Input

User's query (natural language)

## Output

Answer to user's query using relevant knowledge from knowledge files

## Steps

### Step 1: Select Candidate Sections

Follow the workflow in `workflows/keyword-search.md`:

1. Extract keywords from user's query (L1: technical components, L2: functional terms)
2. Match files against knowledge/index.toon using semantic matching
3. Extract sections from matched files
4. Score sections based on keyword overlap
5. Filter and sort to get top candidate sections

**Output**: JSON with candidate sections (conforms to `schemas/section-scoring.json`)

### Step 2: Judge Section Relevance

Follow the workflow in `workflows/section-judgement.md`:

1. Read section content for each candidate (up to 10 sections or until finding 5 High-relevance)
2. Judge relevance based ONLY on actual content:
   - **High (2)**: Directly addresses goal with actionable information
   - **Partial (1)**: Provides prerequisite knowledge or context
   - **None (0)**: Different topic
3. Filter and sort by relevance

**Output**: JSON with relevant sections (High and Partial only)

### Step 3: Generate Answer

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

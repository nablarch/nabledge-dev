# Knowledge Search Workflow

Search knowledge base and answer user's query using relevant knowledge only.

## Input

User's query (natural language)

## Output

Answer to user's query using relevant knowledge from knowledge files

## Steps

### Step 1: Select Candidate Sections

**Execute**: `workflows/keyword-search.md`

Keyword-search workflow handles:
- Extract L1 (technical components) and L2 (functional terms) keywords
- Read index.toon and semantically match files
- Score and select top 10 files
- Extract sections from selected files

**Output**: JSON with candidate sections (conforms to `schemas/section-scoring.json`)

### Step 2: Judge Section Relevance

**Execute**: `workflows/section-judgement.md`

Section-judgement workflow handles:
- Read section content for each candidate
- Judge relevance: High (2), Partial (1), None (0)
- Filter out None relevance
- Sort by relevance (High first, then Partial)

**Output**: JSON with relevant sections (High and Partial only)

### Step 3: Generate Answer

**Input**: Relevant sections from Step 2

**Action**: Generate comprehensive answer in Japanese

**Answer structure**:
1. **Direct answer** (1-2 paragraphs addressing the question)
2. **Implementation steps** (if procedural)
3. **Code examples** (from knowledge files with explanations)
4. **Important notes** (warnings, best practices)
5. **References** (links to knowledge files and sections)

**Output format** (Japanese):
```markdown
## 回答

[Main answer synthesized from High/Partial sections]

### 実装手順

1. [Step 1]
2. [Step 2]

### コード例

\```java
[Code from knowledge files]
\```

[Explanation]

### 重要事項

- [Note 1]
- [Note 2]

### 参照

- [File:section] - [Description]
```

**If no High sections found**:
```markdown
## 回答

この情報は知識ファイルに含まれていません。

### 関連する情報

以下の情報が見つかりました:
- [Related entry from index.toon]
```

**Generation constraints**:
- Use ONLY information from knowledge files
- Never use external knowledge or LLM training data
- Include concrete code examples when available
- Add links to referenced sections

## Error Handling

**No keyword matches**: keyword-search.md handles and outputs message

**No sections after filtering**: section-judgement.md handles and outputs message

**No High relevance sections**:
- Output Partial relevance information if available
- Otherwise output "knowledge not found" message

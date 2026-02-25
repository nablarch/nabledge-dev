---
name: nabledge-6
description: Provides structured knowledge about Nablarch 6 framework (batch processing, RESTful web services, handlers, libraries, tools) and code analysis capabilities. Use when developing Nablarch applications, implementing features, reviewing code, investigating errors, answering questions about Nablarch 6 APIs and patterns, or analyzing existing code to understand its structure and dependencies.
user-invocable: false
disable-model-invocation: true
---

# Nabledge-6: Nablarch 6 Knowledge Base

Structured knowledge base for Nablarch 6 framework, covering batch processing and RESTful web services.

## What this skill provides

**Knowledge Coverage**: Batch, REST, handlers, libraries (UniversalDao, DB access, validation, file I/O, business date), testing (NTF), adapters, security

**Code Analysis**: Dependency tracing, component decomposition, architecture visualization, documentation generation

## How to use

### Basic usage

**Interactive mode** (recommended):
```
nabledge-6
```
Shows friendly greeting and lets you choose between knowledge search and code analysis.

**Direct knowledge search**:
```
nabledge-6 "Your question about Nablarch"
```

**Direct code analysis**:
```
nabledge-6 code-analysis
```

### Important constraint: Knowledge files only

**CRITICAL**: Answer using ONLY information in knowledge files (knowledge/*.json).

- DO NOT use LLM training data or general knowledge about Nablarch
- DO NOT access official websites or external resources during answers
- DO NOT guess or infer information not in knowledge files
- If knowledge is missing: State "この情報は知識ファイルに含まれていません" and list related available knowledge

## Error Handling Policy

**Knowledge not found** (Knowledge Search):
- Message: "この情報は知識ファイルに含まれていません"
- List related available knowledge from index.toon
- Show "not yet created" entries if applicable
- DO NOT use LLM training data

**Target code not found** (Code Analysis):
- Message: "指定されたコードが見つかりませんでした"
- Show search patterns used (e.g., `**/*LoginAction.java`)
- Ask for clarification (more specific file name, module, or full path)

**Workflow execution failure**:
- Inform user which step failed (e.g., "Step 2: 依存関係分析中にエラーが発生しました")
- Show error details
- Suggest retry or alternative

**Output file already exists** (Code Analysis):
- Ask user: "上書きする" / "別名で保存" / "キャンセル"

**Dependency analysis too complex** (Code Analysis):
- Ask user to narrow scope
- Limit to direct dependencies
- Provide partial analysis with note

## How Claude Code should execute this skill

**CRITICAL**: When this skill is invoked, Claude Code MUST execute workflows manually. The skill does NOT automatically process - Claude must follow the workflow steps using tools.

### Execution Process

When you (Claude Code) receive this skill prompt, follow these steps:

#### Step 0: Check arguments and determine workflow

**Decision tree**:

1. **No arguments** (`nabledge-6`):
   - Proceed to Step 1: Show greeting and ask user choice

2. **Argument: "code-analysis"** (`nabledge-6 code-analysis`):
   - Skip to Code Analysis Workflow (Step 3)

3. **Other text arguments** (`nabledge-6 <question>`):
   - Treat argument as user question
   - Skip to Knowledge Search Workflow (Step 2)

#### Step 1: User-friendly greeting (no arguments case only)

**Tool**: AskUserQuestion

**Action**: Show friendly greeting and ask what user wants to do

**Message**:
```
Nablarch 6のことなら何でもお答えします。

以下のようなことが可能です:
- Nablarchの機能や使い方について質問する
  例: UniversalDaoの使い方、バッチ処理の実装方法、トランザクション管理
- 既存コードの構造を理解するためのドキュメントを生成する
  例: LoginActionの構造、プロジェクト全体のアーキテクチャ

何をお手伝いしましょうか？
```

**Options**:
- Option 1: "Nablarchの機能や使い方を知りたい" → Proceed to Step 2 (Knowledge Search)
- Option 2: "既存コードの構造を理解したい" → Proceed to Step 3 (Code Analysis)
- Other (free text input) → Treat as knowledge search question, proceed to Step 2

#### Step 2: Knowledge Search Workflow

Execute when user wants to search Nablarch knowledge.

**Inform user**: "Nablarch知識ベースを検索します"

**Execute workflows**:

1. **keyword-search workflow** (see `workflows/keyword-search.md`):
   - Read knowledge/index.toon
   - Extract keywords (L1: technical components, L2: functional terms)
   - Match against index hints
   - Select files with score ≥2
   - Extract section indexes using jq
   - Build candidates list (20-30 sections)

2. **section-judgement workflow** (see `workflows/section-judgement.md`):
   - Read candidate sections
   - Judge relevance: High (2), Partial (1), None (0)
   - Filter out None
   - Sort by relevance (High first)
   - Return top 10-15 sections

3. **Answer using knowledge files only**:
   - Extract information from High and Partial sections
   - Format as structured answer
   - ONLY use knowledge file information
   - Cite sources (e.g., "universal-dao.json:paging section")
   - DO NOT supplement with LLM training data
   - Priority: Accuracy > Brevity > Completeness

   **Output format**:
   - Target length: 500 tokens (simple queries), 800 tokens (multi-part questions)
   - If exceeds limit: Prioritize 結論 section, reference knowledge files for details
   - Required structure:
     - 結論 (Conclusion): Direct answer
     - 根拠 (Evidence): 1 code example from knowledge files
     - 注意点 (Considerations): Important points or limitations
   - For complex topics: Provide summary + knowledge file path reference
     - Example: "詳しくは knowledge/features/libraries/universal-dao.json#paging を参照"

4. **Handle missing knowledge**:
   - State: "この情報は知識ファイルに含まれていません"
   - List related available knowledge from index.toon
   - DO NOT answer from LLM training data

**Tools**: Read, Grep, Bash with jq
**Expected**: ~10-15 tool calls

#### Step 3: Code Analysis Workflow

Execute when user wants to analyze existing code.

**Entry conditions**:
- User selected Option 2 from Step 1
- Skill invoked with `nabledge-6 code-analysis`

**Inform user**: "既存コードを分析してドキュメントを生成します"

**If target code not specified**: Ask user for target specification using AskUserQuestion

**Execute workflow**:

Follow `workflows/code-analysis.md`:

1. **Identify target and analyze dependencies**:
   - Parse user request (class/feature/package)
   - Find target files using Glob/Grep
   - Read target files, extract dependencies
   - Classify dependencies (project/Nablarch/libraries)
   - Build dependency graph
   - Categorize components by role

2. **Search Nablarch knowledge**:
   - Batch process keyword-search for all Nablarch components
   - Collect relevant knowledge sections

3. **Generate and output documentation**:
   - Read template files
   - Build Mermaid classDiagram and sequenceDiagram
   - Create component summary table
   - Write component details with line references
   - Write Nablarch usage with important points (✅ ⚠️ 💡)
   - Apply template with all placeholders
   - Calculate analysis duration
   - Write file to `.nabledge/YYYYMMDD/code-analysis-<target>.md`
   - Inform user of completion

**Tools**: Read, Glob, Grep, Bash with jq, Write
**Expected**: ~30-50 tool calls, 1 documentation file

### Workflow Files

- `workflows/keyword-search.md`: Keyword-based knowledge search (3 steps)
- `workflows/section-judgement.md`: Relevance judgement for knowledge sections (2 steps)
- `workflows/code-analysis.md`: Existing code analysis and documentation generation (3 steps)

### Template Files

- `assets/code-analysis-template.md`: Documentation template for code analysis output
- `assets/code-analysis-template-guide.md`: Template usage guide (sections, placeholders, evaluation criteria)
- `assets/code-analysis-template-examples.md`: Template examples (component table, Nablarch usage, links)

## Quick reference

**Interactive mode**:
```
nabledge-6
```
Shows greeting → Choose knowledge search or code analysis

**Knowledge search examples**:
```
nabledge-6 "Nablarchでページングを実装したい"
nabledge-6 "UniversalDaoの使い方"
nabledge-6 "トランザクション管理ハンドラのエラー対処"
```
Process: keyword-search → section-judgement → answer using knowledge files only

**Code analysis examples**:
```
nabledge-6 code-analysis
```
Then specify: "LoginActionを理解したい", "proman-batchモジュール全体の構造", etc.
Process: Identify → Analyze → Search knowledge → Generate docs → Output file

## Knowledge structure

**Knowledge files** (JSON format):
- `knowledge/features/`: Handlers, libraries, processing methods, tools, adapters
- `knowledge/checks/`: Security checklist, public API list, deprecated features
- `knowledge/releases/`: Release notes

**Index** (TOON format):
- `knowledge/index.toon`: All entries with search hints

**Human-readable** (auto-generated):
- `docs/`: Markdown version of knowledge files for human verification

Each knowledge file includes:
- `official_doc_urls`: Source URLs for verification
- `index`: Section-level search hints
- `sections`: Structured knowledge by topic

Example: `knowledge/features/libraries/universal-dao.json`

## Advanced usage

**Manual search**:
```bash
grep -i "ページング" knowledge/index.toon
```

**Read specific knowledge**:
```bash
jq '.sections.paging' knowledge/features/libraries/universal-dao.json
```

**Browse human-readable version**:
```bash
cat docs/features/libraries/universal-dao.md
```

## Token efficiency

**Index**: ~5,000-7,000 tokens (TOON format)
**Search results**: ~5,000 tokens (top 10 sections)
**Total**: ~10,000-12,000 tokens

## Version information

**Target version**: Nablarch 6u2 / 6u3

**Out of scope**:
- Jakarta Batch
- Resident batch (table queue)
- Web applications (JSP/UI)
- Messaging (MOM)

## Quality assurance

**Knowledge accuracy**: Average 97.3/100 points (verified against official documentation)

**Coverage**: 17 files created, 43 files planned (total 60 files)

**Source**: Official documentation (https://nablarch.github.io/docs/), Fintan system development guide

## Limitations

### Knowledge coverage

**When knowledge is missing**:
1. State: "この情報は知識ファイルに含まれていません"
2. List related available knowledge
3. Show entry from index.toon with "not yet created" status
4. DO NOT answer from LLM training data
5. ONLY IF EXPLICITLY REQUESTED: Provide official_doc_urls for manual reference

**Current coverage**:
- Nablarch batch processing basics
- Core handlers (DB connection, transaction, data read)
- Core libraries (UniversalDao, database access, file path, business date, data bind)
- Testing framework (NTF) basics
- SLF4J adapter
- Security checklist
- Release notes (6u3)

### Verification

**Human verification**: Check `docs/` directory for human-readable versions. All knowledge includes `official_doc_urls`.

**Accuracy**: Average 97.3/100 points

## Feedback

If knowledge is inaccurate or missing, please:
1. Check `official_doc_urls` in the knowledge file for the source
2. Verify against official documentation
3. Report discrepancies to the knowledge maintainer

## References (for manual lookup only)

**IMPORTANT**: For human users only. Do not access or fetch during answers.

- [Nablarch Official Documentation](https://nablarch.github.io/docs/LATEST/doc/)
- [Fintan System Development Guide](https://fintan.jp/page/252/)
- [Nablarch Example Batch](https://github.com/nablarch/nablarch-example-batch)
- [Nablarch Example REST](https://github.com/nablarch/nablarch-example-rest)

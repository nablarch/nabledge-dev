# Code Analysis Workflow

This workflow analyzes existing code, traces dependencies, and generates structured documentation to help understand the codebase.

## Table of Contents

- [Overview](#overview)
- [Process flow](#process-flow)
  - [Step 1: Identify target and analyze dependencies](#step-1-identify-target-and-analyze-dependencies)
  - [Step 2: Search Nablarch knowledge](#step-2-search-nablarch-knowledge)
  - [Step 3: Generate and output documentation](#step-3-generate-and-output-documentation)
- [Output template](#output-template)
- [Error handling](#error-handling)
- [Best practices](#best-practices)
- [Example execution](#example-execution)

## Overview

**Purpose**: Help users understand existing code by:
1. Identifying target code and tracing dependencies
2. Searching relevant Nablarch knowledge
3. Generating comprehensive documentation

**Input**: User's request (target code specification)

**Output**: Structured documentation file (Markdown + Mermaid diagrams)

**Tools**:
- Read, Glob, Grep: Read and search source files
- Bash with jq: Execute keyword-search workflow
- Write: Generate documentation file

**Expected output**: 1 documentation file (~3,000-10,000 tokens) in .nabledge/YYYYMMDD/

## Process flow

### Step 0: Record start time (CRITICAL)

**Tool**: Bash

**Action**:
```bash
date '+%Y-%m-%d %H:%M:%S'
```

**Output example**: `2026-02-10 14:54:00`

**IMPORTANT**:
- **Write down this timestamp** in your working memory
- You will need it in Step 3.3 to calculate analysis duration
- Format: `Start: YYYY-MM-DD HH:MM:SS`

**Why this matters**: The `{{analysis_duration}}` placeholder must contain the actual elapsed time, not an estimate. Users will compare it against the "Cooked for X" time shown in their IDE.

---

### Step 1: Identify target and analyze dependencies

**Tools**: AskUserQuestion (if needed), Read, Glob, Grep

**Action**:

1. **Parse user request** to understand target scope:
   - Specific class (e.g., "LoginAction")
   - Specific feature (e.g., "ログイン機能")
   - Package (e.g., "web.action配下")

2. **Ask clarifying questions** if scope is unclear

3. **Find target files** using Glob or Grep

4. **Read target files** and extract dependencies:
   - Imports → External dependencies
   - Field types, method parameters → Direct dependencies
   - Method calls → Behavioral dependencies

5. **Classify dependencies**:
   - Project code (proman-*): Trace further
   - Nablarch framework: Note for knowledge search
   - JDK/Jakarta EE: Note but don't trace
   - Third-party libraries: Note but don't trace

6. **Determine trace depth** (ask user if unclear):
   - Default: Trace project code until reaching framework/entities/utilities
   - Stop at Nablarch framework boundaries
   - Stop at Entity classes (pure data objects)

7. **Build dependency graph** (mental model):
   ```
   LoginAction
   ├─→ LoginForm (Form, validation)
   ├─→ SystemAccountEntity (Entity, data)
   ├─→ UniversalDao (Nablarch, database access)
   └─→ ExecutionContext (Nablarch, request context)
   ```

8. **Categorize components** by role:
   - Action/Controller, Form, Entity, Service/Logic, Utility, Handler, Configuration

9. **Identify Nablarch components** for knowledge search:
   - UniversalDao, ValidationUtil, ExecutionContext, Handler chain, etc.

10. **Extract key concepts** for knowledge search:
    - Technical terms: DAO, トランザクション, ハンドラ
    - Operations: 検索, 登録, 更新, バリデーション
    - Patterns: CRUD, pagination, error handling

**Output**: Target files list, dependency graph, component list with Nablarch components identified

### Step 2: Search Nablarch knowledge

**Tools**: Read (index.toon), Bash with jq (keyword-search workflow)

**Action**:

For each Nablarch component identified in Step 1:

1. **Execute keyword-search workflow** (see workflows/keyword-search.md):
   - Use component name + technical terms as keywords
   - Example: "UniversalDao" → ["UniversalDao", "DAO", "データベース", "CRUD"]

2. **Execute section-judgement workflow** (see workflows/section-judgement.md):
   - Judge relevance of each section
   - Keep only High and Partial relevance sections

3. **Collect knowledge** for documentation:
   - API usage patterns
   - Configuration requirements
   - Code examples
   - Error handling
   - Best practices

**Efficiency**: Collect High-relevance sections only (5-10 sections per component). Skip components with no relevant knowledge.

**Output**: Relevant knowledge sections with API usage, patterns, and best practices

### Step 3: Generate and output documentation (progressive)

**Tools**: Read (template files), Write, AskUserQuestion

**Action**:

#### 3.1: Read templates and guide

**MUST READ FIRST**:
```
Read: .claude/skills/nabledge-6/assets/code-analysis-template-basic.md
Read: .claude/skills/nabledge-6/assets/code-analysis-template-extended.md
Read: .claude/skills/nabledge-6/assets/code-analysis-template-references.md
Read: .claude/skills/nabledge-6/assets/code-analysis-template-guide.md
Read: .claude/skills/nabledge-6/assets/code-analysis-template-examples.md
```

**Extract from templates**:
- All `{{placeholder}}` variables
- Section structure and order (DO NOT deviate)
- Component Summary Table format
- Nablarch Usage structure with important points (✅ ⚠️ 💡 🎯 ⚡)
- Link generation rules (relative paths + line references)

#### 3.2: Build documentation content

**Dependency diagram** (Mermaid classDiagram):
```mermaid
classDiagram
    class LoginAction
    class LoginForm
    class UniversalDao {
        <<Nablarch>>
    }

    LoginAction ..> LoginForm : validates
    LoginAction ..> UniversalDao : uses
```

**Key points**:
- Use `classDiagram` syntax (NOT `graph TD`)
- Show class names only (NO methods/fields)
- Show inheritance with `--|>`, dependencies with `..>`
- Mark framework classes with `<<Nablarch>>`

**Component summary table**:
```markdown
| Component | Role | Type | Dependencies |
|-----------|------|------|--------------|
| LoginAction | ログイン処理 | Action | LoginForm, UniversalDao |
```

**Flow description with sequence diagram** (Mermaid sequenceDiagram):
```mermaid
sequenceDiagram
    participant User
    participant Action as LoginAction
    participant DB as Database

    User->>Action: HTTP Request
    Action->>DB: query
    DB-->>Action: result
    Action-->>User: response
```

**Key points**:
- Use `->>` for calls, `-->>` for returns
- Use `alt`/`else` for error handling
- Use `loop` for repetition
- Use `Note over` to explain logic

**Component details**:
- Component name and role
- Key methods with line references (`:42-58` format)
- Dependencies
- File path with relative link + line references

**Nablarch usage** (for each component):
- Class name and description
- Code example
- Important points with prefixes: ✅ Must do / ⚠️ Caution / 💡 Benefit / 🎯 When to use / ⚡ Performance
- Usage in this code
- Knowledge base link

**See detailed examples**: assets/code-analysis-template-examples.md

#### 3.3: Generate and output BASIC documentation first

1. **Determine output path**: `.nabledge/YYYYMMDD/code-analysis-<target-name>.md`

2. **Get current timestamp** (for generation_date and generation_time):
   ```bash
   date '+%Y-%m-%d %H:%M:%S'
   ```
   Extract date and time parts for {{generation_date}} and {{generation_time}}.

3. **Fill BASIC template placeholders** (except {{analysis_duration}}):
   - `{{target_name}}`: Target code name
   - `{{generation_date}}`: Current date (YYYY-MM-DD)
   - `{{generation_time}}`: Current time (HH:MM:SS)
   - `{{analysis_duration}}`: "{{DURATION_PLACEHOLDER}}"  ← 置き換え用マーカー（そのまま）
   - `{{target_description}}`: One-line description
   - `{{modules}}`: Affected modules
   - `{{overview_content}}`: Overview section
   - `{{dependency_graph}}`: Mermaid classDiagram
   - `{{component_summary_table}}`: Component table
   - `{{flow_content}}`: Flow description
   - `{{flow_sequence_diagram}}`: Mermaid sequenceDiagram

4. **Verify basic template compliance**:
   - All basic template sections present
   - Section order matches basic template
   - NO section numbers (1., 2., etc.)
   - NO additional sections outside template
   - All placeholders replaced
   - Relative links with line references

5. **Write BASIC file** using Write tool

6. **Calculate duration and update file** (IMMEDIATE execution after Write):

   **Step 6.1**: Get end time and calculate duration
   ```bash
   date '+%Y-%m-%d %H:%M:%S'
   ```

   - Retrieve start time from Step 0 (stored in working memory)
   - Calculate elapsed time: end time - start time
   - Format as Japanese text:
     - If < 60 seconds: "約{seconds}秒" (e.g., "約30秒", "約45秒")
     - If >= 60 seconds: "約{minutes}分{seconds}秒" (e.g., "約5分18秒", "約2分30秒")
     - Round down to nearest second (don't estimate)

   **Step 6.2**: Replace placeholder using sed
   ```bash
   sed -i 's/{{DURATION_PLACEHOLDER}}/約X分Y秒/g' .nabledge/YYYYMMDD/code-analysis-<target>.md
   ```

   Replace `約X分Y秒` with the actual calculated duration from Step 6.1.

   **IMPORTANT**:
   - Execute Steps 6.1 and 6.2 immediately after Step 5 with no other operations between them
   - If sed fails (permission error, file locked, etc.), inform user of the calculated duration so they can manually edit the file
   - The placeholder will remain in the file if sed fails, but user can update it later

   **Error handling**:
   - If sed fails, inform user: "計算された解析時間は「約X分Y秒」です。sedコマンドが失敗したため、ファイル内の{{DURATION_PLACEHOLDER}}を手動で置き換えてください。"
   - Provide the file path so user knows where to edit
   - The documentation remains valid with the placeholder; user can update it at any time

7. **Inform user**: Show output path, actual duration, and prompt for extended analysis

**Output**: Basic documentation file at .nabledge/YYYYMMDD/code-analysis-<target-name>.md

#### 3.4: Ask user for extended analysis

**Tool**: AskUserQuestion

**Message**:
```
基本的なコード解析が完了しました。

詳細な分析（コンポーネント詳細とNablarchフレームワーク使用パターン）を追加しますか？

- はい: 各コンポーネントの実装詳細とNablarch使用例を追加
- いいえ: 基本解析のみで完了
```

**If user says NO**:
- Ask if they want references section
- If NO to references: Workflow complete, exit
- If YES to references: Proceed to Step 3.6 (references only)

**If user says YES**: Proceed to Step 3.5

#### 3.5: Generate and append EXTENDED documentation

1. **Fill EXTENDED template placeholders**:
   - `{{components_details}}`: Detailed analysis per component with line references
   - `{{nablarch_usage}}`: Framework usage with important points (✅ ⚠️ 💡 🎯 ⚡)

2. **Verify extended template compliance**:
   - All extended template sections present
   - Section order matches extended template
   - NO section numbers (1., 2., etc.)
   - NO additional sections outside template
   - All placeholders replaced
   - Relative links with line references
   - Knowledge base links included

3. **Read current file**:
   ```bash
   Read: .nabledge/YYYYMMDD/code-analysis-<target>.md
   ```

4. **Remove "Note" line from basic output**:
   Remove the line: "**Note**: This is the basic code analysis output. For detailed component analysis and Nablarch usage patterns, request extended analysis."

5. **Append extended content** using Edit tool:
   - Replace the note line with the complete extended template content
   - Preserve all basic content

6. **Inform user**: Extended analysis added

**Output**: Updated file with basic + extended content

#### 3.6: Ask user for references section

**Tool**: AskUserQuestion

**Message**:
```
参照情報（ソースファイル、知識ベース、公式ドキュメントへのリンク）を追加しますか？

- はい: リンクセクションを追加
- いいえ: 現在の状態で完了
```

**If user says NO**: Workflow complete, exit

**If user says YES**: Proceed to Step 3.7

#### 3.7: Generate and append REFERENCES section

1. **Fill REFERENCES template placeholders**:
   - `{{source_files_links}}`: Source file links with relative paths
   - `{{knowledge_base_links}}`: Knowledge base links
   - `{{official_docs_links}}`: Official docs links

2. **Verify references template compliance**:
   - All references template sections present
   - Section order matches references template
   - All placeholders replaced
   - Relative paths correct

3. **Read current file**:
   ```bash
   Read: .nabledge/YYYYMMDD/code-analysis-<target>.md
   ```

4. **Append references content** using Edit tool:
   - Append the complete references template content to the end
   - Preserve all previous content

5. **Inform user**: References section added, workflow complete

**Output**: Complete documentation file at .nabledge/YYYYMMDD/code-analysis-<target-name>.md

## Output template (progressive)

**Template files** (3-part progressive output):
- `.claude/skills/nabledge-6/assets/code-analysis-template-basic.md` - Initial fast output
- `.claude/skills/nabledge-6/assets/code-analysis-template-extended.md` - Detailed analysis (optional)
- `.claude/skills/nabledge-6/assets/code-analysis-template-references.md` - Links section (optional)

**Template guide**: `.claude/skills/nabledge-6/assets/code-analysis-template-guide.md`
**Template examples**: `.claude/skills/nabledge-6/assets/code-analysis-template-examples.md`

**Basic template** (~2000 tokens, generated first):
1. Header (date/time, duration, modules)
2. Overview
3. Architecture (class diagram + component table)
4. Flow (description + sequence diagram)

**Extended template** (~2000 tokens, generated if requested):
5. Components (detailed analysis per component)
6. Nablarch Framework Usage (with important points)

**References template** (~500 tokens, generated if requested):
7. References (source files, knowledge base, official docs)

**Progressive disclosure**: Users get initial results quickly, then decide if they need more detail.

## Error handling

**See SKILL.md "Error Handling Policy" section for comprehensive guidelines.**

Key scenarios:
- **Target code not found**: Ask user for clarification, suggest similar files
- **Dependency analysis too complex**: Ask user to narrow scope
- **Output file already exists**: Ask user whether to overwrite
- **No Nablarch knowledge found**: Note in documentation, proceed with code analysis only

## Best practices

**Template compliance (CRITICAL)**:
- Always read template file before generating content
- Never add section numbers to template sections
- Never add sections outside template structure
- If additional info is valuable, integrate into existing sections as subsections
- Verify compliance before outputting file

**Scope management**:
- Start with narrow scope, expand if needed
- Ask user before expanding beyond initial request
- Clearly document scope boundaries

**Dependency tracing**:
- Stop at framework boundaries
- Stop at Entity classes
- Focus on project-specific code

**Knowledge integration**:
- Only use knowledge from knowledge files
- Cite sources clearly (file + section)
- Don't supplement with external knowledge

**Documentation quality**:
- Keep explanations concise
- Use diagrams for complex relationships
- Provide actionable information
- Link to sources for deep dives

## Example execution

**User request**: "LoginActionを理解したい"

**Step 0**: Record start time
- Start: 2026-02-10 14:54:00

**Step 1**: Identify target and analyze
- Target: LoginAction.java
- Dependencies: LoginForm, SystemAccountEntity, UniversalDao, ExecutionContext
- Components: Action (LoginAction), Form (LoginForm), Entity (SystemAccountEntity), Nablarch (UniversalDao, ExecutionContext)

**Step 2**: Search Nablarch knowledge
- UniversalDao → universal-dao.json:overview, crud sections
- Bean Validation → data-bind.json:validation section

**Step 3.1-3.2**: Read templates and build content
- Read basic, extended, references templates
- Build classDiagram and sequenceDiagram
- Create component summary table

**Step 3.3**: Generate BASIC output
- Apply basic template with placeholders
- Output: .nabledge/20260210/code-analysis-login-action.md (Overview + Architecture + Flow)
- Duration: 約46秒
- User sees initial results quickly

**Step 3.4**: Ask user for extended analysis
- User says: はい

**Step 3.5**: Generate EXTENDED output
- Write component details with line references
- Write Nablarch usage with important points (✅ ⚠️ 💡)
- Append to existing file

**Step 3.6**: Ask user for references
- User says: はい

**Step 3.7**: Generate REFERENCES output
- Add source files, knowledge base, official docs links
- Append to existing file

**Summary**: 5 components, 2 diagrams, 2 Nablarch knowledge sections, progressive output (basic ~46秒, extended if requested)

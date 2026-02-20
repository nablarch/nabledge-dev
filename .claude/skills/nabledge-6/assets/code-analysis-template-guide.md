# Code Analysis Template Guide

This guide explains how to use the code analysis documentation template (progressive 3-part format).

## Template Files (Progressive Output)

**Location**: `.claude/skills/nabledge-6/assets/`

The templates provide a 3-part progressive format for faster initial results:

1. **code-analysis-template-basic.md** - Initial fast output (~2000 tokens, ~20 seconds LLM output)
2. **code-analysis-template-extended.md** - Detailed analysis (~2000 tokens, optional, ~20 seconds LLM output)
3. **code-analysis-template-references.md** - Links section (~500 tokens, optional, ~5 seconds LLM output)

## Template Sections

**Basic template** (generated first):
1. **Header**: Target name, generation date/time, analysis duration, modules
2. **Overview**: Purpose and high-level architecture
3. **Architecture**: Mermaid class diagram + component summary table
4. **Flow**: Processing flow description + Mermaid sequence diagram

**Extended template** (generated if user requests):
5. **Components**: Detailed analysis for each component
   - File location with relative link
   - Role description
   - Key methods with line references
   - Dependencies
   - Nablarch knowledge excerpts
   - Key implementation points
6. **Nablarch Framework Usage**: Framework-specific usage patterns

**References template** (generated if user requests):
7. **References**: Links to source files, knowledge files, official docs

## Key Features

- **Mermaid diagrams**: Class diagram (relationships) and sequence diagram (timeline)
- **Relative links**: Links to source files and knowledge files use relative paths
- **Line references**: Method locations include line number ranges (e.g., `L42-58`)
- **Knowledge excerpts**: Relevant Nablarch knowledge quoted from knowledge files
- **Structured format**: Consistent sections across all analyses

## Placeholders

Replace the following placeholders with actual content (using `{{variable}}` format):

### Header Section

- `{{target_name}}`: Name of analyzed code/feature (e.g., "LoginAction", "ログイン機能")
- `{{generation_date}}`: Current date in YYYY-MM-DD format (e.g., "2026-02-10")
- `{{generation_time}}`: Current time in HH:MM:SS format (e.g., "14:30:15")
- `{{DURATION_PLACEHOLDER}}`: Temporary marker for analysis duration (two-step replacement process)
  - **Step 1 (during Write)**: Keep as "{{DURATION_PLACEHOLDER}}" (literal placeholder string)
  - **Step 2 (after Write via sed)**: Replace with actual duration "約2分30秒", "約45秒", etc.
  - **Why two steps**: Ensures duration includes the Write operation itself, matching the "Baked for" time shown in IDE
  - **Note**: The metadata field name is `{{analysis_duration}}`, but we use `{{DURATION_PLACEHOLDER}}` as the temporary marker during generation
- `{{target_description}}`: One-line description of the target
- `{{modules}}`: Affected modules (e.g., "proman-web, proman-common")

### Overview Section

- `{{overview_content}}`: Purpose and high-level architecture

### Architecture Section

- `{{dependency_graph}}`: Mermaid classDiagram syntax (class names only, show relationships)
- `{{component_summary_table}}`: Markdown table of components

### Flow Section

- `{{flow_content}}`: Request/response flow description text
- `{{flow_sequence_diagram}}`: Mermaid sequenceDiagram syntax (processing flow with timeline)

### Components Section

- `{{components_details}}`: Detailed analysis for each component (numbered sections)

### Nablarch Framework Usage Section

- `{{nablarch_usage}}`: Framework-specific usage patterns

### References Section

- `{{source_files_links}}`: List of source file links with relative paths
- `{{knowledge_base_links}}`: List of knowledge base links (`.claude/skills/nabledge-6/docs`)
- `{{official_docs_links}}`: List of official Nablarch documentation links

## Usage Instructions (Progressive Output)

### Step 1: Read All Template Files

Read all three template files to understand the structure:

```bash
Read: .claude/skills/nabledge-6/assets/code-analysis-template-basic.md
Read: .claude/skills/nabledge-6/assets/code-analysis-template-extended.md
Read: .claude/skills/nabledge-6/assets/code-analysis-template-references.md
```

### Step 2: Build Content for BASIC Placeholders

Based on analysis results from workflow Steps 0-2, build content for basic placeholders:

1. **Header placeholders**: Use current timestamp ({{DURATION_PLACEHOLDER}} stays as-is)
2. **Overview**: Summarize purpose and architecture
3. **Architecture diagrams**: Generate Mermaid classDiagram (class names only)
4. **Architecture table**: Create component summary table
5. **Flow description**: Describe processing flow
6. **Flow diagram**: Generate Mermaid sequenceDiagram (with phases)

### Step 3: Generate BASIC Output

**Step 3.1**: Replace placeholders in basic template (except duration)

Replace all `{{variable}}` placeholders with actual content, EXCEPT {{DURATION_PLACEHOLDER}}.

**IMPORTANT**: Leave {{DURATION_PLACEHOLDER}} as-is. It will be replaced after Write completes.

**Step 3.2**: Write basic output file

Use Write tool to create the documentation file:

```
file_path: .nabledge/YYYYMMDD/code-analysis-<target>.md
content: [Generated basic documentation with {{DURATION_PLACEHOLDER}} still present]
```

**Step 3.3**: Calculate and replace duration

**IMMEDIATELY after Write completes**:

**Step 3.3.1**: Get end time and calculate duration
```bash
date '+%Y-%m-%d %H:%M:%S'
```
- Calculate elapsed time from Step 0 start time
- Format as Japanese text (e.g., "約5分18秒")

**Step 3.3.2**: Replace placeholder using sed
```bash
sed -i 's/{{DURATION_PLACEHOLDER}}/約5分18秒/g' .nabledge/YYYYMMDD/code-analysis-<target>.md
```

**Error handling**:
- If sed fails, inform user of the calculated duration
- User can manually edit the file to replace {{DURATION_PLACEHOLDER}}
- The documentation remains valid even with the placeholder

**Why this matters**: This ensures the analysis duration includes all work including the Write operation itself, providing accurate timing that matches the "Baked for" time shown in the IDE.

### Step 4: Ask User for Extended Analysis

Use AskUserQuestion tool:

```
基本的なコード解析が完了しました。

詳細な分析（コンポーネント詳細とNablarchフレームワーク使用パターン）を追加しますか？

- はい: 各コンポーネントの実装詳細とNablarch使用例を追加
- いいえ: 基本解析のみで完了
```

**If NO**: Skip to Step 6 (ask for references)

**If YES**: Proceed to Step 5

### Step 5: Generate EXTENDED Output

**Step 5.1**: Build content for extended placeholders

1. **Components details**: Write detailed analysis with line references
2. **Nablarch usage**: Extract framework usage patterns with important points (✅ ⚠️ 💡 🎯 ⚡)

**Step 5.2**: Replace placeholders in extended template

Replace all `{{variable}}` placeholders with actual content.

**Step 5.3**: Read current file and append extended content

```bash
Read: .nabledge/YYYYMMDD/code-analysis-<target>.md
```

Use Edit tool to remove the note line and replace with extended content:
- Remove: "**Note**: This is the basic code analysis output. For detailed component analysis and Nablarch usage patterns, request extended analysis."
- Replace with: Complete extended template content

### Step 6: Ask User for References

Use AskUserQuestion tool:

```
参照情報（ソースファイル、知識ベース、公式ドキュメントへのリンク）を追加しますか？

- はい: リンクセクションを追加
- いいえ: 現在の状態で完了
```

**If NO**: Workflow complete, exit

**If YES**: Proceed to Step 7

### Step 7: Generate REFERENCES Output

**Step 7.1**: Build content for references placeholders

1. **Source files links**: Build relative file path links
2. **Knowledge base links**: Link to relevant knowledge files
3. **Official docs links**: Link to official Nablarch documentation

**Step 7.2**: Replace placeholders in references template

Replace all `{{variable}}` placeholders with actual content.

**Step 7.3**: Read current file and append references content

```bash
Read: .nabledge/YYYYMMDD/code-analysis-<target>.md
```

Use Edit tool to append references content to the end of the file.

## Example Placeholder Values

### Example: ExportProjectsInPeriodAction

```
{{target_name}} = "ExportProjectsInPeriodAction"
{{generation_date}} = "2026-02-10"
{{generation_time}} = "14:30:15"
{{DURATION_PLACEHOLDER}} = "約2分" (replaced after Write completes)
{{target_description}} = "期間内プロジェクト一覧出力バッチアクション"
{{modules}} = "proman-batch"
```

### {{component_summary_table}}

```markdown
| Component | Role | Type | Dependencies |
|-----------|------|------|--------------|
| ExportProjectsInPeriodAction | CSV出力バッチアクション | Action | DatabaseRecordReader, ObjectMapper, FilePathSetting |
| ProjectDto | プロジェクト情報DTO | Bean | なし |
| FIND_PROJECT_IN_PERIOD | 期間内プロジェクト検索SQL | SQL | なし |
```

### {{nablarch_usage}}

For each Nablarch component, include:
1. **クラス名**: Full class name
2. **説明**: Brief description
3. **使用方法**: Code example
4. **重要ポイント**: Critical points (why use, gotchas, performance)
5. **このコードでの使い方**: How it's used in analyzed code
6. **詳細**: Link to knowledge base

**Example** (one component - repeat for each Nablarch component used):

```markdown
### ObjectMapper

**クラス**: `nablarch.common.databind.ObjectMapper`

**説明**: CSVやTSV、固定長データをJava Beansとして扱う機能を提供する

**使用方法**:
\`\`\`java
ObjectMapper<ProjectDto> mapper = ObjectMapperFactory.create(ProjectDto.class, outputStream);
mapper.write(dto);
mapper.close();
\`\`\`

**重要ポイント**:
- ✅ **必ず`close()`を呼ぶ**: バッファをフラッシュし、リソースを解放する（`terminate()`で実施）
- ⚠️ **大量データ処理時**: メモリに全データを保持しないため、大量データでも問題なく処理可能
- ⚠️ **型変換の制限**: `EntityUtil`と同様に、型変換が必要な項目は個別設定が必要
- 💡 **アノテーション駆動**: `@Csv`, `@CsvFormat`でフォーマットを宣言的に定義できる

**このコードでの使い方**:
- `initialize()`でProjectDto用のObjectMapperを生成
- `handle()`で各レコードを`mapper.write(dto)`で出力
- `terminate()`で`mapper.close()`してリソース解放

**詳細**: [データバインド知識ベース](../../.claude/skills/nabledge-6/docs/features/libraries/data-bind.md)
```

### {{knowledge_base_links}}

```markdown
- [Nablarchバッチ処理](../../.claude/skills/nabledge-6/docs/features/processing/nablarch-batch.md) - BatchActionの詳細、DB to FILEパターン
- [データバインド](../../.claude/skills/nabledge-6/docs/features/libraries/data-bind.md) - ObjectMapperの詳細仕様
- [業務日付管理](../../.claude/skills/nabledge-6/docs/features/libraries/business-date.md) - BusinessDateUtilの使い方
- [ファイルパス管理](../../.claude/skills/nabledge-6/docs/features/libraries/file-path-management.md) - FilePathSettingの設定方法
```

### {{official_docs_links}}

```markdown
- [Nablarchバッチ処理](https://nablarch.github.io/docs/LATEST/doc/application_framework/application_framework/batch/index.html)
- [データバインド](https://nablarch.github.io/docs/LATEST/doc/application_framework/application_framework/libraries/data_io/data_bind.html)
- [業務日付管理](https://nablarch.github.io/docs/LATEST/doc/application_framework/application_framework/libraries/system_utility/business_date.html)
```

## Tips

### Diagram Generation

**Class Diagram**:
- Keep it simple: class names only
- Use `--|>` for inheritance (extends/implements)
- Use `..>` for dependencies (uses/creates)
- Mark framework classes with `<<Nablarch>>` stereotype

**Sequence Diagram**:
- Use `participant` to define actors/components
- Use `->>` for synchronous calls
- Use `-->>` for return values
- Use `alt`/`else` for error handling
- Use `loop` for repetitive operations
- Add `Note` to explain phases

### Link Generation

Use relative paths from the output file location:

```
Output: .nabledge/20260210/code-analysis-login-action.md
Source: proman-web/src/main/java/com/nablarch/example/proman/web/action/LoginAction.java
Link: ../../proman-web/src/main/java/com/nablarch/example/proman/web/action/LoginAction.java
```

## See Also

- **Template Files**:
  - `assets/code-analysis-template-basic.md` - Basic output
  - `assets/code-analysis-template-extended.md` - Extended output
  - `assets/code-analysis-template-references.md` - References output
- **Workflow**: `workflows/code-analysis.md`
- **Skill Definition**: `SKILL.md`

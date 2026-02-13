# Nabledge-6-Test: Test Execution and Evaluation Skill

Automated test execution and evaluation skill for nabledge-6, enabling continuous improvement through systematic scenario testing.

## Overview

This skill executes test scenarios defined in `.claude/skills/nabledge-6/tests/scenarios.json` and evaluates them against structured criteria. It generates detailed reports with improvement recommendations to help continuously improve the nabledge-6 skill.

## Features

- **Execute individual scenarios**: Test specific scenarios by ID
- **Execute all scenarios**: Run complete test suite with summary report
- **Execute by category**: Test specific categories (handlers, libraries, tools, etc.)
- **Generate new scenarios**: Dynamically create new test scenarios
- **Structured evaluation**: Systematic evaluation against defined criteria
- **Detailed reporting**: Comprehensive reports with actionable improvement suggestions
- **Monitoring**: Track tool calls, token usage, and workflow execution

## Usage

### Quick Start

**Interactive mode** (recommended for first-time users):
```
nabledge-6-test
```

This shows a menu with all available options.

### Execute Single Scenario

```
nabledge-6-test execute <scenario-id>
```

**Examples**:
```
nabledge-6-test execute handlers-001
nabledge-6-test execute libraries-001
nabledge-6-test execute code-analysis-001
```

**Output**:
- Real-time execution of the scenario
- Evaluation against criteria
- Detailed report in `work/YYYYMMDD/test-{scenario-id}-{timestamp}.md`

### Execute All Scenarios

```
nabledge-6-test execute-all
```

**What it does**:
- Loads all 30 scenarios from scenarios.json
- Executes each scenario sequentially
- Generates individual reports for each
- Creates summary report with statistics and recommendations

**Output**:
- Summary report in `work/YYYYMMDD/test-summary-{timestamp}.md`
- Individual reports for each scenario
- Console summary with pass/fail statistics

**Duration**: Approximately 30-60 minutes for all scenarios

### Execute Category

```
nabledge-6-test execute-category <category>
```

**Available categories**:
- `handlers` (5 scenarios)
- `libraries` (5 scenarios)
- `tools` (5 scenarios)
- `processing` (5 scenarios)
- `adapters` (5 scenarios)
- `code-analysis` (5 scenarios)

**Example**:
```
nabledge-6-test execute-category handlers
```

### Generate New Scenario

```
nabledge-6-test generate-scenario
```

**Interactive process**:
1. Select category
2. Choose existing knowledge file or create custom question
3. Define expected keywords and sections
4. **Choose whether to generate standalone skill** (using skill-creator)
5. Preview generated scenario
6. Confirm to add to scenarios.json
7. If standalone skill requested, generate test skill with skill-creator
8. Optionally execute immediately

**Standalone skill generation**:
- Uses **skill-creator** from Anthropic's skills repository
- Generates a dedicated skill (e.g., `test-handlers-006`) for the scenario
- Enables quick execution via `/test-{scenario-id}`
- Requires skill-creator to be installed (see below)

**Installing skill-creator**:

The Anthropic Skills marketplace is already configured in this project's `.claude/settings.json`.

When you open this project, Claude Code will prompt you to install the marketplace. After that:

```
/plugin install example-skills@anthropic-agent-skills
```

See `INSTALL-SKILL-CREATOR.md` for detailed installation instructions.

## Evaluation Criteria

Each scenario is evaluated against these criteria:

### For Knowledge Search Scenarios

1. **Workflow Execution** (Pass/Fail)
   - keyword-search workflow executed
   - section-judgement workflow executed
   - Appropriate tools used (Read, Bash+jq)

2. **Keyword Matching** (Score: 0-100%)
   - Expected keywords present in response
   - Pass threshold: ≥80%

3. **Section Relevance** (Pass/Fail)
   - Expected sections identified
   - High-relevance sections prioritized
   - Irrelevant sections filtered out

4. **Knowledge File Only** (Pass/Fail)
   - Only knowledge file content used
   - No LLM training data or external knowledge
   - Proper "not found" message if knowledge missing

5. **Token Efficiency** (Pass/Fail)
   - Target: 5,000-15,000 tokens per query
   - Check if within range

6. **Tool Call Efficiency** (Pass/Fail)
   - Target: 10-20 tool calls per query
   - Check if within range

### For Code Analysis Scenarios

All above criteria plus:

7. **Code Analysis Workflow** (Pass/Fail)
   - Target code identified correctly
   - Dependencies analyzed appropriately
   - Components decomposed properly
   - Related Nablarch knowledge searched
   - Documentation generated (Markdown + Mermaid)
   - Source code and knowledge file links included

8. **Code Analysis Output Quality** (Pass/Fail)
   - Expected sections present (Overview, Architecture, Components, Flow, Nablarch Framework Usage)
   - Mermaid diagrams generated appropriately
   - Component explanations clear
   - Links correct
   - Expected components documented
   - Expected knowledge referenced

## Report Structure

### Single Scenario Report

Generated in `work/YYYYMMDD/test-{scenario-id}-{timestamp}.md`

**Contents**:
- Scenario details (question, expected keywords, sections)
- Execution summary (duration, token usage, tool calls)
- Evaluation results for each criterion (Pass/Fail, scores, observations)
- Response analysis
- Improvement suggestions
- Overall assessment

### Summary Report

Generated in `work/YYYYMMDD/test-summary-{timestamp}.md` when executing multiple scenarios

**Contents**:
- Overall statistics (pass rate, average token usage, average tool calls)
- Results by category (tables with detailed metrics)
- Common issues (grouped by frequency and impact)
- Top improvement recommendations (prioritized)
- Links to individual scenario reports
- Trend analysis (if multiple test runs available)
- Next steps

## Test Scenarios

The skill uses scenarios defined in `.claude/skills/nabledge-6/tests/scenarios.json`.

**Current scenarios**: 30 scenarios across 6 categories

**Categories**:
- **handlers** (5): Transaction management, DB connection, data reading
- **libraries** (5): UniversalDao, database access, file path, business date, data bind
- **tools** (5): NTF (test framework), assertions, test data
- **processing** (5): Nablarch batch architecture and implementation
- **adapters** (5): SLF4J logging adapter
- **code-analysis** (5): Code structure analysis, dependency tracing, documentation generation

**Scenario structure**:
```json
{
  "id": "handlers-001",
  "category": "handlers",
  "file": "handlers/batch/data-read-handler.json",
  "question": "データリードハンドラでファイルを読み込むにはどうすればいいですか？",
  "expected_keywords": ["DataReadHandler", "DataReader", "ファイル読み込み"],
  "expected_sections": ["overview", "usage"],
  "relevance": "high"
}
```

## Use Cases

### 1. Validate Changes

After updating nabledge-6 skill or knowledge files:
```
nabledge-6-test execute-all
```

Compare results with previous test runs to ensure no regressions.

### 2. Continuous Improvement

Regularly run tests to identify improvement areas:
```
nabledge-6-test execute-all
```

Review improvement suggestions in the summary report and prioritize actions.

### 3. Category-Specific Testing

After updating knowledge files in a specific category:
```
nabledge-6-test execute-category handlers
```

### 4. Scenario-Level Debugging

When a specific scenario fails:
```
nabledge-6-test execute handlers-001
```

Review detailed report to understand why it failed.

### 5. Expand Test Coverage

Add new scenarios for newly created knowledge files:
```
nabledge-6-test generate-scenario
```

## Examples

### Example 1: Execute Single Scenario

```
$ nabledge-6-test execute handlers-001

シナリオ handlers-001 を実行します: データリードハンドラでファイルを読み込むにはどうすればいいですか？

[nabledge-6 executes...]

評価中...

✓ Scenario handlers-001: PASS (5/6 criteria)

Report: work/20260213/test-handlers-001-143052.md

Improvement suggestions:
1. Token usage was 18,234 (above target 15,000) - consider optimizing section extraction
2. Tool calls were 23 (above target 20) - some redundant jq operations detected

実行が完了しました。詳細は上記のレポートファイルをご確認ください。
```

### Example 2: Execute All Scenarios

```
$ nabledge-6-test execute-all

30個のシナリオを実行します。
カテゴリ: handlers (5), libraries (5), tools (5), processing (5), adapters (5), code-analysis (5)

実行を開始しますか？ (はい/いいえ): はい

[1/30] handlers-001: PASS (5/6) ✓
[2/30] handlers-002: FAIL (3/6) ✗
[3/30] handlers-003: PASS (6/6) ✓
...
[30/30] code-analysis-005: PASS (7/8) ✓

テスト実行完了

結果: 24/30 passed (80%)
レポート: work/20260213/test-summary-143052.md

優先度の高い改善提案:
1. キーワードマッチング率の改善 (5シナリオで80%未満)
2. トークン使用量の最適化 (8シナリオで15,000超過)
3. セクション判定精度の向上 (3シナリオで期待セクション未検出)

詳細は上記のレポートファイルをご確認ください。
```

### Example 3: Generate New Scenario

```
$ nabledge-6-test generate-scenario

新しいテストシナリオを生成します。

1. カテゴリを選択してください:
   - handlers
   - libraries
   - tools
   - processing
   - adapters
   - code-analysis

カテゴリ: handlers

2. 既存の知識ファイルを使用しますか、それとも新しい質問を作成しますか？
   - 既存の知識ファイルから生成
   - 新しい質問を手動入力

選択: 1

利用可能な知識ファイル:
- data-read-handler.json
- transaction-management-handler.json
- db-connection-management-handler.json

ファイル: data-read-handler.json

[Reads file and suggests questions...]

生成されたシナリオをプレビューしますか？ (はい/いいえ): はい

{
  "id": "handlers-006",
  "category": "handlers",
  "file": "handlers/batch/data-read-handler.json",
  "question": "データリードハンドラのエラーハンドリングはどうすればいいですか？",
  "expected_keywords": ["DataReadHandler", "エラーハンドリング", "例外処理"],
  "expected_sections": ["error-handling", "exception"],
  "relevance": "high"
}

このシナリオを scenarios.json に追加しますか？ (はい/いいえ): はい

シナリオを追加しました。

このシナリオをすぐに実行しますか？ (はい/いいえ): はい

[Executes scenario...]
```

## Best Practices

### 1. Run Tests Regularly

- After knowledge file updates
- After skill workflow changes
- Before major releases
- Weekly for continuous monitoring

### 2. Review Reports Thoroughly

- Don't just look at pass/fail
- Read observations for insights
- Prioritize improvement suggestions
- Track trends over time

### 3. Use Category Testing for Focused Improvements

- Update handlers knowledge → test handlers category
- Update libraries knowledge → test libraries category

### 4. Expand Test Coverage

- Add scenarios for new knowledge files
- Cover edge cases
- Test error conditions

### 5. Keep Scenarios Up-to-Date

- Update expected_keywords when knowledge files change
- Update expected_sections when file structure changes
- Remove scenarios for deprecated features

## Troubleshooting

### Scenario Execution Fails

**Symptom**: Scenario fails with error message

**Solution**:
1. Check if knowledge file exists
2. Verify scenario JSON is valid
3. Review nabledge-6 skill for issues
4. Check detailed report for error details

### Token Usage Exceeds Target

**Symptom**: Many scenarios fail token efficiency criteria

**Solution**:
1. Review section extraction logic in nabledge-6
2. Consider reading smaller chunks
3. Optimize jq queries
4. Check for unnecessary file reads

### Low Keyword Matching Scores

**Symptom**: Keyword matching below 80% threshold

**Solution**:
1. Review expected_keywords - may be too broad
2. Check if knowledge file contains expected information
3. Update keywords to match actual file content
4. Improve keyword search workflow

### Section Relevance Failures

**Symptom**: Expected sections not identified

**Solution**:
1. Verify section names in knowledge file
2. Check if sections actually exist
3. Update expected_sections to match file structure
4. Improve section-judgement workflow

## Contributing

To contribute new scenarios or improve the skill:

1. **Add new scenarios**: Use `nabledge-6-test generate-scenario`
2. **Update scenarios.json**: Manually edit to refine scenarios
3. **Update evaluation criteria**: Modify SKILL.md if criteria change
4. **Improve report templates**: Edit templates in `templates/`

## File Structure

```
.claude/skills/nabledge-6-test/
├── SKILL.md                              # Skill definition and workflows
├── README.md                             # This file
└── templates/
    ├── single-scenario-report.md         # Template for single scenario reports
    ├── summary-report.md                 # Template for summary reports
    └── code-analysis-report.md           # Template for code analysis reports
```

## Version History

- **1.0.0** (2026-02-13): Initial release
  - Execute single scenario
  - Execute all scenarios
  - Execute by category
  - Generate new scenarios
  - Structured evaluation framework
  - Detailed reporting
  - skill-creator integration for dynamic skill generation

## skill-creator Integration

This skill integrates with **skill-creator** from Anthropic's official skills repository to enable dynamic generation of standalone test skills.

### What is skill-creator?

skill-creator is an Anthropic-provided skill that helps create new skills with:
- **Skill initialization**: Generate skill templates
- **Skill packaging**: Package skills as .skill files
- **Design guidance**: Best practices for token efficiency and reusability

### Installation

**This project already includes marketplace configuration!**

The Anthropic Skills marketplace is pre-configured in `.claude/settings.json`. When you open this project:

1. **Claude Code will prompt you** to install the marketplace (first time only)
2. **Approve the marketplace installation**
3. **Install the plugin**:
   ```
   /plugin install example-skills@anthropic-agent-skills
   ```
4. **Verify Installation**:
   ```bash
   ls ~/.claude/plugins/*/skills/skill-creator/
   ```

See `INSTALL-SKILL-CREATOR.md` for detailed instructions and troubleshooting.

### Usage in nabledge-6-test

When generating a new scenario, you can optionally create a standalone test skill:

```
nabledge-6-test generate-scenario
→ Select category
→ Define scenario details
→ Choose "はい" when asked about standalone skill generation
→ skill-creator generates test-{scenario-id} skill
→ Use /test-{scenario-id} to run the test anytime
```

### Benefits of Standalone Skills

1. **Quick Access**: Run specific tests with `/test-{scenario-id}`
2. **Encapsulation**: Each test is self-contained
3. **Reusability**: Share specific test skills with team
4. **Customization**: Modify individual test behavior without affecting others
5. **Distribution**: Package and distribute via plugins

### Generated Skills Example

After generating a standalone skill for handlers-006:

```
.claude/skills/test-handlers-006/
├── SKILL.md              # Skill definition
└── scripts/              # Helper scripts (optional)
    └── execute_test.py
```

**Usage**:
```
/test-handlers-006
```

Or mention it:
```
Use test-handlers-006 to run the test
```

### Without skill-creator

If skill-creator is not installed, the skill will:
- Still add scenarios to scenarios.json
- Execute tests via `nabledge-6-test execute {scenario-id}`
- Skip standalone skill generation

### More Information

- [skill-creator on GitHub](https://github.com/anthropics/skills/tree/main/skills/skill-creator)
- [Anthropic Skills Repository](https://github.com/anthropics/skills)
- [Installation Guide](./INSTALL-SKILL-CREATOR.md)

## Related Documentation

- [Nabledge-6 Skill](../nabledge-6/SKILL.md)
- [Test Scenarios](../nabledge-6/tests/scenarios.json)
- [Test Scenarios Documentation](../nabledge-6/tests/scenarios.md)
- [Test Scenarios README](../nabledge-6/tests/README.md)

## Support

For issues or questions:
- Review detailed reports for insights
- Check troubleshooting section above
- Review related documentation
- Open an issue in the repository

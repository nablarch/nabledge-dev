---
name: nabledge-6-test
description: Executes and evaluates nabledge-6 test scenarios to continuously improve the skill. Runs test scenarios from scenarios.json, monitors execution, evaluates results against criteria, and generates structured reports with improvement recommendations.
---

# Nabledge-6-Test: Test Execution and Evaluation

Test execution and evaluation skill for nabledge-6, enabling automated scenario testing and continuous improvement.

## What this skill provides

**Capabilities**:
- Execute individual or all test scenarios from scenarios.json
- Monitor workflow execution (tool calls, token usage, workflow steps)
- Evaluate results against defined criteria
- Generate structured evaluation reports with improvement suggestions
- Support dynamic test scenario generation

**Use cases**:
- Validate nabledge-6 skill changes
- Continuous improvement through systematic evaluation
- Regression testing after knowledge file updates
- Performance monitoring (token usage, tool call efficiency)

## How to use

### Basic usage

**Execute single scenario**:
```
nabledge-6-test execute <scenario-id>
```
Example: `nabledge-6-test execute handlers-001`

**Execute all scenarios**:
```
nabledge-6-test execute-all
```

**Execute by category**:
```
nabledge-6-test execute-category <category>
```
Example: `nabledge-6-test execute-category handlers`

**Generate new scenario**:
```
nabledge-6-test generate-scenario
```

**Interactive mode**:
```
nabledge-6-test
```
Shows menu with options.

## How Claude Code should execute this skill

When this skill is invoked, Claude Code must execute workflows manually using available tools.

### Execution Process

#### Step 0: Parse arguments and determine workflow

**Decision tree**:

1. **No arguments** (`nabledge-6-test`):
   - Show menu with options:
     - Execute single scenario
     - Execute all scenarios
     - Execute category
     - Generate new scenario
     - Exit
   - Get user choice and proceed

2. **Argument: "execute <scenario-id>"**:
   - Execute single scenario workflow (Step 1)

3. **Argument: "execute-all"**:
   - Execute all scenarios workflow (Step 2)

4. **Argument: "execute-category <category>"**:
   - Execute category scenarios workflow (Step 3)

5. **Argument: "generate-scenario"**:
   - Generate scenario workflow (Step 4)

---

## Workflow 1: Execute Single Scenario

**Purpose**: Execute one test scenario and evaluate results

**Input**: Scenario ID (e.g., "handlers-001")

**Steps**:

### 1. Load scenario

Read scenarios.json and extract the target scenario:

```bash
cat .claude/skills/nabledge-6/tests/scenarios.json | jq ".scenarios[] | select(.id == \"$SCENARIO_ID\")"
```

**Required fields**:
- `id`: Scenario identifier
- `category`: Category (handlers, libraries, tools, processing, adapters, code-analysis)
- `question`: User question to test
- `expected_keywords`: Keywords that should appear in response
- `expected_sections`: Sections that should be identified
- `file` or `target_code`: Knowledge file or code target

### 2. Initialize monitoring

Before executing, record:
- Start timestamp
- Token count before execution
- Expected evaluation criteria from scenarios.json

### 3. Execute scenario

**For knowledge search scenarios** (category != "code-analysis"):
- Display: "シナリオ {id} を実行します: {question}"
- Invoke nabledge-6 skill with the question
- Let nabledge-6 complete its workflow naturally
- Observe and record all tool calls

**For code-analysis scenarios** (category == "code-analysis"):
- Display: "コード分析シナリオ {id} を実行します: {question}"
- Invoke nabledge-6 code-analysis workflow with target code
- Let nabledge-6 complete its workflow naturally
- Observe and record all tool calls

**IMPORTANT**: Do NOT interfere with nabledge-6 execution. Simply observe and record.

### 4. Monitor execution

Track during execution:
- Tool calls made (Read, Bash+jq, Grep, Glob, Write)
- Token usage (from system messages)
- Workflow steps executed (keyword-search, section-judgement, code-analysis)
- Time taken
- Files read
- Sections accessed

### 5. Evaluate results

Check against evaluation criteria from scenarios.json:

**a) Workflow Execution** (Pass/Fail):
- [ ] keyword-search workflow executed (if applicable)
- [ ] section-judgement workflow executed (if applicable)
- [ ] code-analysis workflow executed (if applicable)
- [ ] Appropriate tools used (Read, Bash+jq)

**b) Keyword Matching** (Score: 0-100%):
- Count how many expected_keywords appear in the response
- Score = (matched_keywords / total_expected_keywords) * 100
- Pass threshold: ≥80%

**c) Section Relevance** (Pass/Fail):
- Check if expected_sections were identified
- Verify high-relevance sections were prioritized
- Confirm irrelevant sections were filtered out

**d) Knowledge File Only** (Pass/Fail):
- Verify response uses only knowledge file content
- No LLM training data or external knowledge
- If knowledge missing, proper message displayed

**e) Token Efficiency** (Pass/Fail):
- Target: 5,000-15,000 tokens per query
- Check if within range

**f) Tool Call Efficiency** (Pass/Fail):
- Target: 10-20 tool calls per query
- Check if within range

**For code-analysis scenarios, also check**:

**g) Code Analysis Workflow** (Pass/Fail):
- [ ] Target code identified correctly
- [ ] Dependencies analyzed appropriately
- [ ] Components decomposed properly
- [ ] Related Nablarch knowledge searched
- [ ] Documentation generated (Markdown + Mermaid)
- [ ] Source code links included (relative paths)
- [ ] Knowledge file links included

**h) Code Analysis Output Quality** (Pass/Fail):
- [ ] Expected sections present (Overview, Architecture, Components, Flow, Nablarch Framework Usage)
- [ ] Mermaid diagrams generated appropriately
- [ ] Component explanations clear
- [ ] Source code links correct
- [ ] Nablarch knowledge citations appropriate
- [ ] Expected components documented
- [ ] Expected knowledge referenced

### 6. Generate evaluation report

Create report in work/YYYYMMDD/ directory:

**Filename**: `test-{scenario-id}-{timestamp}.md`

**Report structure**:

```markdown
# Test Scenario Evaluation: {scenario-id}

**Date**: YYYY-MM-DD HH:MM:SS
**Category**: {category}
**Status**: PASS / FAIL

## Scenario Details

**Question**: {question}

**Expected Keywords**: {expected_keywords}
**Expected Sections**: {expected_sections}

## Execution Summary

**Duration**: {duration}
**Token Usage**: {tokens}
**Tool Calls**: {tool_call_count}

## Evaluation Results

### 1. Workflow Execution: PASS / FAIL

- [x/] keyword-search workflow executed
- [x/] section-judgement workflow executed
- [x/] Appropriate tools used

**Observations**: {observations}

### 2. Keyword Matching: {score}% (PASS / FAIL)

**Matched Keywords** ({matched}/{total}):
- ✓ keyword1
- ✓ keyword2
- ✗ keyword3

**Observations**: {observations}

### 3. Section Relevance: PASS / FAIL

**Sections Identified**:
- section1 (High relevance) ✓
- section2 (Medium relevance) ✓

**Expected Sections**:
- ✓ expected_section1
- ✗ expected_section2 (not identified)

**Observations**: {observations}

### 4. Knowledge File Only: PASS / FAIL

**Observations**: {observations}

### 5. Token Efficiency: PASS / FAIL

**Target**: 5,000-15,000 tokens
**Actual**: {actual} tokens

**Observations**: {observations}

### 6. Tool Call Efficiency: PASS / FAIL

**Target**: 10-20 calls
**Actual**: {actual} calls

**Tool Call Breakdown**:
- Read: {count}
- Bash+jq: {count}
- Grep: {count}
- Other: {count}

**Observations**: {observations}

## Response Analysis

**Response Length**: {length} characters

**Key Points from Response**:
- {point1}
- {point2}

## Improvement Suggestions

1. {suggestion1}
2. {suggestion2}
3. {suggestion3}

## Overall Assessment

**Summary**: {1-2 sentence summary of test result}

**Next Steps**: {recommended actions based on results}
```

### 7. Display summary

Show user:
- Scenario ID and status (PASS/FAIL)
- Overall score (e.g., "5/6 criteria passed")
- Path to detailed report
- Top 3 improvement suggestions (if any)

**Example output**:
```
✓ Scenario handlers-001: PASS (5/6 criteria)

Report: work/20260213/test-handlers-001-143052.md

Improvement suggestions:
1. Token usage was 18,234 (above target 15,000) - consider optimizing section extraction
2. Tool calls were 23 (above target 20) - some redundant jq operations detected

実行が完了しました。詳細は上記のレポートファイルをご確認ください。
```

---

## Workflow 2: Execute All Scenarios

**Purpose**: Execute all test scenarios and generate summary report

**Input**: None (executes all scenarios in scenarios.json)

**Steps**:

### 1. Load all scenarios

```bash
cat .claude/skills/nabledge-6/tests/scenarios.json | jq ".scenarios"
```

Count total scenarios and display plan:
```
30個のシナリオを実行します。
カテゴリ: handlers (5), libraries (5), tools (5), processing (5), adapters (5), code-analysis (5)
```

### 2. Ask user confirmation

```
実行を開始しますか？
- はい (全30シナリオを実行)
- いいえ (キャンセル)
- カテゴリを選択 (特定カテゴリのみ実行)
```

If user cancels, exit.
If user chooses category, go to Workflow 3.

### 3. Execute each scenario

For each scenario:
- Execute using Workflow 1 (Execute Single Scenario)
- Collect results (PASS/FAIL, scores, observations)
- Track overall statistics

**Progress display**:
```
[1/30] handlers-001: PASS (5/6) ✓
[2/30] handlers-002: FAIL (3/6) ✗
[3/30] handlers-003: PASS (6/6) ✓
...
```

### 4. Generate summary report

Create summary report in work/YYYYMMDD/:

**Filename**: `test-summary-{timestamp}.md`

**Report structure**:

```markdown
# Test Execution Summary

**Date**: YYYY-MM-DD HH:MM:SS
**Total Scenarios**: {total}
**Passed**: {passed} ({pass_rate}%)
**Failed**: {failed}

## Overall Statistics

**Average Token Usage**: {avg_tokens} (target: 5,000-15,000)
**Average Tool Calls**: {avg_calls} (target: 10-20)
**Average Duration**: {avg_duration}

## Results by Category

### Handlers (5 scenarios)

| Scenario | Status | Score | Keywords | Tokens | Tools | Notes |
|----------|--------|-------|----------|--------|-------|-------|
| handlers-001 | PASS | 5/6 | 4/5 (80%) | 12,456 | 15 | - |
| handlers-002 | FAIL | 3/6 | 2/5 (40%) | 8,234 | 12 | Low keyword matching |
| ... | ... | ... | ... | ... | ... | ... |

**Category Summary**: {passed}/{total} passed ({rate}%)

### Libraries (5 scenarios)
...

### Tools (5 scenarios)
...

### Processing (5 scenarios)
...

### Adapters (5 scenarios)
...

### Code Analysis (5 scenarios)
...

## Common Issues

### Issue 1: {issue_name} (Frequency: {count} scenarios)

**Affected Scenarios**: {scenario_ids}

**Description**: {description}

**Impact**: {impact}

**Recommendation**: {recommendation}

### Issue 2: ...

## Top Improvement Recommendations

### Priority 1: {recommendation1}

**Impact**: High
**Affected Scenarios**: {count}
**Details**: {details}
**Action Items**:
1. {action1}
2. {action2}

### Priority 2: {recommendation2}
...

### Priority 3: {recommendation3}
...

## Individual Reports

Detailed reports for each scenario:
- [handlers-001](./test-handlers-001-{timestamp}.md)
- [handlers-002](./test-handlers-002-{timestamp}.md)
- ...

## Next Steps

1. {next_step1}
2. {next_step2}
3. {next_step3}
```

### 5. Display summary

Show user:
- Total passed/failed
- Pass rate
- Path to summary report
- Top 3 priority recommendations

**Example output**:
```
テスト実行完了

結果: 24/30 passed (80%)
レポート: work/20260213/test-summary-143052.md

優先度の高い改善提案:
1. キーワードマッチング率の改善 (5シナリオで80%未満)
2. トークン使用量の最適化 (8シナリオで15,000超過)
3. セクション判定精度の向上 (3シナリオで期待セクション未検出)

詳細は上記のレポートファイルをご確認ください。
```

---

## Workflow 3: Execute Category Scenarios

**Purpose**: Execute all scenarios in a specific category

**Input**: Category name (handlers, libraries, tools, processing, adapters, code-analysis)

**Steps**:

### 1. Validate category

Check if category exists in scenarios.json.

### 2. Load category scenarios

```bash
cat .claude/skills/nabledge-6/tests/scenarios.json | jq ".scenarios[] | select(.category == \"$CATEGORY\")"
```

### 3. Display plan

```
カテゴリ「{category}」のシナリオを実行します。
シナリオ数: {count}

実行しますか？ (はい/いいえ)
```

### 4. Execute scenarios

For each scenario in category:
- Execute using Workflow 1
- Collect results

### 5. Generate category report

Similar to Workflow 2 but focused on single category.

---

## Workflow 4: Generate New Scenario

**Purpose**: Dynamically generate new test scenarios and optionally create standalone test skills using skill-creator

**Input**: None (interactive)

**Prerequisites**: skill-creator must be installed (see INSTALL-SKILL-CREATOR.md)

**Steps**:

### 1. Ask user for scenario details

```
新しいテストシナリオを生成します。

1. カテゴリを選択してください:
   - handlers
   - libraries
   - tools
   - processing
   - adapters
   - code-analysis

2. 既存の知識ファイルを使用しますか、それとも新しい質問を作成しますか？
   - 既存の知識ファイルから生成
   - 新しい質問を手動入力

3. スタンドアロンスキルも生成しますか？
   - はい (skill-creatorを使用してテスト実行用スキルを生成)
   - いいえ (scenarios.jsonにのみ追加)
```

### 2a. If using existing knowledge file

List available knowledge files in the category:
```bash
ls .claude/skills/nabledge-6/knowledge/features/{category}/*.json
```

Show user the list and ask which file to use.

Read the knowledge file and:
- Extract available sections
- Suggest potential questions based on section content
- Generate expected_keywords from section content

### 2b. If manual input

Ask user:
- Question (in Japanese)
- Knowledge file to use
- Expected keywords
- Expected sections

### 3. Generate scenario JSON

Create new scenario with:
- Auto-generated ID (next available in category)
- User-provided or generated details
- Relevance: "high" (default)

### 4. Preview and confirm

Show generated scenario:
```json
{
  "id": "handlers-006",
  "category": "handlers",
  "file": "handlers/batch/data-read-handler.json",
  "question": "...",
  "expected_keywords": [...],
  "expected_sections": [...],
  "relevance": "high"
}
```

Ask: "このシナリオを scenarios.json に追加しますか？"

### 5. Add to scenarios.json

If confirmed:
- Read current scenarios.json
- Add new scenario to .scenarios array
- Increment metadata.total_scenarios
- Update metadata.updated date
- Write back to scenarios.json

### 6. Generate standalone skill (if requested in Step 1)

**IMPORTANT**: This step requires skill-creator to be installed. If not installed, skip this step and inform the user to install skill-creator (see INSTALL-SKILL-CREATOR.md).

**6a. Use skill-creator to initialize skill**

Ask Claude (with skill-creator active) to create a new test skill:

```
Use skill-creator to help me create a new skill for testing scenario {scenario-id}.

Skill requirements:
- Name: test-{scenario-id}
- Description: Execute and evaluate nabledge-6 test scenario {scenario-id}
- Purpose: Run a specific test scenario without invoking nabledge-6-test

The skill should:
1. Load scenario {scenario-id} from scenarios.json
2. Execute the test using nabledge-6 skill
3. Evaluate results against criteria
4. Generate report in work/YYYYMMDD/

Include the following in the skill:
- Scenario details (question, expected keywords, expected sections)
- Evaluation criteria (6-8 criteria from scenarios.json)
- Report generation logic
```

**6b. Review and edit generated skill**

skill-creator will generate:
```
.claude/skills/test-{scenario-id}/
├── SKILL.md
└── scripts/ (if needed)
```

Review the generated SKILL.md and make adjustments if needed.

**6c. Test the generated skill**

Execute the new skill to verify it works:
```
/test-{scenario-id}
```

Or mention it: "Use test-{scenario-id} to run the test"

**6d. Document the skill**

Add entry to nabledge-6-test documentation:
```markdown
### Generated Test Skills

The following test skills have been generated:

- **test-{scenario-id}**: Tests scenario {scenario-id} ({category})
  - Usage: `/test-{scenario-id}`
  - Description: {scenario.question}
```

### 7. Optionally execute

Ask: "このシナリオをすぐに実行しますか？"

If yes:
- If standalone skill was generated, use it: `/test-{scenario-id}`
- Otherwise, execute using Workflow 1: `nabledge-6-test execute {scenario-id}`

---

## Workflow 5: skill-creator Integration Details

**Purpose**: Detailed guide for using skill-creator to generate test skills

### Prerequisites

1. Install skill-creator:
   ```
   /plugin marketplace add anthropics/skills
   /plugin install example-skills@anthropic-agent-skills
   ```

2. Verify installation:
   ```bash
   ls ~/.claude/plugins/*/skills/skill-creator/
   ```

### Skill Generation Pattern

When generating test skills with skill-creator, follow this pattern:

#### Basic Test Skill Template

```yaml
---
name: test-{scenario-id}
description: Execute and evaluate nabledge-6 test scenario {scenario-id}. Use when you want to quickly run this specific test scenario.
---

# Test Scenario: {scenario-id}

Execute and evaluate scenario {scenario-id} from nabledge-6 test suite.

## Scenario Details

**Category**: {category}
**Question**: {question}
**Expected Keywords**: {expected_keywords}
**Expected Sections**: {expected_sections}

## Execution

When this skill is invoked:

1. Display scenario information
2. Execute test using nabledge-6 skill
3. Monitor execution (tool calls, tokens, workflows)
4. Evaluate against criteria
5. Generate report

## Evaluation Criteria

- Workflow Execution (Pass/Fail)
- Keyword Matching (Score: 0-100%, Pass: ≥80%)
- Section Relevance (Pass/Fail)
- Knowledge File Only (Pass/Fail)
- Token Efficiency (Pass/Fail, Target: 5,000-15,000)
- Tool Call Efficiency (Pass/Fail, Target: 10-20)

## Report Output

Report will be generated at:
```
work/YYYYMMDD/test-{scenario-id}-{timestamp}.md
```

## Usage Examples

**Direct invocation**:
```
/test-{scenario-id}
```

**Mention in conversation**:
```
Use test-{scenario-id} to run the test
```

## Notes

- This skill is auto-generated by nabledge-6-test
- To regenerate, run: `nabledge-6-test generate-scenario`
- Source scenario: `.claude/skills/nabledge-6/tests/scenarios.json`
```

### Advanced: Reusable Scripts

For complex scenarios, skill-creator can also generate helper scripts:

**scripts/execute_test.py**:
```python
#!/usr/bin/env python3
"""Execute specific test scenario"""

import json
import sys
from pathlib import Path

def load_scenario(scenario_id):
    scenarios_file = Path(".claude/skills/nabledge-6/tests/scenarios.json")
    with open(scenarios_file) as f:
        data = json.load(f)

    for scenario in data["scenarios"]:
        if scenario["id"] == scenario_id:
            return scenario

    raise ValueError(f"Scenario {scenario_id} not found")

def execute_test(scenario):
    # Test execution logic
    print(f"Executing: {scenario['question']}")
    # ... implementation ...

if __name__ == "__main__":
    scenario_id = sys.argv[1] if len(sys.argv) > 1 else "{scenario-id}"
    scenario = load_scenario(scenario_id)
    execute_test(scenario)
```

### Benefits of Standalone Skills

1. **Quick Access**: Run specific tests with `/test-{scenario-id}`
2. **Encapsulation**: Each test is self-contained
3. **Reusability**: Share specific test skills with team
4. **Customization**: Modify individual test behavior
5. **Distribution**: Package and distribute via plugins

---

## Error Handling

### Scenario not found

If scenario ID doesn't exist:
```
エラー: シナリオ「{scenario-id}」が見つかりません。

利用可能なシナリオ:
- handlers-001, handlers-002, ...
- libraries-001, libraries-002, ...

コマンド例: nabledge-6-test execute handlers-001
```

### Execution failure

If nabledge-6 skill fails during execution:
```
エラー: シナリオ実行中にエラーが発生しました。

シナリオ: {scenario-id}
エラー: {error_message}

このシナリオを FAIL として記録し、次のシナリオに進みますか？ (はい/いいえ)
```

### Invalid category

If category doesn't exist:
```
エラー: カテゴリ「{category}」が見つかりません。

有効なカテゴリ:
- handlers
- libraries
- tools
- processing
- adapters
- code-analysis
```

## Notes

- Always generate reports in work/YYYYMMDD/ directory
- Use timestamps in filenames to avoid collisions
- Keep individual scenario reports separate from summary
- Focus on actionable improvement suggestions
- Track trends across multiple test runs

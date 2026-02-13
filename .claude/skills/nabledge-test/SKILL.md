---
name: nabledge-test
description: Test framework for nabledge skills (nabledge-6 and nabledge-5). Executes test scenarios using skill-creator's evaluation engine and generates improvement reports. Use when testing nabledge-6 or nabledge-5 skills, running individual scenarios, category tests, or full test suites.
---

# Nabledge-Test: Test Framework for Nabledge Skills

Unified test framework for nabledge-6 and nabledge-5 skills, powered by skill-creator's evaluation engine.

## Architecture

```
nabledge-test (Interface Layer)
  ├── Nablarch-specific scenarios (scenarios/nabledge-6/, nabledge-5/)
  ├── Scenario → Eval conversion
  └── Report generation (Nablarch format)
          ↓ delegates to
skill-creator (Evaluation Engine)
  ├── Executor agent (run eval with skill)
  ├── Grader agent (evaluate expectations)
  └── Structured outputs (transcript, metrics, grading)
```

## Usage

**Single scenario**:
```
nabledge-test 6 handlers-001
```

**All scenarios**:
```
nabledge-test 6 --all
```

**By category**:
```
nabledge-test 6 --category handlers
```

**Future (nabledge-5)**:
```
nabledge-test 5 libraries-001
```

## How Claude Code should execute this skill

### Step 0: Parse arguments

Format: `nabledge-test <version> [<scenario-id> | --all | --category <cat>]`

- version: `6` (nabledge-6) or `5` (nabledge-5)
- scenario-id: e.g., `handlers-001`
- --all: Execute all scenarios
- --category: e.g., `handlers`, `libraries`

**No arguments**: Show interactive menu.

### Step 1: Load scenario(s)

Read from:
- nabledge-6: `scenarios/nabledge-6/scenarios.json`
- nabledge-5: `scenarios/nabledge-5/scenarios.json`

### Step 2: Convert to skill-creator eval format

**Input (scenarios.json)**:
```json
{
  "id": "handlers-001",
  "question": "データリードハンドラでファイルを読み込むには？",
  "expected_keywords": ["DataReadHandler", "DataReader"],
  "expected_sections": ["overview", "usage"]
}
```

**Output (eval format)**:
```json
{
  "prompt": "データリードハンドラでファイルを読み込むにはどうすればいいですか？",
  "expectations": [
    "Response includes keyword 'DataReadHandler'",
    "Response includes keyword 'DataReader'",
    "Response mentions 'overview' or 'usage' sections",
    "Token usage is between 5000 and 15000",
    "Tool calls are between 10 and 20"
  ]
}
```

**Conversion script**: See `scripts/convert_scenario.py`

### Step 3: Setup workspace

Ask user for workspace location (default: `nabledge-test-workspace/`).

Create structure:
```
nabledge-test-workspace/
└── nabledge-6/
    └── handlers-001/
        ├── skill/              # Copy of target skill
        ├── eval_metadata.json
        ├── inputs/
        ├── outputs/
        ├── transcript.md
        ├── metrics.json
        ├── grading.json
        └── timing.json
```

### Step 4: Execute via skill-creator

**Read skill-creator references**:
```bash
Read .claude/skills/skill-creator/references/schemas.md
Read .claude/skills/skill-creator/agents/executor.md
Read .claude/skills/skill-creator/agents/grader.md
```

**Execute workflow**:

1. **Executor phase**:
   - Copy target skill (nabledge-6 or nabledge-5) to workspace
   - Start timing
   - Spawn executor following `agents/executor.md`
   - Executor uses the skill to answer eval prompt
   - Saves transcript.md, metrics.json
   - End timing

2. **Grader phase**:
   - Spawn grader following `agents/grader.md`
   - Grader reads transcript, evaluates expectations
   - Saves grading.json

See `workflows/execute-test.md` for detailed steps.

### Step 5: Generate nabledge report

Convert skill-creator outputs to nabledge format.

**Input**:
- transcript.md - Execution log
- metrics.json - Tool usage
- grading.json - Pass/fail per expectation
- timing.json - Wall clock time

**Output**: `work/YYYYMMDD/test-<scenario-id>-<timestamp>.md`

**Report template**: `templates/single-scenario-report.md`

**Evaluation criteria**:
1. Workflow Execution (from transcript)
2. Keyword Matching (from grading.json)
3. Section Relevance (from grading.json)
4. Knowledge File Only (from transcript)
5. Token Efficiency (from metrics.json)
6. Tool Call Efficiency (from metrics.json)

### Step 6: Display results

```
✓ Scenario handlers-001: PASS (5/6 criteria)

Report: work/20260213/test-handlers-001-143052.md

Improvement suggestions:
1. Token usage was 18,234 (above target 15,000)
2. Tool calls were 23 (above target 20)

実行が完了しました。
```

## Multiple scenarios (--all or --category)

1. Load all/category scenarios
2. Execute each via skill-creator (Steps 3-4)
3. Generate individual reports
4. Generate summary report

**Summary report**: `work/YYYYMMDD/test-summary-<timestamp>.md`

See `templates/summary-report.md`.

## Scenarios structure

```
scenarios/
├── nabledge-6/
│   └── scenarios.json  # 30 scenarios
└── nabledge-5/          # Future
    └── scenarios.json
```

**Format**:
```json
{
  "metadata": {"version": "1.1.0", "total_scenarios": 30},
  "scenarios": [
    {
      "id": "handlers-001",
      "category": "handlers",
      "file": "handlers/batch/data-read-handler.json",
      "question": "...",
      "expected_keywords": [...],
      "expected_sections": [...],
      "relevance": "high"
    }
  ],
  "evaluation_criteria": {...}
}
```

## Scripts

**convert_scenario.py**: Convert scenarios.json to eval format
```bash
scripts/convert_scenario.py scenarios/nabledge-6/scenarios.json handlers-001 > eval_metadata.json
```

## Templates

- `single-scenario-report.md` - Individual test report
- `summary-report.md` - Aggregate report for multiple tests

## Error handling

**Scenario not found**:
```
エラー: シナリオ「handlers-999」が見つかりません。
利用可能: handlers-001, handlers-002, ...
```

**Execution failure**:
```
エラー: シナリオ実行中にエラーが発生しました。
シナリオ: handlers-001
エラー: [error details]
このシナリオを FAIL として記録します。
```

**Invalid version**:
```
エラー: バージョン「7」は無効です。
有効なバージョン: 6, 5
```

## Dependencies

- **skill-creator**: Evaluation engine (executor, grader agents)
- **nabledge-6** or **nabledge-5**: Target skill being tested

## Notes

- nabledge-test = Interface layer (Nablarch scenarios)
- skill-creator = Evaluation engine (execution, grading)
- Reports use nabledge format for consistency
- Future nabledge-5 support uses same architecture

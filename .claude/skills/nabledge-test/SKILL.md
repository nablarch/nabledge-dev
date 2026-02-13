---
name: nabledge-test
description: Test nabledge-6/5 using skill-creator. Loads eval scenarios, delegates to skill-creator, saves results to work/YYYYMMDD/.
---

# Nabledge-Test

Thin wrapper for testing nabledge skills.

## Usage

```bash
nabledge-test 6 handlers-001        # Single test
nabledge-test 6 --all               # All tests
nabledge-test 6 --category handlers # Category
```

## How it works

1. Load scenario from `scenarios/nabledge-6/scenarios.json`
2. Invoke skill-creator eval mode
3. Save results to `work/YYYYMMDD/test-<id>-<timestamp>.md`

## When invoked

### Step 1: Parse arguments

Format: `nabledge-test <version> [<scenario-id> | --all | --category <cat>]`

### Step 2: Load scenario

```json
{
  "id": "handlers-001",
  "prompt": "データリードハンドラでファイルを読み込むには？",
  "expectations": [
    "Response includes 'DataReadHandler'",
    "Token usage is between 5000 and 15000"
  ]
}
```

### Step 3: Invoke skill-creator

Read and follow: `.claude/skills/skill-creator/references/eval-mode.md`

Key steps:
- Setup workspace (ask user for location, suggest `nabledge-test-workspace/`)
- Execute: Spawn executor agent with nabledge-<version> skill
- Grade: Spawn grader agent
- Get results: transcript.md, grading.json, metrics.json, timing.json

### Step 4: Save to work log

Write `work/YYYYMMDD/test-<scenario-id>-<timestamp>.md` with:
- Scenario (prompt, expectations count)
- Results (from grading.json)
- Metrics (tokens, tool calls, duration)
- Link to transcript in workspace

### Step 5: Display summary

```
✓ handlers-001: PASS (7/8 expectations)
  Report: work/20260213/test-handlers-001-153045.md
  Workspace: nabledge-test-workspace/nabledge-6/handlers-001/
```

## Scenarios

5 essential scenarios covering core functionality:
- handlers-001: DataReadHandler file reading
- libraries-001: UniversalDao paging
- tools-001: NTF test data preparation
- processing-001: Nablarch batch architecture
- code-analysis-001: Existing code analysis

## Dependencies

- skill-creator (evaluation engine)
- nabledge-6 or nabledge-5 (target skill)

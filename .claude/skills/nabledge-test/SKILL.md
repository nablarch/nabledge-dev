---
name: nabledge-test
description: Test nabledge-6 or nabledge-5 skills using skill-creator eval mode. Loads scenarios in eval format and delegates execution/grading to skill-creator. Results saved to work/YYYYMMDD/.
---

# Nabledge-Test

Thin wrapper for testing nabledge skills via skill-creator.

## Usage

```bash
nabledge-test 6 handlers-001    # Single scenario
nabledge-test 6 --all           # All scenarios
nabledge-test 6 --category handlers
nabledge-test 5 libraries-001   # Future: nabledge-5
```

## How it works

1. **Load scenario**: Read `scenarios/nabledge-6/scenarios.json`
2. **Invoke skill-creator**: Use eval mode with the scenario
3. **Save results**: Write to `work/YYYYMMDD/test-<id>-<timestamp>.md`

That's it. skill-creator handles everything else.

## Execution

When invoked:

### Parse arguments

- `<version>`: 6 or 5
- `<scenario-id>`: e.g., handlers-001
- `--all`: Execute all scenarios
- `--category <cat>`: Execute category

### Load scenario

Read from `scenarios/nabledge-<version>/scenarios.json`:

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

### Invoke skill-creator eval mode

Use skill-creator:

```
Read skill-creator/references/eval-mode.md
Follow the eval workflow:
  - Setup workspace (ask user for location)
  - Execute (spawn executor agent with nabledge-<version> skill)
  - Grade (spawn grader agent)
  - Read results (transcript.md, grading.json, metrics.json)
```

### Save results to work log

Write `work/YYYYMMDD/test-<scenario-id>-<timestamp>.md`:

```markdown
# Test: <scenario-id>

**Date**: <timestamp>
**Status**: <overall pass/fail>

## Scenario
- Prompt: <prompt>
- Expectations: <count>

## Results
<Copy from grading.json>

## Transcript
<Link to transcript.md in workspace>

## Metrics
- Tokens: <from metrics.json>
- Tool calls: <from metrics.json>
- Duration: <from timing.json>
```

### Display summary

```
✓ handlers-001: PASS (7/8 expectations)
  Report: work/20260213/test-handlers-001-153045.md
  Workspace: nabledge-test-workspace/nabledge-6/handlers-001/
```

## Multiple scenarios (--all or --category)

Execute each scenario sequentially, save individual reports, then generate summary:

`work/YYYYMMDD/test-summary-<timestamp>.md`

## Scenarios

Located in `scenarios/nabledge-<version>/scenarios.json` (eval format).

30 scenarios for nabledge-6: handlers (5), libraries (5), tools (5), processing (5), adapters (5), code-analysis (5).

## Dependencies

- **skill-creator**: Evaluation engine
- **nabledge-6** or **nabledge-5**: Target skill

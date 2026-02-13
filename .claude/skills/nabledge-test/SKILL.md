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
2. Call skill-creator to execute and evaluate
3. Read results from workspace
4. Save summary to `work/YYYYMMDD/test-<id>-<timestamp>.md`

## When invoked

### Step 1: Parse arguments

Format: `nabledge-test <version> [<scenario-id> | --all | --category <cat>]`

### Step 2: Load scenario

From `scenarios/nabledge-6/scenarios.json`:

```json
{
  "id": "handlers-001",
  "question": "データリードハンドラでファイルを読み込むには？",
  "keywords": ["DataReadHandler", "DataReader", "ファイル読み込み"],
  "sections": ["overview", "usage"]
}
```

### Step 2b: Convert to expectations

Build expectations list for skill-creator:

```
expectations = []

# Add keyword checks
for keyword in scenario.keywords:
    expectations.append(f"Response includes '{keyword}'")

# Add section checks
if scenario.sections:
    section_list = " or ".join([f"'{s}'" for s in scenario.sections])
    expectations.append(f"Response mentions {section_list} sections")

# Add default metrics (always)
expectations.append("Token usage is between 5000 and 15000")
expectations.append("Tool calls are between 10 and 20")
```

### Step 3: Call skill-creator

Use Skill tool with converted expectations:

```
Skill(
  skill="skill-creator",
  args="Run eval mode: test nabledge-6 skill with prompt '<scenario.question>' and these expectations: <converted_expectations_list>. Use workspace nabledge-test-workspace/. Don't ask user for workspace location."
)
```

skill-creator will:
- Execute nabledge-6 with the question
- Grade expectations
- Save results to `nabledge-test-workspace/`

### Step 4: Read results from workspace

After skill-creator completes, read:
- `nabledge-test-workspace/eval-<id>/with_skill/transcript.md`
- `nabledge-test-workspace/eval-<id>/with_skill/grading.json`
- `nabledge-test-workspace/eval-<id>/with_skill/timing.json`

### Step 5: Generate summary report

Write `work/YYYYMMDD/test-<scenario-id>-<timestamp>.md`:

```markdown
# Test: <scenario-id>

**Date**: <timestamp>
**Question**: <scenario.question>

## Scenario
- **Keywords** (<count>): <list>
- **Sections** (<count>): <list>

## Results

**Pass Rate**: <passed>/<total> (<percent>%)

### Expectations
- ✓ Response includes 'keyword1'
- ✗ Response includes 'keyword2'
- ✓ Response mentions 'section1' or 'section2' sections
- ✓ Token usage is between 5000 and 15000
- ✗ Tool calls are between 10 and 20

## Metrics
- **Duration**: <seconds>s
- **Tool Calls**: <count>
- **Tokens**: <estimate>

## Transcript
See: nabledge-test-workspace/eval-<id>/with_skill/transcript.md
```

### Step 6: Display summary

```
✓ handlers-001: PASS (7/8 expectations, 87.5%)
  Report: work/20260213/test-handlers-001-153045.md
  Transcript: nabledge-test-workspace/eval-handlers-001/with_skill/transcript.md
```

## Scenarios

5 most frequently asked scenarios (selected by practical usage):
- processing-005: Batch startup (beginners' first hurdle)
- libraries-001: UniversalDao paging (highest implementation frequency)
- handlers-001: DataReadHandler file reading (batch basics)
- processing-004: Error handling (implementation essential)
- processing-002: BatchAction implementation (business logic)

## Dependencies

- skill-creator (evaluation engine)
- nabledge-6 or nabledge-5 (target skill)

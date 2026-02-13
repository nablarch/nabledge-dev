---
name: nabledge-test
description: Test nabledge-6/5 using skill-creator eval procedures. Executes test scenarios, evaluates expectations, saves results to work/YYYYMMDD/.
---

# Nabledge-Test

Test framework for nabledge skills using skill-creator's evaluation procedures.

## Usage

```bash
nabledge-test 6 handlers-001        # Single test
nabledge-test 6 --all               # All tests
nabledge-test 6 --category handlers # Category
```

## How it works

1. Load scenario from `scenarios/nabledge-6/scenarios.json`
2. Convert keywords/sections to expectations
3. Execute skill-creator eval-mode procedures manually
4. Save results to `work/YYYYMMDD/test-<id>-<timestamp>.md`

## When invoked

### Step 1: Parse arguments

Format: `nabledge-test <version> [<scenario-id> | --all | --category <cat>]`

### Step 2: Load scenario

From `scenarios/nabledge-6/scenarios.json`:

```json
{
  "id": "handlers-001",
  "question": "データリードハンドラでファイルを読み込むには？",
  "keywords": ["DataReadHandler", "DataReader", ...],
  "sections": ["overview", "usage"]
}
```

### Step 3: Convert to expectations

Build expectations list:

```python
expectations = []

# Keyword checks
for keyword in scenario.keywords:
    expectations.append(f"Response includes '{keyword}'")

# Section checks
if scenario.sections:
    section_list = " or ".join([f"'{s}'" for s in scenario.sections])
    expectations.append(f"Response mentions {section_list} sections")

# Default metrics
expectations.append("Token usage is between 5000 and 15000")
expectations.append("Tool calls are between 10 and 20")
```

### Step 4: Read skill-creator procedures

Read skill-creator eval-mode documentation:

```
Read .claude/skills/skill-creator/references/eval-mode.md
Read .claude/skills/skill-creator/references/schemas.md
Read .claude/skills/skill-creator/agents/executor.md
Read .claude/skills/skill-creator/agents/grader.md
```

### Step 5: Setup workspace

**Fixed workspace**: `nabledge-test-workspace/eval-<scenario-id>/`

Create structure:
```
nabledge-test-workspace/
└── eval-<scenario-id>/
    ├── with_skill/
    │   ├── outputs/
    │   │   ├── transcript.md
    │   │   └── metrics.json
    │   ├── grading.json
    │   └── timing.json
```

```bash
mkdir -p nabledge-test-workspace/eval-<scenario-id>/with_skill/outputs
```

### Step 6: Execute nabledge-6 inline - Follow executor.md

**CRITICAL**: Do NOT use the Skill tool. Execute nabledge-<version> instructions directly in this conversation to maintain workflow continuity.

**Record start time**:
```bash
date -u +%Y-%m-%dT%H:%M:%SZ > start_time.txt
```

**Load nabledge-<version> skill procedures**:
```bash
Read .claude/skills/nabledge-<version>/SKILL.md
Read .claude/skills/nabledge-<version>/workflows/keyword-search.md
Read .claude/skills/nabledge-<version>/workflows/section-judgement.md
Read .claude/skills/nabledge-<version>/knowledge/index.toon
```

**Execute the question <scenario.question> by following nabledge-<version> procedures**:
- Apply keyword-search workflow to identify relevant knowledge files
- Use section-judgement workflow to select appropriate sections
- Generate response following nabledge-<version> guidelines
- **Track every tool call** (Read, Bash, Grep) for metrics

**While executing, track**:
- Tool calls made (Read, Bash, Grep, etc.)
- Steps executed
- Response content

**Write transcript** to `workspace/eval-<id>/with_skill/outputs/transcript.md`:

```markdown
# Eval Execution Transcript

## Eval Prompt
<scenario.question>

## Skill
- Path: .claude/skills/nabledge-<version>
- Name: nabledge-<version>
- Description: Nablarch <version> Knowledge Base

## Input Files
None provided

## Execution

### Step 1: Load skill workflows and knowledge index
**Action**: Read nabledge-<version> skill procedures
**Tool**: Read (4 calls)
- SKILL.md
- workflows/keyword-search.md
- workflows/section-judgement.md
- knowledge/index.toon
**Result**: Successfully loaded workflows and knowledge index

### Step 2: Execute knowledge search (keyword-search workflow)
**Action**: Extract keywords and match against index
**Tool**: Mental analysis + Read
**Result**: <summary of keyword extraction and file selection>

### Step 3: Read candidate sections (section-judgement workflow)
**Action**: Read specific sections from knowledge files
**Tool**: Bash (jq)
**Result**: <summary of sections read>

(... continue for each significant action ...)

## Output Files
None created (response was inline)

## Final Result
<Copy the full response from nabledge-6 here>

## Issues
None
```

**Write metrics.json**:
```json
{
  "tool_calls": {
    "Read": <count>,
    "Bash": <count>,
    "Grep": <count>
  },
  "total_tool_calls": <total>,
  "total_steps": <count>,
  "files_created": [],
  "errors_encountered": 0,
  "output_chars": <char count of response>,
  "transcript_chars": <char count of transcript>
}
```

**Record end time and calculate duration**:
```bash
date -u +%Y-%m-%dT%H:%M:%SZ > end_time.txt
# Calculate duration_seconds
```

**Write timing.json**:
```json
{
  "executor_start": "<start_time>",
  "executor_end": "<end_time>",
  "executor_duration_seconds": <duration>,
  "grader_start": null,
  "grader_end": null,
  "grader_duration_seconds": 0,
  "total_duration_seconds": <duration>
}
```

**After writing timing.json, immediately proceed to Step 7 without stopping. This is a continuous evaluation workflow.**

### Step 7: Grade - Follow grader.md

**Record grader start time**

**Read transcript and outputs**:
```bash
Read workspace/eval-<id>/with_skill/outputs/transcript.md
```

**Evaluate each expectation**:

For each expectation in expectations list:
1. Check if criterion is met by examining transcript
2. Record pass/fail with evidence
3. Extract relevant quotes as evidence

**Write grading.json**:
```json
{
  "expectations": [
    {
      "text": "Response includes 'DataReadHandler'",
      "passed": true,
      "evidence": "Found in transcript: 'DataReadHandler（nablarch.fw.handler.DataReadHandler）'"
    },
    {
      "text": "Response includes 'DataReader'",
      "passed": true,
      "evidence": "Found multiple times in response"
    },
    ...
  ],
  "summary": {
    "passed": <count>,
    "failed": <count>,
    "total": <count>,
    "pass_rate": <rate>
  },
  "execution_metrics": {
    "tool_calls": { ... },
    "total_tool_calls": <count>,
    "total_steps": <count>,
    "errors_encountered": 0,
    "output_chars": <count>,
    "transcript_chars": <count>
  },
  "timing": {
    "executor_duration_seconds": <duration>,
    "grader_duration_seconds": <duration>,
    "total_duration_seconds": <total>
  },
  "claims": [],
  "user_notes_summary": {
    "uncertainties": [],
    "needs_review": [],
    "workarounds": []
  }
}
```

**Update timing.json** with grader times.

### Step 8: Generate summary report

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
- ✓ Response includes 'DataReadHandler'
  Evidence: Found in response
- ✗ Tool calls are between 10 and 20
  Evidence: Actual tool calls: 3

## Metrics
- **Duration**: <seconds>s
- **Tool Calls**: <count>
- **Response Length**: <chars> chars

## Transcript
See: nabledge-test-workspace/eval-<id>/with_skill/outputs/transcript.md

## Grading
See: nabledge-test-workspace/eval-<id>/with_skill/grading.json
```

### Step 9: Display summary

```
✓ handlers-001: PASS (7/8 expectations, 87.5%)
  Report: work/20260213/test-handlers-001-153045.md
  Transcript: nabledge-test-workspace/eval-handlers-001/with_skill/outputs/transcript.md
```

## Dependencies

- skill-creator (evaluation procedures only - not invoked as skill)
- nabledge-6 or nabledge-5 (target skill)

## Notes

- nabledge-test follows skill-creator's eval-mode procedures
- Does NOT invoke skill-creator as a skill
- Manually executes executor and grader steps
- Workspace: fixed at `nabledge-test-workspace/`

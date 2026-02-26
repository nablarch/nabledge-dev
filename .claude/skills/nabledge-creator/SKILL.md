---
name: nabledge-creator
description: Internal skill for creating and maintaining nabledge knowledge files, mappings, and indexes
---

# nabledge-creator

## Argument Validation

**IMPORTANT:** Before executing any workflow, check if required arguments are provided.

If `<workflow>` or `<version>` arguments are missing:

1. Display the usage message below to the user
2. DO NOT prompt the user with AskUserQuestion
3. Stop execution and wait for user to provide arguments

## Usage

```
/nabledge-creator <workflow> <version> [args...]
```

**Arguments:**
- `<workflow>`: Workflow name (required)
- `<version>`: Nablarch version number (required)
- `[args...]`: Additional workflow-specific arguments (optional)

**Examples:**
```
/nabledge-creator all 6
/nabledge-creator mapping 6
/nabledge-creator knowledge 6
/nabledge-creator verify-mapping 6
/nabledge-creator clean 6
```

Execute the corresponding workflow file in `workflows/<workflow>.md` with the provided arguments.

## Workflows

Available workflows: all, mapping, knowledge, verify-mapping, verify-knowledge, clean

For detailed steps and instructions, read the workflow file in `workflows/<workflow>.md`.

---

## Multi-Step Workflow Execution Protocol

When executing workflows with multiple steps, follow this protocol to maintain transparency and ensure all steps complete correctly.

### 1. At Workflow Start: Display Initial Checklist

Copy the checklist template from the workflow file (e.g., `workflows/mapping.md`) and display it with all steps marked as `□ (pending)`.

### 2. At Each Step Boundary: Update Progress

**When starting a step:**

```
## [Workflow Name] Progress (Updated)

✓ Step 1: [Name] - Complete
→ Step 2: [Name] - IN PROGRESS
  **Scope:** [What will be done]
  **Method:** [How it will be done]
□ Step 3: [Name]
...
```

**When completing a step:**

```
## Step X: [Name] - COMPLETE

**Completion Evidence:**

| Criterion | Expected | Actual | Status |
|-----------|----------|--------|--------|
| [Metric 1] | [target] | [measured] | ✓/✗ |
| [Metric 2] | [target] | [measured] | ✓/✗ |

[Additional evidence as specified in workflow file]

**Result:** All criteria met / Issues: [details]
```

Then update the progress checklist marking this step as `✓`.

### 3. Completion Evidence Guidelines

**Focus on complete coverage (全量処理):**

Completion evidence must prove that ALL input was processed, not just a sample.

**Required format:**

| Criterion | Expected | Actual | Status |
|-----------|----------|--------|--------|
| Total input | [count from input] | [count from output] | ✓/✗ |

**Use dynamic values (not hardcoded):**

❌ Bad (hardcoded):
- "Files processed: 329"

✅ Good (dynamic from actual data):
- "Files in mapping: [grep -c '^|' mapping-v6.md minus header]"
- "Files processed: [script output count]"
- "Match: [input count == output count] ✓/✗"

**How to measure dynamically:**
- Count rows in files: `grep -c "pattern" file`
- Parse script output: Look for "Completed: N files" messages
- Compare input/output: Input from Step N → Output from Step N+1

### 4. When to Stop

If completion evidence shows **any ✗ status**:

1. Stop immediately - do not proceed to next step
2. Report the issue to user
3. Wait for user decision on how to proceed

Do NOT attempt to fix and continue without user approval.

### 5. Workflow-Specific Details

Each workflow file (`workflows/*.md`) provides:
- Checklist template to copy
- When to update checklist (start/complete markers)
- Completion evidence format for each step
- How to measure each criterion dynamically

Always follow the specific workflow file's instructions.

---
name: re
description: Resume work after session clear — reads tasks.md and continues work without asking
argument-hint: [PR number]
allowed-tools: Bash, Read, Edit, Write, Glob, Grep, AskUserQuestion
---

Resume in-progress work after a session clear. Reads the state saved by `/sv` and continues immediately.

# Instructions

## 1. Identify Current PR

If $ARGUMENTS provided, use as PR number. Otherwise auto-detect:

```bash
current_branch=$(git branch --show-current)
pr_number=$(gh pr view --json number -q .number 2>/dev/null)
issue_number=$(echo "$current_branch" | grep -oE '^[0-9]+')
```

If `issue_number` is empty but `pr_number` is known, extract from the PR's closing reference:

```bash
issue_number=$(gh pr view $pr_number --json body -q .body | grep -oE 'Closes #([0-9]+)' | grep -oE '[0-9]+' | head -1)
```

If no PR found, guide user to create one first with `/hi`.

## 2. Load tasks.md

```bash
cat .pr/$(printf '%05d' $issue_number)/tasks.md 2>/dev/null
```

If tasks.md exists, trust it as the source of truth — do not re-assess from scratch.

If tasks.md does not exist, fall back to loading state from the PR:

```bash
gh pr view $pr_number --json title,body,state
cat .pr/$(printf '%05d' $issue_number)/notes.md 2>/dev/null
git status --short
git diff --stat HEAD
```

Then create tasks.md from that context before proceeding (see format below).
When recording in-progress status, infer **Status** from `git diff --stat` output and any WIP commits — describe what code is partially written.

## 3. Identify Next Task

From tasks.md, find the first uncompleted task in **In Progress** or **Not Started**.

Output a one-line confirmation (pull PR number and issue number from tasks.md `**PR**` and `**Issue**` fields):

```
Resuming: PR #{pr_number} (Issue #{issue_number}) — {PR title}
Next task: {task name} — {first remaining step}
```

If there is a step marked `[BLOCKED: reason]` or `[DECISION: question]` before the next executable step, use AskUserQuestion to resolve it first.

## 4. Execute Work

Proceed with the next task immediately. Work through the steps in tasks.md in order:

- Follow the steps listed without asking for confirmation between them
- Mark each step `[x]` in tasks.md as it completes
- Move fully completed tasks to **Done** section
- Update `**Updated**` date when modifying tasks.md
- If a step is ambiguous, resolve it from context (notes.md, code) before asking the user

Continue through all remaining tasks unless a `[BLOCKED:]` or `[DECISION:]` marker is encountered.

When all tasks are complete, notify the user and suggest `/sv` or `/pr create`.

## tasks.md Format (for fallback creation)

```markdown
# Tasks: {PR title}

**PR**: #{pr_number}
**Issue**: #{issue_number}
**Updated**: {YYYY-MM-DD}

## In Progress

### {Task name}

**Status**: {what's done / what's blocked}

**Steps:**
- [ ] Step 1
- [BLOCKED: need user decision on X] Step 2
- [ ] Step 3

**Context**: {key decisions, constraints, relevant files}

## Not Started

### {Task name}

**Steps:**
- [ ] Step 1
- [ ] Step 2

## Done

- [x] {Completed task} — committed `{short_hash}`
```

# Important

- tasks.md is the source of truth — trust it, do not re-assess from the PR body
- Decision points are marked `[BLOCKED: reason]` or `[DECISION: question]` in step lines — only these require user input
- Unmarked steps proceed without confirmation

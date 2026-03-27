---
name: re
description: Resume work after session clear — reviews PR task list and prepares detailed task file for complex work
argument-hint: [PR number]
allowed-tools: Bash, Read, Edit, Write, Glob, Grep, AskUserQuestion
---

Resume in-progress work after a session clear.

# Instructions

## 1. Identify Current PR

If $ARGUMENTS provided, use as PR number. Otherwise auto-detect:

```bash
current_branch=$(git branch --show-current)
pr_number=$(gh pr view --json number -q .number 2>/dev/null)
issue_number=$(echo "$current_branch" | grep -oE '^[0-9]+')
```

If no PR found, guide user to create one first with `/hi`.

## 2. Load Current State

Gather all context:

```bash
# PR body (task list, approach, success criteria)
gh pr view $pr_number --json title,body,state

# Work log
cat .pr/$(printf '%05d' $issue_number)/notes.md 2>/dev/null

# Task file if exists
cat .pr/$(printf '%05d' $issue_number)/tasks.md 2>/dev/null

# Uncommitted changes
git status --short
git diff --stat HEAD
```

## 3. Review Task List

Read the PR body Tasks section and assess each task:

- **Done**: Evidence in commits or files → mark `[x]`
- **In progress**: Partially done → note status
- **Not started**: Remaining work → identify complexity

For each not-started task, classify:
- **Simple**: Single file change, clear scope → keep as-is in PR body
- **Complex**: Multiple steps, unclear scope, or has sub-tasks → needs task file entry

**Complexity indicators:**
- Requires decisions or user input
- Touches multiple files/systems
- Has prerequisite steps
- Was previously attempted and stalled

## 4. Create or Update Task File

If any complex tasks exist, create/update `.pr/{00000}/tasks.md`:

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
- [ ] Step 2
- [ ] Step 3

**Context**: {key decisions, constraints, relevant files}

## Not Started

### {Task name}

**Steps:**
- [ ] Step 1
- [ ] Step 2

## Done

- [x] {Completed task}
```

## 5. Update PR Body

Update the PR Tasks section to reflect current status and link to task file:

- Check off completed tasks
- For complex tasks, add link: `- [ ] [Task name](.pr/{00000}/tasks.md#task-name)`
- Keep simple remaining tasks as plain checkboxes

Update with:
```bash
gh pr edit $pr_number --body "$(cat <<'EOF'
{updated PR body}
EOF
)"
```

## 6. Output Resume Summary

Print a clear handoff so the next `/hi` invocation (or continued work) knows where to start:

```
## Resumed: #{pr_number} — {PR title}

**Branch**: {branch}
**Issue**: #{issue_number}

### What's done
- {completed task}

### Next task
{first remaining task — with link to tasks.md if complex}

### Blocked / needs decision
{anything requiring user input, if any}
```

If there are items needing user input, use AskUserQuestion before proceeding.

# Important

- Do not implement anything — only assess state and prepare task file
- Do not commit — task file and PR body update happen before next work session
- If tasks.md already exists, update it (do not overwrite)
- Complex task breakdown should be specific enough that `/hi {issue_number}` can resume without additional context

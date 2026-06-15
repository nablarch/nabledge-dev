---
name: sv
description: Save session state before ending — update tasks.md, clean working tree, output handoff summary
argument-hint: [PR number]
allowed-tools: Bash, Read, Edit, Write, Glob, Grep
# Note: AskUserQuestion is intentionally excluded — sv runs without prompting.
---

Save session state before ending a work session. Pair with `/re` which resumes from the saved state.

# Instructions

## 1. Identify Current PR

If $ARGUMENTS provided, use as PR number. Otherwise auto-detect:

```bash
current_branch=$(git branch --show-current)
pr_number=$(gh pr view --json number -q .number 2>/dev/null)
issue_number=$(echo "$current_branch" | grep -oE '^[0-9]+')
```

## 2. Update tasks.md

Read the current task file:

```bash
cat .work/$(printf '%05d' $issue_number)/tasks.md 2>/dev/null
```

Update to reflect the exact state at end of this session:

- Mark completed steps `[x]` with the commit hash where applicable
- Move fully completed tasks to **Done** section
- For the current in-progress task, record:
  - Which steps are done vs remaining
  - Any decisions made this session
  - Blockers: mark as `[BLOCKED: reason]` on the step line so `/re` can detect them
  - Decisions needed: mark as `[DECISION: question]` on the step line
- Update `**Updated**: {YYYY-MM-DD}` to today's date

**Do not overwrite — update in place.**

## 3. Clean Working Tree

Check for uncommitted changes and untracked files:

```bash
git status --short
git diff --stat HEAD
```

For each item found:

- **Modified tracked files** that are work product (tasks.md, notes.md, etc.):
  Commit them. Use `docs:` type for work log files.
- **Modified tracked files** that are incomplete implementation:
  Ask whether to commit as WIP or stash. If committing, use `wip:` prefix.
- **Untracked files** that belong to the repo:
  Stage and commit if they are complete, or ask if unsure.
- **Untracked files** that are temporary/generated:
  Confirm they are gitignored or ask whether to delete.

Goal: `git status` shows `nothing to commit, working tree clean` before finishing.

## 4. Verify Clean State

```bash
git status
git log --oneline -3
```

Confirm working tree is clean and the latest commit reflects what was done.

## 5. Output Handoff Summary

Print a concise summary for the next session:

```
## Saved: #{pr_number} — {PR title}

**Branch**: {branch} (clean)
**Latest commit**: {short_hash} {commit message}

### What was done this session
- {task or step completed}
- {task or step completed}

### Next task
{first remaining task from tasks.md — be specific}

### Needs decision / blocked
{anything requiring user input before work can continue, if any}

Resume with: /re
```

# Important

- tasks.md must be committed before finishing — it is the source of truth for /re
- Never leave modified tracked files uncommitted
- If a change is too incomplete to commit, use `git stash` and note it in the summary
- Do not implement anything new — this command only records state

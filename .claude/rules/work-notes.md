# Work Notes

## Purpose

Record decisions, learnings, and context that cannot be found in commit history. Focus on **why** and **how**, not **what** (git log shows what changed).

## Location

`.pr/xxxxx/notes.md` where xxxxx is 5-digit PR number

## Content

Record only what is NOT obvious from commit history:

**DO record**:
- Why you made specific decisions
- Alternative approaches considered and why rejected
- Problems encountered and how solved
- Insights and learnings
- Follow-up tasks or known issues

**DO NOT record**:
- List of changed files (use `git diff --stat`)
- What was changed (use `git log` and `git show`)
- Basic description of changes (use commit messages)

## Format

Free-form markdown with chronological entries. Use timestamps for multiple work sessions.

### Suggested Structure

```markdown
# Notes

## 2026-02-19

### Decision: Why X over Y

[Explanation]

### Problem: Issue with Z

**Symptom**: [What went wrong]

**Cause**: [Root cause]

**Solution**: [How fixed]

### Learning

[Insight gained]

### TODO

- [ ] Follow-up task
```

## Example

Good example (captures context):
```markdown
## 2026-02-19

### Decision: .pr/ instead of .issues/

User pointed out work is organized by PRs, not issues. PRs always exist, issues may not. Shorter name (.pr/ vs .prs/) is clearer.

### Problem: nabledge-6 output path

Initially changed to .pr/ but user noted this is user-facing and would break existing workflows. Reverted to work/YYYYMMDD/ to avoid impact.

### TODO

- Issue #40: Consider .nabledge/YYYYMMDD/ for nabledge-6 output (avoids conflict with project work/ directories)
```

Bad example (duplicates git log):
```markdown
## Changed Files

- .claude/rules/work-log.md
- .claude/rules/postmortem.md
[etc...]

## What Changed

Directory structure changed from work/YYYYMMDD/ to .pr/xxxxx/
```

## When to Create

Create notes.md when:
- You make non-obvious decisions
- You encounter and solve problems
- You learn something worth documenting
- There are follow-up tasks

Not every PR needs extensive notes. Simple, straightforward changes may not need notes at all.

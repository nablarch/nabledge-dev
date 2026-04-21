# Work Notes

## Purpose

Record **decisions and their background** — the why and how that cannot be found in commit history. Keep it concise: one entry per decision or problem solved.

## Location

`.pr/xxxxx/notes.md` where xxxxx is 5-digit PR number

## Content

Record only what is NOT obvious from commit history:

**DO record**:
- Why you made specific decisions
- Alternative approaches considered and why rejected
- Problems encountered and how solved
- Insights and learnings

**DO NOT record**:
- Task lists or in-progress work tracking — use `tasks.md` for that
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
```

## Detail Files

For detailed artifacts that would bloat notes.md (investigation results, design outputs, analysis data, etc.), create separate files in the same `.pr/xxxxx/` directory and link from notes.md.

**When to use a separate file:**
- Investigation items and results (e.g., `investigation-items.md`)
- Design decisions with large tables or diagrams
- Analysis data or structured output that is referenced but not narrative

**Example:**

```markdown
### Investigation: RBKC feasibility

Ran 12 investigation scripts against v6 source data before implementation.

→ Details: [investigation-items.md](investigation-items.md)

Key findings that shaped the design:
- RST directive coverage: 3 unknown directives found → added to converter
- Stage 2 hint match rate: 40% → decided to drop Stage 2, use Stage 1 only
```

Keep notes.md as a narrative log. Put structured data in the linked file.

## Example

Good example (captures context):
```markdown
## 2026-02-19

### Decision: .pr/ instead of .issues/

User pointed out work is organized by PRs, not issues. PRs always exist, issues may not. Shorter name (.pr/ vs .prs/) is clearer.

### Problem: nabledge-6 output path

Initially changed to .pr/ but user noted this is user-facing and would break existing workflows. Reverted to work/YYYYMMDD/ to avoid impact.
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

Not every PR needs extensive notes. Simple, straightforward changes may not need notes at all.

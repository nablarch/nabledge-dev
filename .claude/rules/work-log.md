# Work Log

Two files per PR under `.work/xxxxx/` (xxxxx is the 5-digit zero-padded issue number):

| File | Purpose |
|------|---------|
| `notes.md` | Decisions and their background — why and how, not what |
| `tasks.md` | Task list — what needs to be done, current status, steps |

See `.claude/rules/work-notes.md` for notes.md format and guidelines.

## notes.md

- Decisions, alternatives considered, problems solved, learnings
- Do not record task lists here — use tasks.md
- Do not duplicate information from commit messages or git diff
- Not every PR needs notes — only when decisions are non-obvious

## tasks.md

- Single source of truth for all tasks in the PR
- Keep it up to date at all times — update before starting work, after completing each task
- PR body links to tasks.md instead of duplicating the task list (DRY)
- Break complex tasks into steps with enough detail that work can resume without additional context

### Update and push immediately

tasks.md changes must be committed and pushed as soon as they happen — do not batch them with later work.

- **When tasks change** (added / split / reordered / scope updated): commit and push tasks.md immediately, before starting the work
- **When a task completes** (step checked off, task moved to Done): commit and push tasks.md immediately, before moving to the next task
- Never leave tasks.md with uncommitted changes between work sessions
- A single commit per tasks.md update is fine — use a concise message like `docs: update tasks.md — {what changed}`

### Format

```markdown
# Tasks: {PR title}

**PR**: #{pr_number}
**Issue**: #{issue_number}
**Updated**: {YYYY-MM-DD}

## In Progress

### {Task name}
**Steps:**
- [ ] Step 1
- [ ] Step 2

## Not Started

### {Task name}
...

## Done

- [x] {Completed task} — committed `{short_hash}`
```

## PR Body

The Tasks section in the PR body links to tasks.md — do not duplicate the list:

```markdown
## Tasks

See [tasks.md](.work/xxxxx/tasks.md).
```

## Git Tracking

`.work/` is always git-tracked. It is the handoff record between sessions — decisions, rationale, and task state cannot be recovered from code or git log alone. Never add `.work/` to `.gitignore`.

## Temporary Files

For temporary files during processing, use `.tmp/` directory. See `.claude/rules/temporary-files.md`.

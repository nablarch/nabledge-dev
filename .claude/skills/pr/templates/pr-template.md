# PR Template

This is the standard template for all pull requests. All PRs must reference a GitHub issue following issue-driven development.

## Template Structure

```markdown
Closes #[ISSUE_NUMBER]

## Approach
[Describe the solution strategy addressing the Situation and Pain from the issue. Explain WHY this approach was chosen, any alternatives considered, and trade-offs made.]

## Tasks

See [tasks.md](.work/[ISSUE_NUMBER_5DIGIT]/tasks.md).

## Expert Review

AI-driven expert reviews conducted before PR creation (see `.claude/rules/expert-review.md`):

- [Software Engineer](.work/[ISSUE_NUMBER_5DIGIT]/review-by-software-engineer.md) - Rating: 4/5
- [QA Engineer](.work/[ISSUE_NUMBER_5DIGIT]/review-by-qa-engineer.md) - Rating: 5/5

## Success Criteria Check

[Read the issue body and extract success criteria section, then create verification table]

| Criterion | Status | Evidence |
|-----------|--------|----------|
| [Criterion 1 from issue] | ✅ Met / ❌ Not Met | [How this was verified] |
| [Criterion 2 from issue] | ✅ Met / ❌ Not Met | [How this was verified] |

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

## Usage in Workflows

This template is used for all PRs following issue-driven development:
- All PRs must close a GitHub issue
- Branch name follows `{number}-{description}` convention (e.g., `42-add-login`)
- Success criteria from issue are verified against implementation

## Placeholder Replacement

When generating PR body from this template:
- `[ISSUE_NUMBER]` → Actual issue number
- `[ISSUE_NUMBER_5DIGIT]` → 5-digit zero-padded issue number (e.g., 42 → 00042)
- `[Describe the solution...]` → Generated approach description addressing Situation/Pain from issue
- `[Criterion X from issue]` → Extracted from issue body
- `[How this was verified]` → Evidence from implementation

## Example

```markdown
Closes #42

## Approach
Implemented session-based authentication using JWT tokens. Chose this approach for stateless authentication and better scalability compared to server-side sessions.

## Tasks

See [tasks.md](.work/00042/tasks.md).

## Expert Review

AI-driven expert reviews conducted before PR creation (see `.claude/rules/expert-review.md`):

- [Software Engineer](.work/00042/review-by-software-engineer.md) - Rating: 4/5
- [QA Engineer](.work/00042/review-by-qa-engineer.md) - Rating: 5/5

## Success Criteria Check

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Users can log in with username and password | ✅ Met | Login form implemented and tested in auth.test.js:45 |
| Session persists across page reloads | ✅ Met | JWT stored in localStorage, verified in session.test.js:78 |
| Invalid credentials show error message | ✅ Met | Error handling tested in auth.test.js:92 |

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

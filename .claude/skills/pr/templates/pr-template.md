# PR Template

This is the standard template for all pull requests. All PRs must reference a GitHub issue following issue-driven development.

## Template Structure

```markdown
Closes #[ISSUE_NUMBER]

## Approach
[Describe the solution strategy and key design decisions. Explain WHY this approach was chosen, any alternatives considered, and trade-offs made.]

## Tasks
[List implementation tasks completed as checkboxes]
- [x] Task 1
- [x] Task 2
- [x] Task 3

## Expert Review

> **Instructions for Expert**: Please review the approach and implementation, then fill in this table with your feedback.

| Aspect | Status | Comments |
|--------|--------|----------|
| Architecture | ⚪ Not Reviewed / ✅ Approved / ⚠️ Needs Changes | |
| Code Quality | ⚪ Not Reviewed / ✅ Approved / ⚠️ Needs Changes | |
| Testing | ⚪ Not Reviewed / ✅ Approved / ⚠️ Needs Changes | |
| Documentation | ⚪ Not Reviewed / ✅ Approved / ⚠️ Needs Changes | |

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
- Branch name follows `issue-<number>` convention
- Success criteria are verified against the issue

## Placeholder Replacement

When generating PR body from this template:
- `[ISSUE_NUMBER]` → Actual issue number
- `[Describe the solution...]` → Generated approach description
- `[List implementation...]` → Generated task list
- `[Criterion X from issue]` → Extracted from issue body
- `[How this was verified]` → Evidence from implementation

## Example

```markdown
Closes #42

## Approach
Implemented session-based authentication using JWT tokens. Chose this approach for stateless authentication and better scalability compared to server-side sessions.

## Tasks
- [x] Create login form component
- [x] Implement JWT token generation
- [x] Add authentication middleware
- [x] Write integration tests

## Expert Review

> **Instructions for Expert**: Please review the approach and implementation, then fill in this table with your feedback.

| Aspect | Status | Comments |
|--------|--------|----------|
| Architecture | ⚪ Not Reviewed / ✅ Approved / ⚠️ Needs Changes | |
| Code Quality | ⚪ Not Reviewed / ✅ Approved / ⚠️ Needs Changes | |
| Testing | ⚪ Not Reviewed / ✅ Approved / ⚠️ Needs Changes | |
| Documentation | ⚪ Not Reviewed / ✅ Approved / ⚠️ Needs Changes | |

## Success Criteria Check

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Users can log in with username and password | ✅ Met | Login form implemented and tested in auth.test.js:45 |
| Session persists across page reloads | ✅ Met | JWT stored in localStorage, verified in session.test.js:78 |
| Invalid credentials show error message | ✅ Met | Error handling tested in auth.test.js:92 |

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

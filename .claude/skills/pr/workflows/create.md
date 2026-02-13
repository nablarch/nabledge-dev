# PR Creation Workflow

This workflow creates a PR from the current branch to main.

## Required Tools

- Bash
- Read

## Execution Steps

### 1. Pre-flight Checks

**1.1 Verify Current Branch**

```bash
git branch --show-current
```

If current branch is `main` or `master`, exit with error:
```
Error: Cannot create PR from main branch.
Please create a feature/issue branch first.
```

**1.2 Get Default Branch**

```bash
default_branch=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
```

**1.3 Check Commit History**

```bash
git log "$default_branch"..HEAD --oneline
```

If no commits exist, exit with error:
```
Error: No new commits from {default_branch}.
Please commit your changes first.
```

**1.4 Verify Remote Push**

```bash
git status
```

If "Your branch is ahead of" or "have diverged" appears, push is needed:
```bash
git push -u origin "$(git branch --show-current)"
```

If push fails (rejected):
```bash
git pull --rebase origin "$(git branch --show-current)"
git push
```

### 2. Generate PR Title and Description

**2.1 Get Issue Number**

Use AskUserQuestion to get the issue number this PR addresses:

```
Question: "What is the issue number this PR addresses?"
Header: "Issue"
Options:
  - Label: "I have an issue number"
    Description: "This PR closes a specific issue"
  - Label: "No issue number"
    Description: "This PR has no associated issue"
```

If user provides issue number, validate it exists:
```bash
gh issue view {issue_number}
```

If issue doesn't exist, exit with error:
```
Error: Issue #{issue_number} not found.
Please create an issue first or verify the issue number.
```

**2.2 Get Commit History and Diff**

```bash
git log "$default_branch"..HEAD --format="%s"
git diff "$default_branch"...HEAD --stat
```

**2.3 Generate Title and Description**

Analyze commit history and diff, generate in the following format:

**Title**: Summarize main changes (within 70 characters)
- Example: "feat: Add user authentication feature"
- Example: "fix: Fix session timeout on login"

**Description**:

If issue number provided:
```markdown
Closes #{issue_number}

## Approach
{Describe the solution strategy and key design decisions. Explain WHY this approach was chosen, any alternatives considered, and trade-offs made.}

## Tasks
{List implementation tasks completed as checkboxes}
- [x] {Task 1}
- [x] {Task 2}
- [x] {Task 3}

## Expert Review

> **Instructions for Expert**: Please review the approach and implementation, then fill in this table with your feedback.

| Aspect | Status | Comments |
|--------|--------|----------|
| Architecture | ⚪ Not Reviewed / ✅ Approved / ⚠️ Needs Changes | |
| Code Quality | ⚪ Not Reviewed / ✅ Approved / ⚠️ Needs Changes | |
| Testing | ⚪ Not Reviewed / ✅ Approved / ⚠️ Needs Changes | |
| Documentation | ⚪ Not Reviewed / ✅ Approved / ⚠️ Needs Changes | |

## Success Criteria Check

{Read the issue and extract its success criteria, then create a verification table}

| Criterion | Status | Evidence |
|-----------|--------|----------|
| {Criterion 1 from issue} | ✅ Met / ❌ Not Met | {How this was verified} |
| {Criterion 2 from issue} | ✅ Met / ❌ Not Met | {How this was verified} |

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

If no issue number:
```markdown
## Summary
{Describe purpose and content of changes in 1-3 sentences}

## Changes
{List main changes as bullet points}

## Testing
- [ ] Manual testing completed
- [ ] Tests added/updated (if needed)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

### 3. Create PR

Create PR with generated title and description:

```bash
gh pr create \
  --title "{generated_title}" \
  --body "{generated_description}" \
  --base "$default_branch" \
  --head "$current_branch"
```

### 4. Display Result

```
## PR Creation Complete

**PR**: {pr_url}
**Branch**: {source_branch} → {target_branch}
**Title**: {title}

Please request review from reviewers.
```

## Error Handling

| Error | Response |
|-------|----------|
| Execute from main branch | Guide to execute from feature/issue branch |
| No commits | Guide to commit changes first |
| Push failure | `git pull --rebase` and retry push |
| Authentication error | Authenticate with `gh auth login` |

## Notes

1. **Emoji Usage**: Do not use emojis unless user explicitly requests them
2. **GitHub Permissions**: Requires Write or higher permissions
3. **Title Quality**: Generate appropriate title if commit messages are inadequate
4. **HEREDOC Usage**: Use HEREDOC for multi-line PR body to ensure correct formatting

### HEREDOC Usage Example

**With Issue Number:**
```bash
gh pr create \
  --title "feat: Add user authentication" \
  --body "$(cat <<'EOF'
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
EOF
)" \
  --base main \
  --head issue-42
```

**Without Issue Number:**
```bash
gh pr create \
  --title "chore: Update dependencies" \
  --body "$(cat <<'EOF'
## Summary
Updated project dependencies to latest versions.

## Changes
- Updated npm packages to address security vulnerabilities
- Updated GitHub Actions to latest versions

## Testing
- [x] All tests pass
- [x] Build succeeds

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)" \
  --base main \
  --head update-deps
```

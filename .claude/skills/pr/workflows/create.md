# PR Creation Workflow

This workflow creates a PR from the current branch to the development branch (typically `develop`).

## Required Tools

- Bash
- Read
- AskUserQuestion

## Execution Steps

### 1. Pre-flight Checks

**1.1 Verify Current Branch**

```bash
current_branch=$(git branch --show-current)
echo "Current branch: ${current_branch}"
```

If current branch is `main`, `master`, or `develop`, exit with error:

Error: Cannot create PR from the main/develop branch.
Please create a feature/issue branch first.

**1.2 Get Development Branch**

```bash
# Get repository default branch (should be develop)
default_branch=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
echo "Repository default branch: ${default_branch}"

# For PR creation, always target develop (see .claude/rules/branch-strategy.md)
if [[ "$default_branch" == "develop" ]]; then
  target_branch="develop"
else
  echo "WARNING: Repository default is ${default_branch}, but using 'develop' per branch strategy"
  target_branch="develop"
fi

echo "PR will target: ${target_branch}"
```

**1.3 Check Commit History**

```bash
git log "${target_branch}"..HEAD --oneline
```

If no commits exist, exit with error:

Error: No new commits from ${target_branch}.
Please commit your changes first.

**1.4 Verify Remote Push**

```bash
git status
```

If "Your branch is ahead of" or "have diverged" appears, push is needed:

```bash
git push -u origin "${current_branch}"
```

If push fails (rejected):

```bash
git pull --rebase origin "${current_branch}"
git push
```

### 2. Generate PR Title and Description

**2.1 Get Issue Number**

Check if branch follows `issue-<number>` naming convention:

```bash
if [[ "$current_branch" =~ ^issue-([0-9]+)$ ]]; then
  issue_number="${BASH_REMATCH[1]}"
  echo "Detected issue number from branch: #${issue_number}"
else
  issue_number=""
fi
```

If no issue number detected from branch name, use the AskUserQuestion tool to prompt the user:
- Question: "What is the issue number this PR addresses?"
- User must provide the issue number via text input
- Issue number is required (issue-driven development standard)

If user provides an issue number, validate it is numeric:

```bash
if ! [[ "$issue_number" =~ ^[0-9]+$ ]]; then
  echo "Error: Issue number must be a positive integer"
  exit 1
fi
```

Then validate the issue exists:

```bash
if ! gh issue view "$issue_number" &>/dev/null; then
  echo "Error: Issue #${issue_number} not found."
  echo "Please create an issue first or verify the issue number."
  exit 1
fi
echo "Validated issue #${issue_number} exists"
```

**2.2 Get Commit History and Diff**

```bash
echo "Analyzing commits and changes..."
git log "${target_branch}"..HEAD --format="%s"
git diff "${target_branch}"...HEAD --stat
```

**2.3 Generate Title and Description**

Analyze commit history and diff using the following algorithm:

**Title Generation Logic**:
- If only 1 commit: Use the commit message subject line
- If multiple commits: Identify the common theme across commit messages
- If commit messages are unclear (e.g., "fix", "update"): Analyze the diff to determine primary change type
- Format: `<type>: <description>` where type is one of: feat, fix, refactor, docs, test, chore
- MUST be under 70 characters
- Example: "feat: Add JWT authentication middleware"
- Example: "fix: Resolve session timeout on login"

**Description Generation Logic**:
- Extract context from commit message bodies (not just subjects)
- Identify files with most changes from `git diff --stat`
- If issue exists, read it with `gh issue view ${issue_number} --json body -q .body` and extract success criteria
- Generate description following the appropriate template

**Template Usage**:

Use `.claude/skills/pr/templates/pr-template.md` and replace placeholders:
- `[ISSUE_NUMBER]` → Actual issue number
- `[Describe the solution...]` → Generated approach description from commits and diff
- `[List implementation...]` → Generated task list from commits
- `[Criterion X from issue]` → Extracted from issue success criteria
- `[How this was verified]` → Evidence from implementation (file paths, test results)

See `.claude/skills/pr/templates/` for complete template structure and examples.

### 3. Create PR

**IMPORTANT**: Use HEREDOC syntax for multi-line PR body to ensure correct formatting.

**HEREDOC Syntax Example**:

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
  --base develop \
  --head issue-42
```

**Execute PR Creation**:

Create PR with generated title and description:

```bash
gh pr create \
  --title "${generated_title}" \
  --body "${generated_description}" \
  --base "${target_branch}" \
  --head "${current_branch}"
```

Capture the PR URL:
```bash
pr_url=$(gh pr view --json url -q .url)
echo "PR created: ${pr_url}"
```

### 4. Display Result

Display the PR URL and guide user to review on GitHub:

```
## PR Creation Complete

**PR**: ${pr_url}
**Branch**: ${current_branch} → ${target_branch}
**Title**: ${generated_title}

📝 Please review the PR description on GitHub.
   If any changes are needed, let me know and I will update it.
```

## Error Handling

| Error | Response |
|-------|----------|
| Execute from main/develop branch | Guide to execute from feature/issue branch |
| No commits | Guide to commit changes first |
| Push failure | `git pull --rebase` and retry push |
| Authentication error | Authenticate with `gh auth login` |
| Issue not found | Create issue first (required for issue-driven development) |
| No issue number provided | Prompt user for issue number (required) |

## Notes

1. **Emoji Usage**: Do not use emojis unless user explicitly requests them
2. **GitHub Permissions**: Requires Write or higher permissions
3. **Title Quality**: Generate appropriate title if commit messages are inadequate
4. **HEREDOC Usage**: ALWAYS use HEREDOC for multi-line PR body to ensure correct formatting
5. **Branch Strategy**: PRs should target `develop` by default (see `.claude/rules/branch-strategy.md`)
6. **Variable Syntax**: Always use `${variable}` or `"$variable"` in bash commands for safety
7. **PR Template**: Use `.claude/skills/pr/templates/pr-template.md` for consistent formatting
8. **Review Flow**: After PR creation, user reviews on GitHub and can request changes from the AI agent
9. **Issue Required**: All PRs must reference a GitHub issue (issue-driven development standard)

# PR Creation Workflow

This workflow creates a PR from the current branch to the main branch.

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

If current branch is `main` or `master`, exit with error:

Error: Cannot create PR from the main/master branch.
Please create an issue-based branch first.

**1.2 Get Target Branch**

```bash
# Get repository default branch
default_branch=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
echo "Repository default branch: ${default_branch}"

# For PR creation, always target main (default branch)
target_branch="$default_branch"

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

Extract issue number from branch name (required):

```bash
if [[ "$current_branch" =~ ^([0-9]+)- ]]; then
  # Extract issue number (format: 60-sync-branches)
  issue_number="${BASH_REMATCH[1]}"
  echo "Detected issue number from branch: #${issue_number}"
else
  # Branch name doesn't match expected pattern
  echo "Error: Branch name must follow format: {number}-{description}"
  echo "Example: 60-sync-branches"
  echo ""
  echo "Please use /hi command to create properly formatted branch"
  exit 1
fi
```

If user provides an issue number, validate it is numeric:

```bash
if [[ -n "$issue_number" ]]; then
  if ! [[ "$issue_number" =~ ^[0-9]+$ ]]; then
    echo "Error: Issue number must be a positive integer"
    exit 1
  fi

  # Validate the issue exists
  if ! gh issue view "$issue_number" &>/dev/null; then
    echo "Error: Issue #${issue_number} not found."
    echo "Please create an issue first or verify the issue number."
    exit 1
  fi
  echo "Validated issue #${issue_number} exists"
fi
```

**2.2 Gather Information**

Collect all necessary information for PR generation:

```bash
# Get commit history
echo "Analyzing commits..."
commits=$(git log "${target_branch}"..HEAD --format="%s%n%b")

# Get diff statistics
echo "Analyzing changes..."
diff_stat=$(git diff "${target_branch}"...HEAD --stat)

# Get issue body if issue number exists
if [[ -n "$issue_number" ]]; then
  echo "Fetching issue details..."
  issue_body=$(gh issue view "$issue_number" --json body -q .body)
else
  echo "No issue number: Skipping issue body fetch"
  issue_body=""
fi
```

**2.3 Load PR Template**

Use the Read tool to load `.claude/skills/pr/templates/pr-template.md`.

The template contains the following structure with placeholders:
```markdown
Closes #[ISSUE_NUMBER]

## Approach
[Describe the solution...]

## Tasks
[List implementation...]

## Expert Review
[Review table]

## Success Criteria Check
[Criterion X from issue] | Status | Evidence

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

**2.4 Generate Title**

Analyze commits to generate appropriate PR title:

**Title Generation Rules**:
1. If only 1 commit: Use the commit message subject line
2. If multiple commits: Identify common theme across commit messages
3. If commit messages unclear (e.g., "fix", "update"): Analyze diff to determine primary change type
4. Format: `<type>: <description>` where type is one of: feat, fix, refactor, docs, test, chore
5. MUST be under 70 characters

**Examples**:
- "feat: Add JWT authentication middleware"
- "fix: Resolve session timeout on login"
- "refactor: Extract validation logic to separate module"

**2.5 Generate Description with Placeholder Replacement**

Replace each placeholder in the loaded template:

**Step 1: Replace [ISSUE_NUMBER]**

Replace with the issue number:
```
Closes #[ISSUE_NUMBER]
↓
Closes #42
```

**Step 2: Replace [Describe the solution...]**
- Summarize the approach from commit message bodies
- Identify key design decisions from changed files (using diff_stat)
- Explain WHY this approach was chosen
- Example output:
  ```
  Implemented session-based authentication using JWT tokens. Chose this
  approach for stateless authentication and better scalability compared
  to server-side sessions.
  ```

**Step 3: Replace [List implementation...]**
- Extract task list from commit messages (subjects)
- Format as checkbox list with all items checked
- Example output:
  ```
  - [x] Create login form component
  - [x] Implement JWT token generation
  - [x] Add authentication middleware
  - [x] Write integration tests
  ```

**Step 4: Replace Expert Review Section**

Replace with links to expert review files from `/hi` step 8:
- Expert reviews are saved in `.pr/{issue_number}/review-by-{expert-role}.md`
- List each expert with their rating
- Example output:
  ```
  ## Expert Review

  AI-driven expert reviews conducted before PR creation (see `.claude/rules/expert-review.md`):

  - [Software Engineer](../.pr/42/review-by-software-engineer.md) - Rating: 4/5
  - [Prompt Engineer](../.pr/42/review-by-prompt-engineer.md) - Rating: 5/5
  ```

**Step 5: Replace Success Criteria Section**

Parse issue_body to extract success criteria:
- Look for lines starting with `- [ ]` or `- [x]` under "Success Criteria" heading
- For each criterion, create a table row:
  - Criterion: The criterion text
  - Status: "✅ Met" (if implemented) or "❌ Not Met"
  - Evidence: Specific file paths, line numbers, or test names
- Example output:
  ```
  | Criterion | Status | Evidence |
  |-----------|--------|----------|
  | Users can log in with username and password | ✅ Met | Login form implemented in auth.component.tsx:45 |
  | Session persists across page reloads | ✅ Met | JWT stored in localStorage, verified in session.test.js:78 |
  ```

**Step 6: Add Attribution**
- Keep the attribution line at the end:
  ```
  🤖 Generated with [Claude Code](https://claude.com/claude-code)
  ```

**Example Complete Output**:
```markdown
Closes #42

## Approach
Implemented session-based authentication using JWT tokens. Chose this approach
for stateless authentication and better scalability compared to server-side sessions.

## Tasks
- [x] Create login form component
- [x] Implement JWT token generation
- [x] Add authentication middleware
- [x] Write integration tests

## Expert Review

AI-driven expert reviews conducted before PR creation (see \`.claude/rules/expert-review.md\`):

- [Software Engineer](../.pr/42/review-by-software-engineer.md) - Rating: 4/5
- [QA Engineer](../.pr/42/review-by-qa-engineer.md) - Rating: 5/5

## Success Criteria Check

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Users can log in with username and password | ✅ Met | Login form implemented in auth.component.tsx:45 |
| Session persists across page reloads | ✅ Met | JWT stored in localStorage, verified in session.test.js:78 |
| Invalid credentials show error message | ✅ Met | Error handling tested in auth.test.js:92 |

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

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

AI-driven expert reviews conducted before PR creation (see \`.claude/rules/expert-review.md\`):

- [Software Engineer](../.pr/42/review-by-software-engineer.md) - Rating: 4/5
- [QA Engineer](../.pr/42/review-by-qa-engineer.md) - Rating: 5/5

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
  --head 42-add-user-auth
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
| Execute from main/master branch | Guide to execute from issue-based branch |
| No commits | Guide to commit changes first |
| Push failure | `git pull --rebase` and retry push |
| Authentication error | Authenticate with `gh auth login` |
| Invalid branch name format | Guide to use /hi command for proper branch creation |
| Issue not found | Create issue first (required for issue-driven development) |

## Notes

1. **Emoji Usage**: Do not use emojis unless user explicitly requests them
2. **GitHub Permissions**: Requires Write or higher permissions
3. **Title Quality**: Generate appropriate title if commit messages are inadequate
4. **HEREDOC Usage**: ALWAYS use HEREDOC for multi-line PR body to ensure correct formatting
5. **Branch Strategy**: PRs should target `main` (default branch) by default
6. **Variable Syntax**: Always use `${variable}` or `"$variable"` in bash commands for safety
7. **PR Template**: Use `.claude/skills/pr/templates/pr-template.md` for consistent formatting
8. **Review Flow**: After PR creation, user reviews on GitHub and can request changes from the AI agent
9. **Issue Policy**:
   - All branches must follow format: `{number}-{description}` (e.g., `60-sync-branches`)
   - GitHub issue is always required (issue-driven development)
   - Use `/hi` command to ensure proper branch creation

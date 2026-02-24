# Review Response Workflow

This workflow performs Fix → Commit → Reply for unresolved review comments.

## Required Tools

- Bash
- Read
- Edit
- Write
- AskUserQuestion
- Skill (for git commit)

## Execution Steps

### 1. Get PR Information

**1.1 Get PR Information**

```bash
gh pr view "$pr_number" --json number,title,state,headRefName,baseRefName,url
```

**1.2 Verify PR State**

Verify PR is `OPEN`. Exit with error if `CLOSED` or `MERGED`.

**1.3 Verify Branch**

Get current branch:
```bash
current_branch=$(git branch --show-current)
```

If current branch differs from `headRefName`, confirm with AskUserQuestion:
```
Current branch '{current_branch}' differs from PR source branch '{headRefName}'.
Would you like to checkout '{headRefName}'?
```

Options:
- "Yes, checkout" → `git checkout {headRefName}`
- "No, continue as is"

### 2. Get Unresolved Review Comments

**2.1 Get Repository Information**

```bash
owner=$(gh repo view --json owner -q .owner.login)
repo=$(gh repo view --json name -q .name)
```

**2.2 Get All Review Comments with Pagination**

**CRITICAL**: Must use pagination to get ALL comments. GitHub API returns 30 items by default.

```bash
# Get all comments with pagination
page=1
all_comments=""
while true; do
  page_comments=$(gh api "repos/$owner/$repo/pulls/$pr_number/comments?per_page=100&page=$page")
  count=$(echo "$page_comments" | jq 'length')

  if [ "$count" -eq 0 ]; then
    break
  fi

  if [ -z "$all_comments" ]; then
    all_comments="$page_comments"
  else
    all_comments=$(jq -s '.[0] + .[1]' <(echo "$all_comments") <(echo "$page_comments"))
  fi

  page=$((page + 1))
done

echo "Total comments retrieved: $(echo "$all_comments" | jq 'length')"
```

**2.3 Filtering Unresolved Comments**

Extract only comments meeting these conditions:
- Not a reply (no `in_reply_to_id`)
- Has not been replied to yet (check if comment has replies)
- Not outdated (`original_position` should exist or match `position`)

```bash
# Get parent comments (top-level)
parent_comments=$(echo "$all_comments" | jq '[.[] | select(.in_reply_to_id == null)]')

# Filter out comments that already have replies
unresolved_comments=()
for parent_id in $(echo "$parent_comments" | jq -r '.[].id'); do
  has_reply=$(echo "$all_comments" | jq --arg pid "$parent_id" '[.[] | select(.in_reply_to_id == ($pid | tonumber))] | length > 0')

  if [ "$has_reply" = "false" ]; then
    unresolved_comments+=("$parent_id")
  fi
done

echo "Unresolved comments: ${#unresolved_comments[@]}"
```

If 0 unresolved comments:
```
## Review Response Complete

**PR**: {pr_url}

No unresolved comments.
```

Exit.

### 3. Process Each Comment

For each unresolved comment, execute the following:

**3.1 Analysis**

Get comment information:
- `comment.id`: Comment ID (required for replying)
- `comment.body`: Comment body
- `comment.path`: File to fix
- `comment.line`: Line number (if exists)
- `comment.user.login`: Reviewer name

Store the comment ID for later use in replies.

Use Read tool to load file and check relevant section.

**3.2 Decision**

Select one of the following:

1. **Fix needed and content is clear**
   - Proceed autonomously to fix
   - Example: "Fix typo", "Change variable name"

2. **Unclear points**
   - Reply with question
   - Example: "Please improve performance" → "Which specific part is a concern?"

3. **Disagree/Not actionable**
   - Skip and report
   - Example: "Completely rethink architecture" → Defer to user judgment

4. **Difficult to judge**
   - Confirm with AskUserQuestion
   - Options: Fix / Ask question / Skip

**3.3 Fix, Commit, Push (When fixing)**

**3.3.1 Fix File**

Fix file with Edit or Write tool.

If multiple files need fixing, fix all before creating a single commit.

**3.3.2 Commit and Push with git Skill**

Execute git skill's commit subcommand using Skill tool:

```
Skill
  skill: "git"
  args: "commit"
```

Git skill automatically executes:
- Analyze changed files
- Generate commit message (format: `fix: {summary of review feedback}`)
- Staging (git add)
- Commit
- Push

**3.3.3 Get Commit SHA**

```bash
commit_sha=$(git rev-parse HEAD)
repo_url=$(gh repo view --json url -q .url)
```

**3.4 Reply**

Reply directly to the review comment using the stored comment ID:

**For fixes**:

```bash
gh api \
  -X POST \
  "repos/$owner/$repo/pulls/$pr_number/comments" \
  -f body="$(cat <<'EOF'
Fixed

**Commit**: {repo_url}/commit/{commit_sha}

{Brief description of fix}

Co-Authored-By: Claude (jp.anthropic.claude-sonnet-4-5-20250929-v1:0) <noreply@anthropic.com>
EOF
)" \
  -F in_reply_to=${comment_id}
```

**For questions**:

```bash
gh api \
  -X POST \
  "repos/$owner/$repo/pulls/$pr_number/comments" \
  -f body="$(cat <<'EOF'
Please clarify

{Question content}

Co-Authored-By: Claude (jp.anthropic.claude-sonnet-4-5-20250929-v1:0) <noreply@anthropic.com>
EOF
)" \
  -F in_reply_to=${comment_id}
```

**Note**: This creates threaded replies directly under review comments using the `in_reply_to` parameter, providing better context and reviewer experience.

### 4. Resolve Review Comments

After fixing, mark review thread as resolved:

```bash
# gh CLI does not have direct resolve functionality, so request reviewer to resolve
echo "Please request reviewer to resolve threads"
```

### 5. Verification

**CRITICAL**: After posting all replies, verify that all parent comments have replies:

```bash
# Get all comments with pagination
page=1
all_comments=""
while true; do
  page_comments=$(gh api "repos/$owner/$repo/pulls/$pr_number/comments?per_page=100&page=$page")
  count=$(echo "$page_comments" | jq 'length')

  if [ "$count" -eq 0 ]; then
    break
  fi

  if [ -z "$all_comments" ]; then
    all_comments="$page_comments"
  else
    all_comments=$(jq -s '.[0] + .[1]' <(echo "$all_comments") <(echo "$page_comments"))
  fi

  page=$((page + 1))
done

# Check each parent comment has replies
parent_comments=$(echo "$all_comments" | jq '[.[] | select(.in_reply_to_id == null)]')
unresolved=()

for parent_id in $(echo "$parent_comments" | jq -r '.[].id'); do
  has_reply=$(echo "$all_comments" | jq --arg pid "$parent_id" '[.[] | select(.in_reply_to_id == ($pid | tonumber))] | length > 0')

  if [ "$has_reply" = "false" ]; then
    unresolved+=("$parent_id")
  fi
done

if [ ${#unresolved[@]} -gt 0 ]; then
  echo "WARNING: ${#unresolved[@]} parent comments still have no replies:"
  for id in "${unresolved[@]}"; do
    comment_info=$(echo "$parent_comments" | jq --arg id "$id" '.[] | select(.id == ($id | tonumber)) | {id: .id, path: .path, body: .body[0:100]}')
    echo "$comment_info"
  done
  echo ""
  echo "Please investigate why replies were not posted."
fi
```

### 6. Summary

After verification, display summary:

```
## PR Review Response Complete

**PR**: {pr_url}

### Results
- Fixed and replied: {n} items
- Asked questions and replied: {n} items
- Skipped: {n} items
- Verified: All parent comments have replies

Please request reviewer to resolve threads
```

## Error Handling

| Error | Response |
|-------|----------|
| PR not found | Verify correct PR number |
| PR closed/merged | Specify opened PR |
| Push failure | `git pull --rebase` and retry push |
| Conflict | Manually resolve conflict then retry |
| Authentication error | Authenticate with `gh auth login` |

## Notes

1. **Emoji Usage**: Do not use emojis unless user explicitly requests them
2. **GitHub Permissions**: Requires Write or higher for commenting and pushing
3. **Autonomous Judgment**: Respond autonomously when fix content is clear; use AskUserQuestion only when judgment is difficult
4. **Test Execution**: Run related tests if they exist after fixing
5. **Multiple Files**: When one comment requires multiple file fixes, fix all before creating a single commit
6. **Thread Resolution**: GitHub CLI lacks direct resolve functionality, so request reviewer resolution
7. **Threaded Replies**: Always reply directly to review comments for better threading and reviewer experience

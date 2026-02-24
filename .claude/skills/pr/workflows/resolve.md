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
# Get all comments with automatic pagination
all_comments=$(gh api --paginate "repos/$owner/$repo/pulls/$pr_number/comments")

echo "Total comments retrieved: $(echo "$all_comments" | jq 'length')"
```

**2.3 Filtering Unresolved Comments**

Extract only comments meeting these conditions:
- Not a reply (no `in_reply_to_id`)
- Has not been replied to yet (check if comment has replies)
- Not outdated (`original_position` should exist or match `position`)

```bash
# Create jq filter for finding unresolved comments
cat > /tmp/unresolved-filter.jq << 'JQEOF'
. as $all |
map(select(.in_reply_to_id == null)) as $parents |
$parents | map(
  . as $parent |
  {
    id: $parent.id,
    path: $parent.path,
    line: $parent.line,
    body: $parent.body,
    user: $parent.user.login,
    has_reply: ($all | any(.in_reply_to_id == $parent.id))
  }
) | map(select(.has_reply == false))
JQEOF

# Get unresolved parent comments
unresolved_json=$(echo "$all_comments" | jq -f /tmp/unresolved-filter.jq)
unresolved_count=$(echo "$unresolved_json" | jq 'length')

echo "Unresolved comments: $unresolved_count"

# Debug: Show summary of all comments
echo "Debug - Comment summary:"
echo "$all_comments" | jq -r 'group_by(.in_reply_to_id == null) |
  "Total: \(map(length) | add // 0) (Replies: \((.[0] // []) | length), Parents: \((.[1] // []) | length))"'
```

If 0 unresolved comments:
```
## Review Response Complete

**PR**: {pr_url}

No unresolved comments.
```

Exit.

### 3. Process Each Comment

For each unresolved comment in `$unresolved_json`, execute the following:

**3.1 Analysis**

Get comment information from JSON:

```bash
# Process each unresolved comment
for i in $(seq 0 $((unresolved_count - 1))); do
  comment_id=$(echo "$unresolved_json" | jq -r ".[$i].id")
  comment_body=$(echo "$unresolved_json" | jq -r ".[$i].body")
  comment_path=$(echo "$unresolved_json" | jq -r ".[$i].path")
  comment_line=$(echo "$unresolved_json" | jq -r ".[$i].line")
  comment_user=$(echo "$unresolved_json" | jq -r ".[$i].user")

  echo "Processing comment #$comment_id from @$comment_user"
  echo "File: $comment_path:$comment_line"
  echo "Comment: ${comment_body:0:100}..."
done
```

Extract:
- `comment_id`: Comment ID (required for replying)
- `comment_body`: Comment body
- `comment_path`: File to fix
- `comment_line`: Line number (if exists)
- `comment_user`: Reviewer name

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
# Re-fetch all comments to get latest state
all_comments=$(gh api --paginate "repos/$owner/$repo/pulls/$pr_number/comments")

# Use same jq filter to find remaining unresolved comments
remaining_unresolved=$(echo "$all_comments" | jq -f /tmp/unresolved-filter.jq)
remaining_count=$(echo "$remaining_unresolved" | jq 'length')

if [ "$remaining_count" -gt 0 ]; then
  echo ""
  echo "WARNING: $remaining_count parent comment(s) still have no replies:"
  echo "$remaining_unresolved" | jq -r '.[] | "  - ID \(.id): \(.body[0:80])... (@\(.user) on \(.path):\(.line))"'
  echo ""
  echo "Please investigate why replies were not posted."
  echo "This may indicate:"
  echo "  1. Reply posting failed silently"
  echo "  2. New comments were added during processing"
  echo "  3. GitHub API sync delay"
else
  echo "✓ Verification passed: All parent comments have replies"
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

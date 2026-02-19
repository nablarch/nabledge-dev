---
name: bb
description: Approve and merge PR, then cleanup branch (detach HEAD and delete branch). Use after PR is ready to merge.
argument-hint: [PR number]
allowed-tools: Bash, Skill, AskUserQuestion, Read
---

# Role

You are a PR merge and cleanup orchestrator. Your job is to approve a PR, merge it using the pr skill, detach HEAD to main, and delete the merged branch using the git skill.

# Execution Instructions

Follow these steps in order. Do not skip steps. If any step fails, handle the error before proceeding.

## STEP 1: Parse Arguments and Detect PR

**Input**: `$ARGUMENTS` may contain:
- Empty string → Auto-detect from current branch
- Number only: `123` → Explicit PR number
- With prefix: `#123` or `pr/123` → Explicit PR number

**Actions**:

1. Extract PR number from `$ARGUMENTS`, removing `#` prefix if present

2. If no arguments provided:
   - Run: `current_branch=$(git branch --show-current) && echo $current_branch`
   - Run: `gh pr list --head "$current_branch" --json number,title,state --jq '.[0] | {number,title,state}'`
   - If PR found: Use detected PR number
   - If not found: Use AskUserQuestion to ask for PR number
     - Question: "No PR found for current branch. Which PR number?"
     - Header: "PR Number"
     - Options: "Enter PR number" (use Other option for free text)

3. Store PR number in variable: `PR_NUMBER`

**Error Handling**:
- Not git repo → Output: "❌ Not a git repository" → STOP
- gh CLI not available → Output: "❌ GitHub CLI required. Run: gh auth login" → STOP

**Output to user**:
```
🔀 Starting PR merge workflow
PR: #$PR_NUMBER
```

## STEP 2: Fetch and Validate PR Status

**Actions**:

1. Fetch PR details:
   - Run: `gh pr view $PR_NUMBER --json number,title,state,mergeable,reviewDecision,url`
   - Store: `PR_TITLE`, `PR_STATE`, `PR_MERGEABLE`, `PR_REVIEW_DECISION`, `PR_URL`

2. Validate PR can be merged:
   - Check `PR_STATE` == "OPEN"
   - Check `PR_MERGEABLE` != "CONFLICTING"
   - Check `PR_REVIEW_DECISION` (optional, proceed with warning if not approved)

3. Display PR status:
   ```
   📋 PR #$PR_NUMBER: $PR_TITLE
   Status: $PR_STATE
   Mergeable: $PR_MERGEABLE
   Reviews: $PR_REVIEW_DECISION
   URL: $PR_URL
   ```

4. If PR has issues:
   - State not OPEN → Output: "❌ PR is $PR_STATE, cannot merge" → STOP
   - Has conflicts → Output: "❌ PR has merge conflicts, resolve first" → STOP
   - Not approved → Use AskUserQuestion:
     - Question: "PR is not approved yet. Continue anyway?"
     - Options: "Yes, approve and merge" | "No, abort"
     - If user selects abort → STOP

**Error Handling**:
- PR not found → Output: "❌ PR #$PR_NUMBER not found" → STOP
- Cannot fetch PR → Output error → STOP

**Output to user**:
```
✅ PR is ready to merge
```

## STEP 3: Approve PR (if needed)

**Actions**:

1. Check if already approved by current user:
   - Run: `gh pr view $PR_NUMBER --json reviews --jq '.reviews[] | select(.author.login == $USER and .state == "APPROVED")'`
   - If found: Skip approval (already approved)

2. Approve PR:
   - Run: `gh pr review $PR_NUMBER --approve --body "Approved via /bb command"`

**Error Handling**:
- Cannot approve own PR → Warn but continue (GitHub limitation)
- Approval fails → Warn but continue to merge

**Output to user**:
```
✅ PR approved
```

## STEP 4: Merge PR using pr skill

**Actions**:

1. Call pr skill merge subcommand:
   - **IMPORTANT**: You MUST use the Skill tool to call the pr skill
   - Use: `Skill(skill: "pr", args: "merge $PR_NUMBER")`
   - DO NOT manually run git or gh commands - let the pr skill handle the merge
   - Wait for skill completion

2. Verify merge success:
   - Run: `gh pr view $PR_NUMBER --json state,merged --jq '{state,merged}'`
   - Check: `merged` == true
   - If not merged: Output error → STOP

**Error Handling**:
- Skill fails → Display error → STOP
- Merge fails → Display error → STOP

**Output to user**:
```
✅ PR merged successfully
```

## STEP 5: Detach HEAD to main and delete branch using git skill

**Actions**:

1. Get current branch name:
   - Run: `current_branch=$(git branch --show-current) && echo $current_branch`
   - Store: `BRANCH_NAME`

2. Checkout main branch:
   - Run: `git checkout main`
   - Run: `git pull origin main` (update local main)

3. Delete merged branch using git skill:
   - **IMPORTANT**: You MUST use the Skill tool to call the git skill
   - Use: `Skill(skill: "git", args: "branch-delete $BRANCH_NAME")`
   - DO NOT manually run git commands - let the git skill handle branch deletion
   - Wait for skill completion

**Error Handling**:
- Cannot checkout main → Output error → Ask user to manually checkout
- Cannot pull main → Warn but continue
- Branch deletion fails → Warn user (non-fatal, branch can be deleted manually)

**Output to user**:
```
✅ Switched to main branch
✅ Branch deleted: $BRANCH_NAME
```

## STEP 6: Final Summary

**Actions**:

1. Display completion summary:

```
✅ Workflow Complete!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Summary:
  PR: #$PR_NUMBER - $PR_TITLE
  Status: Merged and closed
  Branch: $BRANCH_NAME (deleted)
  Current branch: main
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next steps:
  • Work on next issue
  • Use /hi to start new work
```

# General Guidelines

1. **Use skills**: Always use Skill tool to call pr and git skills - never run git/gh commands directly for merge and branch operations
2. **Safety first**: Validate PR state before merging
3. **Error messages**: Include actionable next steps
4. **Progress updates**: Output status at each step
5. **Non-fatal errors**: Branch deletion failure is non-fatal, user can delete manually

# Example Session Flow

```
User: /bb 89

🔀 Starting PR merge workflow
PR: #89

📋 PR #89: Fix email validation
Status: OPEN
Mergeable: MERGEABLE
Reviews: APPROVED
URL: https://github.com/owner/repo/pull/89

✅ PR is ready to merge
✅ PR approved
✅ PR merged successfully
✅ Switched to main branch
✅ Branch deleted: feature/issue-42

✅ Workflow Complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Summary:
  PR: #89 - Fix email validation
  Status: Merged and closed
  Branch: feature/issue-42 (deleted)
  Current branch: main
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

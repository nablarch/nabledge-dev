---
name: fb
description: Respond to PR review feedback. Fetches review comments, implements fixes, commits, and replies to comments. Use when PR has review feedback.
argument-hint: [PR number]
allowed-tools: Bash, Skill, AskUserQuestion, Read
---

# Role

You are a PR review response orchestrator. Your job is to fetch PR review comments, understand the feedback, implement fixes, and respond to reviewers using the pr skill.

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
💬 Starting PR review response workflow
PR: #$PR_NUMBER
```

## STEP 2: Fetch PR Details and Review Comments

**Actions**:

1. Fetch PR details:
   - Run: `gh pr view $PR_NUMBER --json number,title,state,url`
   - Store: `PR_TITLE`, `PR_STATE`, `PR_URL`

2. Validate PR state:
   - Check `PR_STATE` == "OPEN"
   - If closed/merged → Output: "❌ PR is $PR_STATE, cannot respond to reviews" → STOP

3. Fetch review comments:
   - Run: `gh pr view $PR_NUMBER --json reviews,comments --jq '.reviews[] | select(.state == "CHANGES_REQUESTED" or .state == "COMMENTED")'`
   - Count unresolved review threads
   - Store summary of feedback

4. Display PR and review status:
   ```
   📋 PR #$PR_NUMBER: $PR_TITLE
   Status: $PR_STATE
   URL: $PR_URL

   📝 Review feedback found:
   [List of reviewers and their feedback summary]
   ```

5. If no review comments found:
   - Output: "ℹ️ No review comments found"
   - Use AskUserQuestion: "No review feedback found. What would you like to do?"
   - Options:
     - "Check for inline comments"
     - "Proceed anyway (make changes)"
     - "Abort"
   - Execute user's choice

**Error Handling**:
- PR not found → Output: "❌ PR #$PR_NUMBER not found" → STOP
- Cannot fetch reviews → Output error → STOP

**Output to user**:
```
✅ Fetched review feedback
Found X review comments from Y reviewers
```

## STEP 3: Respond to Reviews using pr skill

**Actions**:

1. Call pr skill resolve subcommand:
   - **IMPORTANT**: You MUST use the Skill tool to call the pr skill
   - Use: `Skill(skill: "pr", args: "resolve $PR_NUMBER")`
   - DO NOT manually implement fixes or reply to comments
   - The pr skill will:
     - Fetch and display all review comments
     - Implement requested changes
     - Run tests if applicable
     - Commit changes
     - Reply to review comments
     - Push updates
   - Wait for skill completion

2. The pr skill handles the entire review response workflow, including:
   - Reading review comments in detail
   - Understanding requested changes
   - Implementing fixes
   - Testing changes
   - Committing with proper messages
   - Replying to each review comment thread
   - Pushing changes to remote

**Error Handling**:
- Skill fails → Display error → STOP
- User intervention needed → pr skill will ask questions → Forward to user

**Output to user**:
```
⚙️ Responding to review feedback via pr skill...
[pr skill output displayed]
✅ Review response complete
```

## STEP 4: Verify Updates

**Actions**:

1. Check that changes were pushed:
   - Run: `git log origin/$(git branch --show-current)..HEAD`
   - If commits exist locally but not pushed → Warn user

2. Verify PR was updated:
   - Run: `gh pr view $PR_NUMBER --json updatedAt --jq '.updatedAt'`
   - Display last update time

**Error Handling**:
- All errors in this step are non-fatal
- Display warnings but don't stop

**Output to user**:
```
✅ PR updated at: $TIMESTAMP
```

## STEP 5: Final Summary

**Actions**:

1. Display completion summary:

```
✅ Review Response Complete!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Summary:
  PR: #$PR_NUMBER - $PR_TITLE
  URL: $PR_URL
  Status: Updated and responded
  Waiting for: Re-review from reviewers
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next steps:
  • Wait for reviewers to re-review
  • Use /fb $PR_NUMBER again if more feedback
  • Use /bb $PR_NUMBER to merge after approval
```

# General Guidelines

1. **Use pr skill**: Always use Skill tool to call pr skill resolve - this handles the entire workflow
2. **No manual fixes**: Do not implement changes yourself - delegate to pr skill
3. **Progress updates**: Output status at each major step
4. **Error messages**: Include actionable next steps
5. **Idempotency**: Can be run multiple times on same PR safely

# Example Session Flow

```
User: /fb 89

💬 Starting PR review response workflow
PR: #89

📋 PR #89: Fix email validation
Status: OPEN
URL: https://github.com/owner/repo/pull/89

📝 Review feedback found:
  • @reviewer1 requested changes (2 comments)
  • @reviewer2 commented (1 comment)

✅ Fetched review feedback
Found 3 review comments from 2 reviewers

⚙️ Responding to review feedback via pr skill...
[pr skill fetches comments, implements fixes, tests, commits, replies]
✅ Review response complete

✅ PR updated at: 2026-02-19T12:45:00Z

✅ Review Response Complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Summary:
  PR: #89 - Fix email validation
  URL: https://github.com/owner/repo/pull/89
  Status: Updated and responded
  Waiting for: Re-review from reviewers
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

# Alternative: Manual Mode

If the pr skill is not available or fails, you can manually:
1. Read review comments: `gh pr view $PR_NUMBER`
2. Implement fixes based on feedback
3. Commit: Use /git commit
4. Reply: `gh pr comment $PR_NUMBER --body "Fixed in commit xyz"`
5. Push: `git push`

But always prefer using the pr skill for consistency.

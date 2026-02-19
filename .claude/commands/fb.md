---
name: fb
description: Respond to PR review feedback. Fetches review comments, implements fixes, commits, and replies to comments. Use when PR has review feedback.
argument-hint: [PR number]
allowed-tools: Bash, Skill, AskUserQuestion, Read
---

# Role

You are a PR review response orchestrator. Your job is to validate PR state, display review feedback summary, and delegate the complete review response workflow to the pr skill (which handles fetching comments, implementing fixes, testing, committing, and replying).

# Execution Instructions

Follow these steps in order. Do not skip steps. If any step fails, handle the error before proceeding.

**Progress Indicator**: Display "💬 [Step X/4]" at the start of each step for user visibility.

## STEP 1: Parse Arguments and Detect PR

**Progress**: Output "💬 [Step 1/4] Detecting PR..."

**Input**: `$ARGUMENTS` may contain:
- Empty string → Auto-detect from current branch
- Number only: `123` → Explicit PR number
- With prefix: `#123` or `pr/123` → Explicit PR number

**Actions**:

1. Verify environment:
   - Run: `git rev-parse --is-inside-work-tree 2>&1`
   - If exit code != 0 → Output: "❌ Not a git repository" → STOP
   - Run: `gh --version 2>&1`
   - If exit code != 0 → Output: "❌ GitHub CLI required. Install: https://cli.github.com" → STOP

2. Parse PR number:
   - If `$ARGUMENTS` is empty: Set `pr_input` = ""
   - Else: Remove `#` prefix and `pr/` prefix, extract number → Set `pr_input` = number

3. Auto-detect PR if needed:
   - **If pr_input is empty**:
     - Run: `current_branch=$(git branch --show-current) && echo "$current_branch"`
     - Store in `CURRENT_BRANCH`
     - Run: `gh pr list --head "$CURRENT_BRANCH" --json number,title,state --jq '.[0]'`
     - If output is empty or "null":
       - Use AskUserQuestion:
         - Question: "No PR found for branch '$CURRENT_BRANCH'. Enter PR number:"
         - Header: "PR Number"
         - Options: List recent PRs with review feedback using:
           `gh pr list --json number,title,reviewDecision --jq '.[] | select(.reviewDecision=="CHANGES_REQUESTED" or .reviewDecision=="COMMENTED") | "#\(.number) - \(.title)"'`
         - Add "Other" option for custom input
       - Extract number from user selection → Set `PR_NUMBER`
     - Else: Parse `number` field from JSON → Set `PR_NUMBER`
   - **If pr_input is not empty**:
     - Set `PR_NUMBER` = pr_input

4. Validate PR number is numeric:
   - If `PR_NUMBER` is not a number → Output: "❌ Invalid PR number: $PR_NUMBER" → STOP

**Error Handling**:
- Not git repo → Output error with diagnostic → STOP
- gh not available → Output install instructions → STOP
- PR number invalid → Output error → STOP

**Output to user**:
```
💬 Starting PR review response workflow
   PR: #$PR_NUMBER
   Branch: $CURRENT_BRANCH (if auto-detected)
```

## STEP 2: Validate PR and Show Review Summary

**Progress**: Output "💬 [Step 2/4] Checking PR status..."

**Actions**:

1. Fetch PR details and review summary:
   - Run: `gh pr view $PR_NUMBER --json number,title,state,url,reviewDecision,reviews 2>&1`
   - If exit code != 0:
     - If output contains "Could not resolve" → Output: "❌ PR #$PR_NUMBER not found" → STOP
     - Else → Output: "❌ Cannot fetch PR: $error_output" → STOP
   - Parse JSON and store:
     - `PR_TITLE` = .title
     - `PR_STATE` = .state (OPEN, CLOSED, MERGED)
     - `PR_URL` = .url
     - `PR_REVIEW_DECISION` = .reviewDecision
     - `PR_REVIEWS` = .reviews (array)

2. Validate PR is open:
   - If `PR_STATE` != "OPEN":
     - Output: "❌ Cannot respond to reviews: PR is $PR_STATE"
     - If `PR_STATE` == "MERGED" → Output: "   PR was already merged"
     - If `PR_STATE` == "CLOSED" → Output: "   PR was closed without merging"
     - STOP

3. Analyze review feedback:
   - Count reviews by state:
     - `CHANGES_REQUESTED` count → Store in `CHANGES_REQUESTED_COUNT`
     - `COMMENTED` count → Store in `COMMENTED_COUNT`
     - `APPROVED` count → Store in `APPROVED_COUNT`
   - Extract unique reviewers:
     - Run: `echo '$PR_REVIEWS' | jq -r '.[].author.login' | sort -u`
     - Store list in `REVIEWERS`
   - Calculate: `TOTAL_FEEDBACK` = CHANGES_REQUESTED_COUNT + COMMENTED_COUNT

4. Display PR and feedback summary:
   ```
   📋 PR #$PR_NUMBER: $PR_TITLE
      State: $PR_STATE
      Review Decision: $PR_REVIEW_DECISION
      URL: $PR_URL

   📝 Review Feedback Summary:
      • Changes requested: $CHANGES_REQUESTED_COUNT
      • Comments: $COMMENTED_COUNT
      • Approvals: $APPROVED_COUNT
      • Reviewers: $REVIEWERS (comma-separated)
   ```

5. Handle no-feedback scenario:
   - If `TOTAL_FEEDBACK` == 0:
     - Output: "ℹ️  No review feedback found"
     - Use AskUserQuestion:
       - Question: "No review comments or change requests found. What would you like to do?"
       - Header: "Action"
       - Options:
         - "Proceed anyway (pr skill will check for inline comments)"
         - "Abort (check PR manually first)"
       - If user selects "Abort" → STOP
     - Output: "⚠️  Proceeding without visible feedback. pr skill will check for inline comments."

**Error Handling**:
- PR not found → Output clear error → STOP
- Network error → Output: "❌ Cannot reach GitHub" → STOP
- JSON parse error → Output: "❌ Unexpected GitHub response" → STOP

**Output to user**:
```
✅ PR validated and feedback analyzed
   Found feedback from $NUM_REVIEWERS reviewer(s)
```

## STEP 3: Delegate to pr skill for review response

**Progress**: Output "💬 [Step 3/4] Responding to feedback..."

**Actions**:

1. **IMPORTANT**: You MUST use the Skill tool to call the pr skill
   - DO NOT manually fetch review comments in detail
   - DO NOT manually implement fixes or edit files
   - DO NOT manually commit or push changes
   - DO NOT manually reply to review comments
   - The pr skill handles the ENTIRE review response workflow

2. Call pr skill resolve subcommand:
   - Use: `Skill(skill: "pr", args: "resolve $PR_NUMBER")`
   - The pr skill will autonomously:
     1. Fetch all review comments (including inline comments)
     2. Display comments to user for context
     3. Understand requested changes
     4. Implement fixes using appropriate tools (Read, Edit, Write)
     5. Run tests if test files exist
     6. Commit changes with descriptive message
     7. Reply to each review comment thread
     8. Push all changes to remote
   - Wait for skill completion
   - Capture skill output and any errors

3. Monitor skill execution:
   - The pr skill may ask questions via AskUserQuestion
   - Forward all questions to user
   - Pass user responses back to skill
   - Do not interrupt skill execution

**Error Handling**:
- Skill execution fails:
  - Capture detailed error message
  - Output: "❌ Review response failed: $skill_error"
  - Check common failure reasons:
    - No write permissions → "You don't have push access to this branch"
    - Tests failed → "Tests failed, fix required before pushing"
    - Network error → "Connection lost, retry needed"
  - STOP
- User aborts during skill execution:
  - Output: "⚠️  Review response aborted by user"
  - Output: "   PR state: Partially updated (some changes may be uncommitted)"
  - Suggest: "Run /fb $PR_NUMBER again to complete response"
  - STOP

**Output to user**:
```
⚙️ Delegating to pr skill...
[Real-time pr skill output displayed here]
✅ Review response complete via pr skill
```

## STEP 4: Final Summary

**Progress**: Output "💬 [Step 4/4] Completing workflow..."

**Actions**:

1. Verify PR was updated:
   - Run: `gh pr view $PR_NUMBER --json updatedAt,commits --jq '{updatedAt,commitCount: .commits | length}' 2>&1`
   - Store: `UPDATED_AT`, `COMMIT_COUNT`
   - If command fails: Use fallback values

2. Check working tree state:
   - Run: `git status --porcelain 2>&1`
   - If output is empty: Set `TREE_STATE` = "Clean"
   - Else: Set `TREE_STATE` = "Modified (uncommitted changes exist)"

3. Display completion summary:

```
✅ Review Response Complete!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Summary:
  ✓ PR responded: #$PR_NUMBER - $PR_TITLE
  ✓ Last updated: $UPDATED_AT
  ✓ Total commits: $COMMIT_COUNT
  ✓ Working tree: $TREE_STATE
  ✓ Waiting for: Re-review from $NUM_REVIEWERS reviewer(s)

Links:
  • PR URL: $PR_URL
  • Review comments: $PR_URL/files

Reviewers notified:
  $REVIEWERS (from Step 2)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next steps:
  • Wait for reviewers to re-review your changes
  • Monitor PR for new comments: gh pr view $PR_NUMBER
  • Respond to additional feedback: /fb $PR_NUMBER
  • Merge after approval: /bb $PR_NUMBER
```

# General Guidelines

1. **Always use pr skill**:
   - **pr skill resolve** handles complete review response workflow (Skill tool required)
   - **Never** manually fetch, implement, commit, or reply to reviews
   - The pr skill has full context and handles all steps autonomously
   - Trust the pr skill output - it's designed for this workflow

2. **Lightweight orchestration**:
   - This command is a thin wrapper around pr skill
   - Only validates PR state and displays summary
   - All actual work delegated to pr skill
   - Avoid duplicating pr skill's functionality

3. **Error handling**:
   - Validate environment and PR state before calling skill
   - Let pr skill handle implementation errors
   - Only intervene for pre-skill validation failures
   - Provide clear error messages with recovery steps

4. **Progress visibility**:
   - Display "[Step X/4]" at each step
   - Use emoji indicators: 💬 (workflow), ✅ (success), ❌ (error), ⚠️ (warning)
   - Show feedback summary before delegating to skill
   - Final summary includes verification data

5. **Idempotency**:
   - Safe to re-run after failures
   - pr skill handles already-resolved comments gracefully
   - No duplicate responses or commits
   - Can resume partial work

6. **User interaction**:
   - Minimal prompts from this orchestrator
   - Most questions come from pr skill (implementation decisions)
   - Always forward pr skill questions to user
   - Never interrupt pr skill execution

# Example Session Flow

## Example 1: Successful Response (Happy Path)

```
User: /fb 89

💬 [Step 1/4] Detecting PR...
✅ PR found: #89
   Branch: feature/issue-42

💬 [Step 2/4] Checking PR status...
📋 PR #89: Fix email validation
   State: OPEN
   Review Decision: CHANGES_REQUESTED
   URL: https://github.com/owner/repo/pull/89

📝 Review Feedback Summary:
   • Changes requested: 2
   • Comments: 1
   • Approvals: 0
   • Reviewers: @reviewer1, @reviewer2

✅ PR validated and feedback analyzed
   Found feedback from 2 reviewer(s)

💬 [Step 3/4] Responding to feedback...
⚙️ Delegating to pr skill...

[pr skill output begins]
Fetching review comments...
Found 3 comments:
  1. @reviewer1: Update regex to handle + in emails
  2. @reviewer1: Add test case for edge cases
  3. @reviewer2: Consider validation performance

Implementing fixes...
  • Updated src/validators/email.py
  • Added tests in tests/test_email_validator.py

Running tests...
  ✓ 22 passed in 0.89s

Committing changes...
  ✓ Committed: Respond to review feedback on PR #89

Replying to comments...
  ✓ Replied to @reviewer1 (2 comments)
  ✓ Replied to @reviewer2 (1 comment)

Pushing changes...
  ✓ Pushed to origin/feature/issue-42
[pr skill output ends]

✅ Review response complete via pr skill

💬 [Step 4/4] Completing workflow...
✅ Review Response Complete!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Summary:
  ✓ PR responded: #89 - Fix email validation
  ✓ Last updated: 2026-02-19T13:15:42Z
  ✓ Total commits: 3
  ✓ Working tree: Clean
  ✓ Waiting for: Re-review from 2 reviewer(s)

Links:
  • PR URL: https://github.com/owner/repo/pull/89
  • Review comments: https://github.com/owner/repo/pull/89/files

Reviewers notified:
  @reviewer1, @reviewer2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next steps:
  • Wait for reviewers to re-review your changes
  • Monitor PR for new comments: gh pr view 89
  • Respond to additional feedback: /fb 89
  • Merge after approval: /bb 89
```

## Example 2: Auto-detect from Current Branch

```
User: /fb

💬 [Step 1/4] Detecting PR...
Looking for PR on branch: feature/issue-45
✅ PR found: #92
   Branch: feature/issue-45

[Steps 2-4 continue as in Example 1]
```

## Example 3: No Review Feedback

```
User: /fb 95

💬 [Step 1/4] Detecting PR...
💬 [Step 2/4] Checking PR status...

📋 PR #95: Add dark mode support
   State: OPEN
   Review Decision: APPROVED
   URL: https://github.com/owner/repo/pull/95

📝 Review Feedback Summary:
   • Changes requested: 0
   • Comments: 0
   • Approvals: 2
   • Reviewers: @reviewer1, @reviewer2

ℹ️  No review feedback found

? No review comments or change requests found. What would you like to do?
  > Proceed anyway (pr skill will check for inline comments)
  > Abort (check PR manually first)

User selects: Abort

[Workflow stops]
```

## Example 4: PR Already Merged

```
User: /fb 88

💬 [Step 1/4] Detecting PR...
💬 [Step 2/4] Checking PR status...

📋 PR #88: Refactor authentication
   State: MERGED

❌ Cannot respond to reviews: PR is MERGED
   PR was already merged

[Workflow stops]
```

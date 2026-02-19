---
name: bb
description: Approve and merge PR, then cleanup branch (detach HEAD and delete branch). Use after PR is ready to merge.
argument-hint: [PR number]
allowed-tools: Bash, Skill, AskUserQuestion, Read
---

# Role

You are a PR merge and cleanup orchestrator. Your job is to validate PR readiness, approve if needed, merge using the pr skill, and cleanup the branch using the git skill. You ensure safe merge operations and complete cleanup.

# Execution Instructions

Follow these steps in order. Do not skip steps. If any step fails, handle the error before proceeding.

**Progress Indicator**: Display "🔀 [Step X/6]" at the start of each step for user visibility.

## STEP 1: Parse Arguments and Detect PR

**Progress**: Output "🔀 [Step 1/6] Detecting PR..."

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
         - Options: ["#42", "#43", "#44"] (use recent PR numbers from `gh pr list --limit 3`)
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
🔀 Starting PR merge workflow
   PR: #$PR_NUMBER
   Branch: $CURRENT_BRANCH (if auto-detected)
```

## STEP 2: Fetch and Validate PR Status

**Progress**: Output "🔀 [Step 2/6] Validating PR status..."

**Actions**:

1. Fetch PR details:
   - Run: `gh pr view $PR_NUMBER --json number,title,state,mergeable,reviewDecision,url,headRefName 2>&1`
   - If exit code != 0:
     - If output contains "Could not resolve" → Output: "❌ PR #$PR_NUMBER not found" → STOP
     - Else → Output: "❌ Cannot fetch PR: $error_output" → STOP
   - Parse JSON and store:
     - `PR_TITLE` = .title
     - `PR_STATE` = .state (possible values: OPEN, CLOSED, MERGED)
     - `PR_MERGEABLE` = .mergeable (possible values: MERGEABLE, CONFLICTING, UNKNOWN)
     - `PR_REVIEW_DECISION` = .reviewDecision (possible values: APPROVED, CHANGES_REQUESTED, REVIEW_REQUIRED, null)
     - `PR_URL` = .url
     - `PR_BRANCH` = .headRefName

2. Display PR information:
   ```
   📋 PR #$PR_NUMBER: $PR_TITLE
      State: $PR_STATE
      Mergeable: $PR_MERGEABLE
      Reviews: $PR_REVIEW_DECISION
      Branch: $PR_BRANCH
      URL: $PR_URL
   ```

3. Validate merge conditions (check in order):

   **Condition 1: State must be OPEN**
   - If `PR_STATE` != "OPEN":
     - Output: "❌ Cannot merge: PR is $PR_STATE"
     - Output: "   Please reopen the PR first" (if CLOSED)
     - Output: "   PR is already merged" (if MERGED)
     - STOP

   **Condition 2: No merge conflicts**
   - If `PR_MERGEABLE` == "CONFLICTING":
     - Output: "❌ Cannot merge: PR has merge conflicts"
     - Output: "   Resolve conflicts first: git checkout $PR_BRANCH && git pull origin main && git mergetool"
     - STOP
   - If `PR_MERGEABLE` == "UNKNOWN":
     - Output: "⚠️  Warning: Merge status unknown (GitHub still calculating)"
     - Use AskUserQuestion:
       - Question: "Merge status is unknown. Continue anyway?"
       - Header: "Proceed?"
       - Options: ["Yes, try to merge", "No, abort"]
       - If user selects "No" → STOP

   **Condition 3: Review approval (optional)**
   - If `PR_REVIEW_DECISION` == "CHANGES_REQUESTED":
     - Output: "⚠️  Warning: Reviewers requested changes"
     - Use AskUserQuestion:
       - Question: "Changes were requested. Continue anyway?"
       - Header: "Proceed?"
       - Options: ["Yes, approve and merge", "No, abort"]
       - If user selects "No" → STOP
       - Store: `NEEDS_APPROVAL` = true
   - Else if `PR_REVIEW_DECISION` == "REVIEW_REQUIRED" or `PR_REVIEW_DECISION` == null:
     - Output: "⚠️  Warning: No approvals yet"
     - Use AskUserQuestion:
       - Question: "PR has no approvals. Continue anyway?"
       - Header: "Proceed?"
       - Options: ["Yes, approve and merge", "No, abort"]
       - If user selects "No" → STOP
       - Store: `NEEDS_APPROVAL` = true
   - Else if `PR_REVIEW_DECISION` == "APPROVED":
     - Store: `NEEDS_APPROVAL` = false
   - Else:
     - Output: "⚠️  Unknown review status: $PR_REVIEW_DECISION"
     - Store: `NEEDS_APPROVAL` = false

**Error Handling**:
- PR not found → Output clear error with PR number → STOP
- Network error → Output: "❌ Network error: cannot reach GitHub" → STOP
- Invalid JSON → Output: "❌ Unexpected response from GitHub" → STOP

**Output to user** (if all validations pass):
```
✅ PR is ready to merge
   State: OPEN ✓
   Mergeable: MERGEABLE ✓
   Reviews: $PR_REVIEW_DECISION
```

## STEP 3: Approve PR (if needed)

**Progress**: Output "🔀 [Step 3/6] Checking approval..."

**Actions**:

1. Check if approval needed:
   - If `NEEDS_APPROVAL` == false:
     - Output: "✅ PR already approved, skipping approval step"
     - Skip to STEP 4
   - Else: Continue with approval

2. Get current GitHub user:
   - Run: `gh api user --jq '.login' 2>&1`
   - Store in `CURRENT_USER`
   - If command fails: Set `CURRENT_USER` = "unknown"

3. Check if current user already approved:
   - Run: `gh pr view $PR_NUMBER --json reviews --jq '.reviews[] | select(.author.login == "'$CURRENT_USER'" and .state == "APPROVED") | .author.login' 2>&1`
   - If output == `$CURRENT_USER`:
     - Output: "✅ You already approved this PR"
     - Skip to STEP 4
   - Else: Continue with approval

4. Attempt to approve PR:
   - Run: `gh pr review $PR_NUMBER --approve --body "Approved via /bb command" 2>&1`
   - Capture exit code and output

5. Handle approval result:
   - **If exit code == 0** (success):
     - Output: "✅ PR approved"
   - **If output contains "cannot review your own"** (own PR):
     - Output: "⚠️  Cannot approve your own PR (GitHub limitation)"
     - Output: "   Proceeding to merge anyway..."
   - **If output contains "already reviewed"** (duplicate):
     - Output: "✅ PR already approved"
   - **Else** (other error):
     - Output: "⚠️  Approval failed: $error_output"
     - Output: "   Proceeding to merge anyway..."

**Error Handling**:
- All errors in this step are non-fatal
- Always proceed to merge even if approval fails
- User may not have permission to approve, but can still merge

**Output to user**:
```
✅ PR approval handled
```

## STEP 4: Merge PR using pr skill

**Progress**: Output "🔀 [Step 4/6] Merging PR..."

**Actions**:

1. **IMPORTANT**: You MUST use the Skill tool to call the pr skill
   - DO NOT manually run `gh pr merge` or `git merge` commands
   - DO NOT manually push or pull
   - Let the pr skill handle the entire merge workflow

2. Call pr skill merge subcommand:
   - Use: `Skill(skill: "pr", args: "merge $PR_NUMBER")`
   - The pr skill will:
     - Verify PR is mergeable
     - Execute merge operation
     - Delete remote branch (if configured)
     - Handle merge conflicts if any
   - Wait for skill completion
   - Capture skill output for error diagnosis

3. Verify merge success:
   - Run: `gh pr view $PR_NUMBER --json state,merged,mergedAt --jq '{state,merged,mergedAt}' 2>&1`
   - Parse JSON:
     - If `.merged` == true:
       - Store `MERGED_AT` = .mergedAt
       - Output: "✅ PR merged successfully at $MERGED_AT"
     - Else:
       - Output: "❌ Merge verification failed"
       - Output: "   PR state: $.state"
       - Output: "   Merged: $.merged"
       - STOP

**Error Handling**:
- Skill execution fails:
  - Capture skill error message
  - Output: "❌ Merge failed: $skill_error"
  - Check if it's a merge conflict → Output conflict resolution steps
  - Check if it's a permission error → Output: "You don't have merge permissions"
  - STOP
- Verification command fails:
  - Output: "⚠️  Cannot verify merge status, but skill reported success"
  - Assume merged, continue to next step
- PR not actually merged:
  - Output: "❌ PR still shows as unmerged despite skill completion"
  - STOP

**Output to user**:
```
✅ PR #$PR_NUMBER merged successfully
   Merged at: $MERGED_AT
```

## STEP 5: Switch to main and delete merged branch

**Progress**: Output "🔀 [Step 5/6] Cleaning up branches..."

**Actions**:

1. Get current branch name:
   - Run: `git branch --show-current 2>&1`
   - Store in `CURRENT_BRANCH`
   - If command fails: Set `CURRENT_BRANCH` = "unknown"

2. Determine target branch to delete:
   - **If CURRENT_BRANCH == PR_BRANCH** (still on PR branch):
     - Set `BRANCH_TO_DELETE` = $CURRENT_BRANCH
     - Need to switch branches first
   - **Else** (already on different branch, maybe main):
     - Set `BRANCH_TO_DELETE` = $PR_BRANCH
     - Can delete without switching

3. Switch to main if needed:
   - **If CURRENT_BRANCH == BRANCH_TO_DELETE**:
     - Run: `git checkout main 2>&1`
     - Capture exit code and output
     - If exit code != 0:
       - If output contains "Already on 'main'" → Continue
       - Else if output contains "did not match any file" → Try: `git checkout master 2>&1`
       - Else:
         - Output: "❌ Cannot switch to main: $error_output"
         - Output: "   Please manually switch: git checkout main"
         - STOP
     - Run: `git pull origin main 2>&1` (update local main)
     - If exit code != 0:
       - Output: "⚠️  Cannot update main branch: $error_output"
       - Output: "   Continuing anyway..."
     - Output: "✅ Switched to main branch"
   - **Else**:
     - Output: "✅ Already on branch: $CURRENT_BRANCH"

4. Delete merged branch using git skill:
   - **IMPORTANT**: You MUST use the Skill tool to call the git skill
   - DO NOT manually run `git branch -d` or `git push origin --delete`
   - Use: `Skill(skill: "git", args: "branch-delete $BRANCH_TO_DELETE")`
   - The git skill will:
     - Delete local branch
     - Delete remote branch if exists
     - Handle errors gracefully
   - Wait for skill completion

5. Verify cleanup:
   - Run: `git branch --list $BRANCH_TO_DELETE 2>&1`
   - If output is empty:
     - Output: "✅ Local branch deleted: $BRANCH_TO_DELETE"
   - Else:
     - Output: "⚠️  Local branch still exists: $BRANCH_TO_DELETE"
     - Output: "   You can delete manually: git branch -D $BRANCH_TO_DELETE"
   - Run: `git ls-remote --heads origin $BRANCH_TO_DELETE 2>&1`
   - If output is empty:
     - Output: "✅ Remote branch deleted: $BRANCH_TO_DELETE"
   - Else:
     - Output: "⚠️  Remote branch still exists: origin/$BRANCH_TO_DELETE"
     - Output: "   Already deleted by merge or still exists remotely"

**Error Handling**:
- Cannot switch branches → Output detailed error → Provide manual steps → STOP
- Cannot update main → Non-fatal warning, continue
- Branch deletion fails → Non-fatal warning, provide manual delete command
- Verification fails → Non-fatal, just warn user

**Output to user**:
```
✅ Branch cleanup complete
   Current branch: main
   Deleted: $BRANCH_TO_DELETE (local and remote)
```

## STEP 6: Final Summary

**Progress**: Output "🔀 [Step 6/6] Completing workflow..."

**Actions**:

1. Gather final state:
   - Run: `git branch --show-current 2>&1` → Store `FINAL_BRANCH`
   - Run: `git status --porcelain 2>&1` → Check if working tree is clean

2. Display completion summary:

```
✅ Merge Workflow Complete!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Summary:
  ✓ PR merged: #$PR_NUMBER - $PR_TITLE
  ✓ Status: MERGED at $MERGED_AT
  ✓ Branch deleted: $BRANCH_TO_DELETE
  ✓ Current branch: $FINAL_BRANCH
  ✓ Working tree: Clean (or "Modified" with file count)

Links:
  • PR URL: $PR_URL
  • Related issue: [extracted from PR body if present]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next steps:
  • Update local branches: git fetch --prune
  • Start new work: /hi <issue-number>
  • Review other PRs: /fb <pr-number>
```

# General Guidelines

1. **Always use skills**:
   - **pr skill** for merge operations (Skill tool required)
   - **git skill** for branch deletion (Skill tool required)
   - **Never** run `gh pr merge`, `git merge`, `git branch -d` manually
   - Skills provide consistent error handling and logging

2. **Safety and validation**:
   - Verify environment (git, gh CLI) before starting
   - Validate PR state, conflicts, and approval status
   - Get explicit user confirmation for risky operations
   - All merge conditions must pass before proceeding

3. **Error handling**:
   - Fatal errors: STOP immediately with clear message
   - Non-fatal errors: WARN and continue (e.g., cannot update main)
   - Include actionable recovery steps in all error messages
   - Distinguish between permission errors, network errors, and state errors

4. **Progress visibility**:
   - Display "[Step X/6]" at each step
   - Use emoji indicators: 🔀 (workflow), ✅ (success), ❌ (error), ⚠️ (warning)
   - Show detailed state information (PR state, branch names, timestamps)
   - Provide real-time feedback during skill execution

5. **Variable management**:
   - Store all parsed values in named variables (PR_NUMBER, PR_TITLE, etc.)
   - Check variable values before using in commands
   - Handle null/empty values explicitly
   - Document expected value ranges for state fields

6. **Idempotency**:
   - Safe to re-run after partial failures
   - Check current state before each operation
   - Skip already-completed steps when possible

7. **User confirmation**:
   - Required for: unapproved PRs, unknown merge status, changes requested
   - Optional for: auto-approval, branch deletion
   - Always offer "abort" option in AskUserQuestion

# Example Session Flow

## Example 1: Successful Merge (Happy Path)

```
User: /bb 89

🔀 [Step 1/6] Detecting PR...
✅ PR found: #89
   Branch: feature/issue-42

🔀 [Step 2/6] Validating PR status...
📋 PR #89: Fix email validation
   State: OPEN
   Mergeable: MERGEABLE
   Reviews: APPROVED
   Branch: feature/issue-42
   URL: https://github.com/owner/repo/pull/89

✅ PR is ready to merge
   State: OPEN ✓
   Mergeable: MERGEABLE ✓
   Reviews: APPROVED

🔀 [Step 3/6] Checking approval...
✅ PR already approved, skipping approval step

🔀 [Step 4/6] Merging PR...
[pr skill executes merge]
✅ PR #89 merged successfully
   Merged at: 2026-02-19T13:45:32Z

🔀 [Step 5/6] Cleaning up branches...
✅ Switched to main branch
[git skill executes branch deletion]
✅ Local branch deleted: feature/issue-42
✅ Remote branch deleted: feature/issue-42
✅ Branch cleanup complete
   Current branch: main
   Deleted: feature/issue-42 (local and remote)

🔀 [Step 6/6] Completing workflow...
✅ Merge Workflow Complete!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Summary:
  ✓ PR merged: #89 - Fix email validation
  ✓ Status: MERGED at 2026-02-19T13:45:32Z
  ✓ Branch deleted: feature/issue-42
  ✓ Current branch: main
  ✓ Working tree: Clean

Links:
  • PR URL: https://github.com/owner/repo/pull/89
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Example 2: Needs Approval

```
User: /bb

🔀 [Step 1/6] Detecting PR...
PR found for branch 'feature/issue-45': #92

🔀 [Step 2/6] Validating PR status...
📋 PR #92: Add dark mode support
   State: OPEN
   Mergeable: MERGEABLE
   Reviews: REVIEW_REQUIRED
   Branch: feature/issue-45

⚠️  Warning: No approvals yet
? PR has no approvals. Continue anyway?
  > Yes, approve and merge
  > No, abort

User selects: Yes, approve and merge

✅ PR is ready to merge (will approve)

🔀 [Step 3/6] Checking approval...
✅ PR approved
   Approved by: @current-user

🔀 [Step 4/6] Merging PR...
✅ PR #92 merged successfully

[Steps 5-6 continue as in Example 1]
```

## Example 3: Merge Conflicts

```
User: /bb 95

🔀 [Step 1/6] Detecting PR...
🔀 [Step 2/6] Validating PR status...

📋 PR #95: Refactor auth module
   State: OPEN
   Mergeable: CONFLICTING
   Reviews: APPROVED
   Branch: feature/refactor-auth

❌ Cannot merge: PR has merge conflicts
   Resolve conflicts first: git checkout feature/refactor-auth && git pull origin main && git mergetool

[Workflow stops - user must resolve conflicts first]
```

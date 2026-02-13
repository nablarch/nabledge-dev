# Branch Creation Workflow

This workflow creates a working branch from the main branch.

## Required Tools

- Bash
- AskUserQuestion

## Execution Steps

### 1. Pre-flight Checks

**1.1 Verify Current Branch**

```bash
git branch --show-current
```

If not on `main`, exit with error:
```
Error: Working branches must be created from the main branch.
Current branch: {current_branch}

To switch to main:
git checkout main
```

**1.2 Verify Clean Working Tree**

```bash
git status --porcelain
```

If uncommitted changes exist, exit with error:
```
Error: You have uncommitted changes.
Please commit or stash changes before proceeding.

Check changes:
git status

Stash changes:
git stash
```

**1.3 Update Remote**

```bash
git fetch origin main
git pull origin main
```

If pull fails (conflicts):
```
Error: Failed to update main branch.
Please resolve conflicts before proceeding.
```

### 2. Get Issue Number and Create Branch Name

**2.1 Ask for Issue Number**

Use AskUserQuestion to get the issue number:

```
Question: What is the issue number for this work?
Header: "Issue"
Options:
  - Label: "I have an issue number"
    Description: "Branch will be named issue-<number>"
  - Label: "No issue yet"
    Description: "Create an issue first"
```

If user selects "No issue yet", exit with guidance:
```
Please create an issue first using GitHub issues.
This ensures work is tracked and follows issue-driven development.

To create an issue:
1. Go to GitHub repository
2. Click "Issues" → "New issue"
3. Follow the format in .claude/rules/issues.md
4. Return here with the issue number
```

If user selects "I have an issue number", ask for the number (free text).

**2.2 Validate Issue**

Verify the issue exists using gh CLI:

```bash
gh issue view {issue_number}
```

If issue doesn't exist, exit with error:
```
Error: Issue #{issue_number} not found.

Please verify the issue number or create the issue first:
gh issue create
```

**2.3 Generate Branch Name**

Branch name is always: `issue-{issue_number}`

**Example**:
- Issue #42 → Branch: `issue-42`
- Issue #123 → Branch: `issue-123`

**2.4 Check for Duplicates**

```bash
git branch --list "issue-{issue_number}"
```

If exists, exit with error:
```
Error: Branch "issue-{issue_number}" already exists.

To work on existing branch:
git checkout issue-{issue_number}

To delete and recreate:
git branch -D issue-{issue_number}
```

### 3. Create Branch

Create branch with issue-based name:

```bash
git checkout -b issue-{issue_number}
```

### 4. Display Result

```
## Branch Creation Complete

**Branch Name**: issue-{issue_number}
**Issue**: #{issue_number}
**Base Branch**: main

You can now start working on this issue.
Use `/git commit` to commit changes.
```

## Error Handling

| Error | Response |
|-------|----------|
| Not on main branch | Guide to switch to main |
| Uncommitted changes | Guide to commit or stash |
| Failed to update main | Guide to resolve conflicts |
| Branch name exists | Guide to use different name or delete existing |

## Important Notes

1. **No emojis**: Never use emojis unless explicitly requested by user
2. **Issue-driven development**: All branches must be linked to a GitHub issue
3. **Branch naming**: Always use `issue-<number>` format for consistency
4. **Safety**: Protect main branch, check duplicates, verify clean working tree
5. **Issue validation**: Always verify issue exists before creating branch

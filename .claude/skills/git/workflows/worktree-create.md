# Worktree Creation Workflow

This workflow creates a new worktree for parallel work.

## Required Tools

- Bash
- AskUserQuestion

## Execution Steps

### 1. Get Current Directory Info

**1.1 Get Current Directory and Repository Name**

```bash
pwd
basename $(pwd)
```

- Current directory: `<workspace-path>/nab-agents`
- Repository name: `nab-agents`

**1.2 Get Parent Directory**

```bash
dirname $(pwd)
```

- Parent directory: `<workspace-parent-path>`

### 2. Get Issue Number and Create Branch Name

**2.1 Ask for Issue Number**

Use AskUserQuestion to get the issue number:

```
Question: What is the issue number for this work?
Header: "Issue"
Options:
  - Label: "I have an issue number"
    Description: "Worktree will be named issue-<number>"
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

To work on existing branch in a new worktree:
git worktree add {path} issue-{issue_number}

To delete and recreate:
git branch -D issue-{issue_number}
```

### 3. Determine Worktree Path

**3.1 Generate Path**

```bash
parent_dir=$(dirname $(pwd))
worktree_path="${parent_dir}/issue-{issue_number}"
```

Example:
- Current: `<workspace-path>/nabledge-dev`
- Issue #42 → Worktree: `<workspace-path>/issue-42`
- Issue #123 → Worktree: `<workspace-path>/issue-123`

**3.2 Check Path Existence**

```bash
test -e {worktree_path}
```

If exists, exit with error:
```
Error: Path "{worktree_path}" already exists.

Delete the existing directory or use a different issue number:
rm -rf {worktree_path}
```

**3.3 Confirm Path**

Use AskUserQuestion to confirm path:

```
Question: Create worktree at the following path. OK?
Header: "Confirm Path"
Options:
  - Label: "Yes, create it"
    Description: "{worktree_path}"
  - Label: "No, cancel"
    Description: ""

Display info:
Path: {worktree_path}
Branch: issue-{issue_number}
Issue: #{issue_number}
Base: main
```

### 4. Create Worktree

**4.1 Update Main Branch**

```bash
git fetch origin main
git pull origin main
```

**4.2 Create Worktree**

```bash
git worktree add -b issue-{issue_number} {worktree_path} main
```

If creation fails:
```
Error: Failed to create worktree.

Please verify:
- Sufficient disk space
- Write permissions to the path
- Valid branch name
```

### 5. Display Result

```
## Worktree Creation Complete

**Path**: {worktree_path}
**Branch**: issue-{issue_number}
**Issue**: #{issue_number}
**Base Branch**: main

### Move to Worktree
cd {worktree_path}

You can now start working on this issue.
Use `/git commit` to commit changes.
```

## Error Handling

| Error | Response |
|-------|----------|
| Branch name exists | Guide to use different name or delete existing |
| Path exists | Guide to use different name or delete existing directory |
| Failed to update main | Guide to resolve conflicts |
| Insufficient permissions | Guide to check write permissions |
| Insufficient disk space | Guide to check disk space |

## Important Notes

1. **No emojis**: Never use emojis unless explicitly requested by user
2. **Path naming convention**: `{parent_dir}/issue-{issue_number}`
3. **Branch naming convention**: `issue-{issue_number}`
4. **Issue-driven development**: All worktrees must be linked to a GitHub issue
5. **Issue validation**: Always verify issue exists before creating worktree
6. **Base branch**: Always branch from main

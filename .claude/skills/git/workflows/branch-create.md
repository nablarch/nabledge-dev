# Branch Creation Workflow

This workflow creates a working branch from the development branch (typically `develop`).

## Required Tools

- Bash
- AskUserQuestion

## Execution Steps

### 1. Pre-flight Checks

**1.1 Get Development Branch and Verify Current Branch**

```bash
# Get repository default branch (should be develop per branch strategy)
default_branch=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
echo "Repository default branch: ${default_branch}"

# For branch creation, always use develop as base (see .claude/rules/branch-strategy.md)
if [[ "$default_branch" == "develop" ]]; then
  base_branch="develop"
else
  echo "WARNING: Repository default is ${default_branch}, but using 'develop' per branch strategy"
  base_branch="develop"
fi

# Get current branch
current_branch=$(git branch --show-current)
echo "Current branch: ${current_branch}"
```

If not on the base branch, exit with error:

Error: Working branches must be created from the development branch.

Current branch: ${current_branch}
Base branch: ${base_branch}

To switch to ${base_branch}:
git checkout ${base_branch}

**1.2 Verify Clean Working Tree**

```bash
git status --porcelain
```

If uncommitted changes exist, exit with error:

Error: You have uncommitted changes.
Please commit or stash changes before proceeding.

Check changes:
git status

Stash changes:
git stash

**1.3 Update Remote**

```bash
echo "Updating ${base_branch} from remote..."
git fetch origin "${base_branch}"
git pull origin "${base_branch}"
echo "Base branch updated successfully"
```

If pull fails (conflicts):

Error: Failed to update ${base_branch} branch.
Please resolve conflicts before proceeding.

### 2. Get Issue Number and Create Branch Name

**2.1 Ask for Issue Number**

Use the AskUserQuestion tool to prompt the user:
- Question: "What is the issue number for this work?"
- Provide two options: "I have an issue number" and "No issue yet"
- If user selects "I have an issue number", they will provide the number via text input
- If user selects "No issue yet", exit with guidance

If user selects "No issue yet", exit with guidance:

Please create an issue first using GitHub issues.
This ensures work is tracked and follows issue-driven development.

I can help create the issue. Please provide:
- Role: Who is affected?
- Goal: What do you want?
- Benefit: Why is this important?

Or you can create it manually on GitHub following .claude/rules/issues.md format.
Once created, return here with the issue number.

If user provides an issue number, validate it is numeric:

```bash
if ! [[ "$issue_number" =~ ^[0-9]+$ ]]; then
  echo "Error: Issue number must be a positive integer"
  exit 1
fi
echo "Issue number validated: ${issue_number}"
```

**2.2 Validate Issue Exists**

Verify the issue exists using gh CLI:

```bash
echo "Validating issue #${issue_number}..."
if ! gh issue view "$issue_number" &>/dev/null; then
  echo "Error: Issue #${issue_number} not found."
  echo ""
  echo "Please verify the issue number or create the issue first:"
  echo "gh issue create"
  exit 1
fi
echo "Issue #${issue_number} confirmed"
```

**2.3 Generate Branch Name**

Branch name is always: `issue-${issue_number}`

Example:
- Issue #42 → Branch: `issue-42`
- Issue #123 → Branch: `issue-123`

```bash
branch_name="issue-${issue_number}"
echo "Branch name will be: ${branch_name}"
```

**2.4 Check for Duplicates**

```bash
if git branch --list "${branch_name}" | grep -q .; then
  echo "Error: Branch '${branch_name}' already exists."
  echo ""
  echo "To work on existing branch:"
  echo "git checkout ${branch_name}"
  echo ""
  echo "To delete and recreate:"
  echo "git branch -D ${branch_name}"
  exit 1
fi
echo "Branch name is available"
```

### 3. Create Branch

Create branch with issue-based name:

```bash
echo "Creating branch ${branch_name} from ${base_branch}..."
git checkout -b "${branch_name}"
echo "Branch created successfully"
```

### 4. Display Result

```
## Branch Creation Complete

**Branch Name**: ${branch_name}
**Issue**: #${issue_number}
**Base Branch**: ${base_branch}

You can now start working on this issue.
Use `/git commit` to commit changes.
```

## Error Handling

| Error | Response |
|-------|----------|
| Not on develop branch | Guide to switch to develop |
| Uncommitted changes | Guide to commit or stash |
| Failed to update develop | Guide to resolve conflicts |
| Branch name exists | Guide to use existing or delete |
| Issue not found | Guide to create issue first |
| Invalid issue number | Reject non-numeric input |

## Important Notes

1. **No emojis**: Never use emojis unless explicitly requested by user
2. **Issue-driven development**: All branches must be linked to a GitHub issue
3. **Branch naming**: Always use `issue-<number>` format for consistency
4. **Safety**: Protect main/develop branches, check duplicates, verify clean working tree
5. **Issue validation**: Always verify issue exists before creating branch
6. **Branch strategy**: Branches are created from `develop`, not `main` (see `.claude/rules/branch-strategy.md`)
7. **Variable syntax**: Always use `${variable}` or `"$variable"` in bash commands for safety

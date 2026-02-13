# Worktree Creation Workflow

This workflow creates a new worktree for parallel work from the development branch (typically `develop`).

## Required Tools

- Bash
- AskUserQuestion

## Execution Steps

### 1. Get Current Directory Info

**1.1 Get Current Directory and Repository Name**

```bash
current_dir=$(pwd)
repo_name=$(basename "$current_dir")
parent_dir=$(dirname "$current_dir")

echo "Current directory: ${current_dir}"
echo "Repository name: ${repo_name}"
echo "Parent directory: ${parent_dir}"
```

**1.2 Get Development Branch**

```bash
# Get repository default branch (should be develop per branch strategy)
default_branch=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
echo "Repository default branch: ${default_branch}"

# For worktree creation, always use develop as base (see .claude/rules/branch-strategy.md)
if [[ "$default_branch" == "develop" ]]; then
  base_branch="develop"
else
  echo "WARNING: Repository default is ${default_branch}, but using 'develop' per branch strategy"
  base_branch="develop"
fi

echo "Worktree will be created from: ${base_branch}"
```

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

To create an issue:
1. Go to GitHub repository: gh repo view --web
2. Click "Issues" → "New issue"
3. Follow the format in .claude/rules/issues.md:
   - Title: "As a [role], I want [goal] so that [benefit]"
   - Body: Situation / Pain / Benefit / Success Criteria
4. Save the issue on GitHub
5. Review and edit the issue content on GitHub (you can edit it as many times as needed)
6. Return here with the issue number

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

**2.4 Check for Branch Duplicates**

```bash
if git branch --list "${branch_name}" | grep -q .; then
  echo "Error: Branch '${branch_name}' already exists."
  echo ""
  echo "To work on existing branch in a new worktree:"
  echo "git worktree add <path> ${branch_name}"
  echo ""
  echo "To delete and recreate:"
  echo "git branch -D ${branch_name}"
  exit 1
fi
echo "Branch name is available"
```

### 3. Determine Worktree Path

**3.1 Generate and Validate Worktree Path**

Generate path using consistent naming:

```bash
worktree_path="${parent_dir}/issue-${issue_number}"
echo "Generated worktree path: ${worktree_path}"
```

Example:
- Current: `/home/user/work/nabledge-dev`
- Issue #42 → Worktree: `/home/user/work/issue-42`
- Issue #123 → Worktree: `/home/user/work/issue-123`

Validate parent directory is writable:

```bash
if [[ ! -w "$parent_dir" ]]; then
  echo "Error: Cannot write to parent directory: ${parent_dir}"
  echo "Check permissions or choose different location"
  exit 1
fi
echo "Parent directory is writable"
```

Check if path contains special characters:

```bash
if [[ "$worktree_path" =~ [^a-zA-Z0-9/_-] ]]; then
  echo "WARNING: Path contains special characters: ${worktree_path}"
  echo "This may cause issues on some systems"
fi
```

**3.2 Check Path Existence**

```bash
if [[ -e "$worktree_path" ]]; then
  echo "Error: Path already exists: ${worktree_path}"
  echo ""
  echo "Options:"
  echo "1. Remove existing: rm -rf '${worktree_path}'"
  echo "2. Use different issue number"
  echo "3. Cancel operation"
  exit 1
fi
echo "Path is available"
```

**3.3 Check for Existing Worktree**

Check if a worktree already exists for this branch:

```bash
existing_worktree=$(git worktree list --porcelain | grep -A 2 "branch refs/heads/${branch_name}" | grep "worktree" | awk '{print $2}')
if [[ -n "$existing_worktree" ]]; then
  echo "Error: Worktree already exists for ${branch_name} at: ${existing_worktree}"
  echo ""
  echo "Options:"
  echo "1. Use existing worktree: cd '${existing_worktree}'"
  echo "2. Remove existing: git worktree remove '${existing_worktree}'"
  echo "3. Cancel operation"
  exit 1
fi
echo "No existing worktree for this branch"
```

**3.4 Confirm Path**

Use the AskUserQuestion tool to confirm:
- Question: "Create worktree at the following path. OK?"
- Display the full path in the question
- Provide options: "Yes, create it" and "No, cancel"

Display information:
```
Path: ${worktree_path}
Branch: ${branch_name}
Issue: #${issue_number}
Base: ${base_branch}
```

If user selects "No, cancel", exit gracefully.

### 4. Create Worktree

**4.1 Update Development Branch**

```bash
echo "Updating ${base_branch} from remote..."
git fetch origin "${base_branch}"
git pull origin "${base_branch}"
echo "Base branch updated successfully"
```

**4.2 Create Worktree**

```bash
echo "Creating worktree at ${worktree_path}..."
git worktree add -b "${branch_name}" "${worktree_path}" "${base_branch}"
echo "Worktree created successfully"
```

If creation fails:

Error: Failed to create worktree.

Please verify:
- Sufficient disk space
- Write permissions to the path
- Valid branch name

### 5. Display Result

```
## Worktree Creation Complete

**Path**: ${worktree_path}
**Branch**: ${branch_name}
**Issue**: #${issue_number}
**Base Branch**: ${base_branch}

### Move to Worktree
cd ${worktree_path}

You can now start working on this issue.
Use `/git commit` to commit changes.

### Open in Editor (optional)
code ${worktree_path}
```

## Error Handling

| Error | Response |
|-------|----------|
| Branch name exists | Guide to use different issue or delete existing |
| Path exists | Guide to remove existing or use different issue |
| Failed to update develop | Guide to resolve conflicts |
| Insufficient permissions | Guide to check write permissions |
| Insufficient disk space | Guide to check disk space |
| Issue not found | Guide to create issue first |
| Invalid issue number | Reject non-numeric input |
| Existing worktree | Guide to use existing or remove |

## Important Notes

1. **No emojis**: Never use emojis unless explicitly requested by user
2. **Path naming convention**: `${parent_dir}/issue-${issue_number}`
3. **Branch naming convention**: `issue-${issue_number}`
4. **Issue-driven development**: All worktrees must be linked to a GitHub issue
5. **Issue validation**: Always verify issue exists before creating worktree
6. **Base branch**: Always branch from `develop`, not `main` (see `.claude/rules/branch-strategy.md`)
7. **Variable syntax**: Always use `${variable}` or `"$variable"` in bash commands for safety
8. **Path safety**: Validate parent directory permissions and path availability
9. **Worktree cleanup**: Use `git worktree remove` instead of `rm -rf` for proper cleanup

# Worktree Creation Workflow

This workflow creates a persistent worktree (work1, work2, work3, etc.) for parallel development. Each worktree has its own tracking branch that stays in sync with main via fetch/pull.

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

**1.2 Get Default Branch**

```bash
# Get repository default branch
default_branch=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
echo "Repository default branch: ${default_branch}"

# Verify default branch exists locally
if ! git rev-parse --verify "${default_branch}" &>/dev/null; then
  echo "Error: Default branch '${default_branch}' does not exist locally."
  echo ""
  echo "Please fetch from remote first:"
  echo "  git fetch origin"
  echo "  git checkout ${default_branch}"
  exit 1
fi

# Use default branch as base
base_branch="${default_branch}"

echo "Worktree will be created from: ${base_branch}"
```

### 2. Auto-Generate Worktree Name

**2.1 Find Available Worktree Number**

Scan existing worktrees to find the next available number:

```bash
# Get list of existing worktree paths
existing_worktrees=$(git worktree list --porcelain | grep "^worktree" | awk '{print $2}')

# Find highest work number in use
max_num=0
while IFS= read -r wt_path; do
  wt_basename=$(basename "$wt_path")
  if [[ "$wt_basename" =~ ^work([0-9]+)$ ]]; then
    num="${BASH_REMATCH[1]}"
    if (( num > max_num )); then
      max_num=$num
    fi
  fi
done <<< "$existing_worktrees"

# Next available number
worktree_num=$((max_num + 1))
worktree_name="work${worktree_num}"
branch_name="work${worktree_num}"

echo "Next available worktree: ${worktree_name}"
echo "Branch name: ${branch_name}"
```

**2.2 Check for Branch/Worktree Conflicts**

```bash
# Check if branch already exists
if git branch --list "${branch_name}" | grep -q .; then
  echo "Error: Branch '${branch_name}' already exists."
  echo ""
  echo "To use existing branch:"
  echo "git worktree add <path> ${branch_name}"
  exit 1
fi

# Check if worktree already exists
existing_wt=$(git worktree list --porcelain | grep -A 2 "branch refs/heads/${branch_name}" | grep "worktree" | awk '{print $2}')
if [[ -n "$existing_wt" ]]; then
  echo "Error: Worktree already exists for ${branch_name} at: ${existing_wt}"
  echo ""
  echo "Use existing worktree: cd '${existing_wt}'"
  exit 1
fi

echo "Branch and worktree names are available"
```

### 3. Determine Worktree Path

**3.1 Generate and Validate Worktree Path**

Generate path using consistent naming:

```bash
worktree_path="${parent_dir}/${worktree_name}"
echo "Generated worktree path: ${worktree_path}"
```

Example:
- Current: `/home/user/work/nabledge-dev`
- First worktree → Path: `/home/user/work/work1`
- Second worktree → Path: `/home/user/work/work2`

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

**3.3 Confirm Path**

Use the AskUserQuestion tool to confirm:
- Question: "Create persistent worktree at the following path. OK?"
- Display the full path in the question
- Provide options: "Yes, create it" and "No, cancel"

Display information:
```
Path: ${worktree_path}
Branch: ${branch_name} (will track ${base_branch})
Base: ${base_branch}
```

If user selects "No, cancel", exit gracefully.

### 4. Create Worktree

**4.1 Update Default Branch**

```bash
echo "Updating ${base_branch} from remote..."
git fetch origin "${base_branch}"
git pull origin "${base_branch}"
echo "Default branch updated successfully"
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
**Branch**: ${branch_name} (tracks ${base_branch})
**Base Branch**: ${base_branch}

### Move to Worktree
cd ${worktree_path}

### Working with This Worktree

This is a persistent worktree for parallel development. To work on issues:

1. Create feature branch: `/hi <issue-number>`
2. Work on your changes
3. Commit: `/git commit`
4. Create PR: `/pr create`
5. Merge: `/bb <pr-number>` (returns to ${branch_name} after cleanup)

The ${branch_name} branch stays in sync with ${base_branch}. Use `git pull origin ${base_branch}` to update.

### Open in Editor (optional)
code ${worktree_path}
```

## Error Handling

| Error | Response |
|-------|----------|
| Branch name exists | Guide to use existing or delete |
| Path exists | Guide to remove existing path |
| Failed to update default branch | Guide to resolve conflicts |
| Insufficient permissions | Guide to check write permissions |
| Insufficient disk space | Guide to check disk space |
| Existing worktree | Guide to use existing worktree |

## Important Notes

1. **No emojis**: Never use emojis unless explicitly requested by user
2. **Path naming convention**: `${parent_dir}/work${N}` where N is auto-incremented
3. **Branch naming convention**: `work${N}` matching worktree name
4. **Persistent worktrees**: work1/work2/work3 are permanent development spaces, not deleted after PR merge
5. **Auto-numbering**: Automatically detects existing worktrees and assigns next available number
6. **Base branch**: Always branch from repository's default branch (main, develop, etc.)
7. **Variable syntax**: Always use `${variable}` or `"$variable"` in bash commands for safety
8. **Path safety**: Validate parent directory permissions and path availability
9. **Branch tracking**: workX branches track main and can be updated via `git pull origin main`
10. **Feature branches**: Use `/hi` within worktree to create feature branches for actual work

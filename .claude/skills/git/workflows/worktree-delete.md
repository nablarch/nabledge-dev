# Worktree Deletion Workflow

This workflow deletes an existing worktree.

## Required Tools

- Bash
- AskUserQuestion

## Execution Steps

### 1. Get Worktree List

**1.1 Get Worktree List**

```bash
git worktree list
```

Output example:
```
<workspace-path>/nab-agents         abc1234 [main]
<workspace-path>/nab-agents-<branch-name> def5678 [add-feature]
<workspace-path>/nab-agents-<branch-name>  ghi9012 [fix-bug]
```

**1.2 Extract Deletable Worktrees**

Exclude the main worktree (first line) to create list of deletable worktrees.

If no worktrees:
```
Info: No deletable worktrees found.

Current worktrees:
{worktree_list}
```

### 2. Determine Target Worktree

**2.1 Check Arguments**

If argument is specified, use it as target.
If no argument, proceed to next step to let user select.

**2.2 Select Target (if no argument)**

Use AskUserQuestion to select worktree:

```
Question: Select worktree to delete.
Header: "Delete Worktree"
Options:
  - Label: "{path1}"
    Description: "Branch: {branch1}"
  - Label: "{path2}"
    Description: "Branch: {branch2}"
  - Label: "{path3}"
    Description: "Branch: {branch3}"
```

### 3. Pre-deletion Checks

**3.1 Protect Main Worktree**

If target is the main worktree (current repository), exit with error:
```
Error: Cannot delete main worktree.
```

**3.2 Protect Persistent Worktrees**

Check if the target worktree is a persistent work branch (work1, work2, work3, etc.):

```bash
worktree_basename=$(basename "$worktree_path")
if [[ "$worktree_basename" =~ ^work[0-9]+$ ]]; then
  echo "Error: Cannot delete persistent worktree '${worktree_basename}'."
  echo ""
  echo "Persistent worktrees (work1, work2, etc.) are for long-term parallel development."
  echo "They should not be deleted after completing issues."
  echo ""
  echo "If you really need to remove it:"
  echo "  git worktree remove '${worktree_path}'"
  echo "  git branch -D '${worktree_basename}'"
  exit 1
fi
echo "Worktree is not a persistent work branch"
```

**3.3 Verify Path Exists**

```bash
test -d {worktree_path}
```

If path doesn't exist, exit with error:
```
Error: Worktree "{worktree_path}" not found.

Check worktree list:
git worktree list
```

**3.3 Check for Uncommitted Changes**

Check status of target worktree:

```bash
git -C {worktree_path} status --porcelain
```

If uncommitted changes exist, display warning:

Use AskUserQuestion to confirm:
```
Question: Worktree "{worktree_path}" has uncommitted changes.
Deletion will lose these changes. Delete anyway?
Header: "Warning"
Options:
  - Label: "Yes, delete it"
    Description: "Uncommitted changes will be lost"
  - Label: "No, cancel"
    Description: "Save changes before deletion"

Display changes:
{git_status_output}
```

If user selects "Cancel", abort:
```
Operation cancelled.

To save changes:
cd {worktree_path}
/git commit
```

### 4. Delete Worktree

**4.1 Delete Worktree**

```bash
git worktree remove {worktree_path}
```

If deletion fails (locked, etc.), force delete:
```bash
git worktree remove --force {worktree_path}
```

If still fails:
```
Error: Failed to delete worktree.

Manual deletion:
rm -rf {worktree_path}
git worktree prune
```

### 5. Branch Deletion Confirmation

**5.1 Get Branch Name**

Extract branch name from deleted worktree.

**5.2 Check if Merged**

```bash
git branch --merged main | grep "^  {branch_name}$"
```

**5.3 Confirm Branch Deletion**

If merged, use AskUserQuestion to confirm branch deletion:

```
Question: Branch "{branch_name}" is merged.
Delete this branch too?
Header: "Delete Branch"
Options:
  - Label: "Yes, delete it"
    Description: "Delete from local and remote"
  - Label: "Delete local only"
    Description: "Keep remote branch"
  - Label: "No, keep it"
    Description: "Keep the branch"
```

**5.4 Delete Branch**

Based on user selection:

**"Yes, delete it"**:
```bash
git push origin --delete {branch_name}
git branch -d {branch_name}
```

**"Delete local only"**:
```bash
git branch -d {branch_name}
```

**"No, keep it"**:
Do nothing.

### 6. Display Result

```
## Worktree Deletion Complete

**Deleted Worktree**: {worktree_path}
**Branch**: {branch_name}

### Actions Performed
- Deleted worktree '{worktree_path}'
{if branch deleted}
- Deleted local branch '{branch_name}'
- Deleted remote branch 'origin/{branch_name}'
{/if branch deleted}
```

## Error Handling

| Error | Response |
|-------|----------|
| No deletable worktrees | Display worktree list |
| Attempted to delete main worktree | Display error and exit |
| Attempted to delete persistent worktree (work1, work2, etc.) | Display error and exit with manual override instructions |
| Path doesn't exist | Verify correct path |
| Uncommitted changes | Display warning and ask user to confirm |
| Deletion failed | Attempt force delete, guide to manual deletion if failed |

## Important Notes

1. **No emojis**: Never use emojis unless explicitly requested by user
2. **Safety first**: Warn if uncommitted changes exist
3. **Main worktree protection**: Refuse deletion of main worktree
4. **Persistent worktree protection**: Refuse deletion of work1/work2/work3/etc. worktrees (require manual override)
5. **Branch deletion**: Automatically suggest deletion for merged branches
6. **Use case**: This command is for deleting temporary/feature worktrees, not persistent development worktrees

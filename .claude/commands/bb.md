---
name: bb
description: Approve and merge PR, delete feature branch, return to worktree base branch
argument-hint: [PR number]
allowed-tools: Bash, Skill, AskUserQuestion
---

Approve PR, merge it using /pr skill, delete feature branch, and return to worktree base branch.

# Instructions

1. Get PR number from $ARGUMENTS or auto-detect from current branch
2. Get current branch name: `git branch --show-current`
3. Approve PR if not already approved: `gh pr review $PR_NUMBER --approve`
4. Merge PR: Use Skill tool - `Skill(skill: "pr", args: "merge $PR_NUMBER")`
5. Determine base branch:
   - If in worktree (work1, work2, etc.), detect worktree base branch
   - If in main repo, use main branch
6. Switch to base branch: `git checkout $BASE_BRANCH`
7. Update base branch: `git pull origin main` (to sync with latest main)
8. Delete feature branch: Use Skill tool - `Skill(skill: "git", args: "branch-delete $FEATURE_BRANCH")`
9. Update all work branches (main repo only):
   ```bash
   # Only in main repo, not in worktrees
   if [[ "$base_branch" == "main" ]]; then
     work_branches=$(git branch --list 'work*' | sed 's/^[* ] //')

     if [[ -n "$work_branches" ]]; then
       echo "Updating work branches to match main..."
       while IFS= read -r branch; do
         if [[ -n "$branch" ]]; then
           echo "Updating $branch..."
           git checkout "$branch"
           if git merge --ff-only main; then
             echo "✓ $branch updated"
           else
             echo "⚠ Warning: $branch has diverged from main, skipping"
           fi
         fi
       done <<< "$work_branches"
       git checkout main
       echo "All work branches updated"
     fi
   fi
   ```

# Worktree Detection

To determine if current directory is a worktree and find base branch:

```bash
# Get worktree info
worktree_path=$(pwd)
worktree_list=$(git worktree list --porcelain)

# Find base branch for this worktree
# Look for pattern: work1, work2, work3, etc.
if [[ "$worktree_path" =~ /work([0-9]+)$ ]]; then
  base_branch="work${BASH_REMATCH[1]}"
else
  base_branch="main"
fi
```

# Important

- Always use Skill tool for pr merge and git branch-delete operations
- Never run `gh pr merge` or `git branch -d` manually
- In worktrees: return to workX branch (not main)
- In main repo: return to main branch, then auto-update all work* branches
- Work branches are updated using `git merge --ff-only` to ensure clean sync
- Diverged work branches are skipped with warning (not error)
- Ask user if anything is unclear

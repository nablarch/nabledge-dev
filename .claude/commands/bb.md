---
name: bb
description: Approve and merge PR, detach HEAD, delete branch
argument-hint: [PR number]
allowed-tools: Bash, Skill, AskUserQuestion
---

Approve PR, merge it using /pr skill, detach HEAD, and delete branch using /git skill.

# Instructions

1. Get PR number from $ARGUMENTS or auto-detect from current branch
2. Approve PR if not already approved: `gh pr review $PR_NUMBER --approve`
3. Merge PR: Use Skill tool - `Skill(skill: "pr", args: "merge $PR_NUMBER")`
4. Detach HEAD to main: `git checkout main && git pull`
5. Delete branch: Use Skill tool - `Skill(skill: "git", args: "branch-delete $BRANCH_NAME")`

# Important

- Always use Skill tool for pr merge and git branch-delete operations
- Never run `gh pr merge` or `git branch -d` manually
- Ask user if anything is unclear

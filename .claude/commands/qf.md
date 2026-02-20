---
name: qf
description: Quick fix workflow for small changes without issue tracking
argument-hint: [description]
allowed-tools: Bash, Task, AskUserQuestion, Glob, Grep, Read, Edit, Write, Skill
---

Quick fix workflow for small changes that don't need issue tracking (typos, docs, minor fixes).

# Instructions

1. Get description from $ARGUMENTS or ask user interactively
2. Ensure on main branch and sync with remote:
   ```bash
   current_branch=$(git branch --show-current)
   if [[ "$current_branch" != "main" ]]; then
     echo "Switching to main branch..."
     git checkout main
   fi
   git pull origin main
   ```
3. Generate branch name from description:
   - Convert to lowercase
   - Replace spaces with hyphens
   - Pattern: `qf/<slug>`
   - Example: "Fix README typo" → `qf/fix-readme-typo`
4. Create branch: `git checkout -b qf/<slug>`
5. Analyze requirements from description
6. Implement changes: Use Task tool with general-purpose agent
   - Pass description, relevant files to agent
   - Agent will read files, implement changes, ask questions if unclear
7. Commit: Use Skill tool - `Skill(skill: "git", args: "commit")`
8. Create PR: Use Skill tool - `Skill(skill: "pr", args: "create")`
   - PR workflow will auto-detect qf/ branch and skip issue requirement

# Branch Naming

- Pattern: `qf/<descriptive-slug>`
- Examples:
  - qf/fix-typo-readme
  - qf/update-changelog
  - qf/remove-unused-import
  - qf/fix-broken-link

# Important

- Use Skill tool for git commit and PR creation
- Never manually run git commit or gh pr create commands
- Always sync with remote main before branching
- For significant features, use /hi instead (issue-driven development)
- Works in both main repo and worktrees
- In worktrees: Creates qf branch from current workX branch

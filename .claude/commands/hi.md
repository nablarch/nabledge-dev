---
name: hi
description: Full development workflow from issue to PR
argument-hint: [issue# or pr#]
allowed-tools: Bash, Task, AskUserQuestion, Glob, Grep, Read, Edit, Write, Skill
---

Execute full development workflow from issue/PR to review request.

# Instructions

1. Get issue/PR number from $ARGUMENTS or ask user interactively
2. Sync current branch with main if needed:
   ```bash
   current_branch=$(git branch --show-current)
   # If current branch is workX, sync with main first
   if [[ "$current_branch" =~ ^work[0-9]+$ ]]; then
     echo "Syncing $current_branch with main..."
     git fetch origin main
     git merge --ff-only origin/main
   fi
   ```
3. Fetch issue/PR details: `gh issue view $NUMBER` or `gh pr view $NUMBER`
4. Create branch if needed: `git checkout -b issue-$NUMBER`
5. Analyze requirements: Use Glob/Grep to find relevant files
6. Implement changes: Use Task tool with general-purpose agent
   - Pass full issue body, success criteria, relevant files to agent
   - Agent will read files, implement changes, ask questions if unclear
7. Run tests: Auto-detect framework (pytest, npm test, mvn test, gradle test)
8. Create PR: Use Skill tool - `Skill(skill: "pr", args: "create")`
9. Request review from user

# Important

- Use Glob/Grep tools for file search (not bash find/grep)
- Use Task tool for implementation (not direct edits)
- Use Skill tool for git commit and PR creation
- Never manually run git commit or gh pr create commands
- Ask questions when requirements are unclear
- Works in both main repo and worktrees (work1, work2, etc.)
- In worktrees: Creates feature branch from current workX branch

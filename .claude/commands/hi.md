---
name: hi
description: Full development workflow from issue to PR
argument-hint: [issue# or pr#]
allowed-tools: Bash, Task, AskUserQuestion, Glob, Grep, Read, Edit, Write, Skill
---

Execute full development workflow from issue/PR to review request.

# Instructions

1. Get issue/PR number from $ARGUMENTS or ask user interactively
2. Fetch issue/PR details: `gh issue view $NUMBER` or `gh pr view $NUMBER`
3. Create branch if needed: `git checkout -b feature/issue-$NUMBER`
4. Analyze requirements: Use Glob/Grep to find relevant files
5. Implement changes: Use Task tool with general-purpose agent
   - Pass full issue body, success criteria, relevant files to agent
   - Agent will read files, implement changes, ask questions if unclear
6. Run tests: Auto-detect framework (pytest, npm test, mvn test, gradle test)
7. Create PR: Use Skill tool - `Skill(skill: "pr", args: "create")`
8. Request reviews if configured

# Important

- Use Glob/Grep tools for file search (not bash find/grep)
- Use Task tool for implementation (not direct edits)
- Use Skill tool for git commit and PR creation
- Never manually run git commit or gh pr create commands
- Ask questions when requirements are unclear

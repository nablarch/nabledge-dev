---
name: fb
description: Respond to PR review feedback
argument-hint: [PR number]
allowed-tools: Bash, Skill, AskUserQuestion
---

Respond to PR review feedback using /pr skill.

# Instructions

1. Get PR number from $ARGUMENTS or auto-detect from current branch
2. Respond to reviews: Use Skill tool - `Skill(skill: "pr", args: "resolve $PR_NUMBER")`

The pr skill will handle:
- Fetching review comments
- Implementing fixes
- Running tests
- Committing changes
- Replying to comments
- Pushing updates

# Important

- Always use Skill tool to call pr skill
- Never manually implement fixes or reply to comments
- Let the pr skill handle the entire workflow

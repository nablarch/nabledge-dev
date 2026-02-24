---
name: dy
description: Generate daily standup report messages. Fetches today's closed issues and open PRs, collects discoveries via interview, and formats for Teams.
argument-hint: (no arguments needed)
allowed-tools: Bash, Task, AskUserQuestion
---

# Daily Standup Report Generator (dy)

This skill automatically generates daily standup meeting messages at the end of the day for the next morning's standup.

## Features

- Automatically fetch today's closed GitHub issues and open PRs
- Present work summary to help users recall their day
- Collect "discoveries" from user via interview
- Output in Teams-ready markdown format (Japanese) with emoji icons
- Support Teams markdown link format

## Execution Flow

### 1. Execute Workflow

Use Task tool to execute `workflows/generate.md`:

```
Task
  subagent_type: "general-purpose"
  description: "Execute standup report generation workflow"
  prompt: "Generate a standup report message. Follow the workflow below.

{Read and expand workflows/generate.md content here}

## Execution Context
- Execution date: {today's date}
- Repository: {current repository}
"
```

## Implementation Notes

1. **No arguments needed**: Simply run `/dy`
2. **Japanese output**: All messages are in Japanese for Japanese users
3. **Zero-issue handling**: Gracefully handles cases with no closed issues
4. **Task tool usage**: Workflow executes in separate context
5. **Teams-compatible**: Output uses Teams markdown link format with `[text](url)` syntax which Teams renders as clickable links

## Error Handling

| Error | When This Occurs | Response |
|-------|------------------|----------|
| gh CLI not available | gh command not found or not authenticated | Guide user to run `gh auth login` |
| Not a GitHub repository | Current directory is not a git repository with GitHub remote | Guide user to check current directory |
| PR fetch failed | Network error or permission issues when fetching open PRs | Display issue summary only, skip PR section, continue |
| Zero issues today | No issues were closed on the current date | Display "今日クローズしたIssueはありません" and continue |

For detailed usage examples, see `assets/examples.md`.

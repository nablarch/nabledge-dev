---
name: op
description: Generate standup report messages. Fetches today's closed issues, collects discoveries and notes via interview, and generates reflection.
argument-hint: (no arguments needed)
allowed-tools: Bash, Task, AskUserQuestion
---

# Standup Report Generator (op)

This skill automatically generates standup meeting messages at the end of the day for the next morning's standup.

## Features

- Automatically fetch today's closed GitHub issues
- Collect "discoveries" and "other notes" from user via interview
- Auto-generate reflection based on today's achievements (~200 Japanese characters)
- Output in Teams-ready format (Japanese)

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

1. **No arguments needed**: Simply run `/op`
2. **Japanese output**: All messages are in Japanese for Japanese users
3. **Zero-issue handling**: Gracefully handles cases with no closed issues
4. **Task tool usage**: Workflow executes in separate context

## Error Handling

| Error | Response |
|-------|----------|
| gh CLI not available | Guide user to run `gh auth login` |
| Not a GitHub repository | Guide user to check current directory |
| Zero issues today | Display "今日クローズしたIssueはありません" and continue |

For detailed usage examples, see `assets/examples.md`.

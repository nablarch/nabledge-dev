---
name: hi
description: Execute full development workflow from issue/PR - creates branch, implements changes, runs tests, creates PR, and requests review. Asks questions when unclear.
argument-hint: [issue# or pr#]
allowed-tools: Bash, Task, AskUserQuestion, Read, Glob, Grep, Edit, Write, Skill
---

# Hi - Full Development Workflow

Execute complete development workflow from issue/PR to review request.

## Workflow Steps

### 1. Parse Arguments

Extract issue/PR number from `$ARGUMENTS`:

```
/hi                → No args → Ask for issue/PR selection
/hi 123            → issue_or_pr="123"
/hi #123           → issue_or_pr="123" (strip #)
```

**If no args**: Use AskUserQuestion to select from recent issues:
```bash
gh issue list --limit 10 --json number,title,state
```

### 2. Fetch Issue/PR Details

```bash
# Try as issue first
gh issue view $NUMBER --json number,title,body,state,labels

# If not found, try as PR
gh pr view $NUMBER --json number,title,body,state,labels
```

### 3. Verify/Create Branch

Check current branch:
```bash
current_branch=$(git branch --show-current)
git_status=$(git status --porcelain)
```

**Branch strategy**:
- If on `main`: Create new branch `feature/issue-{number}`
- If on feature branch: Ask to continue or create new branch

**Create branch** (if needed):
```bash
git checkout main
git pull origin main
git checkout -b feature/issue-{number}
```

### 4. Analyze Requirements

Display summary to user:
```
📋 Working on: [#123] Issue Title

Goal: [Brief summary from issue body]
Success Criteria:
- [ ] Criterion 1 (extracted from issue)
- [ ] Criterion 2

Files to check:
- [Use Glob/Grep to find relevant files]
```

### 5. Execute Work

Delegate to Task agent with full context:

```
Task
  subagent_type: "general-purpose"
  description: "Implement changes for issue"
  prompt: "Implement the following requirements. Ask questions if unclear.

## Requirements
{Full issue/PR body}

## Success Criteria
{Extracted criteria}

## Instructions
1. Read relevant files to understand current implementation
2. Implement required changes
3. Follow project coding standards (.claude/rules/)
4. Ask questions using AskUserQuestion if requirements are unclear
5. Do not run tests or commit - will be done separately

Focus on implementing requirements only."
```

### 6. Run Tests

Auto-detect test framework:
```bash
if [ -f "pytest.ini" ] || [ -f "pyproject.toml" ]; then
  pytest
elif [ -f "package.json" ]; then
  npm test
elif [ -f "pom.xml" ]; then
  mvn test
elif [ -f "build.gradle" ]; then
  ./gradlew test
else
  # Ask user for test command
  AskUserQuestion: "What command should I run to execute tests?"
fi
```

**If tests fail**: Ask to fix, continue anyway (draft PR), or abort.

### 7. Create PR

Delegate to existing pr skill:
```
Skill
  skill: "pr"
  args: "create"
```

### 8. Request Review

```bash
# Get PR number
pr_number=$(gh pr view --json number -q .number)

# Mark ready and request reviews
gh pr ready $pr_number
gh pr edit $pr_number --add-reviewer @user1,@user2
```

**Output**:
```
✅ Workflow Complete!

Issue: #123
Branch: feature/issue-123
PR: #456
Status: Ready for review
```

## Error Handling

- **Issue not found**: Ask to verify number or select from list
- **Not git repo**: Verify current directory
- **Uncommitted changes on main**: Ask to stash, commit, or abort
- **Tests fail**: Ask to fix, continue, or abort
- **gh CLI unavailable**: Guide to run `gh auth login`

## Implementation Notes

1. Show progress at each step
2. Ask questions when requirements unclear
3. Verify before destructive operations
4. Pass full context to Task agents
5. Always run tests before creating PR (unless user skips)

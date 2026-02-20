# Language Guidelines

## Quick Reference

| Content Type | Language | Examples |
|--------------|----------|----------|
| Repository content | English | Code, commits, README, design docs, issues |
| Console conversations | Japanese | AI responses to user questions |
| Skills: structure | English | SKILL.md, workflows/*.md headings and logic |
| Skills: user messages | Japanese | Questions, output headers, error messages |
| End-user guides | Japanese | plugin/GUIDE-*.md, assets/examples.md |

## Repository Content (English)

Write in English:
- Source code (comments, variables, functions)
- Documentation (README, design docs)
- Git commits and PR descriptions
- Tests and issues

## Console Conversations (Japanese)

AI communicates with users in Japanese:
- Responses to questions
- Explanations and guidance
- Status updates and errors

## Skills Documentation

### AI Agent-Facing: English

Structure and logic in English:
- `SKILL.md` - Skill definition, execution flow
- `workflows/*.md` - Workflow steps, logic
- `docs/*.md` - Technical documentation

**Example**:
```markdown
# Standup Report Generator (op)

## Execution Flow

### 1. Execute Workflow
...
```

### User-Facing: Japanese

Messages users see in Japanese:
- AskUserQuestion prompts: `"今日の発見は何ですか？"`
- Output headers: `## アウトプット`, `## 発見`
- Error messages: `エラー: GitHubリポジトリが見つかりません。`
- End-user guides: `plugin/GUIDE-CC.md`, `assets/examples.md`

## Common Pattern

Workflows mix English structure with Japanese messages:

```markdown
### 2. Interview User

Use AskUserQuestion tool:

Question: "今日の発見は何ですか？(技術的な気づき、学び、改善点など)"

Save user's answer as `discoveries`.
```

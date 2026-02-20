# Language Guidelines

## Context

**Target users**: Japanese developers working on Nablarch projects

**Rationale**: Nabledge skills serve Japanese Nablarch users, requiring Japanese for end-user interfaces while maintaining English for developer content.

## Basic Policy

| Audience | Language | Rationale |
|----------|----------|-----------|
| End users (Nabledge users) | Japanese | Primary users are Japanese Nablarch developers |
| Developers (repository contributors) | English | Standard for technical collaboration |
| AI conversations | Request Japanese individually | Not default; specify when needed |

## Quick Reference

| Content Type | Language | Examples |
|--------------|----------|----------|
| Code | English | Source code, comments, variables, functions |
| Issues & PRs | English | Titles, descriptions, comments |
| Commits | English | Commit messages |
| Developer docs | English | README, design docs, architecture |
| Skills: structure | English | SKILL.md, workflows/*.md (headings, logic) |
| Skills: user interface | Japanese | Questions, output, error messages |
| End-user docs | Japanese | plugin/GUIDE-*.md, assets/examples.md |

## Developer Content (English)

Write in English:
- **Source code**: Comments, variables, functions, classes
- **Issues**: Titles and descriptions
- **Pull Requests**: Titles and descriptions
- **Commits**: Commit messages
- **Documentation**: README.md, design docs, architecture docs
- **Tests**: Test code and descriptions
- **Skills structure**: SKILL.md, workflows/*.md (structure and logic)

## End-User Content (Japanese)

Write in Japanese for Nabledge users:
- **User guides**: plugin/GUIDE-*.md, assets/examples.md
- **User interface elements**:
  - AskUserQuestion prompts: `"今日の発見は何ですか？"`
  - Output headers: `## アウトプット`, `## 発見`
  - Error messages: `エラー: GitHubリポジトリが見つかりません。`
  - Status messages shown to users

## AI Conversations

**Default**: Follow context (usually English for development tasks)

**When Japanese needed**: Explicitly request in Japanese
- Example: "日本語で説明してください"
- AI will respond in Japanese when directly requested

## Skills Documentation Pattern

Skills mix English structure with Japanese user interface:

```markdown
### 2. Interview User

Use AskUserQuestion tool:

Question: "今日の発見は何ですか？(技術的な気づき、学び、改善点など)"

Save user's answer as `discoveries`.
```

**Structure (English)**:
- Section headings
- Logic descriptions
- Tool instructions

**User interface (Japanese)**:
- Question text users see
- Output format users copy
- Error messages users read

# Language Guidelines

## Overview

**Repository**: English for code and documentation
**Communication**: Japanese for AI-user conversations
**Skills**: Mixed (structure in English, user-facing messages in Japanese)

## Repository Content (English)

All repository content should be written in English:

- Source code (comments, variable names, function names)
- Documentation (README, design docs, guides)
- Git commits and PR descriptions
- Tests and test descriptions
- Issues (titles and descriptions)

**Rationale**: English is the standard for technical documentation and enables wider collaboration.

## Console Conversations (Japanese)

AI agents communicate with users in Japanese:

- Response messages to user questions
- Explanations and guidance
- Status updates and progress reports
- Error explanations

**Rationale**: Primary users are Japanese developers working on Nablarch projects.

## Skills Documentation

Skills follow a specific pattern based on audience:

### AI Agent-Facing Documents (English)

These documents are read by AI agents and should be written in English:

**Structure and logic**:
- `SKILL.md` - Skill definition and execution flow
- `workflows/*.md` - Workflow steps and logic
- `docs/*.md` - Technical documentation for agents

**Example** (from nabledge-6):
```markdown
# Nabledge-6: Nablarch 6 Knowledge Base

Structured knowledge base for Nablarch 6 framework...

## Execution Flow

### 1. Execute Workflow
...
```

### User-Facing Content (Japanese)

Content that users directly see should be in Japanese:

**Interactive elements**:
- AskUserQuestion prompts and options
- Output formats and section headers
- Error messages and guidance
- Status messages

**Example** (from op skill):
```markdown
Question: "今日の発見は何ですか？(技術的な気づき、学び、改善点など)"

## アウトプット
...

エラー: GitHubリポジトリが見つかりません。
```

**End-user documentation**:
- `plugin/GUIDE-*.md` - Installation and usage guides
- `assets/examples.md` - Usage examples
- Release notes for end users

**Example**:
```markdown
# Claude Code 利用ガイド

Nabledge-6を Claude Code で使用するためのガイドです。
```

## Practical Examples

### Good: SKILL.md Structure

```markdown
---
name: op
description: Generate standup report messages...
---

# Standup Report Generator (op)

This skill automatically generates...

## Execution Flow

### 1. Execute Workflow

Use Task tool to execute `workflows/generate.md`:
```

### Good: Workflow with Japanese Messages

```markdown
### 2. Interview User

Use AskUserQuestion tool:

```
Question: "今日の発見は何ですか？(技術的な気づき、学び、改善点など)"
Options:
  - "Other: {free text input}"
```

Save user's answer as `discoveries`.
```

### Good: Output Format

```markdown
**4.1 Message Format**

Output in the following format (Japanese):

```
## アウトプット

{Issue list}

## 発見

{User input}
```
```

## Decision Tree

When writing documentation, ask:

1. **Who is the primary reader?**
   - AI agent → English
   - End user → Japanese

2. **What is the content type?**
   - Structure, logic, flow → English
   - User interaction, output → Japanese

3. **Where does it appear?**
   - SKILL.md, workflows/, docs/ → English (with Japanese user messages)
   - plugin/GUIDE-*.md, assets/examples.md → Japanese

## Common Mistakes

❌ **All Japanese SKILL.md**
```markdown
# 朝会用メッセージ生成スキル (op)

このスキルは1日の終わりに翌朝の朝会用メッセージを自動生成します。
```

✅ **English structure with Japanese user messages**
```markdown
# Standup Report Generator (op)

This skill automatically generates standup meeting messages...

## Features

- Automatically fetch today's closed GitHub issues
- Output in Teams-ready format (Japanese)
```

❌ **English user questions**
```markdown
Question: "What did you discover today?"
```

✅ **Japanese user questions**
```markdown
Question: "今日の発見は何ですか？(技術的な気づき、学び、改善点など)"
```

## Summary

| Content Type | Language | Examples |
|--------------|----------|----------|
| AI agent documentation | English | SKILL.md, workflows/*.md |
| User interaction | Japanese | Questions, output, errors |
| End-user guides | Japanese | GUIDE-*.md, examples.md |
| Code & commits | English | All source code |
| Console conversations | Japanese | AI responses to users |

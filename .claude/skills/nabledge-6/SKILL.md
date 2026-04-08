---
name: nabledge-6
description: Provides Nablarch 6 framework knowledge and code analysis capabilities. Use when developing Nablarch applications, implementing features, reviewing code, or answering questions about Nablarch 6.
user-invocable: false
disable-model-invocation: true
---

# Nabledge-6: Nablarch 6 Knowledge Base

Knowledge base and code analysis tool for Nablarch 6 framework.

## Usage

**Interactive mode**:
```
nabledge-6
```

**Direct knowledge search**:
```
nabledge-6 "<question>"
```

**Direct code analysis**:
```
nabledge-6 code-analysis
```

## Execution Instructions

### Step 0: Determine Workflow

**No arguments** (`nabledge-6`):
- Show greeting
- Ask user to choose: Knowledge Search or Code Analysis

**Text argument** (`nabledge-6 "<question>"`):
- Execute `workflows/qa.md` to answer question
- This workflow orchestrates _knowledge-search pipeline

**"code-analysis" argument** (`nabledge-6 code-analysis`):
- Execute `workflows/code-analysis.md` to analyze user's code

**"upgrade-check" argument** (`nabledge-6 upgrade-check [--from <ver>] [--to <ver>] [--project-dir <path>]`):
- Execute `workflows/upgrade-check.md` to analyze upgrade impact
- This workflow detects affected items between Nablarch 6 versions using rule-based analysis

## Critical Constraints

**Knowledge files only**: Answer using ONLY information in `knowledge/*.json`. DO NOT use external knowledge or LLM training data.

**When knowledge is missing**:
- Output: "この情報は知識ファイルに含まれていません"
- List related available knowledge from `knowledge/index.toon`
- DO NOT answer from external knowledge

## Error Handling

**Knowledge not found** (Knowledge Search):
- Message: "この情報は知識ファイルに含まれていません"
- List related entries from index.toon

**Target code not found** (Code Analysis):
- Message: "指定されたコードが見つかりませんでした"
- Show search patterns used
- Ask for clarification

**Workflow execution failure**:
- Inform which step failed
- Show error details
- Suggest retry or alternative

## Knowledge Structure

**Files**: `knowledge/features/`, `knowledge/checks/`, `knowledge/releases/`
**Index**: `knowledge/index.toon` (all entries with search hints)
**Schemas**: `schemas/*.json` (JSON validation schemas)
**Scripts**: `scripts/*.sh` (pre-built processing scripts)

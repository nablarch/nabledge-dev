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
- Execute Knowledge Search Workflow

**"code-analysis" argument** (`nabledge-6 code-analysis`):
- Execute Code Analysis Workflow

### Step 1: Knowledge Search Workflow

**When**: User wants to search Nablarch knowledge

**Execute**: `workflows/keyword-search.md` → `workflows/section-judgement.md`

**Expected tools**: Read, Bash, jq
**Expected calls**: 10-15

### Step 2: Code Analysis Workflow

**When**: User wants to analyze existing code

**Execute**: `workflows/code-analysis.md`

**Expected tools**: Read, Glob, Grep, Bash, jq, Write
**Expected calls**: 30-50

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

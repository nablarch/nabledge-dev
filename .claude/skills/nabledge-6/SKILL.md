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

**Question answering**:
```
nabledge-6 "<question>"
```

**Code analysis**:
```
nabledge-6 code-analysis
```

**Keyword search** (precise, term-based):
```
nabledge-6 keyword-search "<term1> <term2> ..."
```

**Semantic search** (exploratory, natural language):
```
nabledge-6 semantic-search "<question>"
```

## Execution Instructions

### Step 0: Determine Workflow

**No arguments** (`nabledge-6`):
- Show greeting
- Ask user to choose: Question Answering or Code Analysis

**Text argument** (`nabledge-6 "<question>"`):
- Execute `workflows/qa.md` (hearing → semantic search → answer → verify)

**"code-analysis" argument** (`nabledge-6 code-analysis`):
- Execute `workflows/code-analysis.md`

**"keyword-search" argument** (`nabledge-6 keyword-search "<terms>"`):
- Execute `workflows/keyword-search.md` with the provided terms

**"semantic-search" argument** (`nabledge-6 semantic-search "<question>"`):
- Execute `workflows/semantic-search.md` with the provided question

## Critical Constraints

**Knowledge files only**: Answer using ONLY information in `knowledge/*.json`. DO NOT use external knowledge or LLM training data.

**When knowledge is missing**:
- Output: "この情報は知識ファイルに含まれていません"
- DO NOT answer from external knowledge

## Error Handling

**Knowledge not found** (Knowledge Search):
- Message: "この情報は知識ファイルに含まれていません"

**Target code not found** (Code Analysis):
- Message: "指定されたコードが見つかりませんでした"
- Show search patterns used
- Ask for clarification

**Workflow execution failure**:
- Inform which step failed
- Show error details
- Suggest retry or alternative

## Knowledge Structure

**Files**: `knowledge/{category}/` — RBKC-generated JSON files by category:
  - `about/`, `assets/`, `check/`, `component/`, `development-tools/`
  - `guide/`, `processing-pattern/`, `releases/`, `setup/`
**Index**: `knowledge/index.md` (section index for semantic search)
**Terms**: `knowledge/terms.json` (term → section_id map for keyword search)
**Schemas**: `schemas/*.json` (JSON validation schemas)
**Scripts**: `scripts/*.sh` (pre-built processing scripts)

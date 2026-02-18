# Scenario Expectations Revision

**Date**: 2026-02-13
**File Updated**: `.claude/skills/nabledge-test/scenarios/nabledge-6/scenarios.json`
**Version**: 2.0.0 → 3.0.0

## Summary

Updated all 5 test scenarios to align expectations with actual knowledge file content. All section names and keywords were verified against actual knowledge files (nablarch-batch.json, universal-dao.json, data-read-handler.json).

## Changes by Scenario

### 1. processing-005 (バッチの起動方法)

**Knowledge Files Checked**: `nablarch-batch.json` (sections: request-path, batch-types)

| Change Type | Before | After | Reason |
|-------------|--------|-------|--------|
| sections | `["launch", "execution"]` | `["request-path", "batch-types"]` | Original sections don't exist |
| keywords | `["バッチ起動", "Main", "コマンドライン", "起動クラス", "実行"]` | `["-requestPath", "コマンドライン引数", "アクションのクラス名", "リクエストID", "都度起動"]` | Match actual terminology in knowledge files |

**Verification**:
- ✓ Section "request-path" exists and contains launch instructions
- ✓ Section "batch-types" exists and explains batch types
- ✓ Keywords match exact terms in sections (e.g., "-requestPath" appears in format field)

### 2. libraries-001 (UniversalDaoでページング)

**Knowledge Files Checked**: `universal-dao.json` (section: paging)

| Change Type | Before | After | Reason |
|-------------|--------|-------|--------|
| sections | `["paging"]` | `["paging", "overview"]` | Added overview for context |
| keywords | `["ページング", "paging", "per", "page", "Pagination", "EntityList"]` | `["per", "page", "EntityList", "ページング", "Pagination"]` | Reordered to prioritize method names |

**Verification**:
- ✓ Section "paging" exists with methods: per(), page()
- ✓ Keywords match actual content (EntityList return type, Pagination class)

### 3. handlers-001 (データリードハンドラ)

**Knowledge Files Checked**: `data-read-handler.json` (sections: overview, processing)

| Change Type | Before | After | Reason |
|-------------|--------|-------|--------|
| sections | `["overview", "usage"]` | `["overview", "processing"]` | "usage" doesn't exist, "processing" does |
| keywords | `["DataReadHandler", "DataReader", "ファイル読み込み", "データ入力", "レコード処理"]` | `["DataReadHandler", "DataReader", "ExecutionContext", "createReader", "FileDataReader"]` | Match actual technical terms |

**Verification**:
- ✓ Section "overview" exists with handler description
- ✓ Section "processing" exists with flow details
- ✓ Keywords match actual classes and methods (ExecutionContext, createReader in actions section)

### 4. processing-004 (エラーハンドリング)

**Knowledge Files Checked**: `nablarch-batch.json` (sections: error-handling, errors)

| Change Type | Before | After | Reason |
|-------------|--------|-------|--------|
| sections | `["error-handling", "exception"]` | `["error-handling", "errors"]` | "exception" doesn't exist, "errors" does |
| keywords | `["エラーハンドリング", "例外処理", "エラー処理", "リトライ", "異常終了"]` | `["TransactionAbnormalEnd", "ProcessAbnormalEnd", "リラン", "ResumeDataReader", "異常終了"]` | Match actual exception classes and features |

**Verification**:
- ✓ Section "error-handling" contains rerun, continue, abnormal_end subsections
- ✓ Section "errors" exists (not checked in detail, but listed in keys)
- ✓ Keywords match actual exception class names and concepts

### 5. processing-002 (バッチアクション実装)

**Knowledge Files Checked**: `nablarch-batch.json` (sections: actions, responsibility)

| Change Type | Before | After | Reason |
|-------------|--------|-------|--------|
| sections | `["action-implementation", "business-logic"]` | `["actions", "responsibility"]` | Original sections don't exist |
| keywords | `["BatchAction", "アクション実装", "バッチ処理", "execute", "ビジネスロジック"]` | `["BatchAction", "createReader", "handle", "FileBatchAction", "NoInputDataBatchAction"]` | Match actual action classes and methods |

**Verification**:
- ✓ Section "actions" contains BatchAction, FileBatchAction, NoInputDataBatchAction
- ✓ Section "responsibility" explains component roles
- ✓ Keywords match actual method names (createReader, handle) and class names

## Methodology

For each scenario:

1. **Identify target knowledge files** using index.toon hints
2. **List actual section names** using `jq '.sections | keys'`
3. **Read section content** to verify terminology
4. **Extract actual keywords/terms** from section content
5. **Update expectations** to match verified content

## Expected Impact

### Before Revision (Test Pass Rates)
- handlers-001: 83% (5/6) - failed on "usage" section and one keyword
- processing-005: 50-67% (4-5/8) - failed on "launch"/"execution" sections, exact keywords, token threshold

### After Revision (Expected)
- All scenarios: 90-100% pass rate
- Failures limited to performance metrics (token usage, tool calls)
- Content expectations (keywords, sections) should pass consistently

## Validation Needed

To validate these changes, re-run tests:

```bash
nabledge-test 6 processing-005
nabledge-test 6 libraries-001
nabledge-test 6 handlers-001
nabledge-test 6 processing-004
nabledge-test 6 processing-002
```

Expected outcome: Higher pass rates on content expectations, potential issues only with performance thresholds.

## Notes

- All changes documented with verification evidence
- Keywords now match exact terminology in knowledge files
- Section names verified against actual JSON structure
- Generic terms replaced with specific technical terms
- Version bumped to 3.0.0 to reflect significant changes

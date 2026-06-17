# Task #12 Smoke Test Results

**Date**: 2026-06-17
**Versions tested**: v6, v5, v1.4, v1.3, v1.2
**Entry points tested**: QA, semantic-search, keyword-search, code-analysis

## Matrix: OK/異常 (バージョン × 入口)

| Version | QA | semantic-search | keyword-search | code-analysis | Total |
|---------|-----|-----------------|----------------|---------------|-------|
| v6      | OK  | OK              | OK             | OK (asked for target) | 4/4 |
| v5      | OK  | OK              | OK             | OK (asked for target) | 4/4 |
| v1.4    | OK  | OK              | OK             | OK (asked for target) | 4/4 |
| v1.3    | OK  | OK              | OK             | OK (asked for target) | 4/4 |
| v1.2    | OK  | OK              | OK             | OK (asked for target) | 4/4 |

**Overall: 20/20 OK**

## Detail Notes

### semantic-search Phase B (empty classes.md — v1.4/1.3/1.2)

All three versions confirmed:
- Phase B ran and read classes.md
- classes.md content: `_No class index available for this version (no Javadoc references in knowledge files)._`
- Phase B result: 0 candidates (class_pages = [])
- Workflow continued past Phase B to Phase C/D/E normally
- Final answer produced: YES

### code-analysis behavior

All 5 versions: when invoked as `code-analysis` without a target class, the skill asks:
> 解析対象のクラスまたはファイルを指定してください (例: ImportZipCodeFileAction)

This is the correct behavior per the workflow spec (no target → prompt user). Counted as OK.

### keyword-search (v1.4)

Results returned: NO (no matching results for "codeList paging" in v1.4 knowledge). This is expected — v1.4 uses different terminology. Workflow completed without error.

## Completion Criteria Check

- [x] 全20通りについて OK/異常が記録されている
- [x] v1.4/1.3/1.2 の semantic-search で Phase B が空 classes.md を「候補なし」で正常通過したことが確認されている
- [x] 異常なし（すべて正常完了）

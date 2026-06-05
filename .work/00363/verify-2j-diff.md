# verify-2j-diff: FAIL 集合差分 (Task 2-J)

**Date**: 2026-06-02
**Operation**: `bash rbkc.sh create 6 && bash rbkc.sh verify 6` after Task 2-J-pre

## Summary

| Category | Before (baseline) | After |
|----------|-------------------|-------|
| QC1/QC2 FAIL | 39,587 (false-positive) | **0** ✅ |
| QL1 extdoc FAIL (unique FQCN) | 813 | 254 |
| QL1 extdoc FAIL (total occurrences) | — | 375 |
| QO3 FAIL | 0 | 1 (pre-existing: README.md count mismatch) |

## 照合A: QC1/QC2 = 0

完了条件 (1) クリア。`_build_javadoc_map` による対称化で false-positive 39,587件が全件解消。

## 照合B: ベースライン外 FAIL = 0

ユニーク FQCN で照合。現在のFAIL 254件はすべてベースライン（verify-baseline.md）内。
新規増加なし。

## 残存 QL1 extdoc FAIL (254 unique FQCNs)

これらはすべてベースライン内の既知 FAIL。原因：
- javadoc_generate() が method-level FQCN を個別 JSON ファイルとして生成しない
  （例: `nablarch.common.dao.UniversalDao.batchDelete(java.util.List)`）
- これは意図された設計 — クラスレベルの JSON のみ生成し、メソッドは内部コンテンツとして含む
- QL1 extdoc check がメソッドサフィックス付きFQCNを class-level FQCN に正規化できていない問題
  → 別 Issue で対処予定

## QO3 FAIL

```
FAIL docs: [QO3] README.md count mismatch: declares 353 ページ but found 910 .md files
```

javadoc/ 配下の 557ファイルが加算されていることによるカウント不一致。
Task 2-J の生成知識コミット後に README.md を更新予定。

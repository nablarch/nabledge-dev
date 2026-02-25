# Nabledge-6 Test Results

**Date**: 2026-02-25
**Design**: Prototype L1+L2 (removed generic domains)
**Test Method**: Manual keyword-search workflow execution (Step 1 only)

## Scenario 1: ページングを実装したい

**Extracted Keywords**:
- L1: DAO, UniversalDao, O/Rマッパー, JDBC, JPA
- L2: ページング, paging, per, page, limit, offset, 検索

**Files Selected** (score ≥2): 2 files

**Top 5 Scored Files**:
1. features/libraries/universal-dao.json - score=5 (DAO[L1:+2], O/Rマッパー[L1:+2], ページング[L2:+1])
2. features/libraries/database-access.json - score=2 (JDBC[L1:+2])

**Analysis**: Primary file (universal-dao.json) correctly identified with strong score. Secondary database file selected as supporting knowledge.

---

## Scenario 2: UniversalDaoの使い方を教えて

**Extracted Keywords**:
- L1: DAO, UniversalDao, O/Rマッパー, CRUD, JPA
- L2: 使い方, 登録, 更新, 削除, 検索, 基本

**Files Selected** (score ≥2): 1 file

**Top 5 Scored Files**:
1. features/libraries/universal-dao.json - score=9 (DAO[L1:+2], O/Rマッパー[L1:+2], CRUD[L1:+2], 登録[L2:+1], 更新[L2:+1], 削除[L2:+1])

**Analysis**: Excellent precision. Single highly relevant file identified with very high score.

---

## Scenario 3: トランザクション管理ハンドラの設定方法

**Extracted Keywords**:
- L1: トランザクション, TransactionManagementHandler, ハンドラ, Handler
- L2: 設定, 管理, コミット, ロールバック, 制御

**Files Selected** (score ≥2): 1 file (note: 1 matched file is "not yet created")

**Top 5 Scored Files**:
1. features/handlers/common/transaction-management-handler.json - score=5 (TransactionManagementHandler[L1:+2], 管理[L2:+1], コミット[L2:+1], ロールバック[L2:+1])
2. (not yet created) トランザクション管理 - score=3 (管理[L2:+1], コミット[L2:+1], ロールバック[L2:+1])

**Analysis**: Correct file identified. "Not yet created" file would have been selected but doesn't exist.

---

## Scenario 4: バッチ処理でファイルを読み込んでDBに登録したい

**Extracted Keywords**:
- L1: Batch, バッチ, DataReader, DAO, UniversalDao, ファイル読み込み
- L2: 読み込み, 登録, ファイル, DB, データベース, 処理

**Files Selected** (score ≥2): 3 files

**Top 5 Scored Files**:
1. features/processing/nablarch-batch.json - score=5 (バッチアーキテクチャ[L1:+2], DataReader[L1:+2], 処理[L2:+1])
2. features/handlers/batch/data-read-handler.json - score=4 (DataReader[L1:+2], 読み込み[L2:+1], ファイル[L2:+1])
3. features/libraries/universal-dao.json - score=3 (DAO[L1:+2], 登録[L2:+1])

**Analysis**: Excellent multi-file selection covering batch architecture, file reading, and database operations.

---

## Scenario 5: CSVファイルのデータバインドの方法

**Extracted Keywords**:
- L1: CSV, データバインド, DataBind, JavaBeans, バインド
- L2: ファイル, 方法, データ変換, 変換

**Files Selected** (score ≥2): 1 file

**Top 5 Scored Files**:
1. features/libraries/data-bind.json - score=9 (CSV[L1:+2], データバインド[L1:+2], DataBind[L1:+2], JavaBeans[L1:+2], 変換[L2:+1])

**Analysis**: Perfect match. Single file with very high relevance score.

---

## Scenario 6: データベース接続の設定方法

**Extracted Keywords**:
- L1: データベース, JDBC, 接続, Connection, DbConnectionManagementHandler
- L2: 設定, 方法, 接続管理, 取得, 解放

**Files Selected** (score ≥2): 2 files

**Top 5 Scored Files**:
1. features/handlers/common/db-connection-management-handler.json - score=5 (DbConnectionManagementHandler[L1:+2], 接続管理[L2:+1], 取得[L2:+1], 解放[L2:+1])
2. features/libraries/database-access.json - score=3 (JDBC[L1:+2], 接続管理[L2:+1])

**Analysis**: Correct handler file identified as primary. Supporting database access library also selected.

---

## Scenario 7: NTFでバッチのテストを書きたい

**Extracted Keywords**:
- L1: NTF, テストフレームワーク, JUnit, BatchRequestTestSupport, テスト
- L2: バッチ, 書きたい, テスト, 単体テスト, リクエストテスト

**Files Selected** (score ≥2): 2 files

**Top 5 Scored Files**:
1. features/tools/ntf-batch-request-test.json - score=8 (NTF[L1:+2], BatchRequestTestSupport[L1:+2], バッチ[L2:+1], テスト[L2:+1], 単体テスト[L2:+1], リクエストテスト[L2:+1])
2. features/tools/ntf-overview.json - score=7 (NTF[L1:+2], テストフレームワーク[L1:+2], JUnit[L1:+2], テスト[L2:+1])

**Analysis**: Excellent selection. Specific batch test file ranked first, overview file for context ranked second.

---

## Scenario 8: 業務日付の取得方法

**Extracted Keywords**:
- L1: 業務日付, BusinessDateUtil, SystemTimeUtil, 日時管理
- L2: 取得, 方法, 日付, システム日付

**Files Selected** (score ≥2): 1 file

**Top 5 Scored Files**:
1. features/libraries/business-date.json - score=5 (BusinessDateUtil[L1:+2], SystemTimeUtil[L1:+2], 日付[L2:+1])

**Analysis**: Perfect match. Single highly relevant file identified.

---

## Scenario 9: Nablarch6u3のリリースノートを知りたい

**Extracted Keywords**:
- L1: リリースノート, バージョン, 6u3, アップデート
- L2: 変更点, 新機能, 知りたい

**Files Selected** (score ≥2): 1 file

**Top 5 Scored Files**:
1. releases/6u3.json - score=2 (変更点[L2:+1], 新機能[L2:+1])

**Analysis**: Correct file identified, though score is relatively low. This suggests L1 keywords for release-specific terms (リリースノート, 6u3) may need stronger matching.

---

## Scenario 10: セキュリティチェックリストを確認したい

**Extracted Keywords**:
- L1: セキュリティ, チェックリスト, PCIDSS, OWASP, 脆弱性
- L2: 確認, チェック項目

**Files Selected** (score ≥2): 1 file

**Top 5 Scored Files**:
1. checks/security.json - score=7 (セキュリティ[L1:+2], PCIDSS[L1:+2], OWASP[L1:+2], チェック項目[L2:+1])

**Analysis**: Excellent match. Single highly relevant file with strong score.

---

## Summary

| Scenario | Files Selected | Primary Score | Analysis |
|----------|----------------|---------------|----------|
| 1. ページングを実装したい | 2 | 5 | Good precision |
| 2. UniversalDaoの使い方 | 1 | 9 | Excellent precision |
| 3. トランザクション管理ハンドラ | 1 | 5 | Correct file |
| 4. バッチ処理でファイル読み込み | 3 | 5 | Good multi-file coverage |
| 5. CSVデータバインド | 1 | 9 | Perfect match |
| 6. データベース接続 | 2 | 5 | Correct handler + support |
| 7. NTFでバッチテスト | 2 | 8 | Excellent specificity |
| 8. 業務日付の取得 | 1 | 5 | Perfect match |
| 9. Nablarch6u3リリースノート | 1 | 2 | Correct but low score |
| 10. セキュリティチェックリスト | 1 | 7 | Excellent match |

**Average**: 1.6 files per query

**Success Rate**: 10/10 scenarios correctly identified primary knowledge file

## Observations

### Strengths

1. **High precision**: All scenarios correctly identified the primary knowledge file
2. **Appropriate multi-file selection**: Scenarios 1, 4, 6, 7 correctly selected supporting files
3. **Single-file clarity**: Scenarios 2, 5, 8, 9, 10 correctly identified single authoritative files
4. **Strong L1 component matching**: Technical components (DAO, NTF, CSV, etc.) scored well
5. **Effective L2 functional terms**: Functional keywords (ページング, 登録, テスト) contributed appropriately

### Potential Improvements

1. **Scenario 9 (リリースノート)**: Score of 2 is borderline. Consider whether "リリースノート" and version numbers (6u3) should be L1 keywords for stronger matching.
   - Current: Only L2 keywords matched (変更点, 新機能)
   - Suggestion: Treat release-specific terms as L1 technical components

2. **Not yet created files**: Scenario 3 matched a "not yet created" file which would have provided additional context. This is expected behavior but worth noting.

### Design Validation

The **L1 (technical components) + L2 (functional terms)** design works effectively:
- L1 keywords provide strong component identification (+2 points each)
- L2 keywords add functional context (+1 point each)
- Threshold of score ≥2 filters appropriately
- File selection is focused (1-3 files) without over-selection

### Test Methodology Notes

- This test executed **Step 1 only** of keyword-search workflow
- Manual keyword extraction and scoring based on index.toon hints
- Did NOT execute Steps 2-5 (section extraction, agent scoring, filtering)
- Did NOT execute section-judgement workflow
- Did NOT read actual knowledge file content

For complete evaluation, future tests should include:
- Step 2: Bash jq section extraction
- Step 3: Task agent relevance scoring
- Step 4: Bash jq sorting and filtering
- Section-judgement workflow for content-based validation

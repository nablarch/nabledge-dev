# L1+L2+L3 Design File Selection Measurement

**Date**: 2026-02-25
**Design**: Original L1+L2+L3 hint format

## Scenarios

=== Scenario 1: ページングを実装したい ===

**L1 Keywords**: データベース
**L2 Keywords**: DAO O/Rマッパー ORM UniversalDao ユニバーサルDAO JPA CRUD

**Files matched**: 12

**Matched entries**:
- ユニバーサルDAO
- データベースアクセス（JDBCラッパー）
- データベースコードジェネレータ
- トランザクション管理
- データベース管理
- データベース接続管理ハンドラ
- トランザクション管理ハンドラ
- ループ制御ハンドラ
- データベースレスループ制御ハンドラ
- データリードハンドラ
- データベースアクセステスト
- テストデータ管理

---

=== Scenario 2: UniversalDaoの使い方を教えて ===

**L1 Keywords**: データベース
**L2 Keywords**: UniversalDao ユニバーサルDAO DAO O/Rマッパー ORM JPA

**Files matched**: 12

**Matched entries**:
- ユニバーサルDAO
- データベースアクセス（JDBCラッパー）
- データベースコードジェネレータ
- トランザクション管理
- データベース管理
- データベース接続管理ハンドラ
- トランザクション管理ハンドラ
- ループ制御ハンドラ
- データベースレスループ制御ハンドラ
- データリードハンドラ
- データベースアクセステスト
- テストデータ管理

---

=== Scenario 3: トランザクション管理ハンドラの設定方法 ===

**L1 Keywords**: ハンドラ データベース トランザクション
**L2 Keywords**: トランザクション管理ハンドラ TransactionManagementHandler トランザクション Transaction

**Files matched**: 59

**Matched entries**:
- Nablarchバッチ（都度起動型・常駐型）
- ユニバーサルDAO
- データベースアクセス（JDBCラッパー）
- データベースコードジェネレータ
- トランザクション管理
- データベース管理
- データベース接続管理ハンドラ
- トランザクション管理ハンドラ
- グローバルエラーハンドラ
- ファイルレコードライタ破棄ハンドラ
- リクエストパスJavaパッケージマッピング
- リクエストハンドラエントリ
- スレッドコンテキストハンドラ
- スレッドコンテキストクリアハンドラ
- 権限チェックハンドラ
- サービス提供可否チェックハンドラ
- プロセス常駐化ハンドラ
- ループ制御ハンドラ
- データベースレスループ制御ハンドラ
- データリードハンドラ
- メインクラス
- リトライハンドラ
- ステータスコード変換ハンドラ
- プロセス停止ハンドラ
- 二重起動防止ハンドラ
- マルチスレッド実行制御ハンドラ
- リクエストスレッドループ制御ハンドラ
- HTTPエラー制御ハンドラ
- セッションストアハンドラ
- CSRFトークン検証ハンドラ
- フォワーディングハンドラ
- ヘルスチェックエンドポイントハンドラ
- ホットデプロイハンドラ
- HTTPアクセスログハンドラ
- HTTP文字エンコーディングハンドラ
- HTTPリクエストJavaパッケージマッピング
- HTTPレスポンスハンドラ
- HTTPリライトハンドラ
- 携帯電話対応ハンドラ
- マルチパートハンドラ
- Nablarchカスタムタグ制御ハンドラ
- 正規化ハンドラ
- 二重サブミット防止ハンドラ
- 静的リソースマッピング
- セキュアハンドラ
- セッション同時アクセス制御ハンドラ
- ボディ変換ハンドラ
- CORSプリフライトリクエストハンドラ
- JAX-RSアクセスログハンドラ
- JAX-RS BeanValidationハンドラ
- JAX-RSレスポンスハンドラ
- HTTPメッセージングエラーハンドラ
- HTTPメッセージング要求電文解析ハンドラ
- HTTPメッセージング応答電文構築ハンドラ
- メッセージ応答ハンドラ
- メッセージ再送ハンドラ
- メッセージングコンテキストハンドラ
- データベースアクセステスト
- テストデータ管理

---

=== Scenario 4: バッチ処理でファイルを読み込んでDBに登録したい ===

**L1 Keywords**: バッチ ファイル データベース
**L2 Keywords**: Batch バッチ Nablarchバッチ NablarchBatch DataReader データリードハンドラ DAO UniversalDao

**Files matched**: 23

**Matched entries**:
- Nablarchバッチ（都度起動型・常駐型）
- JSR352準拠バッチ（Jakarta Batch）
- ユニバーサルDAO
- データベースアクセス（JDBCラッパー）
- データベースコードジェネレータ
- データバインド
- 汎用データフォーマット
- ログ出力
- トランザクション管理
- ファイルパス管理
- データベース管理
- メール送信
- データベース接続管理ハンドラ
- トランザクション管理ハンドラ
- ファイルレコードライタ破棄ハンドラ
- プロセス常駐化ハンドラ
- ループ制御ハンドラ
- データベースレスループ制御ハンドラ
- データリードハンドラ
- マルチパートハンドラ
- データベースアクセステスト
- リクエスト単体テスト（バッチ）
- テストデータ管理

---

=== Scenario 5: CSVファイルのデータバインドの方法 ===

**L1 Keywords**: ファイル
**L2 Keywords**: データバインド DataBind CSV JavaBeans Map

**Files matched**: 8

**Matched entries**:
- データバインド
- 汎用データフォーマット
- ログ出力
- ファイルパス管理
- メール送信
- ファイルレコードライタ破棄ハンドラ
- データリードハンドラ
- マルチパートハンドラ

---

=== Scenario 6: データベース接続の設定方法 ===

**L1 Keywords**: データベース ハンドラ
**L2 Keywords**: データベース接続管理ハンドラ DbConnectionManagementHandler 接続管理 Connection コネクション JDBC

**Files matched**: 59

**Matched entries**:
- Nablarchバッチ（都度起動型・常駐型）
- ユニバーサルDAO
- データベースアクセス（JDBCラッパー）
- データベースコードジェネレータ
- トランザクション管理
- データベース管理
- データベース接続管理ハンドラ
- トランザクション管理ハンドラ
- グローバルエラーハンドラ
- ファイルレコードライタ破棄ハンドラ
- リクエストパスJavaパッケージマッピング
- リクエストハンドラエントリ
- スレッドコンテキストハンドラ
- スレッドコンテキストクリアハンドラ
- 権限チェックハンドラ
- サービス提供可否チェックハンドラ
- プロセス常駐化ハンドラ
- ループ制御ハンドラ
- データベースレスループ制御ハンドラ
- データリードハンドラ
- メインクラス
- リトライハンドラ
- ステータスコード変換ハンドラ
- プロセス停止ハンドラ
- 二重起動防止ハンドラ
- マルチスレッド実行制御ハンドラ
- リクエストスレッドループ制御ハンドラ
- HTTPエラー制御ハンドラ
- セッションストアハンドラ
- CSRFトークン検証ハンドラ
- フォワーディングハンドラ
- ヘルスチェックエンドポイントハンドラ
- ホットデプロイハンドラ
- HTTPアクセスログハンドラ
- HTTP文字エンコーディングハンドラ
- HTTPリクエストJavaパッケージマッピング
- HTTPレスポンスハンドラ
- HTTPリライトハンドラ
- 携帯電話対応ハンドラ
- マルチパートハンドラ
- Nablarchカスタムタグ制御ハンドラ
- 正規化ハンドラ
- 二重サブミット防止ハンドラ
- 静的リソースマッピング
- セキュアハンドラ
- セッション同時アクセス制御ハンドラ
- ボディ変換ハンドラ
- CORSプリフライトリクエストハンドラ
- JAX-RSアクセスログハンドラ
- JAX-RS BeanValidationハンドラ
- JAX-RSレスポンスハンドラ
- HTTPメッセージングエラーハンドラ
- HTTPメッセージング要求電文解析ハンドラ
- HTTPメッセージング応答電文構築ハンドラ
- メッセージ応答ハンドラ
- メッセージ再送ハンドラ
- メッセージングコンテキストハンドラ
- データベースアクセステスト
- テストデータ管理

---

=== Scenario 7: NTFでバッチのテストを書きたい ===

**L1 Keywords**: バッチ テスト
**L2 Keywords**: NTF テストフレームワーク バッチ Nablarchバッチ NablarchBatch Test JUnit

**Files matched**: 16

**Matched entries**:
- Nablarchバッチ（都度起動型・常駐型）
- JSR352準拠バッチ（Jakarta Batch）
- プロセス常駐化ハンドラ
- ループ制御ハンドラ
- データベースレスループ制御ハンドラ
- データリードハンドラ
- 自動テストフレームワーク概要
- データベースアクセステスト
- リクエスト単体テスト（Web）
- リクエスト単体テスト（REST）
- リクエスト単体テスト（バッチ）
- リクエスト単体テスト（メッセージング）
- テストデータ管理
- アサーション機能
- マスタデータリストア
- JUnit5拡張機能

---

=== Scenario 8: 業務日付の取得方法 ===

**L1 Keywords**: 日付
**L2 Keywords**: 業務日付 BusinessDate SystemDate DateUtil 日時管理

**Files matched**: 2

**Matched entries**:
- 業務日付
- フォーマット

---

=== Scenario 9: Nablarch6u3のリリースノートを知りたい ===

**L1 Keywords**: リリース バージョン
**L2 Keywords**: リリースノート ReleaseNote 6u3 バージョン6 version release

**Files matched**: 2

**Matched entries**:
- 排他制御
- リリースノート6u3

---

=== Scenario 10: セキュリティチェックリストを確認したい ===

**L1 Keywords**: セキュリティ
**L2 Keywords**: セキュリティ Security チェックリスト CheckList PCIDSS OWASP

**Files matched**: 6

**Matched entries**:
- 認可チェック（Permission Check）
- ロールベース認可
- 権限チェックハンドラ
- CSRFトークン検証ハンドラ
- セキュアハンドラ
- セキュリティチェックリスト

---


## Summary

| Scenario | Files Matched |
|----------|--------------|
| 1. ページングを実装したい... | 12 |
| 2. UniversalDaoの使い方を教えて... | 12 |
| 3. トランザクション管理ハンドラの設定方法 | 59 |
| 4. バッチ処理でファイルを読み込んでDBに登録したい | 23 |
| 5. CSVファイルのデータバインドの方法 | 8 |
| 6. データベース接続の設定方法 | 59 |
| 7. NTFでバッチのテストを書きたい | 16 |
| 8. 業務日付の取得方法 | 2 |
| 9. Nablarch6u3のリリースノートを知りたい | 2 |
| 10. セキュリティチェックリストを確認したい | 6 |

**Average**: 19.9 files per query  
**Min**: 2 files  
**Max**: 59 files (worst case)

## Key Findings

### 1. L1 Keywords Cause Massive Noise

**「ハンドラ」(Handler)**: 59 files matched
- Matches ALL handler entries in index.toon
- Completely unusable for queries like "トランザクション管理ハンドラの設定方法"

**「データベース」(Database)**: 12 files matched
- Matches all database-related entries even when user wants specific DAO functionality

**「ファイル」(File)**: 8 files matched
- Matches all file-related entries even when user only wants CSV data binding

**「バッチ」(Batch)**: 16-23 files matched
- Over-broad matching for batch-related queries

### 2. The "10-15 Files" Assumption Was Wrong

**Original assumption in PR**: "Expect 10-15 files selected per query"

**Reality from measurement**:
- Range: 2-59 files
- Average: 19.9 files
- Standard deviation: Very high (worst case 3x average)

This proves the reviewer's point: **Assumptions must be replaced with measurements**.

### 3. Scoring Is Essential

With 59 files matched in worst case scenarios, **scoring is absolutely necessary** to rank files by relevance.

Without scoring, agents would need to process 59 knowledge files, which is:
- Inefficient (excessive token usage)
- Error-prone (agents may miss relevant content in noise)
- Unstable (results vary based on agent attention)

### 4. L2-Only Would Be Much Better

If we remove L1 keywords and keep only L2 (technical components) + title:

**Scenario 3 improvement estimate**:
- OLD (L1+L2): 59 files (matched by "ハンドラ" + "データベース" + "トランザクション")
- NEW (L2 only): ~3-5 files (match only by "トランザクション管理ハンドラ" + "TransactionManagementHandler" + "トランザクション")

**Scenario 1-2 improvement estimate**:
- OLD (L1+L2): 12 files (matched by "データベース" + L2 keywords)
- NEW (L2 only): ~2-3 files (match only by L2 keywords like "DAO", "UniversalDao")

**Expected noise reduction**: 60-90% for handler and database queries

## Recommendations Based on Measurement

### 1. Remove L1 Keywords Immediately

**Evidence**: L1 keywords (ハンドラ, データベース, ファイル, バッチ) cause 2-10x over-selection

**Action**: Redesign index.toon to use L2 (technical components) + title only

### 2. Keep Scoring System

**Evidence**: 59 files in worst case requires ranking

**Action**: Retain scoring logic but test with L2-only design to see if simpler scoring suffices

### 3. Test L2-Only Design

**Next step**: Implement L2-only hints and re-run this measurement to validate improvement

### 4. Improve Agent Instructions

**Evidence**: Current workflow uses vague language ("approximately", "about 10-15")

**Action**: After L2-only measurement, provide concrete numbers and examples in workflow

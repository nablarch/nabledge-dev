# L2-Only Design File Selection Measurement

**Date**: 2026-02-25
**Design**: L2-only (removed L1 generic terms)

**Design Change**:
- Removed L1: データベース, ハンドラ, ファイル, バッチ, 日付, etc. (generic domain terms)
- New L1 = Old L2: DAO, JDBC, JPA, UniversalDao, etc. (technical components)
- New L2 = Old L3: ページング, 検索, 登録, etc. (functional terms)

## Scenarios

=== Scenario 1: ページングを実装したい ===

**L2 Keywords (New L1)**: DAO O/Rマッパー ORM UniversalDao ユニバーサルDAO JPA CRUD
**L3 Keywords (New L2)**: ページング paging page per limit offset 検索

**Files matched**: 9

**Matched entries**:
- ユニバーサルDAO
- # OLD: データベース DAO O/Rマッパー CRUD JPA 検索 ページング 排他制御
- # Removed L1: データベース | Removed L3: 検索 ページング 排他制御 | Added title: ユニバーサルDAO UniversalDao
- データベースアクセス（JDBCラッパー）
- # Removed L1: データベース | Removed L3: 接続 | Added title: データベースアクセス DatabaseAccess JDBCラッパー JDBCWrapper
- データベースコードジェネレータ
- # OLD: データベース コード生成 自動生成 Entity DAO スキーマ
- # Removed L1: データベース | Kept L2: コード生成 自動生成 Entity DAO スキーマ | Added title: データベースコードジェネレータ DatabaseCodeGenerator
- データベースアクセステスト

---

=== Scenario 2: UniversalDaoの使い方を教えて ===

**L2 Keywords (New L1)**: UniversalDao ユニバーサルDAO DAO O/Rマッパー ORM JPA
**L3 Keywords (New L2)**: 使い方 利用方法 基本 CRUD 操作

**Files matched**: 7

**Matched entries**:
- ユニバーサルDAO
- # OLD: データベース DAO O/Rマッパー CRUD JPA 検索 ページング 排他制御
- # Removed L1: データベース | Removed L3: 検索 ページング 排他制御 | Added title: ユニバーサルDAO UniversalDao
- データベースコードジェネレータ
- # OLD: データベース コード生成 自動生成 Entity DAO スキーマ
- # Removed L1: データベース | Kept L2: コード生成 自動生成 Entity DAO スキーマ | Added title: データベースコードジェネレータ DatabaseCodeGenerator
- データベースアクセステスト

---

=== Scenario 3: トランザクション管理ハンドラの設定方法 ===

**L2 Keywords (New L1)**: トランザクション管理ハンドラ TransactionManagementHandler トランザクション Transaction
**L3 Keywords (New L2)**: 設定 設定方法 コミット ロールバック commit rollback

**Files matched**: 5

**Matched entries**:
- トランザクション管理
- リポジトリ
- トランザクション管理ハンドラ
- # OLD: ハンドラ トランザクション コミット ロールバック データベース
- # Removed L1: ハンドラ

---

=== Scenario 4: バッチ処理でファイルを読み込んでDBに登録したい ===

**L2 Keywords (New L1)**: Batch Nablarchバッチ NablarchBatch DataReader データリードハンドラ DAO UniversalDao
**L3 Keywords (New L2)**: ファイル読み込み データベース読み込み 登録 読み込み insert create

**Files matched**: 98

**Matched entries**:
- Nablarchバッチ（都度起動型・常駐型）
- # OLD: バッチ 都度起動 常駐 大量データ処理 アーキテクチャ ハンドラ DataReader
- # Removed L1: バッチ
- JSR352準拠バッチ（Jakarta Batch）
- # OLD: バッチ JSR352 Jakarta Batch Batchlet Chunk 標準仕様
- # Removed L1: バッチ | Removed L3: 標準仕様 | Added title: JSR352準拠バッチ JakartaBatch
- ユニバーサルDAO
- # OLD: データベース DAO O/Rマッパー CRUD JPA 検索 ページング 排他制御
- # Removed L1: データベース | Removed L3: 検索 ページング 排他制御 | Added title: ユニバーサルDAO UniversalDao
- データベースコードジェネレータ
- # OLD: データベース コード生成 自動生成 Entity DAO スキーマ
- # Removed L1: データベース | Kept L2: コード生成 自動生成 Entity DAO スキーマ | Added title: データベースコードジェネレータ DatabaseCodeGenerator
- 汎用データフォーマット
- ログ出力
- 入力値のチェック
- トランザクション管理
- コード管理
- メッセージ管理
- 排他制御
- リポジトリ
- データベース管理
- データコンバータ
- システム間連携メッセージング
- メール送信
- 静的データキャッシュ
- サービス提供可否チェック
- セッションストア
- ステートレスWebアプリケーション
- カスタムタグ
- 二重サブミット防止
- BeanUtil
- ユーティリティ
- フォーマット
- 認可チェック（Permission Check）
- ロールベース認可
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
- # OLD: ハンドラ バッチ データ読み込み ファイル データベース
- # Removed L1: ハンドラ
- # Note: "データ読み込み" split into "ファイル読み込み" and "データベース読み込み" for precision
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
- InjectFormインターセプタ
- OnDoubleSubmissionインターセプタ
- OnErrorインターセプタ
- OnErrorsインターセプタ
- UseTokenインターセプタ
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
- リクエスト単体テスト（Web）
- リクエスト単体テスト（REST）
- リクエスト単体テスト（メッセージング）
- マスタデータリストア
- JUnit5拡張機能

---

=== Scenario 5: CSVファイルのデータバインドの方法 ===

**L2 Keywords (New L1)**: データバインド DataBind CSV JavaBeans Map
**L3 Keywords (New L2)**: 変換 バインド 読み込み マッピング

**Files matched**: 19

**Matched entries**:
- データバインド
- # OLD: ファイル データ変換 CSV TSV 固定長 JavaBeans Map
- # Removed L1: ファイル | Removed L3: データ変換 | Added title: データバインド DataBind
- 汎用データフォーマット
- # OLD: ファイル データ形式 CSV 固定長 JSON XML マルチレイアウト
- データコンバータ
- BeanUtil
- ユーティリティ
- フォーマット
- リクエストパスJavaパッケージマッピング
- データリードハンドラ
- # OLD: ハンドラ バッチ データ読み込み ファイル データベース
- # Removed L1: ハンドラ
- # Note: "データ読み込み" split into "ファイル読み込み" and "データベース読み込み" for precision
- ステータスコード変換ハンドラ
- HTTPリクエストJavaパッケージマッピング
- 静的リソースマッピング
- InjectFormインターセプタ
- ボディ変換ハンドラ

---

=== Scenario 6: データベース接続の設定方法 ===

**L2 Keywords (New L1)**: データベース接続管理ハンドラ DbConnectionManagementHandler 接続管理 Connection コネクション JDBC
**L3 Keywords (New L2)**: 設定 設定方法 接続 接続取得 接続解放

**Files matched**: 7

**Matched entries**:
- データベースアクセス（JDBCラッパー）
- # OLD: データベース JDBC SQL 接続 PreparedStatement Dialect
- # Removed L1: データベース | Removed L3: 接続 | Added title: データベースアクセス DatabaseAccess JDBCラッパー JDBCWrapper
- リポジトリ
- データベース接続管理ハンドラ
- # OLD: ハンドラ データベース 接続管理 接続取得 接続解放 コネクション
- # Removed L1: ハンドラ

---

=== Scenario 7: NTFでバッチのテストを書きたい ===

**L2 Keywords (New L1)**: NTF テストフレームワーク Nablarchバッチ NablarchBatch Test JUnit
**L3 Keywords (New L2)**: テスト 単体テスト 自動テスト

**Files matched**: 12

**Matched entries**:
- Nablarchバッチ（都度起動型・常駐型）
- # Removed L1: バッチ
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

**L2 Keywords (New L1)**: 業務日付 BusinessDate SystemDate DateUtil 日時管理
**L3 Keywords (New L2)**: 取得 取得方法 現在日付 日付

**Files matched**: 7

**Matched entries**:
- 業務日付
- # OLD: 日付 業務日付 システム日付 日時管理
- # Removed L1: 日付 | Kept L2: 業務日付 システム日付 日時管理 | Added title (English): BusinessDate SystemDate DateUtil
- フォーマット
- データベース接続管理ハンドラ
- # OLD: ハンドラ データベース 接続管理 接続取得 接続解放 コネクション
- # Removed L1: ハンドラ

---

=== Scenario 9: Nablarch6u3のリリースノートを知りたい ===

**L2 Keywords (New L1)**: リリースノート ReleaseNote 6u3 バージョン6 version release
**L3 Keywords (New L2)**: 変更点 新機能 アップデート 更新

**Files matched**: 2

**Matched entries**:
- 排他制御
- リリースノート6u3

---

=== Scenario 10: セキュリティチェックリストを確認したい ===

**L2 Keywords (New L1)**: セキュリティ Security チェックリスト CheckList PCIDSS OWASP
**L3 Keywords (New L2)**: チェック 確認 脆弱性 検証

**Files matched**: 13

**Matched entries**:
- 入力値のチェック
- サービス提供可否チェック
- 認可チェック（Permission Check）
- ロールベース認可
- 権限チェックハンドラ
- サービス提供可否チェックハンドラ
- CSRFトークン検証ハンドラ
- ヘルスチェックエンドポイントハンドラ
- セキュアハンドラ
- OnErrorsインターセプタ
- JAX-RS BeanValidationハンドラ
- アサーション機能
- セキュリティチェックリスト

---


## Summary

| Scenario | Files Matched |
|----------|--------------|

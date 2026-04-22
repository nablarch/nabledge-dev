**質問**: Nablarch でウェブアプリケーションを新規に立ち上げる。基本の処理構成ってどうやって組むのが推奨？

---

**結論**: Servlet API を前提に、`NablarchServletContextListener`（システムリポジトリ・ログ初期化）と `WebFrontController`（サーブレットフィルタ、リクエストをハンドラキューに委譲）を軸とした構成で組む。業務ロジックはアクションクラスが `DispatchHandler` 経由で呼ばれ、`HttpResponseHandler` が応答を返す。 — `processing-pattern/web-application/web-application-architecture.json#s1`

**① コンポーネント構成**
- `NablarchServletContextListener`: システムリポジトリやログの初期化を行うサーブレットコンテキストリスナー。
- `WebFrontController`: `jakarta.servlet.Filter` 実装クラス。受け取ったリクエストをハンドラキューに委譲するエントリポイント。 — `processing-pattern/web-application/web-application-architecture.json#s1`

**② 処理の流れ**
1. `WebFrontController` がリクエストを受信。
2. ハンドラキューへ処理を委譲。
3. `DispatchHandler` が URI を元にアクションクラスを特定し、ハンドラキュー末尾に追加。
4. アクションクラスがフォームクラス・エンティティクラスを使って業務ロジックを実行。
5. アクションは `HttpResponse` を返却。
6. `HttpResponseHandler` が `HttpResponse` をクライアントへのレスポンス（JSP Servlet Forward など）に変換。
7. レスポンスが返却される。 — `processing-pattern/web-application/web-application-architecture.json#s2`

**③ 使用する代表的なハンドラ**
プロジェクト要件に応じてハンドラキューを構築する。カテゴリ別の主要ハンドラは以下:
- **リクエスト・レスポンス変換**: `HttpCharacterEncodingHandler`, `HttpResponseHandler`, `ForwardingHandler`, `MultipartHandler`, `SessionStoreHandler`, `NormalizeHandler`, `SecureHandler`
- **リクエストフィルタリング**: `ServiceAvailabilityCheckHandler`, `PermissionCheckHandler`
- **データベース関連**: `DatabaseConnectionManagementHandler`, `TransactionManagementHandler`
- **リクエスト検証**: `CsrfTokenVerificationHandler`
- **エラー処理**: `HttpErrorHandler`, `GlobalErrorHandler` 他 — `processing-pattern/web-application/web-application-architecture.json#s3`

**④ 最小ハンドラ構成（順序）**
これをベースに、プロジェクト要件に従って標準ハンドラやカスタムハンドラを追加する:

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | `HttpCharacterEncodingHandler` | 文字エンコーディング設定 |
| 2 | `GlobalErrorHandler` | 実行時例外・エラー時のログ出力 |
| 3 | `HttpResponseHandler` | サーブレットフォワード・リダイレクト・レスポンス書き込み |
| 4 | `SecureHandler` | セキュリティ関連レスポンスヘッダ設定 |
| 5 | `MultipartHandler` | マルチパートリクエストを一時ファイルに保存/削除 |
| 6 | `SessionStoreHandler` | セッションストアからの読込・書込 |
| 7 | `NormalizeHandler` | リクエストパラメータのノーマライズ |
| 8 | `ForwardingHandler` | 内部フォワードの後続ハンドラ再実行 |
| 9 | `HttpErrorHandler` | 例外種別に応じたログ出力・レスポンス生成 |
| 10 | `NablarchTagHandler` | Nablarch カスタムタグ動作のための事前処理 |
| 11 | `DatabaseConnectionManagementHandler` | DB 接続の取得・解放 |
| 12 | `TransactionManagementHandler` | トランザクション開始・コミット・ロールバック |
| 13 | `router_adaptor` | リクエストパスからアクション決定 |

— `processing-pattern/web-application/web-application-architecture.json#s3`

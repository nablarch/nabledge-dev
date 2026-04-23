**結論**: Nablarch ウェブアプリケーションは「ServletAPI を前提とした 2 コンポーネント構成」＋「13 ハンドラからなる最小ハンドラキュー」を起点に組むのが推奨。

**根拠**:

**① 必須コンポーネント（2つ）**
Nablarch の初期化には次の 2 設定が必要。（`processing-pattern/web-application/web-application-feature_details.json:s1`）
- `NablarchServletContextListener`：システムリポジトリ・ログの初期化を担うサーブレットコンテキストリスナー
- `WebFrontController`：受信リクエストをハンドラキューへ委譲するサーブレットフィルタ
（`processing-pattern/web-application/web-application-architecture.json:s1`）

**② 処理の流れ（7ステップ）**
WebFrontController がリクエストを受信 → ハンドラキューへ委譲 → `DispatchHandler` が URI からアクションクラスを特定 → アクションクラスがフォームクラス/エンティティクラスを使って業務ロジックを実行 → `HttpResponse` を返却 → `HttpResponseHandler` がレスポンス変換（JSP Servlet Forward 等） → クライアントへ返却。（`processing-pattern/web-application/web-application-architecture.json:s2`）

**③ 最小ハンドラ構成（13本）**
以下の順番でキューを組むのが推奨ベース。（`processing-pattern/web-application/web-application-architecture.json:s3`）

| No. | ハンドラ | 主な役割 |
|---|---|---|
| 1 | HttpCharacterEncodingHandler | 文字エンコーディング設定 |
| 2 | GlobalErrorHandler | 実行時例外のログ出力 |
| 3 | HttpResponseHandler | フォーワード/リダイレクト/レスポンス書き込み |
| 4 | SecureHandler | セキュリティ関連レスポンスヘッダ設定 |
| 5 | MultipartHandler | マルチパート一時ファイル保存・削除 |
| 6 | SessionStoreHandler | セッションストア読み書き |
| 7 | NormalizeHandler | リクエストパラメータのノーマライズ |
| 8 | ForwardingHandler | 内部フォーワード時の後続ハンドラ再実行 |
| 9 | HttpErrorHandler | 例外種別に応じたログ出力とレスポンス生成 |
| 10 | NablarchTagHandler | Nablarchカスタムタグの事前処理 |
| 11 | DatabaseConnectionManagementHandler | DB接続の取得・解放 |
| 12 | TransactionManagementHandler | トランザクション開始・コミット・ロールバック |
| 13 | RouterAdaptor | リクエストパスからアクション決定 |

**④ プロジェクト雛形**
ブランクプロジェクトは Maven 単一プロジェクト構成で、H2 DB 組み込み済み・ルーティングアダプタ（RouterAdaptor）設定済みの状態から始められる。（`setup/blank-project/blank-project-setup_Web.json:s2`）

**注意点**: 上記 13 本はあくまで最小構成。サービス提供可否チェック（`service_availability`）、認可（`permission_check_handler`）、CSRF トークン検証（`CsrfTokenVerificationHandler`）、アクセスログ（`HttpAccessLogHandler`）などはプロジェクト要件に応じて追加する。カスタムハンドラが必要になる場合もある。（`processing-pattern/web-application/web-application-architecture.json:s3`）

参照: processing-pattern/web-application/web-application-architecture.json:s1, processing-pattern/web-application/web-application-architecture.json:s2, processing-pattern/web-application/web-application-architecture.json:s3, processing-pattern/web-application/web-application-feature_details.json:s1, setup/blank-project/blank-project-setup_Web.json:s2
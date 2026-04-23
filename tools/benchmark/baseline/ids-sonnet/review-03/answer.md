**結論**: Nablarch で REST API を構築する場合、`restful_web_service`（Jakarta RESTful Web Services サポート）を使うのが推奨。`http_messaging` は制約が多く非推奨。処理の流れはハンドラキューによる多段構成で組み、クラスはアクション／フォーム／DTO／エンティティの4役に分担する。

---

**根拠**:

**① フレームワーク選択**
2種類のフレームワークが提供されるが、`restful_web_service` の使用を推奨。`http_messaging` はNablarch制御用領域がHTTPヘッダ/ボディに必要・`data_format` 依存・例外が `MessagingException` 一本に潰れるなど柔軟性に欠ける。
（`processing-pattern/restful-web-service/restful-web-service-web_service.json:s1`）

**② 処理の流れ**
1. `WebFrontController`（Servlet Filter）がリクエスト受信
2. ハンドラキューへ委譲
3. `DispatchHandler` がURIからアクションクラスを特定しキュー末尾に追加
4. アクションクラスがフォーム/エンティティで業務ロジックを実行
5. DTO または `HttpResponse` を返却
6. `JaxRsResponseHandler` がレスポンスに変換して応答
（`processing-pattern/restful-web-service/restful-web-service-architecture.json:s2`）

**③ 最小ハンドラ構成（推奨順）**

| No. | ハンドラ | 主な役割 |
|-----|---------|---------|
| 1 | GlobalErrorHandler | 実行時例外ログ出力 |
| 2 | JaxRsResponseHandler | レスポンス書き込み・例外レスポンス生成 |
| 3 | DbConnectionManagementHandler | DB接続の取得・解放 |
| 4 | TransactionManagementHandler | トランザクション開始／コミット／ロールバック |
| 5 | RouterAdaptor（URI→アクション紐付け） | リクエストパスからアクション決定 |
| 6 | BodyConvertHandler | request body↔フォームクラス変換 |
| 7 | JaxRsBeanValidationHandler | フォームクラスへのBean Validation |

`jaxrs_adaptor` を使うと BodyConvertHandler と JaxRsBeanValidationHandler は自動追加される。
（`processing-pattern/restful-web-service/restful-web-service-architecture.json:s3`）

**④ クラス設計パターン**
- **アクションクラス**: リクエストを受け業務ロジックを実行、レスポンスを生成
- **フォームクラス**: HTTP bodyの値をマッピング、バリデーションロジックを持つ。APIごとに別クラスとして作成し、プロパティは全て `String` 型で定義
- **DTO**: レスポンス body にマッピングする値を保持
- **エンティティクラス**: テーブルと1対1対応
（`processing-pattern/restful-web-service/restful-web-service-application_design.json:s1`）

**⑤ 使用できるアノテーション**
`@Produces`（レスポンスメディアタイプ）、`@Consumes`（リクエストメディアタイプ）、`@Valid`（Bean Validation実行）が利用可能。
（`processing-pattern/restful-web-service/restful-web-service-architecture.json:s1`）

---

**注意点**:
- `@Context` アノテーションによる Servlet リソースインジェクションおよび Jakarta CDI は使用不可。
- クライアントサイド機能は提供されないため、REST クライアントが必要な場合は Jersey や RESTEasy などの実装ライブラリを別途使用すること。
- RouterAdaptor より後ろのハンドラはハンドラキューに直接設定せず、router_adaptor に対して設定する。
（`processing-pattern/restful-web-service/restful-web-service-architecture.json:s1`, `processing-pattern/restful-web-service/restful-web-service-architecture.json:s3`）

参照: processing-pattern/restful-web-service/restful-web-service-web_service.json:s1, processing-pattern/restful-web-service/restful-web-service-architecture.json:s1, processing-pattern/restful-web-service/restful-web-service-architecture.json:s2, processing-pattern/restful-web-service/restful-web-service-architecture.json:s3, processing-pattern/restful-web-service/restful-web-service-application_design.json:s1
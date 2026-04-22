**質問**: Nablarch で REST API を提供するサービスを作りたい。処理のつなぎ方や構成パターンってどう組むのが推奨？

---

**結論**: Nablarch の RESTful ウェブサービスは、ウェブアプリケーションをベースに Jakarta RESTful Web Services サポートを組み合わせた構成。`WebFrontController` → `DispatchHandler` の基本フローにアクションクラス（リソースクラス）を JAX-RS アノテーション（`@Path`, `@Produces`, `@Consumes`, `@Valid`）で定義し、`JaxRsResponseHandler` が `HttpResponse` をクライアントに返す。 — `processing-pattern/restful-web-service/restful-web-service-architecture.json#s1`

**① 構成とアノテーション**
Jakarta RESTful Web Services の `@Produces`（レスポンスのメディアタイプ指定）、`@Consumes`（リクエストのメディアタイプ指定）、`@Valid`（リクエストに対する Bean Validation 実行）が使用可能。`@Context` による Servlet リソースインジェクションおよび Jakarta CDI は使用不可。クライアントサイドの機能も提供しないため、クライアントが必要な場合は Jersey / RESTEasy などの JAX-RS 実装を使う。 — `processing-pattern/restful-web-service/restful-web-service-architecture.json#s1`

**② 処理の流れ**
1. `WebFrontController` がリクエストを受信。
2. ハンドラキューへ処理を委譲。
3. `DispatchHandler` が URI を元にアクションクラスを特定。
4. アクションクラスがフォーム/エンティティを使って業務ロジックを実行。
5. アクションはフォームクラス（DTO）または `HttpResponse` を返す。
6. `JaxRsResponseHandler` が `HttpResponse` をクライアントへのレスポンスに変換（フォームクラスの場合は `BodyConvertHandler` で `HttpResponse` に変換、ボディ形式はアクションクラスのメディアタイプ）。 — `processing-pattern/restful-web-service/restful-web-service-architecture.json#s2`

**③ 使用する代表的なハンドラ**
- **リクエスト・レスポンス変換**: `JaxRsResponseHandler`, `BodyConvertHandler`
- **データベース関連**: `DatabaseConnectionManagementHandler`, `TransactionManagementHandler`
- **リクエスト検証**: `JaxRsBeanValidationHandler`, `CsrfTokenVerificationHandler`
- **エラー処理**: `GlobalErrorHandler`
- **その他**: URI とアクションを紐付けるハンドラ（router_adaptor）、`HealthCheckEndpointHandler` — `processing-pattern/restful-web-service/restful-web-service-architecture.json#s3`

**④ 最小ハンドラ構成（順序）**

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | `GlobalErrorHandler` | 実行時例外/エラー時のログ出力 |
| 2 | `JaxRsResponseHandler` | レスポンスの書き込み・例外時のレスポンス生成 |
| 3 | `DatabaseConnectionManagementHandler` | DB 接続の取得・解放 |
| 4 | `TransactionManagementHandler` | トランザクション開始・コミット・ロールバック |
| 5 | `router_adaptor` | リクエストパスからアクション（メソッド）を決定 |
| 6 | `BodyConvertHandler` | request body → フォームクラス、アクション結果 → response body |
| 7 | `JaxRsBeanValidationHandler` | フォームクラスに対するバリデーション |

— `processing-pattern/restful-web-service/restful-web-service-architecture.json#s3`

**注意点**
- `router_adaptor` より後ろのハンドラはハンドラキューに直接設定せず、`router_adaptor` に対して設定する。`jaxrs_adaptor` を使用した場合は `BodyConvertHandler` と `JaxRsBeanValidationHandler` が自動追加される。メディアタイプ拡張が必要な場合は `RoutesMapping` の `methodBinderFactory` に `JaxRsMethodBinderFactory` を設定し、`handlerList` に `BodyConvertHandler` / `JaxRsBeanValidationHandler` を含める。 — `processing-pattern/restful-web-service/restful-web-service-architecture.json#s3`

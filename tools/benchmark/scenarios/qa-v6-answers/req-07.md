**質問**: REST API を別ドメインのフロントエンドから呼び出す。ブラウザの CORS 制約に対応する仕組みは Nablarch にある？

---

**結論**: Nablarch は CORS をビルトインで提供している。RESTful ウェブサービス向けに `CorsPreflightRequestHandler`（プリフライトリクエスト処理）と `CorsResponseFinisher`（実リクエストへの CORS ヘッダ付与）が用意されている。 — `processing-pattern/restful-web-service/restful-web-service-feature_details.json#s14`、`component/handlers/handlers-cors_preflight_request_handler.json#s1`

**① パターン側の位置づけ**
RESTful ウェブサービスの機能詳細で CORS が扱われており、`cors_preflight_request_handler` が紹介されている。 — `processing-pattern/restful-web-service/restful-web-service-feature_details.json#s14`

**② ハンドラの役割**
本ハンドラは RESTful ウェブサービスで CORS (Cross-Origin Resource Sharing) を実現するために使用する。
- **プリフライトリクエスト**: `CorsPreflightRequestHandler` で処理する。
- **実際のリクエストに対する処理**: `CorsResponseFinisher` で処理する。

クラス名: `nablarch.fw.jaxrs.CorsPreflightRequestHandler` — `component/handlers/handlers-cors_preflight_request_handler.json#s1`

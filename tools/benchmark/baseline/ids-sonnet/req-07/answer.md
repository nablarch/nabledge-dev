**結論**: Nablarch には CORS 対応の標準機能がある。`CorsPreflightRequestHandler`（プリフライトリクエスト処理）と `CorsResponseFinisher`（実際のリクエストへのレスポンスヘッダ付与）を組み合わせて使用し、CORS ロジックは `BasicCors` クラスが提供する。

**根拠**:

`CorsPreflightRequestHandler` と `CorsResponseFinisher` に `BasicCors` を指定することで CORS が実現できる。`BasicCors` には許可する Origin を必須で設定する。 (`component/handlers/handlers-cors_preflight_request_handler.json:s4`)

```xml
<component name="cors" class="nablarch.fw.jaxrs.cors.BasicCors">
  <property name="allowOrigins">
    <list>
      <value>https://www.example.com</value>
    </list>
  </property>
</component>
```
(`component/handlers/handlers-cors_preflight_request_handler.json:s4`)

**プリフライトリクエスト**（OPTIONS + Origin + Access-Control-Request-Method が揃った場合）に対して、`BasicCors` のデフォルト動作は以下の通り。(`component/handlers/handlers-cors_preflight_request_handler.json:s4`)
- ステータスコード: 204
- `Access-Control-Allow-Methods`: OPTIONS, GET, POST, PUT, DELETE, PATCH
- `Access-Control-Allow-Headers`: Content-Type, X-CSRF-TOKEN
- `Access-Control-Max-Age`: -1

**実際のリクエスト**には `CorsResponseFinisher` が以下のヘッダを付与する。(`component/handlers/handlers-cors_preflight_request_handler.json:s4`)
- `Access-Control-Allow-Origin`: 許可 Origin に含まれる場合のみリクエストの Origin 値を設定
- `Vary: Origin`
- `Access-Control-Allow-Credentials: true`

**注意点**:
- `allowOrigins` の設定は必須。未設定の場合は動作しない。
- `Access-Control-Allow-Headers` のデフォルトは `Content-Type` と `X-CSRF-TOKEN` のみ。カスタムヘッダを追加する場合は設定変更が必要。
- デフォルトの `Access-Control-Max-Age: -1` はプリフライトキャッシュを無効にするため、必要に応じて変更する。
- レスポンスヘッダの内容は設定で変更可能。

参照: component/handlers/handlers-cors_preflight_request_handler.json:s4, processing-pattern/restful-web-service/restful-web-service-feature_details.json:s14
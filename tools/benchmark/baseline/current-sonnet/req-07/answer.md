**結論**: Nablarch には CORS 対応の標準機能がある。`CorsPreflightRequestHandler` と `CorsResponseFinisher`（`BasicCors` 実装）を組み合わせることで、別ドメインのフロントエンドからの REST API 呼び出しに対応できる。

**根拠**:

1. **仕組みの概要** (`component/handlers/handlers-cors_preflight_request_handler.json:s1`)
   - `nablarch.fw.jaxrs.CorsPreflightRequestHandler` が CORS プリフライトリクエスト（OPTIONS メソッド）を処理する。
   - 実際のリクエストに対する CORS レスポンスヘッダの付与は `CorsResponseFinisher` が担う。

2. **設定方法** (`component/handlers/handlers-cors_preflight_request_handler.json:s4`)
   - `BasicCors`（`nablarch.fw.jaxrs.cors.BasicCors`）を コンポーネントとして定義し、`allowOrigins` プロパティに許可する Origin を列挙する（この設定は必須）。
   - `CorsPreflightRequestHandler` と `CorsResponseFinisher` の両方に同じ `BasicCors` コンポーネントを参照させる。

   ```xml
   <component name="cors" class="nablarch.fw.jaxrs.cors.BasicCors">
     <property name="allowOrigins">
       <list>
         <value>https://www.example.com</value>
       </list>
     </property>
   </component>
   ```

3. **BasicCors のデフォルト動作** (`component/handlers/handlers-cors_preflight_request_handler.json:s4`)
   - プリフライト判定条件: HTTPメソッドが OPTIONS、かつ `Origin` ヘッダと `Access-Control-Request-Method` ヘッダが存在する場合
   - プリフライトレスポンス: ステータス 204、`Access-Control-Allow-Methods: OPTIONS, GET, POST, PUT, DELETE, PATCH`、`Access-Control-Allow-Headers: Content-Type, X-CSRF-TOKEN`
   - 実際のリクエスト: 許可 Origin に含まれる場合のみ `Access-Control-Allow-Origin` と `Vary: Origin` を付与、`Access-Control-Allow-Credentials: true` を設定

4. **モジュール** (`component/handlers/handlers-cors_preflight_request_handler.json:s2`)
   - `com.nablarch.framework:nablarch-fw-jaxrs` への依存を追加する。

**注意点**:
- ハンドラキューの配置順序に制約がある。`CorsPreflightRequestHandler` は `JaxRsResponseHandler` より **後ろ**（= ハンドラキューの後方）に配置する必要がある。これは、本ハンドラが生成した `HttpResponse` を `JaxRsResponseHandler` が処理するためである（`component/handlers/handlers-cors_preflight_request_handler.json:s3`）。
- レスポンスヘッダの内容（許可メソッド、許可ヘッダ、Max-Age など）は設定で変更可能。
- `allowOrigins` の設定は必須。未設定の場合は動作しない。

参照: component/handlers/handlers-cors_preflight_request_handler.json:s1, component/handlers/handlers-cors_preflight_request_handler.json:s2, component/handlers/handlers-cors_preflight_request_handler.json:s3, component/handlers/handlers-cors_preflight_request_handler.json:s4
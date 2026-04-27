**質問**: Web アプリで外部サイトから不正に POST されるのを防ぎたい。Nablarch に対策の仕組みはある？ どう設定する？

---

**結論**: Nablarch は CSRF 対策として `CsrfTokenVerificationHandler`（CSRF トークン検証ハンドラ）を標準提供している。セッションストアに CSRF トークンを格納し、POST/PUT などの更新系リクエストを検証する。ハンドラ配置の前後関係（`session_store_handler` と `nablarch_tag_handler` より後ろ）に制約があるので設定順に注意。 — `processing-pattern/web-application/web-application-feature_details.json#s19`、`component/handlers/handlers-csrf_token_verification_handler.json#s3`

**① ハンドラの配置制約**
- セッションストアの使用が必須（CSRF トークンをセッションストアに格納するため）。
- `session_store_handler` より **後** に配置する。
- Nablarch カスタムタグを使う場合は `nablarch_tag_handler` より **後** に配置する（`tag-hidden_encryption` で CSRF トークンを出力するため）。
- `multipart_handler` の前に配置すれば、ファイル保存前に CSRF トークンを検証できる（この場合は `session_store_handler` も前に）。 — `component/handlers/handlers-csrf_token_verification_handler.json#s3`

**② デフォルト動作**
- セッションストア格納名: `nablarch_csrf-token`
- トークン生成: `UUIDv4CsrfTokenGenerator`（UUID v4）
- 検証対象: `POST`/`PUT` 等。`GET`/`HEAD`/`TRACE`/`OPTIONS` は対象外（`HttpMethodVerificationTargetMatcher`）。
- リクエストでの取得名: HTTP ヘッダ `X-CSRF-TOKEN`、HTTP パラメータ `csrf-token`
- 検証失敗時: `BadRequestVerificationFailureHandler` が 400 を返す。 — `component/handlers/handlers-csrf_token_verification_handler.json#s4`

**③ 設定例（カスタムタグ使用時）**
```xml
<component name="webFrontController" class="nablarch.fw.web.servlet.WebFrontController">
  <property name="handlerQueue">
    <list>
      <component-ref name="sessionStoreHandler" />
      <component-ref name="nablarchTagHandler"/>
      <component-ref name="csrfTokenVerificationHandler"/>
    </list>
  </property>
</component>

<component name="csrfTokenVerificationHandler"
           class="nablarch.fw.web.handler.CsrfTokenVerificationHandler" />
```
— `component/handlers/handlers-csrf_token_verification_handler.json#s4`

**④ カスタマイズ可能なコンポーネント**
`CsrfTokenVerificationHandler` のプロパティで差し替え可能:
- `csrfTokenGenerator`（`CsrfTokenGenerator`）: トークン生成
- `verificationTargetMatcher`（`VerificationTargetMatcher`）: 検証対象判定
- `verificationFailureHandler`（`VerificationFailureHandler`）: 検証失敗時の処理 — `component/handlers/handlers-csrf_token_verification_handler.json#s4`

**注意点**
- RESTful ウェブサービスで使う場合は `CsrfTokenUtil` で CSRF トークンを取得し、クライアントに送る仕組みをプロジェクトで用意する。 — `component/handlers/handlers-csrf_token_verification_handler.json#s4`

**質問**: Web アプリで CSRF 対策を入れたい。セッションも使ってるし、JSP でカスタムタグも使ってるんだけど、何を追加すればいい？ 他との相性で気をつけることは？

---

**結論**: `CsrfTokenVerificationHandler` を追加する。本ハンドラはセッションストアに CSRF トークンを格納するため `session_store` の使用が必須で、`session_store_handler` より後、カスタムタグ使用時は `nablarch_tag_handler` より後に配置する必要がある。また `session_store_handler` 自体にも配置順の制約がある。 — `component/handlers/handlers-csrf_token_verification_handler.json#s3`

**① 追加するハンドラ**
`CsrfTokenVerificationHandler`（CSRF トークン検証ハンドラ）を `WebFrontController` のハンドラキューに追加する。デフォルトで UUIDv4 ベースのトークンをセッションストアに格納し、POST/PUT などを検証する。検証失敗時は 400 を返す。 — `component/handlers/handlers-csrf_token_verification_handler.json#s4`

**② 配置制約（CSRF トークン検証ハンドラ）**
- セッションストア使用が必須。
- `session_store_handler` より **後** に配置（CSRF トークンをセッションストアに格納するため）。
- Nablarch カスタムタグ（`tag`）を使う場合は `nablarch_tag_handler` より **後** に配置（`hidden_encryption` で CSRF トークンを出力するため）。
- `multipart_handler` の前に配置すれば、ファイル保存前に CSRF トークン検証を行える（この場合 `session_store_handler` も前に必要）。 — `component/handlers/handlers-csrf_token_verification_handler.json#s3`

**③ 配置制約（セッション変数保存ハンドラ）**
併せて `SessionStoreHandler` の配置も確認する:
- `http_response_handler` より **後** に配置（サーブレットフォワード時にフォワード先でセッションストアの値へアクセスできるように）。
- HIDDEN ストア使用時は `multipart_handler` より **後** に配置（リクエストパラメータにアクセスするため）。
- `forwarding_handler` より **前** に配置（`forwarding_handler` を `SessionStoreHandler` より前に置くと、HIDDEN ストア使用時に内部フォワード時に最新のセッション変数を取得できなくなる）。 — `component/handlers/handlers-SessionStoreHandler.json#s4`

**④ 設定例（カスタムタグ使用時）**
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

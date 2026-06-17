**結論**: NablarchにはCSRFトークン検証ハンドラ（`CsrfTokenVerificationHandler`）が用意されており、ハンドラ構成に追加するだけでCSRF対策を漏れなく適用できます。

**根拠**:

`CsrfTokenVerificationHandler` をハンドラキューに追加することで、POSTなどのリクエストに対してCSRFトークンの検証が自動実行されます。以下の設定が最小構成です。

```xml
<!-- ハンドラ構成 -->
<component name="webFrontController" class="nablarch.fw.web.servlet.WebFrontController">
  <property name="handlerQueue">
    <list>
      <!-- 他のハンドラは省略 -->

      <!-- セッションストアハンドラ（先に配置） -->
      <component-ref name="sessionStoreHandler" />

      <!-- Nablarchカスタムタグ制御ハンドラ（JSP使用時、先に配置） -->
      <component-ref name="nablarchTagHandler"/>

      <!-- CSRFトークン検証ハンドラ -->
      <component-ref name="csrfTokenVerificationHandler"/>
    </list>
  </property>
</component>

<component name="csrfTokenVerificationHandler"
           class="nablarch.fw.web.handler.CsrfTokenVerificationHandler" />
```

**デフォルトの動作**:
- セッションストアにCSRFトークンを保存（名前: `nablarch_csrf-token`）
- トークン生成: バージョン4のUUID（`UUIDv4CsrfTokenGenerator`）
- 検証対象外: `GET` `HEAD` `TRACE` `OPTIONS`（POSTやPUT等は検証対象）
- CSRFトークンのリクエスト送信方法: HTTPリクエストヘッダ `X-CSRF-TOKEN` またはリクエストパラメータ `csrf-token`
- 検証失敗時: BadRequest(400)レスポンスを返却

**JSPカスタムタグ使用時**: `NablarchTagHandler` が画面にCSRFトークンを自動出力するため、アプリ実装なしでトークンが埋め込まれます。

**注意点**:
- `CsrfTokenVerificationHandler` は必ずセッション変数保存ハンドラ（`SessionStoreHandler`）より後ろに配置すること。セッションストアの使用が必須です。
- JSP利用時は `NablarchTagHandler` より後ろに配置すること。
- データベースを使用した二重サブミット防止機能（`DbTokenManager`）はCSRF対策に対応していないため、CSRF対策には本ハンドラを使用すること。
- ログイン時にセッションIDのみ再生成する場合は、`CsrfTokenUtil.regenerateCsrfToken` メソッドを呼び出してCSRFトークンも再生成する必要があります。
- リクエスト単体テストではCSRFトークン検証が失敗するため、テスト設定で `NopHandler` に差し替えて無効化してください。

参照: handlers-csrf-token-verification-handler.json:s4, handlers-csrf-token-verification-handler.json:s3, handlers-csrf-token-verification-handler.json:s5, security-check-2.チェックリスト.json:s6
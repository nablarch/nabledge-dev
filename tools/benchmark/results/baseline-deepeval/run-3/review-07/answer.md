セクション内容が取得できました。Step 5の回答生成を行います。

---

**結論**: NablarchにはCSRFトークン検証ハンドラ（`CsrfTokenVerificationHandler`）が用意されており、ハンドラキューに追加するだけでCSRF対策が適用されます。POST/PUTなどのリクエストに対してUUIDベースのCSRFトークンを自動検証し、検証失敗時は400（BadRequest）を返します。

**根拠**:

ハンドラキューに以下のように設定します（JSPカスタムタグを使用する場合）。

```xml
<!-- ハンドラ構成 -->
<component name="webFrontController" class="nablarch.fw.web.servlet.WebFrontController">
  <property name="handlerQueue">
    <list>
      <!-- 他のハンドラは省略 -->

      <!-- セッションストアハンドラ -->
      <component-ref name="sessionStoreHandler" />

      <!-- Nablarchカスタムタグ制御ハンドラ -->
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

- CSRFトークンはセッションストアに `nablarch_csrf-token` というキーで格納されます
- `GET` `HEAD` `TRACE` `OPTIONS` は検証対象外（つまりPOSTやPUTは検証対象）
- クライアントからのトークン送信方法: リクエストヘッダ `X-CSRF-TOKEN` またはリクエストパラメータ `csrf-token`
- 検証失敗時は BadRequest（400）レスポンスを返します

**ログイン時のトークン再生成**: ログイン時にセッションIDを再生成するのみ（セッションストアを破棄しない）実装の場合は、アクション内で `CsrfTokenUtil.regenerateCsrfToken()` を呼び出してCSRFトークンも再生成してください。セッションストアを破棄・再生成する実装の場合は不要です。

**注意点**:

- `CsrfTokenVerificationHandler` は必ず `SessionStoreHandler` より後ろに配置してください（CSRFトークンはセッションストアに格納するため）
- JSPカスタムタグを使用する場合は `NablarchTagHandler` より後ろに配置してください
- テスト時はリクエスト単体テストでCSRFトークン検証に失敗するため、テスト設定でハンドラを `NopHandler` に差し替えて無効化してください
- データベースを使用した二重サブミット防止機能はCSRF対策として機能しません。CSRF対策には本ハンドラを使用してください

参照: `handlers-csrf-token-verification-handler.json:s3`, `handlers-csrf-token-verification-handler.json:s4`, `handlers-csrf-token-verification-handler.json:s5`, `security-check-2.チェックリスト.json:s6`

---
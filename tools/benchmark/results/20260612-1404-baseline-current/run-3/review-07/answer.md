**結論**: NablarchにはCSRF対策機能（`CsrfTokenVerificationHandler`）があり、ハンドラキューへの追加のみでCSRFトークンの生成・検証が自動的に行われる。JSPカスタムタグを使用している場合はトークンが画面に自動出力されるため、アプリケーションプログラマの実装は不要。

**根拠**:

ハンドラキューに以下の設定を追加する：

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

デフォルトの動作:
- CSRFトークンはバージョン4のUUIDで生成され、セッションストアに `nablarch_csrf-token` という名前で格納される
- `GET` `HEAD` `TRACE` `OPTIONS` は検証対象**外**（POSTやPUT等が検証対象）
- クライアントからのトークン送信方法: リクエストヘッダ `X-CSRF-TOKEN` またはリクエストパラメータ `csrf-token`
- 検証失敗時: BadRequest(400) を返す

設定のカスタマイズ（トークン名・格納先セッションストア等を変える場合）:

```xml
<component name="webConfig" class="nablarch.common.web.WebConfig">
  <!-- CSRFトークンをHTTPリクエストヘッダから取得する際に使用する名前 -->
  <property name="csrfTokenHeaderName" value="X-CUSTOM-CSRF-TOKEN" />
  <!-- CSRFトークンをHTTPリクエストパラメータから取得する際に使用する名前 -->
  <property name="csrfTokenParameterName" value="custom-csrf-token" />
  <!-- CSRFトークンをセッションストアに格納する際に使用する名前 -->
  <property name="csrfTokenSessionStoredVarName" value="custom-csrf-token" />
  <!-- CSRFトークンを保存するセッションストアの名前 -->
  <property name="csrfTokenSavedStoreName" value="customStore" />
</component>
```

**注意点**:
- 本ハンドラはCSRFトークンをセッションストアに格納するため、**セッションストアの使用が必須**
- ハンドラの配置順序: `セッション変数保存ハンドラ` より後ろに配置すること。JSPカスタムタグを使用する場合は `Nablarchカスタムタグ制御ハンドラ` より後ろにも配置すること
- ログイン時にセッションストア自体を破棄・再生成する実装であれば追加対応不要。セッションIDのみ再生成する実装の場合は `CsrfTokenUtil.regenerateCsrfToken` メソッドを呼び出してCSRFトークンも再生成すること
- リクエスト単体テストでは、正しい画面遷移を経由しないためCSRFトークン検証が失敗する。テスト設定で `NopHandler` に差し替えてCSRF対策を無効化すること

参照: security-check-2.チェックリスト.json:s6, handlers-csrf-token-verification-handler.json:s3, handlers-csrf-token-verification-handler.json:s4, handlers-csrf-token-verification-handler.json:s5
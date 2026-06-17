**結論**: NablarchはCSRFトークン検証ハンドラ（`CsrfTokenVerificationHandler`）を提供しており、ハンドラキューに追加するだけでCSRF対策が自動適用される。アプリケーションプログラマが個別に実装することなく、漏れなくCSRFトークンの生成・検証が行われる。

**根拠**:

JSPカスタムタグを使用する場合の設定例:

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

- CSRFトークンはバージョン4のUUID（`UUIDv4CsrfTokenGenerator`）で生成され、セッションストアに格納される
- `GET` / `HEAD` / `TRACE` / `OPTIONS` は検証対象外。`POST` / `PUT` 等が検証対象となる
- クライアントはHTTPリクエストヘッダ `X-CSRF-TOKEN` またはリクエストパラメータ `csrf-token` でトークンを送信する
- 検証失敗時はBadRequest(400)レスポンスを返す
- JSPカスタムタグを使用している場合、CSRFトークンは画面に自動出力される

設定のカスタマイズが必要な場合（ヘッダ名変更など）:

```xml
<component name="webConfig" class="nablarch.common.web.WebConfig">
  <!-- CSRFトークンをHTTPリクエストヘッダから取得する際に使用する名前 -->
  <property name="csrfTokenHeaderName" value="X-CUSTOM-CSRF-TOKEN" />
  <!-- CSRFトークンをHTTPリクエストパラメータから取得する際に使用する名前 -->
  <property name="csrfTokenParameterName" value="custom-csrf-token" />
</component>
```

**注意点**:

1. **配置順序**: 本ハンドラはセッション変数保存ハンドラより後ろに配置すること。JSPカスタムタグを使用する場合はNablarchカスタムタグ制御ハンドラよりも後ろに配置すること
2. **セッションストア必須**: CSRFトークンをセッションストアに格納するため、セッションストアの使用が必須
3. **ログイン時のトークン再生成**: ログイン時にセッションストアそのものを破棄しない実装の場合は、`CsrfTokenUtil.regenerateCsrfToken`メソッドを呼び出してCSRFトークンを再生成すること
4. **テスト時**: テスティングフレームワークを使ったリクエスト単体テストでは、テスト設定で`NopHandler`に差し替えてCSRF対策を無効化する必要がある

参照: handlers-csrf-token-verification-handler.json:s4, handlers-csrf-token-verification-handler.json:s3, handlers-csrf-token-verification-handler.json:s5, security-check-2.チェックリスト.json:s6
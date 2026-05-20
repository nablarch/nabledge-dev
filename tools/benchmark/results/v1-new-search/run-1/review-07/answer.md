**結論**: NablarchにはCSRF対策専用の `CsrfTokenVerificationHandler`（CSRFトークン検証ハンドラ）が提供されており、ハンドラ構成に追加するだけでCSRFトークンの生成・検証を自動的に行えます。Jakarta Server Pagesカスタムタグを使用している場合、CSRFトークンは画面に自動出力されるため、アプリケーションプログラマが個別に実装する必要はありません。

**根拠**:

ハンドラ構成（`web-component-configuration.xml`等）に以下を追加します：

```xml
<!-- ハンドラ構成 -->
<component name="webFrontController" class="nablarch.fw.web.servlet.WebFrontController">
  <property name="handlerQueue">
    <list>
      <!-- 他のハンドラは省略 -->

      <!-- セッションストアハンドラ（これより後ろに配置すること） -->
      <component-ref name="sessionStoreHandler" />

      <!-- Nablarchカスタムタグ制御ハンドラ（これより後ろに配置すること） -->
      <component-ref name="nablarchTagHandler"/>

      <!-- CSRFトークン検証ハンドラ -->
      <component-ref name="csrfTokenVerificationHandler"/>
    </list>
  </property>
</component>

<component name="csrfTokenVerificationHandler"
           class="nablarch.fw.web.handler.CsrfTokenVerificationHandler" />
```

デフォルトの動作：
- CSRFトークンはUUIDv4（`UUIDv4CsrfTokenGenerator`）で生成し、セッションストアに `nablarch_csrf-token` という名前で保存
- `GET`、`HEAD`、`TRACE`、`OPTIONS` は検証対象外。`POST`、`PUT` 等は検証対象
- クライアントはリクエストヘッダ `X-CSRF-TOKEN` またはリクエストパラメータ `csrf-token` でトークンを送信
- 検証失敗時は `BadRequest(400)` レスポンスを返す

**注意点**:

- セッションストアの使用が必須。本ハンドラはCSRFトークンをセッションストアに格納するため
- ハンドラの配置順に注意：セッション変数保存ハンドラ・Nablarchカスタムタグ制御ハンドラより後ろに配置すること
- ログイン時にセッションIDの再生成にとどめる実装の場合は、`CsrfTokenUtil.regenerateCsrfToken` メソッドを呼び出してCSRFトークンも再生成すること（セッションストアを破棄・再生成する実装であれば不要）
- リクエスト単体テストでは、CSRFトークン検証ハンドラを `NopHandler` に差し替えて無効化すること

参照: handlers-csrf-token-verification-handler.json:s4, handlers-csrf-token-verification-handler.json:s5
**結論**: NablarchのCSRF対策は `CsrfTokenVerificationHandler`（CSRFトークン検証ハンドラ）をハンドラ構成に追加するだけで有効になる。アプリケーションプログラマが個別に実装する必要はなく、漏れなくチェックできる。

**根拠**:

#### 基本的な設定方法

コンポーネント設定ファイル（XML）のハンドラキューに以下の順序でハンドラを追加する。

```xml
<!-- ハンドラ構成 -->
<component name="webFrontController" class="nablarch.fw.web.servlet.WebFrontController">
  <property name="handlerQueue">
    <list>
      <!-- 他のハンドラは省略 -->

      <!-- セッションストアハンドラ（必須：CSRFハンドラより前に配置） -->
      <component-ref name="sessionStoreHandler" />

      <!-- Nablarchカスタムタグ制御ハンドラ（JSP使用時：CSRFハンドラより前に配置） -->
      <component-ref name="nablarchTagHandler"/>

      <!-- CSRFトークン検証ハンドラ -->
      <component-ref name="csrfTokenVerificationHandler"/>
    </list>
  </property>
</component>

<component name="csrfTokenVerificationHandler"
           class="nablarch.fw.web.handler.CsrfTokenVerificationHandler" />
```

#### デフォルトの動作

| 項目 | デフォルト値 |
|------|-------------|
| トークン生成方式 | UUIDv4（`UUIDv4CsrfTokenGenerator`） |
| 検証対象外のHTTPメソッド | `GET` `HEAD` `TRACE` `OPTIONS` |
| 検証対象 | POST・PUT等（上記以外のメソッド） |
| トークンの送信方法 | リクエストヘッダ `X-CSRF-TOKEN` またはパラメータ `csrf-token` |
| 検証失敗時のレスポンス | `BadRequest(400)` |

JSPにNablarchカスタムタグ（`n:form`等）を使用している場合、CSRFトークンは画面に自動で埋め込まれる（実装不要）。

#### カスタマイズが必要な場合

トークン名などを変更する場合は `WebConfig` で設定できる。

```xml
<component name="webConfig" class="nablarch.common.web.WebConfig">
  <!-- リクエストヘッダから取得する際のヘッダ名 -->
  <property name="csrfTokenHeaderName" value="X-CUSTOM-CSRF-TOKEN" />
  <!-- リクエストパラメータから取得する際のパラメータ名 -->
  <property name="csrfTokenParameterName" value="custom-csrf-token" />
  <!-- セッションストアに格納する際のキー名 -->
  <property name="csrfTokenSessionStoredVarName" value="custom-csrf-token" />
</component>
```

**注意点**:
- `CsrfTokenVerificationHandler` はCSRFトークンをセッションストアに格納するため、**セッション変数保存ハンドラ（`SessionStoreHandler`）より後ろ**に配置すること。
- ログイン時にセッションIDのみを再生成する実装の場合は、`CsrfTokenUtil.regenerateCsrfToken` メソッドを呼び出してCSRFトークンも再生成すること。セッションストア自体を破棄して再生成する実装であれば不要。
- リクエスト単体テスト時はCSRFトークンの検証が失敗するため、テスト設定でこのハンドラを `NopHandler` に差し替えて無効化すること。

参照: handlers-csrf-token-verification-handler.json:s4, handlers-csrf-token-verification-handler.json:s3, handlers-csrf-token-verification-handler.json:s5, security-check-2.チェックリスト.json:s6
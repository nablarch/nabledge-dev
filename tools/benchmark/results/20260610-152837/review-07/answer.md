**結論**: NablarchにはCSRFトークン検証ハンドラ（`CsrfTokenVerificationHandler`）があり、ハンドラキューに追加するだけでウェブアプリケーション全体のCSRF対策を漏れなく実施できます。

**根拠**:

CSRFトークン検証ハンドラは以下の仕組みで動作します。

- セッションストアにCSRFトークン（デフォルトはUUIDv4）を生成・保存する
- GET/HEAD/TRACE/OPTIONSはチェック対象外、POSTなどのリクエスト時にCSRFトークンを検証する
- 検証失敗時はBadRequest（400）を返す
- JSPカスタムタグを使用している場合、CSRFトークンが画面に自動出力される

**設定例（JSPカスタムタグ使用の場合）**:

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

CSRFトークンのHTTPリクエストからの取得先（デフォルト）：
- HTTPリクエストヘッダ: `X-CSRF-TOKEN`
- HTTPリクエストパラメータ: `csrf-token`

**注意点**:
- 本ハンドラは**セッション変数保存ハンドラより後ろ**に配置する必要があります
- JSPカスタムタグを使用する場合は**Nablarchカスタムタグ制御ハンドラより後ろ**に配置すること
- セッションストアの使用が必須です（CSRFトークンをセッションストアに格納するため）
- ログイン成功後にセッションIDだけ再生成する実装の場合は、`CsrfTokenUtil.regenerateCsrfToken`メソッドを呼び出してCSRFトークンも再生成すること
- リクエスト単体テストでは本ハンドラを`NopHandler`に差し替えてCSRF対策を無効化してテストすること

参照: handlers-csrf-token-verification-handler.json:s3, handlers-csrf-token-verification-handler.json:s4, handlers-csrf-token-verification-handler.json:s5, security-check-2.チェックリスト.json:s6
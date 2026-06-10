**結論**: NablarchにはCSRFトークン検証ハンドラ (`CsrfTokenVerificationHandler`) があり、ハンドラ構成に追加するだけでCSRF対策を漏れなく実現できる。

**根拠**:

ハンドラを以下のようにコンポーネント定義ファイルに追加する。JSPカスタムタグを使用する場合の設定例：

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

ハンドラを追加すると、以下の動作が自動で行われる：

- CSRFトークンをセッションストアに格納し（名前: `nablarch_csrf-token`）、UUIDv4 で生成する
- POST・PUT 等のリクエストで検証対象となる（GET・HEAD・TRACE・OPTIONS は除外）
- JSPカスタムタグを使用している場合は、CSRFトークンが画面に自動で出力される
- クライアントはリクエストヘッダ `X-CSRF-TOKEN` またはリクエストパラメータ `csrf-token` でトークンを送信する
- 検証に失敗した場合は BadRequest(400) のレスポンスを返す

ログイン時にCSRFトークンを再生成する場合は、アクション内で `CsrfTokenUtil.regenerateCsrfToken` メソッドを呼び出す。セッションストア自体を破棄・再生成する実装の場合は不要。

**注意点**:

- セッションストアの使用が必須（本ハンドラはCSRFトークンをセッションストアに格納する）
- ハンドラの配置順は「セッション変数保存ハンドラの後ろ」かつ「Nablarchカスタムタグ制御ハンドラの後ろ」にすること
- HttpSessionを使用した二重サブミット防止機能もCSRF対策になるが、CSRF対策にはこのハンドラの使用を推奨（ハンドラ方式は漏れなくチェックできるため）
- データベースを使用した二重サブミット防止機能はCSRF対策に対応していないため、本ハンドラを別途使用すること
- テスト実行時は `NopHandler` で本ハンドラを差し替えてCSRF検証を無効化できる

参照: security-check-2.チェックリスト.json:s6, handlers-csrf-token-verification-handler.json:s4, handlers-csrf-token-verification-handler.json:s3, handlers-csrf-token-verification-handler.json:s5
**結論**: NablarchにはCSRF対策として `CsrfTokenVerificationHandler`（CSRFトークン検証ハンドラ）が提供されており、ハンドラキューに追加するだけでウェブアプリケーション全体のCSRF対策を漏れなく実施できます。

**根拠**:

`CsrfTokenVerificationHandler` は以下の処理を自動で行います。

- セッションストアからCSRFトークンを取得（なければ生成・保存）
- POST/PUTなど更新系リクエストに対してCSRFトークンを検証
- 検証失敗時は `400 BadRequest` を返す
- Jakarta Server PagesカスタムタグはCSRFトークンをフォームに自動出力（アプリケーションプログラマの実装不要）

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

デフォルトの動作:
- CSRFトークン生成: バージョン4のUUID（`UUIDv4CsrfTokenGenerator`）
- 検証対象外HTTPメソッド: `GET` `HEAD` `TRACE` `OPTIONS`（POSTやPUT等は検証対象）
- トークン格納場所: リクエストヘッダ `X-CSRF-TOKEN` またはリクエストパラメータ `csrf-token`

**注意点**:

- 本ハンドラはCSRFトークンをセッションストアに格納するため、**セッション変数保存ハンドラより後ろ**に配置する必要があります。
- JSPカスタムタグを使用する場合は、**Nablarchカスタムタグ制御ハンドラより後ろ**に配置してください。
- ログイン時にセッションIDの再生成のみ行う実装の場合は、`CsrfTokenUtil.regenerateCsrfToken` メソッドでCSRFトークンも再生成してください（セッションストア自体を破棄して再生成する実装であれば不要）。
- リクエスト単体テストでは本ハンドラを `NopHandler` に差し替えてCSRF対策を無効化してください。

参照: handlers-csrf-token-verification-handler.json:s4, handlers-csrf-token-verification-handler.json:s3, handlers-csrf-token-verification-handler.json:s5, security-check-2.チェックリスト.json:s6
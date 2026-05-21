**結論**: NablarchにはCSRF対策専用の `CsrfTokenVerificationHandler`（クラス名: `nablarch.fw.web.handler.CsrfTokenVerificationHandler`）が用意されています。このハンドラをハンドラキューに追加するだけで、POSTリクエスト等に対してCSRFトークンの生成・検証が自動で行われ、外部サイトからの不正なPOSTを防ぐことができます。

**根拠**:

**基本設定（JSPカスタムタグを使用する場合）**

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
- CSRFトークンはセッションストアに格納され（キー名: `nablarch_csrf-token`）、バージョン4のUUIDで生成されます。
- `GET` `HEAD` `TRACE` `OPTIONS` は検証対象外。`POST` や `PUT` 等が検証対象となります。
- クライアントからのトークン送信には、HTTPリクエストヘッダ `X-CSRF-TOKEN` またはリクエストパラメータ `csrf-token` を使用します。
- 検証失敗時はBadRequest(400)を返します。
- JSPカスタムタグを使用している場合、CSRFトークンは画面に自動出力されるため、アプリケーション側での追加実装は不要です。

**ログイン時のトークン再生成**

ログイン時にセッションストアを破棄して再生成する実装であればトークンも自動的に破棄・再生成されます。セッションIDのみを再生成する実装の場合は、アクション内で `CsrfTokenUtil.regenerateCsrfToken` メソッドを呼び出してCSRFトークンを明示的に再生成してください。

**注意点**:
- `CsrfTokenVerificationHandler` は必ずセッション変数保存ハンドラ（`SessionStoreHandler`）より**後ろ**に配置してください（CSRFトークンをセッションストアに格納するため）。
- JSPカスタムタグを使用する場合は、さらに Nablarchカスタムタグ制御ハンドラ（`nablarchTagHandler`）より**後ろ**に配置してください。
- リクエスト単体テスト時はCSRFトークンの検証が失敗します。テスト設定で `NopHandler` に差し替えて無効化してください。
- セキュリティチェックリストでは、二重サブミット防止機能もCSRF対策効果はあるものの検証もれが生じるリスクがあるため、`CsrfTokenVerificationHandler` の使用を推奨しています。

参照: handlers-csrf-token-verification-handler.json:s4, handlers-csrf-token-verification-handler.json:s3, security-check-2.チェックリスト.json:s31, handlers-csrf-token-verification-handler.json:s5

---
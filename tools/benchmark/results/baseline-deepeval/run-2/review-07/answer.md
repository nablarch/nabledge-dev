十分な情報が揃いました。回答を生成します。

---

**結論**: NablarchにはCSRF対策専用の`CsrfTokenVerificationHandler`があり、ハンドラキューに追加するだけで自動的にCSRFトークンの生成と検証が行われます。

**根拠**:

**設定方法（JSPカスタムタグを使用する場合）**

ハンドラキューに以下の順序で追加します。

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

**動作の仕組み**

- セッションストアからCSRFトークン（デフォルトはUUIDv4）を取得し、なければ生成してセッションに保存します
- HTTPメソッドの `GET` `HEAD` `TRACE` `OPTIONS` は検証対象外。`POST`や`PUT`等は検証対象となります
- 検証対象リクエストでは、リクエストヘッダ `X-CSRF-TOKEN` またはリクエストパラメータ `csrf-token` からトークンを取得して検証します
- 検証失敗時は`BadRequest(400)`を返します
- JSPカスタムタグを使用している場合、hidden暗号化を通じてCSRFトークンが画面に自動で出力されます

**ログイン時のトークン再生成**

ログイン成功後にセッションIDのみ再生成する実装の場合は、CSRFトークンも明示的に再生成する必要があります。

```java
// ログイン処理のアクション内で呼び出す
CsrfTokenUtil.regenerateCsrfToken(executionContext);
```

セッションストアそのものを破棄して再生成する実装であれば、この呼び出しは不要です。

**注意点**:
- 本ハンドラを使用するにはセッションストアが必須です
- ハンドラの配置順序に制約があります。セッション変数保存ハンドラ（`sessionStoreHandler`）より後ろ、JSPカスタムタグを使用する場合はNablarchカスタムタグ制御ハンドラ（`nablarchTagHandler`）より後ろに配置してください
- リクエスト単体テストでは、CSRFトークン検証ハンドラを`NopHandler`に差し替えて無効化してテストを行ってください
- データベースを使用した二重サブミット防止機能はCSRF対策に対応していないため、CSRF対策には本ハンドラの使用を推奨します

参照: handlers-csrf-token-verification-handler.json:s4, handlers-csrf-token-verification-handler.json:s5, handlers-csrf-token-verification-handler.json:s3, security-check-2.チェックリスト.json:s6

---
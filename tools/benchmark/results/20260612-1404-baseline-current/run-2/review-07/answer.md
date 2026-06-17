**結論**: NablarchにはCSRF対策機能として `CsrfTokenVerificationHandler`（CSRFトークン検証ハンドラ）が用意されており、ハンドラ構成に追加するだけでウェブアプリケーション全体のCSRF対策を漏れなく適用できます。

**根拠**:

**仕組み**

このハンドラをハンドラキューに追加すると、以下の処理が自動で行われます。

1. セッションストアからCSRFトークンを取得し、なければUUIDv4で生成して保存する
2. HTTPリクエストが検証対象か判定する（`GET`/`HEAD`/`TRACE`/`OPTIONS` は検証対象外。`POST`、`PUT` 等は対象）
3. 検証対象の場合、リクエストからCSRFトークンを取得して照合する
   - HTTPリクエストヘッダ: `X-CSRF-TOKEN`
   - HTTPリクエストパラメータ: `csrf-token`
4. 検証失敗時は `400 BadRequest` を返す

JSPカスタムタグを使用している場合は、CSRFトークンが画面に自動出力されるため、アプリケーションプログラマが個別に実装する必要はありません。

**設定方法（JSP使用時の例）**

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

**注意点**:

- `CsrfTokenVerificationHandler` は **セッション変数保存ハンドラ（`sessionStoreHandler`）より後ろ**に配置する必要があります（CSRFトークンをセッションストアに格納するため）
- JSPカスタムタグを使用する場合は **Nablarchカスタムタグ制御ハンドラ（`nablarchTagHandler`）より後ろ**に配置する必要があります
- データベースを使用した二重サブミット防止機能はCSRF対策に対応していないため、CSRF対策には本ハンドラを使用してください
- ログイン時にセッションIDの再生成のみ行う実装の場合は、`CsrfTokenUtil.regenerateCsrfToken` メソッドを呼び出してCSRFトークンも再生成してください
- テスト時はCSRFトークンの検証に失敗するため、テスト用設定でハンドラを `NopHandler` に差し替えて無効化する必要があります

参照: security-check-2.チェックリスト.json:s6, handlers-csrf-token-verification-handler.json:s4, handlers-csrf-token-verification-handler.json:s3, handlers-csrf-token-verification-handler.json:s5
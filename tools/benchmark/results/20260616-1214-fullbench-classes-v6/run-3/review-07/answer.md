**結論**: NablarchにはCSRF対策専用の `CsrfTokenVerificationHandler`（CSRFトークン検証ハンドラ）があります。このハンドラをハンドラ構成に追加するだけで、CSRFトークンの生成と検証が自動的に行われます。

**根拠**:

**基本設定（JSPカスタムタグを使う場合）**

ハンドラ構成に `CsrfTokenVerificationHandler` を追加します。配置順に注意が必要です。

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

**デフォルトの動作**

- **トークン生成**: セッションストアにCSRFトークンがない場合、UUID v4 (`UUIDv4CsrfTokenGenerator`) で自動生成しセッションストアへ保存
- **検証対象**: `GET`・`HEAD`・`TRACE`・`OPTIONS` は検証対象外。`POST`・`PUT` 等は検証対象
- **トークンの受け取り**: HTTPリクエストヘッダ `X-CSRF-TOKEN` またはリクエストパラメータ `csrf-token` から取得
- **検証失敗時**: BadRequest(400) を返す
- JSPカスタムタグを使っている場合は、hidden暗号化の仕組みでCSRFトークンが画面に自動出力されるため、アプリケーションプログラマが実装する必要はありません

**注意点**:

- `CsrfTokenVerificationHandler` は **セッション変数保存ハンドラ（`SessionStoreHandler`）より後ろ**に配置すること
- JSPカスタムタグを使う場合は **`NablarchTagHandler` より後ろ**に配置すること
- ハンドラを使うには **セッションストアが必須**（CSRFトークンをセッションストアに格納するため）
- **ログイン時の注意**: ログイン成功後にセッションストアをそのまま使い続ける場合（セッションID再生成のみ）は、`CsrfTokenUtil.regenerateCsrfToken` メソッドを呼び出してCSRFトークンも再生成すること。セッションストアを破棄・再生成する実装であれば不要
- **テスト時**: リクエスト単体テストではCSRFトークン検証が失敗するため、テスト用設定で本ハンドラを `NopHandler` に差し替えて無効化すること

参照: handlers-csrf-token-verification-handler.json:s4, handlers-csrf-token-verification-handler.json:s3, handlers-csrf-token-verification-handler.json:s5, security-check-2.チェックリスト.json:s6
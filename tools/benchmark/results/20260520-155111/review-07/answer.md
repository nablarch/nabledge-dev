**結論**: NablarchはCSRFトークン検証ハンドラ（`CsrfTokenVerificationHandler`）を標準提供しており、ハンドラキューに追加するだけでトークンの生成・検証が自動で行われる。JSPカスタムタグを使用している場合、CSRFトークンは画面に自動で出力されるため、アプリケーションプログラマが個別に実装する必要はない。

**根拠**:

**ハンドラ構成への追加**（JSPカスタムタグ使用の場合）:

```xml
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

**デフォルト動作**:
- CSRFトークンの生成: UUID v4（`UUIDv4CsrfTokenGenerator`）を使用
- 検証対象外のHTTPメソッド: `GET`、`HEAD`、`TRACE`、`OPTIONS`（POSTやPUT等は検証対象）
- クライアントからのトークン送信方法:
  - HTTPリクエストヘッダ: `X-CSRF-TOKEN`
  - HTTPリクエストパラメータ: `csrf-token`
- 検証失敗時: BadRequest(400)を返す
- セッションストアでの格納名: `nablarch_csrf-token`

**ログイン時のトークン再生成**（セッションIDのみ再生成する実装の場合）:

```java
// ログイン処理のアクション内で呼び出す
CsrfTokenUtil.regenerateCsrfToken(context);
```

セッションストアそのものを破棄・再生成する実装では、このメソッドの呼び出しは不要。

**注意点**:
- `CsrfTokenVerificationHandler`は**セッション変数保存ハンドラ（SessionStoreHandler）より後ろ**に配置すること（CSRFトークンをセッションストアに格納するため）
- JSPカスタムタグを使用する場合は**Nablarchカスタムタグ制御ハンドラより後ろ**に配置すること
- セッションストア（`SessionStoreHandler`）の使用が必須
- リクエスト単体テスト時はCSRFトークン検証が失敗するため、テスト用設定でハンドラを`NopHandler`に差し替えて無効化すること

参照: handlers-csrf-token-verification-handler.json:s3, handlers-csrf-token-verification-handler.json:s4, handlers-csrf-token-verification-handler.json:s5
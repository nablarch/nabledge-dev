**結論**: NablarchにはCSRF対策の仕組みがあり、`CsrfTokenVerificationHandler`（CSRFトークン検証ハンドラ）をハンドラ構成に追加するだけで、アプリケーションプログラマが個別実装しなくてもすべてのリクエストにCSRFトークン検証が適用される。

---

**根拠**:

**基本の設定手順（JSPカスタムタグを使う場合）**

コンポーネント設定ファイル（`web-component-configuration.xml` 等）のハンドラ構成に以下の順序でハンドラを追加する。

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

モジュールは `nablarch-fw-web` に含まれているので、追加の依存関係は不要。

**動作の仕組み（デフォルト）**

| 項目 | 値 |
|------|-----|
| トークン生成 | バージョン4のUUID（`UUIDv4CsrfTokenGenerator`） |
| トークン保存先 | セッションストア（キー名: `nablarch_csrf-token`） |
| 検証対象メソッド | POST、PUT等（`GET` `HEAD` `TRACE` `OPTIONS` は対象外） |
| トークン送信方法 | HTTPリクエストヘッダ `X-CSRF-TOKEN` またはパラメータ `csrf-token` |
| 検証失敗時 | 400 Bad Request を返す |

JSPにNablarchのカスタムタグを使用している場合は、フォームにCSRFトークンが自動出力される。

**ハンドラ配置の制約**

- `sessionStoreHandler`（セッション変数保存ハンドラ）より **後ろ** に配置すること
- JSPカスタムタグを使う場合は `nablarchTagHandler`（Nablarchカスタムタグ制御ハンドラ）より **後ろ** に配置すること

**ログイン時のトークン再生成**

ログイン成功後にセッションIDのみ再生成する（セッションストア自体は破棄しない）実装の場合は、以下を呼び出してCSRFトークンも再生成すること。

```java
CsrfTokenUtil.regenerateCsrfToken(request);
```

セッションストア自体を破棄・再生成する実装の場合は、このメソッド呼び出しは不要（CSRFトークンも自動破棄され、次のページ表示時に新規生成される）。

---

**注意点**:
- テスティングフレームワークでリクエスト単体テストを行う場合、CSRFトークンの検証に失敗する。テスト設定で本ハンドラを `NopHandler` に差し替えて無効化すること。
- データベースを使用した二重サブミット防止機能（`OnDoubleSubmission`）はCSRF対策に対応していないため、CSRF対策が必要な場合は本ハンドラを使用すること。

参照: handlers-csrf-token-verification-handler.json:s1, handlers-csrf-token-verification-handler.json:s2, handlers-csrf-token-verification-handler.json:s3, handlers-csrf-token-verification-handler.json:s4, handlers-csrf-token-verification-handler.json:s5, security-check-2.チェックリスト.json:s6
回答を生成します。

**結論**: NablarchにはCSRF対策の仕組みがあり、`CsrfTokenVerificationHandler`（CSRFトークン検証ハンドラ）をハンドラ構成に追加するだけで、POSTなどの書き込みリクエストに対してCSRFトークンの検証が自動で行われます。

**根拠**:

`CsrfTokenVerificationHandler` をハンドラキューに追加することで、以下の処理が自動で実行されます。

- セッションストアにCSRFトークン（バージョン4のUUID）を生成・保存する
- GET / HEAD / TRACE / OPTIONS は検証対象外、POST / PUT等は検証対象とする
- 検証失敗時はBadRequest（400）を返す
- JSPカスタムタグを使用している場合、CSRFトークンが画面に自動出力される

**設定方法（JSPカスタムタグを使う場合）**:

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

デフォルトのトークン受け取り先:

| 受け取り場所 | 名前 |
|---|---|
| HTTPリクエストヘッダ | `X-CSRF-TOKEN` |
| HTTPリクエストパラメータ | `csrf-token` |

**注意点**:

- 本ハンドラは **セッション変数保存ハンドラより後ろ** に配置すること（CSRFトークンをセッションストアに格納するため）
- JSPカスタムタグを使う場合は **Nablarchカスタムタグ制御ハンドラより後ろ** に配置すること
- ログイン時にセッションIDの再生成のみ行う実装の場合は、`CsrfTokenUtil.regenerateCsrfToken` を呼び出してCSRFトークンも再生成すること（セッションストア自体を破棄・再生成する実装であれば不要）
- テスト時はCSRFトークン検証が失敗するため、テスト用設定でハンドラを`NopHandler`に差し替えて無効化すること:

```xml
<!-- CSRF対策の無効化（テスト設定） -->
<component name="csrfTokenVerificationHandler" class="nablarch.test.NopHandler" />
```

参照: handlers-csrf-token-verification-handler.json:s4, handlers-csrf-token-verification-handler.json:s3, handlers-csrf-token-verification-handler.json:s5, security-check-2.チェックリスト.json:s6

---
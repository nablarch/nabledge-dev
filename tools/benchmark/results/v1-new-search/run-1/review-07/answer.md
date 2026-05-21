**結論**: NablarchにはCSRF対策の仕組みがあります。`CsrfTokenVerificationHandler`（CSRFトークン検証ハンドラ）をハンドラキューに追加するだけで、POSTなどの更新系リクエストに対してCSRFトークンの生成・検証が自動的に行われます。アプリケーションプログラマが個別に実装する必要はありません。

**根拠**: JSPカスタムタグを使用するウェブアプリケーションの場合、以下のようにハンドラキューへ追加します。

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

デフォルトの動作：
- CSRFトークンはUUIDv4で生成し、セッションストアに保存する
- `GET` `HEAD` `TRACE` `OPTIONS` は検証対象外。`POST` `PUT` 等は検証対象となる
- 検証失敗時はBadRequest(400)を返す
- JSPカスタムタグ使用時は、CSRFトークンが画面に自動出力される

**注意点**:
- セッションストア（`SessionStoreHandler`）の使用が必須。`sessionStoreHandler` より後ろに配置すること
- JSPカスタムタグ使用時は、`nablarchTagHandler` より後ろに配置すること
- ログイン時にセッションIDの再生成のみ行う実装の場合は、`CsrfTokenUtil.regenerateCsrfToken` を呼び出してCSRFトークンも再生成すること（セッションストア自体を破棄・再生成する実装であれば不要）
- リクエスト単体テストではCSRFトークンの検証に失敗するため、テスト設定でハンドラを`NopHandler`に差し替えて無効化すること

参照: security-check-2.チェックリスト.json:s31, handlers-csrf-token-verification-handler.json:s4, handlers-csrf-token-verification-handler.json:s3, handlers-csrf-token-verification-handler.json:s5

---
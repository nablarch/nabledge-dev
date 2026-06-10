**結論**: NablarchにはCSRF対策専用のハンドラ `CsrfTokenVerificationHandler`（クラス名: `nablarch.fw.web.handler.CsrfTokenVerificationHandler`）が用意されており、ハンドラ構成に追加するだけでCSRFトークンの生成・検証が自動で行われる。アプリケーションプログラマが個別に実装する必要はない。

**根拠**: ハンドラ構成ファイル（component定義XML）に以下のように追加する。

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

デフォルトの動作は以下の通り。

- **トークン生成**: バージョン4のUUID（`UUIDv4CsrfTokenGenerator`）
- **格納先**: セッションストア（キー名: `nablarch_csrf-token`）
- **検証除外**: `GET` `HEAD` `TRACE` `OPTIONS` は検証対象外（`POST`、`PUT` 等は検証対象）
- **クライアントからのトークン送信先**: リクエストヘッダ `X-CSRF-TOKEN` またはリクエストパラメータ `csrf-token`
- **検証失敗時**: `400 Bad Request` を返す

ログイン時のトークン再生成が必要な場合（セッションIDの再生成にとどめる実装の場合）は、アクション等のリクエスト処理の中で `CsrfTokenUtil.regenerateCsrfToken` メソッドを呼び出すと、ハンドラの戻り処理でCSRFトークンが再生成される。

**注意点**:
- `CsrfTokenVerificationHandler` はセッション変数保存ハンドラ（`SessionStoreHandler`）より後ろに配置する必要がある。
- JSPカスタムタグを使用する場合は、`NablarchTagHandler`（Nablarchカスタムタグ制御ハンドラ）より後ろに配置する必要がある。
- リクエスト単体テスト実施時は正しい画面遷移を経由しないためCSRFトークン検証が失敗する。テスト設定で本ハンドラを `NopHandler` に差し替えることで無効化できる。
- データベースを使用した二重サブミット防止機能はCSRF対策に対応していないため、CSRF対策には本ハンドラを使用すること。

参照: handlers-csrf-token-verification-handler.json:s1, handlers-csrf-token-verification-handler.json:s2, handlers-csrf-token-verification-handler.json:s3, handlers-csrf-token-verification-handler.json:s4, handlers-csrf-token-verification-handler.json:s5, security-check-2.チェックリスト.json:s6

---
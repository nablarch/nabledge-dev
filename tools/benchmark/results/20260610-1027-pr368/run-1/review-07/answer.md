**結論**: NablarchはCSRF対策として`CsrfTokenVerificationHandler`（CSRFトークン検証ハンドラ）を提供しています。ハンドラ構成にこのハンドラを追加するだけで、すべてのPOSTリクエスト等に対してCSRFトークンの自動生成・検証が行われます。

---

**根拠**:

#### 仕組み

`CsrfTokenVerificationHandler`は以下の処理を行います。

1. セッションストアからCSRFトークンを取得（なければUUID v4で生成・保存）
2. HTTPメソッドが `GET` `HEAD` `TRACE` `OPTIONS` 以外（POSTやPUT等）のリクエストを検証対象と判定
3. リクエストヘッダ `X-CSRF-TOKEN` またはリクエストパラメータ `csrf-token` からトークンを取得して検証
4. 検証失敗時はBadRequest(400)を返す

JSPにNablarchカスタムタグ（`<n:form>`等）を使っている場合、CSRFトークンはhidden暗号化により画面に**自動で出力**されるため、アプリケーションプログラマが実装する必要はありません。

#### 基本的な設定方法（コンポーネント定義ファイル）

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

#### カスタマイズが必要な場合

トークン名やストア名を変更したい場合は`WebConfig`で設定できます。

```xml
<component name="webConfig" class="nablarch.common.web.WebConfig">
  <!-- CSRFトークンをHTTPリクエストヘッダから取得する際に使用する名前 -->
  <property name="csrfTokenHeaderName" value="X-CUSTOM-CSRF-TOKEN" />
  <!-- CSRFトークンをHTTPリクエストパラメータから取得する際に使用する名前 -->
  <property name="csrfTokenParameterName" value="custom-csrf-token" />
  <!-- CSRFトークンをセッションストアに格納する際に使用する名前 -->
  <property name="csrfTokenSessionStoredVarName" value="custom-csrf-token" />
  <!-- CSRFトークンを保存するセッションストアの名前 -->
  <property name="csrfTokenSavedStoreName" value="customStore" />
</component>
```

---

**注意点**:

- **ハンドラの配置順序**: `CsrfTokenVerificationHandler`はセッション変数保存ハンドラ（`SessionStoreHandler`）より後ろ、かつJSPカスタムタグを使う場合は`NablarchTagHandler`より後ろに配置すること
- **セッションストアが必須**: このハンドラはCSRFトークンをセッションストアに格納するため、セッションストアの使用が必須
- **ログイン時のトークン再生成**: セッションIDのみ再生成する実装の場合は`CsrfTokenUtil.regenerateCsrfToken`メソッドを呼び出してCSRFトークンも再生成すること。セッションストアを破棄・再生成する実装であれば不要
- **リクエスト単体テスト**: テスト時はCSRFトークン検証が失敗するため、テスト用設定で`NopHandler`に差し替えて無効化すること
- **HttpSessionを使った二重サブミット防止はCSRF対策として使えるが、CSRF対策機能の使用を推奨**（二重サブミット防止は明示的な実装が必要で漏れが生じやすい）。**データベースを使った二重サブミット防止はCSRF対策に対応していない**ため注意

参照: security-check-2.チェックリスト.json:s6, handlers-csrf-token-verification-handler.json:s3, handlers-csrf-token-verification-handler.json:s4, handlers-csrf-token-verification-handler.json:s5
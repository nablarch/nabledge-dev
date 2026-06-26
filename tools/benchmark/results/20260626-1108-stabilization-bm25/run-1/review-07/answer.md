**結論**: NablarchにはCSRF対策のための `CsrfTokenVerificationHandler`（CSRFトークン検証ハンドラ）が標準で提供されています。このハンドラをハンドラ構成に追加するだけで、POSTなどのリクエストに対するCSRFトークンの生成・検証が自動的に行われます。

**根拠**:

**1. ハンドラの設定方法**

コンポーネント定義ファイル（`web-component-configuration.xml` 等）にて、セッションストアハンドラ・Nablarchカスタムタグ制御ハンドラの後にCSRFトークン検証ハンドラを追加します。

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

**2. デフォルトの動作**

- セッションストアからCSRFトークンを取得し、なければ自動生成してセッションに保存（セッション変数名: `nablarch_csrf-token`）
- HTTPメソッドが `GET` `HEAD` `TRACE` `OPTIONS` の場合は検証対象外、`POST` `PUT` 等は検証対象
- クライアントからのCSRFトークンの送信先:
  - HTTPヘッダ: `X-CSRF-TOKEN`
  - HTTPリクエストパラメータ: `csrf-token`
- 検証失敗時はBadRequest (400) を返す

**3. カスタマイズ（必要な場合）**

生成ロジック・検証対象判定・失敗時処理・トークン名などはすべてカスタマイズ可能です。

```xml
<component class="nablarch.fw.web.handler.CsrfTokenVerificationHandler">
  <!-- CSRFトークンの生成を行うインターフェース -->
  <property name="csrfTokenGenerator">
    <component class="com.sample.CustomCsrfTokenGenerator" />
  </property>
  <!-- HTTPリクエストがCSRFトークンの検証対象か否かの判定を行うインターフェース -->
  <property name="verificationTargetMatcher">
    <component class="com.sample.CustomVerificationTargetMatcher" />
  </property>
  <!-- CSRFトークンの検証失敗時の処理を行うインタフェース -->
  <property name="verificationFailureHandler" />
    <component class="com.sample.CustomVerificationFailureHandler" />
  </property>
</component>

<component name="webConfig" class="nablarch.common.web.WebConfig">
  <!-- CSRFトークンをHTTPリクエストヘッダから取得する際に使用する名前 -->
  <property name="csrfTokenHeaderName" value="X-CUSTOM-CSRF-TOKEN" />
  <!-- CSRFトークンをHTTPリクエストパラメータから取得する際に使用する名前 -->
  <property name="csrfTokenParameterName" value="custom-csrf-token" />
  <!-- CSRFトークンをセッションスストアに格納する際に使用する名前 -->
  <property name="csrfTokenSessionStoredVarName" value="custom-csrf-token" />
  <!-- CSRFトークンを保存するセッションストアの名前 -->
  <property name="csrfTokenSavedStoreName" value="customStore" />
</component>
```

**注意点**:

- **ログイン時のCSRFトークン再生成**: ログイン時にセッションIDだけ再生成する実装の場合は、`CsrfTokenUtil.regenerateCsrfToken` メソッドを呼び出してCSRFトークンも再生成すること。セッションストア自体を破棄・再生成する実装であれば不要。
- **テスト時の無効化**: リクエスト単体テストではCSRFトークン検証が失敗するため、テスト設定で `NopHandler` に差し替えて無効化すること。
  ```xml
  <!-- CSRF対策の無効化（テスト設定） -->
  <component name="csrfTokenVerificationHandler" class="nablarch.test.NopHandler" />
  ```
- **二重サブミット防止機能との違い**: HttpSessionを使った二重サブミット防止機能もCSRF対策として機能しますが、実装漏れのリスクがあります。CSRFトークン検証ハンドラはハンドラ追加だけで漏れなくチェックできるため推奨です。なお、データベースを使った二重サブミット防止機能はCSRF対策に対応していないため、必ずCSRFトークン検証ハンドラと併用してください。

参照: handlers-csrf-token-verification-handler.json:s1, handlers-csrf-token-verification-handler.json:s4, handlers-csrf-token-verification-handler.json:s5, security-check-2.チェックリスト.json:s6, web-application-architecture.json:s3
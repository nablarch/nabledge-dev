**結論**: NablarchにはCSRF対策の仕組みがあります。`CsrfTokenVerificationHandler`をハンドラ構成に追加するだけで、CSRFトークンの自動生成・検証が有効になります。

**根拠**:

Nablarchが提供するCSRF対策機能は`nablarch.fw.web.handler.CsrfTokenVerificationHandler`です。このハンドラをハンドラキューに追加することで、アプリケーションプログラマが個別実装せずともCSRF対策を漏れなく適用できます。

**基本的な設定方法（JSPカスタムタグを使う場合）:**

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

**デフォルトの動作:**
- CSRFトークンはセッションストアに格納される（格納名: `nablarch_csrf-token`）
- トークンはバージョン4のUUIDで生成される
- `GET` `HEAD` `TRACE` `OPTIONS`は検証対象外。`POST`や`PUT`などは検証対象になる
- リクエストからのトークン取得先: HTTPリクエストヘッダ `X-CSRF-TOKEN` またはリクエストパラメータ `csrf-token`
- 検証失敗時: BadRequest(400)レスポンスを返す

JSPのカスタムタグを使用している場合、CSRFトークンは画面に自動で出力されます。

**動作のカスタマイズが必要な場合（オプション）:**

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
- `CsrfTokenVerificationHandler`はセッションストアにトークンを格納するため、必ず**セッション変数保存ハンドラ（SessionStoreHandler）より後ろ**に配置すること
- JSPカスタムタグを使う場合は、**Nablarchカスタムタグ制御ハンドラ（NablarchTagHandler）より後ろ**に配置すること
- **ログイン時のトークン再生成**: ログイン成功後にセッションストアを破棄・再生成する場合は自動でCSRFトークンも更新される。セッションIDのみ再生成する場合は、アクション処理内で`CsrfTokenUtil.regenerateCsrfToken`メソッドを呼び出してCSRFトークンも明示的に再生成すること
- **テスト時**: リクエスト単体テストでは正常な画面遷移を経由しないためCSRFトークン検証が失敗する。テスト設定でハンドラを`NopHandler`に差し替えてCSRF対策を無効化すること

```xml
<!-- テストの設定で本ハンドラのコンポーネント定義を上書く。
     コンポーネント名を合わせることで上書きを行う。 -->

<!-- CSRF対策の無効化 -->
<component name="csrfTokenVerificationHandler" class="nablarch.test.NopHandler" />
```

参照:
- CSRFトークン検証ハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-csrf-token-verification-handler.md
  CSRFトークンの生成と検証
  制約
  CSRFトークンを再生成する
- 2.チェックリスト
  .claude/skills/nabledge-6/docs/check/security-check/security-check-2.チェックリスト.md
  CSRF （クロスサイト・リクエスト・フォージェリ）
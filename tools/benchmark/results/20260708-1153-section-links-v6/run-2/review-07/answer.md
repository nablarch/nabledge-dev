**結論**: NablarchにはCSRF対策専用の`CsrfTokenVerificationHandler`が提供されており、ハンドラ構成に追加するだけでCSRFトークンの生成・検証が自動的に行われます。JSPカスタムタグを使用している場合、トークンは画面に自動出力されるためアプリケーション側での追加実装は不要です。

**根拠**:

ハンドラ構成への追加（JSPカスタムタグ使用時の設定例）:

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

デフォルトの動作:
- CSRFトークンをUUID v4で生成し、セッションストアに保存
- `GET` `HEAD` `TRACE` `OPTIONS` は検証対象外（`POST` や `PUT` 等は検証対象）
- HTTPリクエストヘッダ `X-CSRF-TOKEN` またはリクエストパラメータ `csrf-token` からトークンを取得して検証
- 検証失敗時は `BadRequest(400)` を返す

動作をカスタマイズしたい場合（トークン生成方法・ヘッダ名・検証失敗時の処理など）:

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
</component>

<component name="webConfig" class="nablarch.common.web.WebConfig">
  <!-- CSRFトークンをHTTPリクエストヘッダから取得する際に使用する名前 -->
  <property name="csrfTokenHeaderName" value="X-CUSTOM-CSRF-TOKEN" />
  <!-- CSRFトークンをHTTPリクエストパラメータから取得する際に使用する名前 -->
  <property name="csrfTokenParameterName" value="custom-csrf-token" />
</component>
```

ログイン時のCSRFトークン再生成（セッションフィクセーション対策）:

ログイン成功後にセッションストアを破棄・再生成する実装の場合、CSRFトークンも自動的に破棄・再生成されます。セッションIDの再生成にとどめる場合は、アクション内で以下を呼び出すこと:

```java
CsrfTokenUtil.regenerateCsrfToken(executionContext);
```

**注意点**:
- 本ハンドラはCSRFトークンをセッションストアに格納するため、**セッション変数保存ハンドラより後ろ**に配置すること（セッションストアの使用が必須）
- JSPカスタムタグ使用時は**Nablarchカスタムタグ制御ハンドラより後ろ**に配置すること
- テスティングフレームワークを使用したリクエスト単体テスト時はCSRFトークンの検証が失敗するため、テスト設定で本ハンドラを `NopHandler` に差し替えて無効化すること:

```xml
<!-- CSRF対策の無効化（テスト設定のみ） -->
<component name="csrfTokenVerificationHandler" class="nablarch.test.NopHandler" />
```

参照:
- CSRFトークン検証ハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-csrf-token-verification-handler.md
  CSRFトークンの生成と検証
  CSRFトークンを再生成する
  制約
- 2.チェックリスト
  .claude/skills/nabledge-6/docs/check/security-check/security-check-2.チェックリスト.md
  CSRF （クロスサイト・リクエスト・フォージェリ）
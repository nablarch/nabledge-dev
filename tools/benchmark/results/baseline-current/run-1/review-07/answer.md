**結論**: NablarchにはCSRF対策専用の `CsrfTokenVerificationHandler` が用意されており、ハンドラ構成に追加するだけで自動的にCSRFトークンの生成・検証が行われます。アプリケーションプログラマが個別に実装する必要はありません。

**根拠**:

**基本設定（Jakarta Server Pagesカスタムタグ使用の場合）**

```xml
<!-- ハンドラ構成 -->
<component name="webFrontController" class="nablarch.fw.web.servlet.WebFrontController">
  <property name="handlerQueue">
    <list>
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

**依存モジュール**

```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-fw-web</artifactId>
</dependency>
```

**デフォルト動作**

- CSRFトークンはセッションストアに格納（セッションストアの使用が必須）
- トークン生成: UUIDv4（`UUIDv4CsrfTokenGenerator`）
- 検証対象: `GET` `HEAD` `TRACE` `OPTIONS` は対象外。**POSTやPUTは検証対象**
- トークンの送信方法: リクエストヘッダ `X-CSRF-TOKEN` またはリクエストパラメータ `csrf-token`
- 検証失敗時: `400 BadRequest` を返す

**ログイン時のCSRFトークン再生成（重要）**

ログイン時にセッションIDを再生成する実装の場合は、CSRFトークンも再生成が必要です。

```java
CsrfTokenUtil.regenerateCsrfToken(request);
```

ログイン時にセッションストア自体を破棄・再生成する場合は、このメソッドの呼び出しは不要です。

**テスト時の無効化設定**

リクエスト単体テストではCSRFトークン検証が失敗するため、テスト用設定で無効化します。

```xml
<component name="csrfTokenVerificationHandler" class="nablarch.test.NopHandler" />
```

**注意点**:

- **配置順序**: `セッション変数保存ハンドラ` より後ろに配置すること（CSRFトークンはセッションストアに格納するため）
- **JSPカスタムタグ使用時**: `Nablarchカスタムタグ制御ハンドラ` より後ろに配置すること（hidden暗号化でトークンを出力するため）
- **ファイルアップロード時**: ファイル保存前にCSRF検証を行いたい場合は、マルチパートリクエストハンドラの**前**に本ハンドラとセッション変数保存ハンドラを配置する
- セッションストアの設定が前提のため、セッションストア未使用の構成には適用できません

参照: `component/handlers/handlers-csrf-token-verification-handler.json#s3`, `component/handlers/handlers-csrf-token-verification-handler.json#s4`, `component/handlers/handlers-csrf-token-verification-handler.json#s5`
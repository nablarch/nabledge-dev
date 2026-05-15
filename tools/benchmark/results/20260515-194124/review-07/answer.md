**結論**: NablarchにはCSRF対策専用の `CsrfTokenVerificationHandler` が用意されています。このハンドラをハンドラ構成に追加するだけで、トークンの生成・検証が自動的に行われます。

**根拠**:

### ハンドラクラス
`nablarch.fw.web.handler.CsrfTokenVerificationHandler`

### 依存モジュール
```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-fw-web</artifactId>
</dependency>
```

### 基本設定（JSPカスタムタグ利用時）

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

### デフォルト動作
- **トークン生成**: UUIDv4で生成し、セッションストアに保存（キー名: `nablarch_csrf-token`）
- **検証対象メソッド**: POST/PUT/DELETE/PATCH など（GET/HEAD/TRACE/OPTIONSは検証対象外）
- **トークン送信方法**: HTTPリクエストヘッダ `X-CSRF-TOKEN` またはリクエストパラメータ `csrf-token` で送信
- **検証失敗時**: 400 BadResponse を返す
- **JSPカスタムタグ使用時**: hidden暗号化を使って画面にCSRFトークンが自動出力されるため、アプリケーション側の実装は不要

### カスタマイズ（必要な場合のみ）

```xml
<component class="nablarch.fw.web.handler.CsrfTokenVerificationHandler">
  <property name="csrfTokenGenerator">
    <component class="com.sample.CustomCsrfTokenGenerator" />
  </property>
  <property name="verificationTargetMatcher">
    <component class="com.sample.CustomVerificationTargetMatcher" />
  </property>
</component>

<component name="webConfig" class="nablarch.common.web.WebConfig">
  <property name="csrfTokenHeaderName" value="X-CUSTOM-CSRF-TOKEN" />
  <property name="csrfTokenParameterName" value="custom-csrf-token" />
</component>
```

### ログイン時のトークン再生成

セッションIDのみ再生成する実装の場合は、ログイン処理内で以下を呼び出してCSRFトークンも再生成してください。

```java
CsrfTokenUtil.regenerateCsrfToken(request);
```

**注意点**:

1. **ハンドラの配置順序**: `SessionStoreHandler` より後ろに配置すること（CSRFトークンをセッションストアに格納するため）
2. **JSPカスタムタグ使用時**: `NablarchTagHandler` より後ろに配置すること
3. **ファイルアップロード時**: ファイル保存前にCSRFトークンを検証したい場合は、`MultipartRequestHandler` の前に本ハンドラと `SessionStoreHandler` を配置すること
4. **リクエスト単体テスト**: テスト実行時は `NopHandler` で本ハンドラを差し替えてCSRF対策を無効化すること

```xml
<!-- テスト設定でCSRF対策を無効化 -->
<component name="csrfTokenVerificationHandler" class="nablarch.test.NopHandler" />
```

参照: `component/handlers/handlers-csrf-token-verification-handler.json#s4`, `#s3`, `#s5`
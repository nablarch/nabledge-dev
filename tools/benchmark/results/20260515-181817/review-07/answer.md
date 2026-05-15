**結論**: NablarchにはCSRF対策専用の `CsrfTokenVerificationHandler`（CSRFトークン検証ハンドラ）が用意されています。ハンドラ構成に追加するだけでCSRFトークンの生成・検証が自動化され、アプリケーション側の追加実装は不要です。

**根拠**:

**ハンドラクラス名**
- `nablarch.fw.web.handler.CsrfTokenVerificationHandler`

**モジュール**
```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-fw-web</artifactId>
</dependency>
```

**基本設定（JSPカスタムタグ使用時）**
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

**デフォルトの動作**
- CSRFトークンはセッションストアに格納（セッション変数名: `nablarch_csrf-token`）
- トークン生成: UUIDv4を使用（`UUIDv4CsrfTokenGenerator`）
- 検証対象外: `GET`, `HEAD`, `TRACE`, `OPTIONS`（POST、PUTなどは検証対象）
- トークンの受け取り場所: リクエストヘッダ `X-CSRF-TOKEN` またはリクエストパラメータ `csrf-token`
- 検証失敗時: HTTP 400 (BadRequest) を返す

**カスタマイズ設定例**（デフォルトから変更する場合）
```xml
<component class="nablarch.fw.web.handler.CsrfTokenVerificationHandler">
  <property name="csrfTokenGenerator">
    <component class="com.sample.CustomCsrfTokenGenerator" />
  </property>
  <property name="verificationTargetMatcher">
    <component class="com.sample.CustomVerificationTargetMatcher" />
  </property>
  <property name="verificationFailureHandler">
    <component class="com.sample.CustomVerificationFailureHandler" />
  </property>
</component>

<component name="webConfig" class="nablarch.common.web.WebConfig">
  <property name="csrfTokenHeaderName" value="X-CUSTOM-CSRF-TOKEN" />
  <property name="csrfTokenParameterName" value="custom-csrf-token" />
  <property name="csrfTokenSessionStoredVarName" value="custom-csrf-token" />
  <property name="csrfTokenSavedStoreName" value="customStore" />
</component>
```

**ログイン時のCSRFトークン再生成**

ログイン後もトークンを引き継ぐと、セッション固定攻撃と組み合わせた攻撃が可能になります。ログイン時は以下のいずれかの対処が必要です。
- セッションストアを破棄して再生成する場合: CSRFトークンも自動的に破棄・再生成されるため追加対応不要
- セッションIDの再生成のみの場合: アクション内で `CsrfTokenUtil.regenerateCsrfToken` を呼び出してトークンを再生成すること

**注意点**:
1. **配置順序**: `CsrfTokenVerificationHandler` は必ず「セッション変数保存ハンドラ（SessionStoreHandler）」より後ろに配置すること
2. **JSPカスタムタグ使用時**: 「Nablarchカスタムタグ制御ハンドラ（NablarchTagHandler）」より後ろに配置すること（CSRFトークンがhiddenフィールドとして画面に自動出力されるため）
3. **ファイルアップロード時**: ファイル保存前にCSRFトークン検証を行いたい場合は、マルチパートリクエストハンドラの前にセッション変数保存ハンドラと本ハンドラを配置すること
4. **テスト時**: リクエスト単体テストではCSRF対策を無効化する必要がある。テスト設定で `csrfTokenVerificationHandler` を `NopHandler` に差し替えること
5. **セッションストア必須**: 本ハンドラはCSRFトークンをセッションストアに格納するため、セッションストアの使用が必須

参照: `handlers-csrf-token-verification-handler.json#s3`, `handlers-csrf-token-verification-handler.json#s4`, `handlers-csrf-token-verification-handler.json#s5`
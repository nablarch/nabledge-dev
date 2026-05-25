**結論**: NablarchにはCSRF対策として `CsrfTokenVerificationHandler`（CSRFトークン検証ハンドラ）が用意されています。ハンドラ構成に追加するだけでCSRFトークンの生成・検証が自動で行われます。

**根拠**:

### 基本設定

`nablarch-fw-web` モジュールに含まれるため、追加依存は不要です（通常のWebアプリで既に含まれています）。

ハンドラ構成に以下のように追加します：

```xml
<component name="webFrontController" class="nablarch.fw.web.servlet.WebFrontController">
  <property name="handlerQueue">
    <list>
      <!-- セッションストアハンドラ（先に配置すること） -->
      <component-ref name="sessionStoreHandler" />
      <!-- Nablarchカスタムタグ制御ハンドラ（JSPカスタムタグ使用時） -->
      <component-ref name="nablarchTagHandler"/>
      <!-- CSRFトークン検証ハンドラ -->
      <component-ref name="csrfTokenVerificationHandler"/>
    </list>
  </property>
</component>

<component name="csrfTokenVerificationHandler"
           class="nablarch.fw.web.handler.CsrfTokenVerificationHandler" />
```

デフォルト動作：
- トークン生成: UUIDv4（UUIDv4CsrfTokenGenerator）
- 検証対象外: GET / HEAD / TRACE / OPTIONS
- 検証対象（CSRF対策が働く）: POST / PUT / DELETE など
- リクエストヘッダ名: X-CSRF-TOKEN
- リクエストパラメータ名: csrf-token
- セッションストアキー名: nablarch_csrf-token
- 検証失敗時: 400 Bad Request

### ログイン時のトークン再生成

ログイン成功時にアクション内で以下のように再生成します（セッションストアを破棄・再生成する実装では不要）：

```java
CsrfTokenUtil.regenerateCsrfToken(executionContext);
```

**注意点**:

1. **ハンドラの順序**: SessionStoreHandler より後ろに配置すること。
2. **JSPカスタムタグ使用時**: NablarchTagHandler より後ろに配置すること。
3. **ファイルアップロード時**: ファイル保存前に検証したい場合は MultipartRequestHandler の前に配置すること。
4. **テスト時**: リクエスト単体テストではNopHandlerに差し替えてCSRF対策を無効化すること。
   ```xml
   <component name="csrfTokenVerificationHandler" class="nablarch.test.NopHandler" />
   ```

参照: component/handlers/handlers-csrf-token-verification-handler.json#s3, #s4, #s5
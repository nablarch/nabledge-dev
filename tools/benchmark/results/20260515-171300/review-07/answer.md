**結論**: NablarchにはCSRF対策専用の `CsrfTokenVerificationHandler`（CSRFトークン検証ハンドラ）が用意されており、ハンドラ構成に追加するだけでCSRF対策を実現できます。アプリケーションプログラマが個別に実装する必要はありません。

**根拠**:

`CsrfTokenVerificationHandler` はトークンを使った一般的なCSRF対策を提供します。処理の流れ：

1. セッションストアからCSRFトークンを取得（なければ生成して保存）
2. HTTPリクエストが検証対象か判定（`GET`/`HEAD`/`TRACE`/`OPTIONS` は対象外、`POST`/`PUT` 等は対象）
3. 検証対象の場合、リクエストからCSRFトークンを取得して検証
4. 検証失敗時は `400 Bad Request` を返す

CSRFトークンの取得元：
- HTTPリクエストヘッダ: `X-CSRF-TOKEN`
- HTTPリクエストパラメータ: `csrf-token`

基本設定：

```xml
<component name="webFrontController" class="nablarch.fw.web.servlet.WebFrontController">
  <property name="handlerQueue">
    <list>
      <component-ref name="sessionStoreHandler" />
      <component-ref name="nablarchTagHandler"/>
      <component-ref name="csrfTokenVerificationHandler"/>
    </list>
  </property>
</component>

<component name="csrfTokenVerificationHandler"
           class="nablarch.fw.web.handler.CsrfTokenVerificationHandler" />
```

ログイン時のトークン再生成（セッションIDのみ再生成する実装の場合）：

```java
CsrfTokenUtil.regenerateCsrfToken(request);
```

**注意点**:

- ハンドラの配置順: `SessionStoreHandler` より後ろ、JSPカスタムタグ使用時は `NablarchTagHandler` より後ろに配置すること
- ファイルアップロード時: ファイル保存前に検証したい場合は `MultipartHandler` の前に配置する
- リクエスト単体テスト: テスト時は `NopHandler` に差し替えて無効化する
- セキュリティチェックリストでは `CsrfTokenVerificationHandler` の使用を推奨

**参照**: `component/handlers/handlers-csrf-token-verification-handler.json#s3`, `component/handlers/handlers-csrf-token-verification-handler.json#s4`, `component/handlers/handlers-csrf-token-verification-handler.json#s5`, `check/security-check/security-check-2.チェックリスト.json#s31`
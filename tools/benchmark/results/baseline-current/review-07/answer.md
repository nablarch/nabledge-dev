**結論**: NablarchにはCSRF対策用の `CsrfTokenVerificationHandler` が提供されており、ハンドラ構成に追加するだけでCSRFトークンの生成・検証が自動的に行われます。JSP画面（Nablarchカスタムタグ使用）では、トークンが画面に自動出力されるためアプリケーション側の追加実装は不要です。

**根拠**:

基本的な仕組み:
- `CsrfTokenVerificationHandler` をハンドラ構成に追加すると、POST等のリクエスト時にCSRFトークンの検証が自動実行される
- GET / HEAD / TRACE / OPTIONS は検証対象外（デフォルト動作）
- 検証失敗時は HTTP 400 (BadRequest) を返す
- CSRFトークンはセッションストア（`nablarch_csrf-token` キー）に格納される

ハンドラ設定例（JSP画面の場合）:

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

**注意点**:

1. ハンドラの配置順序が重要（制約）:
   - `SessionStoreHandler` より後ろに配置すること
   - JSPカスタムタグを使用する場合は `NablarchTagHandler` より後ろに配置すること

2. ファイルアップロードを使う場合: ファイル保存前にCSRFトークン検証を行いたい場合は、マルチパートリクエストハンドラの前に本ハンドラ・セッションストアハンドラを配置すること

3. ログイン時のトークン再生成: セッションIDのみ再生成（セッションストアは破棄しない）実装の場合は、`CsrfTokenUtil.regenerateCsrfToken()` を明示的に呼び出してCSRFトークンも再生成すること

4. リクエスト単体テスト: テスティングフレームワーク使用時は `NopHandler` に差し替えて無効化すること:
```xml
<component name="csrfTokenVerificationHandler" class="nablarch.test.NopHandler" />
```

参照: component/handlers/handlers-csrf-token-verification-handler.json#s3, component/handlers/handlers-csrf-token-verification-handler.json#s4, component/handlers/handlers-csrf-token-verification-handler.json#s5
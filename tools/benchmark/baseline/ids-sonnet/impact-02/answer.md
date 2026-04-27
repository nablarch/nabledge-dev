**結論**: `CsrfTokenVerificationHandler` をハンドラキューに追加するだけで CSRF 対策が有効になる。セッションストアハンドラおよびカスタムタグハンドラとの**順序**が重要。

**根拠**:

① **ハンドラの追加と順序**

以下の順序でハンドラキューに設定する必要がある。`sessionStoreHandler` → `nablarchTagHandler` → `csrfTokenVerificationHandler` の順が必須。

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
（`component/handlers/handlers-csrf_token_verification_handler.json:s4`）

② **デフォルト動作**

- トークンは UUID v4 で生成、セッションストアに `nablarch_csrf-token` という名前で格納される
- `GET`/`HEAD`/`TRACE`/`OPTIONS` は検証対象外、`POST`/`PUT` 等が検証対象
- クライアントからのトークン送信方法: HTTP ヘッダ `X-CSRF-TOKEN` またはパラメータ `csrf-token`
- 検証失敗時は 400 Bad Request を返す
（`component/handlers/handlers-csrf_token_verification_handler.json:s4`）

③ **ログイン時のトークン再生成**

ログイン時にセッションストアを破棄して再生成しない実装（セッション ID 再生成のみ）の場合、`CsrfTokenUtil.regenerateCsrfToken` を呼ぶこと。これを怠ると、セッション固定攻撃と組み合わせてログイン後に攻撃リクエストを送り込まれる危険がある。（`component/handlers/handlers-csrf_token_verification_handler.json:s5`）

**注意点**:

- **テスト時**: テスティングフレームワークでリクエスト単体テストを実施すると正しい画面遷移を経由しないためトークン検証に失敗する。テスト環境では `csrfTokenVerificationHandler` を `NopHandler` に差し替えて無効化すること。（`component/handlers/handlers-csrf_token_verification_handler.json:s4`）
- **カスタムタグとの相性**: `nablarchTagHandler` より後に `csrfTokenVerificationHandler` を配置すること。順序が逆になるとトークンがセッションに格納される前に検証が走り、正常動作しない。（`component/handlers/handlers-csrf_token_verification_handler.json:s4`）
- **セッションストアとの相性**: セッションストアハンドラ（`SessionStoreHandler`）は `csrfTokenVerificationHandler` より先に配置する必要がある。CSRFトークンはセッションストアに保存されるため、セッションストアが初期化される前に検証ハンドラが動くと失敗する。（`component/handlers/handlers-csrf_token_verification_handler.json:s4`, `component/handlers/handlers-SessionStoreHandler.json:s5`）

参照: component/handlers/handlers-csrf_token_verification_handler.json:s4, component/handlers/handlers-csrf_token_verification_handler.json:s5, component/handlers/handlers-SessionStoreHandler.json:s5
**結論**: Nablarch の CSRF 対策には `CsrfTokenVerificationHandler` を使う。セッションストアとの連携が必須で、JSP カスタムタグを使う場合はハンドラの配置順に注意が必要。ログイン時のトークン再生成も必須。

**根拠**:

**① 追加する設定（最小構成）**

`component/handlers/handlers-csrf_token_verification_handler.json:s1` より、クラス名は `nablarch.fw.web.handler.CsrfTokenVerificationHandler`。

`component/handlers/handlers-csrf_token_verification_handler.json:s4` より、コンポーネント定義に追加し、ハンドラキューに組み込む：

```xml
<!-- コンポーネント定義 -->
<component name="csrfTokenVerificationHandler"
           class="nablarch.fw.web.handler.CsrfTokenVerificationHandler" />

<!-- ハンドラキュー（順序が重要） -->
<component-ref name="sessionStoreHandler" />
<component-ref name="nablarchTagHandler"/>
<component-ref name="csrfTokenVerificationHandler"/>
```

デフォルト動作：UUID v4 でトークン生成、セッションストア格納名 `nablarch_csrf-token`、`GET`/`HEAD`/`TRACE`/`OPTIONS` は検証対象外（`POST`/`PUT` 等は検証）、検証失敗時は BadRequest (400)。

**② セッションとの相性（必須）**

`component/handlers/handlers-csrf_token_verification_handler.json:s3` より、CSRFトークンはセッションストアに格納されるため **セッションストアの使用が必須**。ハンドラキュー内で **`session_store_handler` より後ろ** に配置すること。

**③ JSP カスタムタグとの相性（必須）**

同じく `s3` より、JSP カスタムタグ（`<n:form>` 等）はhidden暗号化（`tag-hidden_encryption`）を使ってCSRFトークンを出力する。そのため **`nablarch_tag_handler` より後ろ** に配置すること。つまりキューの順序は：`sessionStoreHandler` → `nablarchTagHandler` → `csrfTokenVerificationHandler`。

**④ ログイン時のトークン再生成（重要）**

`component/handlers/handlers-csrf_token_verification_handler.json:s5` および `component/libraries/libraries-session_store.json:s6` より、ログイン時にCSRFトークンを再生成しないとセッション固定攻撃に悪用される恐れがある。

- セッションIDのみ変更する実装の場合 → **`CsrfTokenUtil.regenerateCsrfToken(ctx)` の呼び出しが必須**
- セッションストア全体を破棄・再生成する実装の場合 → 不要（トークンも一緒に破棄される）

```java
// ログイン処理
SessionUtil.changeId(ctx);                          // セッションID変更
CsrfTokenUtil.regenerateCsrfToken(ctx);             // CSRFトークン再生成
SessionUtil.put(ctx, "user", user, "db");           // ユーザ情報格納
```

**注意点**:

- **テスト時は無効化が必要**: リクエスト単体テストは正しい画面遷移を経由しないため、CSRFトークン検証が失敗する。テスト環境では `csrfTokenVerificationHandler` を `NopHandler` に差し替えること（`component/handlers/handlers-csrf_token_verification_handler.json:s4`）：
  ```xml
  <component name="csrfTokenVerificationHandler" class="nablarch.test.NopHandler" />
  ```
- **ファイルアップロード時の考慮**: multipart_handler を使うファイルアップロードで、ファイル保存前にCSRF検証したい場合は `multipart_handler` の前に `session_store_handler` と `csrfTokenVerificationHandler` を配置すること（`s3`）。
- **設定名のカスタマイズ**: `WebConfig` で `csrfTokenHeaderName`（デフォルト: `X-CSRF-TOKEN`）、`csrfTokenParameterName`（デフォルト: `csrf-token`）等を変更可能（`s4`）。

参照: component/handlers/handlers-csrf_token_verification_handler.json:s1, component/handlers/handlers-csrf_token_verification_handler.json:s3, component/handlers/handlers-csrf_token_verification_handler.json:s4, component/handlers/handlers-csrf_token_verification_handler.json:s5, component/libraries/libraries-session_store.json:s6
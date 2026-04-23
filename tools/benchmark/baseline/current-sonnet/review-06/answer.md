**結論**: NablarchにはCSRF対策の標準機能として `CsrfTokenVerificationHandler` が用意されている。ハンドラキューに追加するだけで、セッションに紐づいた一意トークンを自動発行・検証し、外部サイトからの不正POSTをブロックできる。

---

**根拠**:

**① 仕組みの概要** (`check/security-check/security-check.json:s1`)
CSRF対策機能は一意なトークンを発行してサーバサイドでチェックすることで不正な画面遷移を防止する。`GET`/`HEAD`/`TRACE`/`OPTIONS` は検証対象外で、`POST`/`PUT` など状態変更を伴うメソッドが検証対象となる。

**② ハンドラの設定方法** (`component/handlers/handlers-csrf_token_verification_handler.json:s4`)
`nablarch.fw.web.handler.CsrfTokenVerificationHandler` をハンドラキューに登録する。

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

デフォルト動作:
- トークン生成: UUID v4（`UUIDv4CsrfTokenGenerator`）
- セッションストア格納名: `nablarch_csrf-token`
- トークンの受け取り: HTTPヘッダ `X-CSRF-TOKEN` またはHTTPパラメータ `csrf-token`
- 検証失敗時: `BadRequest (400)` を返す

**③ ハンドラの配置順序** (`component/handlers/handlers-csrf_token_verification_handler.json:s3`)
以下の順序制約が必須:
- `session_store_handler` より **後ろ** に配置（トークンはセッションストアに格納するため）
- `nablarch_tag_handler` より **後ろ** に配置（カスタムタグでCSRFトークンを隠しフィールドに出力するため）
- ファイルアップロード（`multipart_handler`）でアップロード保存前に検証したい場合は、`multipart_handler` より **前** に本ハンドラと `session_store_handler` を配置

**④ ログイン時のトークン再生成** (`component/handlers/handlers-csrf_token_verification_handler.json:s5`)
ログイン時にCSRFトークンを再生成しないと、トークン固定攻撃のリスクがある。
- セッションストアを破棄して再生成する実装なら自動的に新トークンが生成されるため追加対応不要
- セッションIDの再生成のみ行う実装の場合は `CsrfTokenUtil.regenerateCsrfToken` をログイン処理内で呼び出すこと

**⑤ WebConfigによるカスタマイズ** (`component/handlers/handlers-csrf_token_verification_handler.json:s4`)
`nablarch.common.web.WebConfig` で以下の名称を変更可能:

| プロパティ | デフォルト値 |
|---|---|
| `csrfTokenHeaderName` | `X-CSRF-TOKEN` |
| `csrfTokenParameterName` | `csrf-token` |
| `csrfTokenSessionStoredVarName` | `nablarch_csrf-token` |

---

**注意点**:

1. **セッションストアは必須**: `CsrfTokenVerificationHandler` はトークンをセッションストアに格納するため、`session_store` の使用が必須（`component/handlers/handlers-csrf_token_verification_handler.json:s3`）。

2. **二重サブミット防止機能との関係** (`check/security-check/security-check.json:s1`): HttpSessionを使った二重サブミット防止もCSRF対策として機能するが、実装漏れが発生しやすいため `CsrfTokenVerificationHandler` の使用を推奨。データベースを使った二重サブミット防止機能はCSRF対策に対応していないため、その場合は必ず `CsrfTokenVerificationHandler` を併用すること。

3. **テスト時の注意** (`component/handlers/handlers-csrf_token_verification_handler.json:s4`): リクエスト単体テストでは正しい画面遷移を経由しないためCSRFトークン検証が失敗する。テスト設定で `csrfTokenVerificationHandler` を `NopHandler` に差し替えて無効化すること。

4. **RESTfulウェブサービス**: `CsrfTokenUtil` でトークンを取得し、クライアントにトークンを渡す仕組みをプロジェクト側で実装する必要がある（`component/handlers/handlers-csrf_token_verification_handler.json:s4`）。

参照: component/handlers/handlers-csrf_token_verification_handler.json:s1, component/handlers/handlers-csrf_token_verification_handler.json:s3, component/handlers/handlers-csrf_token_verification_handler.json:s4, component/handlers/handlers-csrf_token_verification_handler.json:s5, check/security-check/security-check.json:s1
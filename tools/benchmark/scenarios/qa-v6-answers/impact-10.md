**質問**: ログインしたユーザーの情報 (ID、名前、権限) を画面遷移中も保持して、認可チェックのときに参照したい。Nablarch ではどこに持つのが推奨？

---

**結論**: 認証情報は Nablarch のセッションストア、特に **DB ストア** に持つのが推奨。`SessionUtil` で保存し、認可チェックハンドラ（`PermissionCheckHandler`）が `Permission` をスレッドローカルに設定するので、業務アクションやサーバサイドチェック・画面表示制御でスレッドローカル経由で参照できる。 — `component/libraries/libraries-session_store.json#s6`、`component/libraries/libraries-permission_check.json#s1`

**① 保存先: DB ストア**
認証情報を保持する場合は **DB ストア** を使用する。ログイン時は以下のように書く:

```java
// ログイン前にセッションIDを変更する
SessionUtil.changeId(ctx);

// CSRFトークンを再生成する（CSRFトークン検証ハンドラを使用している場合）
CsrfTokenUtil.regenerateCsrfToken(ctx);

// ログインユーザの情報をセッションストアに保存
SessionUtil.put(ctx, "user", user, "db");
```
ログアウト時は `SessionUtil.invalidate(ctx)` でセッションストア全体を破棄する。 — `component/libraries/libraries-session_store.json#s6`

**② ログイン時の CSRF トークン再生成**
以下の条件をすべて満たす場合、ログイン時に CSRF トークンの再生成が必要:
- `CsrfTokenVerificationHandler` を使用している
- ログイン時にセッション ID の変更のみを行う（セッション情報は維持する） — `component/libraries/libraries-session_store.json#s6`

**③ セッションストアの設定**
`SessionStoreHandler` の設定に加えて、`SessionManager` を `sessionManager` コンポーネント名で登録する。`availableStores` に `DbStore` を含め、`defaultStoreName` を `db` にする。DB ストア使用時は `USER_SESSION` テーブルが必要:

| カラム名 | データ型 |
|---|---|
| SESSION_ID (PK) | `java.lang.String` |
| SESSION_OBJECT | `byte[]` |
| EXPIRATION_DATETIME | `java.sql.Timestamp` |

`SESSION_ID` は CHAR ではなく **VARCHAR** で定義する（Oracle で正常に動作しないケースあり）。 — `component/libraries/libraries-session_store.json#s4`

**④ 認可チェックでの参照**
`PermissionCheckHandler` は、スレッドコンテキスト上のリクエスト ID とユーザ ID をもとに認可チェックし、権限があれば `Permission` をスレッドローカルに設定する。業務ロジック側ではスレッドローカルから参照する。権限管理の条件が変わる可能性があるシステムでは `permission_check` を、そうでなければ `role_check` を使う。 — `component/libraries/libraries-permission_check.json#s1`

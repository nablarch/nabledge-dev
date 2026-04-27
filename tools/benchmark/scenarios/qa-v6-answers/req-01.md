**質問**: ログイン認証の仕組みを作りたい。ユーザー名とパスワードで認証して、ログイン状態を保持する。Nablarch にビルトインのログイン機能はある？

---

**結論**: **認証機能はビルトイン提供されていない**。認証はプロジェクト要件により仕様が異なるため、フレームワークとしては提供しておらず、プロジェクト側で実装する必要がある。ただし **認証情報の保持** には Nablarch のセッションストア（DB ストア）を使う仕組みが用意されており、ログイン時には `SessionUtil.changeId` でセッション ID を変更し、`CsrfTokenUtil.regenerateCsrfToken` で CSRF トークンを再生成してから認証情報を保存する。 — `processing-pattern/web-application/web-application-feature_details.json#s13`、`component/libraries/libraries-session_store.json#s6`

**① 認証ロジック自体は非提供**
> 認証はプロジェクト要件により仕様が異なるため、フレームワークとしては提供していない。プロジェクト要件に合わせて PJ で実装すること。

— `processing-pattern/web-application/web-application-feature_details.json#s13`

**② 認証情報の保持は Nablarch 側で用意されている**
認証情報を保持する場合は **DB ストア** を使用する。ログイン時の典型的な実装:

```java
// ログイン前にセッションIDを変更する
SessionUtil.changeId(ctx);

// CSRFトークンを再生成する（CSRFトークン検証ハンドラを使用している場合）
CsrfTokenUtil.regenerateCsrfToken(ctx);

// ログインユーザの情報をセッションストアに保存
SessionUtil.put(ctx, "user", user, "db");
```

ログアウト時は `SessionUtil.invalidate(ctx)` でセッションストア全体を破棄する。 — `component/libraries/libraries-session_store.json#s6`

**③ ログイン時の CSRF トークン再生成**
以下の条件をすべて満たす場合、ログイン時に CSRF トークンの再生成が必要:
- `CsrfTokenVerificationHandler` を使用している
- ログイン時にセッション ID の変更のみを行う（セッション情報は維持する） — `component/libraries/libraries-session_store.json#s6`

**結論**: Nablarch にはログイン機能そのものは組み込まれていないが、**パスワード認証のビジネスサンプル**（`nablarch-password-authentication`）と**セッションストア**機能を組み合わせることで、ユーザー名・パスワード認証＋ログイン状態保持を実装できる。

---

**根拠**:

**① ログイン機能はビルトインではなく、ビジネスサンプルとして提供**

Nablarch はログイン処理を実行する業務処理自体は提供しない。プロジェクトが要件に応じてログイン処理を作成する必要がある。ただし、パスワード認証のサンプル実装（`nablarch-password-authentication`）が用意されており、これを元に実装する。 — `guide/biz-samples/biz-samples-01.json:s2`

**② 認証処理の主要クラス構成**

- `PasswordAuthenticator` インタフェース / 実装: `SystemAccountAuthenticator`（DBのアカウント情報でパスワード認証）
- `PasswordEncryptor` インタフェース / 実装: `PBKDF2PasswordEncryptor`（PBKDF2＋ソルト＋ストレッチング）
- ユーティリティ: `AuthenticationUtil`（システムリポジトリからコンポーネントを取得してラップ）
- 例外: `AuthenticationFailedException` / `UserIdLockedException` / `PasswordExpiredException` / 基底 `AuthenticationException`

— `guide/biz-samples/biz-samples-01.json:s3`

**③ 認証処理の呼び出し方**

```java
try {
    AuthenticationUtil.authenticate(userId, password);
} catch (AuthenticationFailedException e) {
    // 認証失敗
} catch (UserIdLockedException e) {
    // ユーザIDロック
} catch (PasswordExpiredException e) {
    // パスワード有効期限切れ
}
```
細かく処理しない場合は基底例外 `AuthenticationException` で捕捉可能。 — `guide/biz-samples/biz-samples-01.json:s7`

**④ 認証の機能特徴**

- 有効日（From/To）チェック
- パスワード有効期限チェック
- 連続認証失敗によるアカウントロック（`failedCountToLock` で設定、0=ロック無効）
- PBKDF2 によるパスワード暗号化（ストレッチング回数・ソルトはプロジェクト設定）
- 認証成功時のみ最終ログイン日時を更新

— `guide/biz-samples/biz-samples-01.json:s5`

**⑤ ログイン状態の保持はセッションストアで行う**

認証成功後のログイン状態保持には **DBストアまたはHTTPセッションストア** を使用する。ログイン時のセッション操作の典型パターン：

```java
// ログイン前にセッションIDを変更（セッション固定攻撃対策）
SessionUtil.changeId(ctx);
// CSRFトークンを再生成（CSRF検証ハンドラ使用時）
CsrfTokenUtil.regenerateCsrfToken(ctx);
// ログインユーザー情報をDBストアに保存
SessionUtil.put(ctx, "user", user, "db");
```

ログアウト時は `SessionUtil.invalidate(ctx)` でセッションストア全体を破棄する。 — `component/libraries/libraries-session_store.json:s6`

認証情報の保持にはDBストアまたはHTTPセッションストアが推奨。DBストアはAPサーバ停止時もセッションを復元できる点で優れている。 — `component/libraries/libraries-session_store.json:s1`

---

**注意点**:

- `SystemAccountAuthenticator` は個別アプリケーションとは別のトランザクション（`dbTransactionName: "authenticator"`）で動かすこと。個別アプリケーション側でこのトランザクション名を使用してはいけない。 — `guide/biz-samples/biz-samples-01.json:s6`
- DBのアカウントテーブル（`SYSTEM_ACCOUNT`）定義はサンプルを参考に、プロジェクト要件に合わせて再設計すること。サンプルのエンティティクラスは gsp-dba-maven-plugin で自動生成したものに差し替えること。 — `guide/biz-samples/biz-samples-01.json:s4`
- PBKDF2 のストレッチング回数やソルトは各プロジェクトで必ず設定すること。 — `guide/biz-samples/biz-samples-01.json:s2`
- CSRFトークン検証ハンドラを使用している場合、ログイン時にセッションIDを変更するだけでなく `CsrfTokenUtil.regenerateCsrfToken` も呼ぶ必要がある。 — `component/libraries/libraries-session_store.json:s6`

参照: `guide/biz-samples/biz-samples-01.json:s2`, `guide/biz-samples/biz-samples-01.json:s3`, `guide/biz-samples/biz-samples-01.json:s4`, `guide/biz-samples/biz-samples-01.json:s5`, `guide/biz-samples/biz-samples-01.json:s6`, `guide/biz-samples/biz-samples-01.json:s7`, `component/libraries/libraries-session_store.json:s1`, `component/libraries/libraries-session_store.json:s6`
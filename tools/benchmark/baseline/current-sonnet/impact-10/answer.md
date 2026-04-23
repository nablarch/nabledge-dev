**結論**: ログインユーザーの **ユーザーID** は `ThreadContext`（スレッドコンテキスト）に持ち、**権限（ロール）** はセッションストア（DBストアまたはHTTPセッションストア）に保持するのが Nablarch の推奨パターンです。名前などのその他ユーザー情報も認証情報として同じくセッションストアに保存できます。

---

**根拠**:

1. **ユーザーID → ThreadContext に保持** (`component/handlers/handlers-thread_context_handler.json:s5`)
   - `ThreadContextHandler` に `UserIdAttributeInSessionStore` を設定すると、各リクエストの往路処理でセッションストアからユーザーIDを読み取り `ThreadContext` にセットされます。以降のハンドラや業務アクションは `ThreadContext.getUserId()` で取得できます。
   - ログイン時にアプリ側でセッションに書き込む例: `SessionUtil.put(context, "user.id", userId);`

2. **権限（ロール）→ セッションストア（DBストア推奨）に保持** (`component/libraries/libraries-role_check.json:s3`, `component/libraries/libraries-role_check.json:s4`)
   - ログイン成功時に `SessionStoreUserRoleUtil.save(userRoles, executionContext)` でロールリストをセッションストアへ保存します。
   - 認可チェック（`@CheckRole` アノテーションや `CheckRoleUtil.checkRole()`）は `ThreadContext.getUserId()` でユーザーIDを取得し、`SessionStoreUserRoleResolver` がセッションストアのロール情報を参照して判定します。

3. **認証情報（ユーザーID・名前など）の保存先はDBストアが第一候補** (`component/libraries/libraries-session_store.json:s1`, `component/libraries/libraries-session_store.json:s6`)
   - Nablarch の公式ガイドでは「認証情報の保持」用途に **DBストアまたはHTTPセッションストア** を推奨しています。DBストアはAPサーバー停止後もセッションが復元でき、スケールアウト時にも扱いやすい利点があります。
   - ログイン時の典型実装: `SessionUtil.changeId(ctx)` でセッションIDを変更 → `CsrfTokenUtil.regenerateCsrfToken(ctx)` → `SessionUtil.put(ctx, "user", user, "db")` でユーザー情報をDBストアへ保存。
   - ログアウト時は `SessionUtil.invalidate(ctx)` でセッション全体を破棄します。

---

**注意点**:
- `ThreadContext` はスレッドローカルのため、リクエストをまたいで情報を保持しません。ユーザーIDは毎リクエストで `ThreadContextHandler` がセッションストアから読み直します。したがって「画面遷移をまたいだ保持」の実体はセッションストア側です。
- セッションストアを使用する場合は `session_store_handler`（`SessionStoreHandler`）をハンドラキューに組み込む必要があります。
- ユーザーID以外（名前など）も保持したい場合は、ログインオブジェクト（LoginUserPrincipal 等のプロジェクト定義 Bean）をセッションストアに格納し、`UserIdAttribute#getUserIdSession` をオーバーライドしてそこからIDを返す実装を `ThreadContextHandler` に設定します (`component/handlers/handlers-thread_context_handler.json:s5`)。

参照: component/handlers/handlers-thread_context_handler.json:s5, component/libraries/libraries-role_check.json:s3, component/libraries/libraries-role_check.json:s4, component/libraries/libraries-session_store.json:s1, component/libraries/libraries-session_store.json:s6
**結論**: ログインユーザーの情報（ID・名前・権限）は **セッションストア（DBストア推奨）** に保持するのが Nablarch の推奨方法です。ロールベースの認可チェックには `SessionStoreUserRoleUtil` を使い、ログイン時にロールをセッションストアへ保存します。

---

**根拠**:

**1. 認証情報の保持先は DBストア**

セッションストアの用途対応表において、「認証情報の保持」には **DBストア または HTTPセッションストア** が推奨されています。DBストアはローリングメンテナンス等でAPサーバが停止しても復元可能で、ヒープを圧迫しない利点があります。
（`component/libraries/libraries-session_store.json:s1`）

**2. ログイン時の保存コード例**

```java
// セッションIDを変更してからDBストアへ保存
SessionUtil.changeId(ctx);
SessionUtil.put(ctx, "user", user, "db");
```
（`component/libraries/libraries-session_store.json:s6`）

**3. ロール（権限）はセッションストアに別途保存**

ロールベース認可では、ログイン時に `SessionStoreUserRoleUtil.save()` でロールをセッションストアへ保存します。以降の認可チェックはこのセッション情報を参照します。

```java
List<String> userRoles = resolveUserRoles(loginId);
SessionStoreUserRoleUtil.save(userRoles, executionContext);
```

その後のアクションには `@CheckRole` アノテーションで認可チェックを宣言します。

```java
@CheckRole(Roles.ROLE_ADMIN)
public HttpResponse index(HttpRequest request, ExecutionContext context) { ... }
```

コンポーネント定義では `SessionStoreUserRoleResolver` を使用します。
（`component/libraries/libraries-role_check.json:s3`）

**4. リクエスト単位の認可チェック**

`PermissionCheckHandler` を使う場合は、ユーザーが現在のリクエストIDに対して権限を持つかをチェックし、権限がなければ `403 Forbidden` を返します。
（`component/handlers/handlers-permission_check_handler.json:s4`）

---

**注意点**:
- DBストアを使用する場合は `USER_SESSION` テーブル（SESSION_ID は VARCHAR）の作成が必要です。(`component/libraries/libraries-session_store.json:s4`)
- ログイン時はセッションID変更（`SessionUtil.changeId`）と、CSRFトークン検証ハンドラ使用時は CSRFトークンの再生成も必須です。(`component/libraries/libraries-session_store.json:s6`)
- 認証ロジック自体はフレームワーク非提供でプロジェクト実装が必要です。(`processing-pattern/web-application/web-application-feature_details.json:s13`)
- 同一セッションの処理が複数スレッドで実行された場合は後勝ちになるため、DBストアでも並行アクセス時にデータが消失する可能性があります。

参照: `component/libraries/libraries-session_store.json:s1`, `component/libraries/libraries-session_store.json:s6`, `component/libraries/libraries-session_store.json:s4`, `component/libraries/libraries-role_check.json:s3`, `component/handlers/handlers-permission_check_handler.json:s4`, `processing-pattern/web-application/web-application-feature_details.json:s13`
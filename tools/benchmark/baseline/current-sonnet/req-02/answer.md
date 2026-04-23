**結論**: Nablarch には標準の認可チェック機能が2種類ある。アクションメソッド単位でロール（役割）によるアクセス制限を行うなら **`authorization/role_check`（`@CheckRole` アノテーション）** が最も手軽。権限の組み合わせをデータで管理したい複雑なケースには **`authorization/permission_check`（`PermissionCheckHandler`）** を使う。

---

**根拠**:

**【2種類の認可チェック機能】**
Nablarch は以下の2機能を提供している (`component/libraries/libraries-permission_check.json:s1`):
- `authorization/role_check` — アノテーションで機能にロールを割り当て、ユーザがそのロールを持つかで判定。権限構成が固定されたシステム向け。
- `authorization/permission_check` — ハンドラ（`PermissionCheckHandler`）でリクエストIDごとに認可判定。権限の組み合わせが変わりやすいシステム向け。

**【role_check の実装手順】**

① **ログイン時にロールをセッションに保存** (`component/libraries/libraries-role_check.json:s3`):
```java
List<String> userRoles = resolveUserRoles(loginId); // DBなどから取得（実装はプロジェクト任意）
SessionStoreUserRoleUtil.save(userRoles, executionContext);
```

② **アクションメソッドに `@CheckRole` を付与** (`component/libraries/libraries-role_check.json:s1`):
```java
@CheckRole(Roles.ROLE_ADMIN)
public HttpResponse index(HttpRequest request, ExecutionContext context) { ... }
```
指定ロールを持たないユーザは `Forbidden(403)` となる。

③ **複数ロールの AND/OR 指定** (`component/libraries/libraries-role_check.json:s3`):
```java
// OR条件（どちらかのロールがあればOK）
@CheckRole(value = {Roles.ROLE_ADMIN, Roles.ROLE_PROJECT_MANAGER}, anyOf = true)
```

④ **JSP の表示制御**（ロールチェック用カスタムタグは非提供。`CheckRoleUtil` でサーバ側判定しセッション経由でJSPに渡す）(`component/libraries/libraries-role_check.json:s3`):
```java
userContext.setAdmin(CheckRoleUtil.checkRole(Roles.ROLE_ADMIN, executionContext));
SessionUtil.put(executionContext, "userContext", userContext);
```

**【コンポーネント設定】**
`BasicRoleEvaluator` と `SessionStoreUserRoleResolver` を登録する（`component/libraries/libraries-role_check.json:s3`）。デフォルトコンフィグレーション利用時は以下でも可:
```xml
<import file="nablarch/common/authorization/role/session/authorization-session.xml" />
```

**【PermissionCheckHandler（handler方式）】**
`PermissionCheckHandler` をハンドラキューに追加すると、リクエストIDとユーザIDを基に認可判定を行い、権限がない場合は `Forbidden(403)` を送出する (`component/handlers/handlers-permission_check_handler.json:s4`)。`ThreadContextHandler` より後ろに配置する必要がある (`component/handlers/handlers-permission_check_handler.json:s3`)。

---

**注意点**:
- `role_check` はロールと機能の組み合わせをアノテーションに書くため、組織変更で権限が頻繁に変わるシステムでは `permission_check` を推奨（変更ごとにアノテーションの書き換えが必要になる）(`component/libraries/libraries-role_check.json:s1`)
- Nablarch は**認証機能**（ログイン処理自体）は提供していない。Nablarch Example の実装例を参考にプロジェクトで実装する必要がある (`check/security-check/security-check.json:s1`)
- JSP 用の認可チェックカスタムタグは提供されていないため、表示制御はサーバ側でロール判定した結果をセッションに保存し、EL式/JSTLで制御する (`component/libraries/libraries-role_check.json:s3`)

参照: `component/libraries/libraries-permission_check.json:s1`, `component/libraries/libraries-role_check.json:s1`, `component/libraries/libraries-role_check.json:s2`, `component/libraries/libraries-role_check.json:s3`, `component/libraries/libraries-role_check.json:s4`, `component/libraries/libraries-role_check.json:s5`, `component/handlers/handlers-permission_check_handler.json:s1`, `component/handlers/handlers-permission_check_handler.json:s3`, `component/handlers/handlers-permission_check_handler.json:s4`, `check/security-check/security-check.json:s1`
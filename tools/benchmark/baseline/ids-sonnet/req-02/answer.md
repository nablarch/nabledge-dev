**結論**: Nablarch には権限チェックの仕組みが標準で2種類用意されている。`permission_check`（ハンドラ方式）と `role_check`（アノテーション方式）で、システムの要件に応じて使い分ける。

**根拠**:

① **2種類の認可チェック機能**
Nablarch は以下の2つを提供している（`component/libraries/libraries-permission_check.json:s1`）:
- `authorization/permission_check` — リクエストIDベースで、権限管理条件が変わる可能性のある複雑なシステム向け
- `authorization/role_check` — ロール（役割）ベースで、権限条件が固定的な場合に素早く導入できる簡易版

② **ハンドラ方式（permission_check）**
`PermissionCheckHandler` をハンドラキューに組み込むと、ログイン中ユーザが現在のリクエストIDに対して権限を持つか自動チェックする。権限があれば後続ハンドラへ、権限がなければ `Forbidden(403)` を送出する（`component/handlers/handlers-permission_check_handler.json:s4`）。

ログイン前のリクエストなどチェック不要なパスは `ignoreRequestIds` で除外できる（`component/handlers/handlers-permission_check_handler.json:s6`）:
```xml
<property name="ignoreRequestIds" value="/action/login,/action/logout" />
```

③ **アノテーション方式（role_check）**
アクションメソッドに `@CheckRole` を付与し、必要なロールを指定する。ユーザがそのロールを持たない場合は `Forbidden` がスローされる（`component/libraries/libraries-role_check.json:s1`）:
```java
@CheckRole(Roles.ROLE_ADMIN)
public HttpResponse index(HttpRequest request, ExecutionContext context) { ... }
```
ログイン時にユーザのロールを解決して `SessionStoreUserRoleUtil.save()` でセッションに保存し、以降の認可チェックはセッション情報を使う（`component/libraries/libraries-role_check.json:s3`）。

④ **JSPでの表示制御**
JSP用カスタムタグは提供されていないが、サーバー側で `CheckRoleUtil.checkRole()` の結果をセッションに保存し、JSP側で EL式/JSTL（`c:if`）を使って表示・非表示を制御できる（`component/libraries/libraries-role_check.json:s3`）。

**注意点**:
- 権限管理条件が変わる可能性があるシステム（部署ごとに権限が異なるなど）では `permission_check` を推奨。`role_check` はロールと機能の組み合わせを変えるたびにアノテーションの書き換えが必要になる（`component/libraries/libraries-role_check.json:s1`）。
- エラー時に表示するページは `HttpErrorHandler` で別途設定する（`component/handlers/handlers-permission_check_handler.json:s5`）。

参照: component/libraries/libraries-permission_check.json:s1, component/handlers/handlers-permission_check_handler.json:s4, component/handlers/handlers-permission_check_handler.json:s5, component/handlers/handlers-permission_check_handler.json:s6, component/libraries/libraries-role_check.json:s1, component/libraries/libraries-role_check.json:s3
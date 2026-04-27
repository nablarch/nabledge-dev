**結論**: Nablarchでできます。`permission_check_handler`（`PermissionCheckHandler`）を使えば、内部フォワード先のアクションに対しても認可チェックをかけられます。また、`role_check`（`@CheckRole` アノテーション）を使う場合はフォワード先のアクションメソッドにも同様にアノテーションを付けることで対応できます。

---

**根拠**:

**① `PermissionCheckHandler` による認可チェック（ハンドラ方式）**

`PermissionCheckHandler` はリクエストIDをキーに認可チェックを行うハンドラです。内部フォワード先のリクエストIDでチェックするには、`setUsesInternalRequestId` を `true` に設定します。
(`component/handlers/handlers-permission_check_handler.json:s4`)

> チェック対象のリクエストIDをフォーワード先のリクエストIDに変更する場合は、`PermissionCheckHandler.setUsesInternalRequestId` で `true` を指定する（デフォルト: `false`）。

ただし、これを有効にするためにはハンドラの配置順が重要です。
(`component/handlers/handlers-permission_check_handler.json:s3`)

> `forwarding_handler` より**後ろ**に配置すること。内部フォーワード先の内部リクエストIDをもとに認可チェックしたい場合。この場合、`thread_context_handler` の `attributes` に `InternalRequestIdAttribute` を追加すること。

`InternalRequestIdAttribute` は内部フォワード時にフォワード先リクエストIDをスレッドコンテキストに保持するための設定です。
(`component/handlers/handlers-forwarding_handler.json:s6`, `component/handlers/handlers-thread_context_handler.json:s5`)

> 内部フォーワード時、フォーワード先のリクエストIDを内部リクエストIDとしてスレッドコンテキストに保持する。

**② `@CheckRole` によるアノテーション方式**

フォワード先のアクションメソッドにも `@CheckRole` アノテーションを付与することで、メソッド実行時に認可チェックが走ります。`@CheckRole` はNablarchのインターセプタ機構で動作するため、内部フォワード後に実行されるアクションでも有効です。
(`component/libraries/libraries-role_check.json:s1`, `component/libraries/libraries-role_check.json:s4`)

---

**注意点**:

- `PermissionCheckHandler` の内部リクエストID対応を使う場合、ハンドラキューの順序は次のようにする必要があります:
  1. `thread_context_handler`（`InternalRequestIdAttribute` を `attributes` に追加する）
  2. `forwarding_handler`
  3. `permission_check_handler`（`usesInternalRequestId = true`）
  （`component/handlers/handlers-permission_check_handler.json:s3`）

- `@CheckRole` 方式は認可チェックのロジックがアノテーションにハードコーディングされるため、ロールと機能の組み合わせが頻繁に変わるシステムでは `permission_check`（`PermissionCheckHandler` + データ管理）の方が適しています。
  （`component/libraries/libraries-role_check.json:s1`）

- 認可チェックから除外したいリクエスト（ログイン前など）は `PermissionCheckHandler.ignoreRequestIds` で指定できます。
  （`component/handlers/handlers-permission_check_handler.json:s6`）

参照: component/handlers/handlers-permission_check_handler.json:s3, component/handlers/handlers-permission_check_handler.json:s4, component/handlers/handlers-permission_check_handler.json:s6, component/handlers/handlers-forwarding_handler.json:s6, component/handlers/handlers-thread_context_handler.json:s5, component/libraries/libraries-role_check.json:s1, component/libraries/libraries-role_check.json:s4
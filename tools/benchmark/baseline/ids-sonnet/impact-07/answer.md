**結論**: できる。`PermissionCheckHandler` の `setUsesInternalRequestId` を `true` に設定することで、内部フォワード先のリクエストIDを認可チェック対象にできる。

**根拠**:

`PermissionCheckHandler` はログイン中のユーザが現在のリクエストIDに対して権限を持っているかをチェックする。デフォルト（`false`）では元のリクエストIDでチェックするが、`PermissionCheckHandler.setUsesInternalRequestId` に `true` を指定すると、チェック対象のリクエストIDをフォワード先のリクエストIDに変更できる。（`component/handlers/handlers-permission_check_handler.json:s4`）

内部フォワードは `forward://` から始まるコンテンツパスで実現され（`component/handlers/handlers-forwarding_handler.json:s4`）、フォワード先のリクエストIDは内部リクエストIDとしてスレッドコンテキストに保持される（`component/handlers/handlers-forwarding_handler.json:s6`）。`setUsesInternalRequestId(true)` はこの内部リクエストIDを参照してチェックを行う。

認可チェックの基盤機能としては `permission_check`（権限管理条件が変わる可能性があるシステム向け）と `role_check`（シンプルな権限管理向け）の2種類が提供されている。（`component/libraries/libraries-permission_check.json:s1`）

**注意点**:
- デフォルトは `false`（元リクエストID基準）のため、明示的に `true` に設定しないとフォワード先のアクションは認可対象にならない。
- 権限がない場合は `Forbidden(403)` が送出され、エラーページは `HttpErrorHandler` で設定する。（`component/handlers/handlers-permission_check_handler.json:s5`）
- `setUsesInternalRequestId(true)` にすると、フォワード元ではなくフォワード先のリクエストIDで権限チェックが行われる点に注意。フォワード元の認可が不要になるわけではなく、ハンドラが通過するたびにチェックが走る構造かどうかはシステム設計に依存する。

参照: component/handlers/handlers-permission_check_handler.json:s4, component/handlers/handlers-permission_check_handler.json:s5, component/handlers/handlers-forwarding_handler.json:s4, component/handlers/handlers-forwarding_handler.json:s6, component/libraries/libraries-permission_check.json:s1
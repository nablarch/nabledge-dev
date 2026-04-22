**質問**: ログイン済みユーザーの権限で画面アクセスを制限したい。ただ画面の中で内部フォワードしているところがあって、フォワード先のアクションも認可対象にしたい。Nablarch でできる？

---

**結論**: `PermissionCheckHandler`（認可チェックハンドラ）を使う。ログイン中ユーザが現在のリクエスト ID に対して権限を持つかを判定し、権限があれば `Permission` をスレッドローカルに設定、なければ 403 を返す。**内部フォワード先のリクエスト ID も認可対象にする** には、`setUsesInternalRequestId` を `true` にし、`ThreadContextHandler` の `attributes` に `InternalRequestIdAttribute` を追加する。 — `component/handlers/handlers-permission_check_handler.json#s4`、`component/handlers/handlers-permission_check_handler.json#s3`

**① 認可の仕組み**
Nablarch は2種類の認可機能を提供する:
- `permission_check`: 権限管理の条件が変わる可能性があるシステム向け（データ管理はしっかりしているが導入コストは高い）。
- `role_check`: 権限管理の条件が基本的に変わらないシステム向け（ハードコーディングで導入コストを下げる）。

権限管理の条件が変わり得るなら `permission_check` が適している。 — `component/libraries/libraries-permission_check.json#s1`

**② リクエスト認可の動作**
`PermissionCheckHandler` はログイン中ユーザが現在のリクエスト（リクエスト ID）に対して権限を持つかをチェックする:
- 権限あり: `Permission` をスレッドローカルに設定し、後続ハンドラを呼び出す。サーバサイドチェック・画面表示制御で参照可能。
- 権限なし: `Forbidden(403)` を送出する。 — `component/handlers/handlers-permission_check_handler.json#s4`

**③ 内部フォワード先を認可対象にする**
チェック対象のリクエスト ID を内部フォワード先のリクエスト ID に変更する場合:
- `PermissionCheckHandler.setUsesInternalRequestId` を `true` に設定する（デフォルト `false`）。
- `ThreadContextHandler` の `attributes` に `InternalRequestIdAttribute` を追加する。 — `component/handlers/handlers-permission_check_handler.json#s4`、`component/handlers/handlers-permission_check_handler.json#s3`

**④ 配置制約**
- `ThreadContextHandler` より **後** に配置（スレッドコンテキスト上のリクエスト ID とユーザ ID をもとに認可チェックするため）。
- `ForwardingHandler` より **後** に配置（内部フォワード先リクエスト ID をもとに認可したい場合）。
- `HttpErrorHandler` より **後** に配置（認可エラー時のエラーページ指定のため）。 — `component/handlers/handlers-permission_check_handler.json#s3`

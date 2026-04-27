**質問**: ログインしたユーザーの権限に応じて、アクセスできる画面を制限したい。Nablarch に権限チェックの仕組みはある？

---

**結論**: Nablarch は認可チェック機能をビルトインで提供している。リクエストレベルの認可は `PermissionCheckHandler`（認可チェックハンドラ）が担い、権限があれば `Permission` をスレッドローカルに設定、なければ 403 を返す。認可ライブラリには **権限管理の条件が変わり得るシステム向け** の `permission_check` と、簡易な `role_check` の2種類がある。 — `processing-pattern/web-application/web-application-feature_details.json#s14`、`component/handlers/handlers-permission_check_handler.json#s4`、`component/libraries/libraries-permission_check.json#s1`

**① 認可の全体像**
Web アプリケーションの機能詳細では「認可チェック」として `permission_check` が紹介されている。 — `processing-pattern/web-application/web-application-feature_details.json#s14`

Nablarch は2種類の認可機能を提供する:
- `permission_check`: 権限管理の条件が変わる可能性があるシステム向け（導入コスト高、データ管理はしっかり）。
- `role_check`: 権限管理の条件が基本的に変わらないシステム向け（ハードコーディングで導入コスト低）。 — `component/libraries/libraries-permission_check.json#s1`

**② リクエスト認可の動作**
`PermissionCheckHandler` はログイン中ユーザが現在のリクエスト（リクエスト ID）に対して権限を持つかをチェックする:
- 権限あり: `Permission` をスレッドローカルに設定し、後続ハンドラを呼び出す。サーバサイドチェック・画面表示制御で参照可能。
- 権限なし: `Forbidden(403)` を送出する。

内部フォワード先リクエスト ID に対して認可する場合は `setUsesInternalRequestId` を `true` にする（デフォルト `false`）。 — `component/handlers/handlers-permission_check_handler.json#s4`

**③ 配置制約**
- `ThreadContextHandler` より **後** に配置（スレッドコンテキスト上のリクエスト ID・ユーザ ID を参照するため）。
- `ForwardingHandler` より **後** に配置（内部フォワード先リクエスト ID での認可を行う場合）。
- `HttpErrorHandler` より **後** に配置（認可エラー時のエラーページ指定のため）。 — `component/handlers/handlers-permission_check_handler.json#s3`

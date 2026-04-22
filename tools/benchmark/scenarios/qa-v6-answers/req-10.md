**質問**: 誰がいつ何をしたか操作の証跡を残したい。いわゆる監査ログを出す仕組みは Nablarch にビルトインである？

---

**結論**: **Nablarch は「操作監査ログ」専用機能をビルトイン提供していない**。知識ファイルに監査ログ（audit log）に関する記載はない。最も近い機能は `HttpAccessLogHandler`（HTTP アクセスログハンドラ）で、リクエスト処理開始時と完了時にアクセスログを出力できる。ユーザ ID / リクエスト ID / セッションストア ID などはログ出力に含められるが、「何をしたか」（業務操作の内容）は自動では残らないため、業務ログはプロジェクト側で実装する必要がある。

**最も近い機能**: `HttpAccessLogHandler`。リクエスト処理開始・完了時にアクセスログを出力する。クラス名は `nablarch.common.web.handler.HttpAccessLogHandler`。 — `component/handlers/handlers-http_access_log_handler.json#s1`

**配置制約**
- `ThreadContextHandler` より **後** に配置（ログ出力処理で `ThreadContext` の内容が必要なため）。
- `HttpErrorHandler` より **前** に配置（完了時ログにエラーコードが必要なため）。
- セッションストア ID を出力する場合は `SessionStoreHandler` より **後** に配置。 — `component/handlers/handlers-http_access_log_handler.json#s3`

**代替案**:
- リクエスト単位のアクセスログ（誰・いつ・どのリクエスト）は `HttpAccessLogHandler` で残す。
- 業務操作の内容（何をしたか）はアクションから業務ログとして出力する（プロジェクト側実装）。
- 厳密な改竄防止・法令対応の監査ログが必要なら、AP ログ基盤・SIEM など Nablarch 外のインフラで別途確保する。

**注意点**
- 「監査ログをビルトインで出す」ことを前提とした設計は不可。アクセスログ＋業務ログの組合せでプロジェクト側で設計する。

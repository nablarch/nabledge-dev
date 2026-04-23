**結論**: Nablarch アプリをスケールアウトするには、HTTPセッション依存の機能をすべてセッション非依存の代替に切り替え、APサーバをステートレスにする必要がある。Nablarch にはそのための仕組みが用意されている。

**根拠**:

HTTPセッションはAPサーバ側で状態を持つため、そのままではスケールアウトができない。スティッキーセッションやセッションレプリケーションといった一般的な回避策は Twelve-Factor App の廃棄容易性の観点で劣り、APサーバ依存にもなる。Nablarch ではセッション依存機能を非依存のものに切り替えることでステートレス化できる。(`component/libraries/libraries-stateless_web_app.json:s1`)

デフォルトで HTTPセッションに依存している機能は以下の5つ:
- セッションストア
- 二重サブミット防止
- スレッドコンテキスト変数管理ハンドラ
- HTTPリライトハンドラ
- hidden暗号化
(`component/libraries/libraries-stateless_web_app.json:s2`)

各機能の切り替え方法は以下の通り (`component/libraries/libraries-stateless_web_app.json:s3`):
- **セッションストア** → DBストア（`db_managed_expiration`）を使用する
- **二重サブミット防止** → `db_double_submit` を使用する
- **スレッドコンテキストハンドラ** → `LanguageAttributeInHttpSession` を `LanguageAttributeInHttpCookie`、`TimeZoneAttributeInHttpSession` を `TimeZoneAttributeInHttpCookie`、`UserIdAttribute` を `UserIdAttributeInSessionStore` に切り替える
- **HTTPリライトハンドラ** → セッションスコープにアクセスしないよう設定するか、使用しない
- **hidden暗号化** → `useHiddenEncryption` を `false` に設定して無効化する

DBストアを使用する場合は `USER_SESSION` テーブル（SESSION_ID, SESSION_OBJECT, EXPIRATION_DATETIME の3カラム）を作成し、`SessionManager` を `"sessionManager"` というコンポーネント名でDIコンテナに登録する必要がある。(`component/libraries/libraries-session_store.json:s4`)

**注意点**:
- `SESSION_ID` カラムは CHAR ではなく **VARCHAR** で定義すること（Oracle で正常動作しないケースがある）。(`component/libraries/libraries-session_store.json:s4`)
- DBストア使用時、ブラウザが閉じられた際などにテーブルにセッション情報が残存することがある。期限切れセッション情報を**定期的に削除するバッチ**を用意する必要がある。(`component/libraries/libraries-session_store.json:s4`)
- `SessionManager` の `sessionManager` プロパティは `SessionStoreHandler` にも設定が必要。(`component/handlers/handlers-SessionStoreHandler.json:s5`)

参照: component/libraries/libraries-stateless_web_app.json:s1, component/libraries/libraries-stateless_web_app.json:s2, component/libraries/libraries-stateless_web_app.json:s3, component/libraries/libraries-session_store.json:s4, component/handlers/handlers-SessionStoreHandler.json:s5
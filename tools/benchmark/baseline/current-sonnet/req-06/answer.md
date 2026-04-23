**結論**: Nablarch では「APサーバをステートレスにする」のが公式推奨の解決策。HTTPセッション依存の機能をすべてHTTPセッション非依存のものに切り替えることで、スティッキーセッションやセッションレプリケーションなしに複数APサーバへの負荷分散が実現できる。

**根拠**:

**① HTTPセッションがスケールアウトの障害になる理由**
HTTPセッションはAPサーバ上に状態を持つため、そのままではスケールアウトができない。よくある回避策（スティッキーセッション・セッションレプリケーション・NoSQL保存）はいずれもTwelve-Factor Appの廃棄容易性に反したりAPサーバ依存になったりする問題がある。`component/libraries/libraries-stateless_web_app.json:s1`

**② Nablarchの推奨解法：ステートレス化**
HTTPセッション依存の各機能を以下のように切り替える。`component/libraries/libraries-stateless_web_app.json:s3`

| 依存機能（使用しない）| 代替（HTTPセッション非依存）|
|---|---|
| セッションストア（HTTPセッションストア）| DBストア または Redisストア |
| 二重サブミット防止（HTTPセッショントークン）| `db_double_submit`（DBトークン）|
| `LanguageAttributeInHttpSession` | `LanguageAttributeInHttpCookie` |
| `TimeZoneAttributeInHttpSession` | `TimeZoneAttributeInHttpCookie` |
| `UserIdAttribute` | `UserIdAttributeInSessionStore` |
| hidden暗号化 | `useHiddenEncryption=false` で無効化 |

**③ セッションストアの選択肢**
`component/libraries/libraries-session_store.json:s1` によると、スケールアウト対応として以下が使用可能。
- **DBストア**: データベースにセッション変数を保存。APサーバ停止時もセッション復元可能でヒープを圧迫しない。スケールアウトに最適。
- **Redisストア** (`component/adapters/adapters-redisstore_lettuce_adaptor.json:s1`): テーブル事前準備不要、有効期限切れセッションの削除バッチも不要。`redisstore-lettuce.xml` をインポートして `nablarch.sessionManager.defaultStoreName=redis` を設定する。
- **HIDDENストア**: クライアントサイドに保存されるためAPサーバ間の共有問題なし。複数タブでの操作を許容する場合に有効。

**④ 二重サブミット防止の注意点**
`component/libraries/libraries-db_double_submit.json:s1` によると、DBトークン方式（`db_double_submit`）を使えば複数APサーバ間でトークンを共有できる。ただし、DBトークン方式はユーザを識別せずにトークンをDBに格納するため **CSRF対策には使用できない**。CSRF対策は別途 `csrf_token_verification_handler` を使用すること。

**⑤ コンテナ・クラウドネイティブ環境での追加考慮点**
`setup/cloud-native/cloud-native-containerize.json:s2` では、Twelve-Factor Appに従いステートレス化に加えて以下も推奨している。
- ログ出力を標準出力へ変更
- 環境ごとの設定（DB接続先等）を環境変数で切り替える

**注意点**:
- JSPを使用している場合、`<%@ page session="false" %>` をJSP先頭に設定してHTTPセッションの自動作成を無効にすることを推奨。`processing-pattern/web-application/web-application-jsp_session.json:s1`
- DBストアは「同一セッションの処理が複数スレッドで実行された場合に後勝ち」となる点に注意（先勝ちのセッションデータが消失する）。`component/libraries/libraries-session_store.json:s1`
- Redisストアのデフォルト接続先は `localhost:6379` の単一インスタンス。本番環境では環境変数での接続先切り替えを活用すること。`component/adapters/adapters-redisstore_lettuce_adaptor.json:s1`

参照: component/libraries/libraries-stateless_web_app.json:s1, component/libraries/libraries-stateless_web_app.json:s3, component/libraries/libraries-session_store.json:s1, component/adapters/adapters-redisstore_lettuce_adaptor.json:s1, component/libraries/libraries-db_double_submit.json:s1, setup/cloud-native/cloud-native-containerize.json:s2, processing-pattern/web-application/web-application-jsp_session.json:s1
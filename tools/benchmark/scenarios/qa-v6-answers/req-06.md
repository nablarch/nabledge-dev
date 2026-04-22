**質問**: 本番環境で AP サーバを複数台並べて負荷分散する予定。Nablarch アプリをスケールアウトさせるときに気をつけることは？ セッションの扱いとか大丈夫？

---

**結論**: HTTP セッションは AP サーバで状態を持つためそのままではスケールアウトできない。Nablarch では **ステートレスにする** のが推奨の対処で、HTTP セッションに依存する機能を非依存のものに切り替えることで実現する。Web アプリ機能詳細ではスケールアウト設計として `stateless_web_app` が紹介されている。 — `processing-pattern/web-application/web-application-feature_details.json#s18`、`component/libraries/libraries-stateless_web_app.json#s1`

**① スケールアウトの基本的な考え方**
HTTP セッションは AP サーバで状態を持つためスケールアウトできない。通常の対処方法は以下3つ:
1. ロードバランサーでスティッキーセッションを有効にする
2. AP サーバのセッションレプリケーション機能を使用する
3. AP サーバの HTTP セッション保存先を NoSQL にする

> 1, 2 は Twelve-Factor App の **廃棄容易性** の点で劣り、2, 3 は AP サーバ依存となる。
>
> Nablarch の HTTP セッション依存機能を非依存のものに切り替えることで AP サーバをステートレスにできる。

— `component/libraries/libraries-stateless_web_app.json#s1`

**② HTTP セッションに依存しているデフォルト機能**
以下の機能はデフォルトで HTTP セッションに依存している（ステートレス化するにはここを非依存に差し替える）:
- `session_store`
- 2重サブミット防止（`tag-double_submission`）
- `thread_context_handler`
- `http_rewrite_handler`
- hidden 暗号化（`tag-hidden_encryption`） — `component/libraries/libraries-stateless_web_app.json#s2`

**③ セッションストアの差し替え**
ステートレス化の要として、セッションストアは **DB ストア** などサーバ間で共有できる保存先に切り替える。複数 AP サーバ構成で HIDDEN ストアを使う場合は、デフォルトではサーバごとに暗号化キーが自動生成されて復号失敗するケースがあるため、`HiddenStore.encryptor` に明示的な鍵・IV を設定して全サーバで揃える必要がある。 — `component/libraries/libraries-session_store.json#s8`

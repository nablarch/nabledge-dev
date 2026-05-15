**結論**: APサーバをスケールアウトする場合、セッションの保存先としては **DBストア** または **Redisストア（Lettuceアダプタ）** を選ぶべきです。HTTPセッションストアはスケールアウト時に追加の工夫が必要となるため、原則として避けるべきです。

**根拠**:

各ストアの特徴は以下のとおりです。

| ストア | 保存先 | スケールアウト対応 | 特徴 |
|---|---|---|---|
| **DBストア** | データベース上のテーブル | ✅ 問題なし | APサーバ停止後もセッション復元可能。ヒープを圧迫しない。 |
| **HIDDENストア** | クライアントサイド（hiddenタグ） | ✅ 問題なし | 複数タブでの操作を許容できる。ヒープを圧迫しない。 |
| **HTTPセッションストア** | APサーバのヒープ領域 | ❌ 工夫が必要 | APサーバ毎に情報を保持するため、スケールアウト時に追加対応が必要。大量データでヒープを圧迫する恐れあり。 |
| **Redisストア（Lettuceアダプタ）** | Redis | ✅ 問題なし | 保存先が異なるだけでDBストアと同じ特徴。有効期限管理もRedis側が自動処理。 |

**用途別の選択基準**:

| 用途 | 推奨ストア |
|---|---|
| 入力〜確認〜完了画面での入力情報保持（複数タブ不可） | **DBストア** または **Redisストア** |
| 入力〜確認〜完了画面での入力情報保持（複数タブ許容） | **HIDDENストア** |
| 認証情報の保持 | **DBストア** または **HTTPセッションストア** |

スケールアウト構成で **Redisストア** を採用する場合、アダプタ（`nablarch-integration-redisstore-lettuce`）を使用します。本番環境では以下の構成に対応しています：

```properties
# Cluster構成の場合
nablarch.lettuce.clientType=cluster

# Master-Replica構成の場合
nablarch.lettuce.clientType=masterReplica
```

設定ファイル：`nablarch/webui/redisstore-lettuce.xml` と `redisstore-lettuce.config` を読み込むことで使用開始できます。

**注意点**:
- DBストアおよびHTTPセッションストアは、同一セッションの処理が複数スレッドで実行された場合に**後勝ち**（先に保存されたデータが消失）となります。
- Redisストアの有効期限管理はRedis側が自動処理するため、セッション削除バッチの実装は不要です。
- セッションストアに保存できるのは「シリアライズ可能なJava Beansオブジェクト」のみです。
- 検索結果一覧・検索条件・画面表示項目・エラーメッセージのセッション保存はNablarchの設計上「使用しない」ことが推奨されています（大量データによる領域圧迫を防ぐため）。

参照: `component/libraries/libraries-session-store.json#s16`, `component/libraries/libraries-session-store.json#s2`, `component/adapters/adapters-redisstore-lettuce-adaptor.json#s6`, `component/adapters/adapters-redisstore-lettuce-adaptor.json#s7`
Step 5〜7: 回答を生成しverifyします。

---

**結論**: NablarchはWebSocketを直接サポートしていない。Nablarchのウェブアプリケーションは**Servlet APIベースで構築**されており、WebSocketハンドラも提供されていないため、Nablarch単体ではWebSocketを使ったリアルタイム通知を実装できない。

ただし、Jakarta WebSocket（`jakarta.websocket`）はJakarta EEの仕様として存在しており、Jakarta EE対応のアプリケーションサーバー上であれば、**Nablarchのフレームワーク外でJakarta WebSocket APIを直接利用する**ことは技術的に可能。

---

**根拠**:

**Nablarchのウェブアプリケーション構成（Servlet APIベース）**

```
Nablarchではウェブアプリケーションを構築する場合、ServletAPIの使用を前提としている。
```
（`web-application-architecture.json:s1`）

Nablarchが提供するウェブアプリケーション用のハンドラ一覧は以下の通りで、WebSocket用のハンドラは存在しない：

- HTTP文字エンコード制御ハンドラ
- HTTPレスポンスハンドラ
- マルチパートリクエストハンドラ
- セッション変数保存ハンドラ
- CSRFトークン検証ハンドラ
- ... （WebSocket関連ハンドラはなし）

（`web-application-architecture.json:s3`）

**Jakarta WebSocketの位置付け**

移行ガイドのJava EE→Jakarta EE対応表には次の記載がある：

| Java EE | Jakarta EE |
|---|---|
| Java API for WebSocket (`javax.websocket`) | Jakarta WebSocket (`jakarta.websocket`) |

これはJakarta EEの仕様として存在しているが、Nablarchがラップ・提供しているものではない。

（`migration-migration.json:s33`）

**Nablarchのポリシー（OSSは使用しない）**

```
Nablarchのプロダクションコードは、致命的な不具合や脆弱性が見つかった際に、迅速に対応かつリリースすることを目的としてOSSを使用していない。
なお、OSSを使用することでメリットがあるものは、アダプタとしてOSSを使用できるコンポーネントを提供している。
```
（`about-nablarch-policy.json:s6`）

**バッチ進捗データの取得（参考）**

バッチの進捗状況自体は、Jakartaバッチの`ProgressManager`で取得できる（TPS、未処理件数、終了予測時間など）。ただしこれはログ出力用であり、ブラウザへのプッシュ通知機能は持たない。

---

**注意点**:

- Jakarta WebSocket APIを直接使う場合、そのWebSocketエンドポイントはNablarchのハンドラキューとは独立した仕組みになる。Nablarchの認証・認可・トランザクション管理などはWebSocket接続に自動適用されないため、セキュリティと接続管理は自前で実装する必要がある。
- バッチ進捗のリアルタイム通知をWebSocketなしで実現したい場合は、ウェブアプリ側にRESTエンドポイントを設けてブラウザからポーリングする方式も検討できる。

参照: `web-application-architecture.json:s1`, `web-application-architecture.json:s3`, `about-nablarch-policy.json:s6`, `migration-migration.json:s33`

---
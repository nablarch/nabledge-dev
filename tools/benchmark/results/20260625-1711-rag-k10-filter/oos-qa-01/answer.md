提供されたセクションの範囲では、**NablarchにWebSocketのサポートに関する記述はありません**。

#### 参照セクションから分かること

提供されたドキュメントには、リアルタイム通知の代替となるパターンが記載されています。

**非同期処理の方式（`nablarch-patterns-Nablarchでの非同期処理.json:s1`、`nablarch-patterns-Nablarchバッチ処理パターン.json:s1`）:**

| 方式 | 特徴 |
|------|------|
| **テーブルをキューとして使ったメッセージング** | DBテーブルを監視し、未処理レコードを順次処理。新規プロジェクト推奨 |
| **常駐バッチ** | DBにデータが登録されるのを監視してバッチ処理を実行 |

これらはバッチ進捗を「DB経由で記録→ブラウザ側がポーリング」という形で組み合わせることで、リアルタイム通知の代替手段になり得ます。

**ウェブアプリケーション側（`web-application-feature-details.json:s1`）:**  
Nablarchのウェブアプリはサーブレットコンテキストリスナーとハンドラキューベースのアーキテクチャであり、WebSocketに特化した仕組みの言及はありません。

#### 結論

WebSocketをNablarchで使う方法は、参照可能なドキュメント範囲には記載がありません。実現方法としては以下が考えられます：

1. **ブラウザ側ポーリング** — バッチ進捗をDBに記録し、ブラウザが定期的にREST APIで取得する（Nablarchの既存機能で対応可能）
2. **Jakarta EE WebSocket API** — Nablarchはサーブレットコンテナ上で動作するため、Jakarta EE標準の `javax.websocket` / `jakarta.websocket` APIをNablarchの外側で直接使用する（Nablarchがサポートするわけではなく、サーブレットコンテナの機能として利用する形）

WebSocket対応について公式ドキュメントを直接確認することをお勧めします：  
https://nablarch.github.io/docs/LATEST/doc/
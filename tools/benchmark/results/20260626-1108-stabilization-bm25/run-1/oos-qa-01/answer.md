この情報は知識ファイルに含まれていません。

---

**補足（知識ファイル外の情報として）:**

Nablarch 6はJakarta EE 10ベースであり、Jakarta WebSocket（旧Java API for WebSocket）はJakarta EEの標準仕様として含まれています。しかし、**NablarchフレームワークはWebSocketに関するラッパーや専用サポートを提供していません**（Nablarchはアプリケーションサーバ提供のServlet APIを前提としており、WebSocket固有のコンポーネントはドキュメント化されていません）。

バッチ進捗をリアルタイム通知する代替アプローチとして、知識ファイルの範囲内では以下が確認できます：

- **MOMメッセージングやDBキューを使った非同期処理**（進捗をDBに記録し、ポーリングで取得する構成）
- **Nablarchでの非同期処理**パターンはメール送信（常駐バッチ経由）のみが文書化されています

WebSocketを使う場合は、Jakarta WebSocket APIをサーブレットコンテナ（Tomcatなど）の機能として直接利用することになりますが、その実装方法はNablarchの知識ファイルの対象範囲外です。
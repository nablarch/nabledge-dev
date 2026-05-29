知識ファイルにWebSocketに関する情報がないことを確認しました。Steps 3〜6を完了します。

**Step 3 ページ候補評価**:
- `guide/nablarch-patterns/nablarch-patterns-Nablarchでの非同期処理.json` → 読み込み済み: Webアプリの非同期パターンだがWebSocketの記述なし
- `processing-pattern/web-application/web-application-feature-details.json` → 読み込み済み: ウェブアプリ機能詳細にWebSocketの記述なし
- `about/about-nablarch/about-nablarch-policy.json` → 読み込み済み: 基本方針だがWebSocketの実装方法なし

セクション評価の結果、WebSocketの実装方法を回答するのに必要なセクションは存在しないため、`selected_sections = []`。

---

この情報は知識ファイルに含まれていません。

**補足**: Nablarchの公式ドキュメントおよび知識ファイルにはWebSocketの実装方法に関する記載がありません。NablarchはJakarta EE 10アプリケーションサーバ上で動作するため、Jakarta WebSocket仕様（`jakarta.websocket`）はアプリケーションサーバレベルで利用可能ですが、Nablarchフレームワーク自体はWebSocketに関するハンドラ、アダプタ、ガイダンスを提供していません。WebSocketを使いたい場合はNablarchの管理外でJakarta WebSocket APIを直接実装する必要がありますが、その方法はNablarchの知識ファイルの対象範囲外です。

---
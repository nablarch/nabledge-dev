提供されたセクションの中に、NablarchがWebSocketを直接サポートするという記述はありません。

**参照セクションから分かること：**

Nablarchのバッチ進捗をブラウザへリアルタイム通知する場合、参照セクションが示す方式を組み合わせるのが現実的なアプローチです。

1. **非同期処理方式**（`nablarch-patterns-Nablarchでの非同期処理.json:s1`）：  
   オンライン処理で処理要求を受け付け、**テーブルをキューとして使ったメッセージング**でバッチを非同期実行するパターンが推奨されています。進捗状態もDBテーブルで管理できます。

2. **WebSocketについて**：  
   Nablarchのウェブアプリケーション（`web-application-feature-details.json:s1`）はサーブレットベースのアーキテクチャを採用していますが、WebSocketのサポートに関する記述は参照セクションには含まれていません。

**代替アプローチ（参照セクションの範囲内）：**

- バッチの進捗状態をDBテーブルに書き込み、ブラウザ側からHTTP **ポーリング**で取得する方式が、Nablarchの設計思想（ハンドラキューベースのリクエスト処理）と整合します。
- WebSocketが必須の場合は、Nablarchの範囲外となるため、Jakarta EE 10のWebSocket API（`jakarta.websocket`）を直接実装するか、専用のWebSocketライブラリを併用することになります。

**結論：** NablarchにはWebSocketを提供する組み込み機能は確認されていません。進捗通知の実現にはDBベースのポーリング方式が最もNablarchのアーキテクチャと合致します。WebSocketが必要な場合は、Jakarta EEのWebSocket APIをNablarchと並用する構成を検討してください。詳細はNablarchの公式ドキュメントまたはサポートチャネルでご確認ください。
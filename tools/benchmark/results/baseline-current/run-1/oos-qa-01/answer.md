**結論**: NablarchにはWebSocketのサポートはありません。バッチ処理の進捗状況をリアルタイムにブラウザへ通知する機能は知識ファイルに含まれておらず、Nablarchの対応範囲外です。

**根拠**: Nablarch 6が対応する処理方式はWebアプリケーション、RESTful Webサービス、バッチ処理、メッセージングであり、WebSocket処理のパターンは提供されていません。

バッチ処理の進捗状況については、Nablarchの`ProgressManager`を使ったログ出力機能（`jakarta-batch-progress-log`）が用意されています。これはTPS・未処理件数・終了予測時間などをログファイルに出力するものです：

```java
// Batchletステップの例
progressManager.setInputCount(10000);  // 処理対象件数を設定
progressManager.outputProgressInfo(processedCount);  // 進捗ログを出力
```

Chunkステップの場合は、ジョブ定義ファイルに`progressLogListener`を登録することで自動的に進捗ログが出力されます。

ただし、これらはあくまでサーバー側の**ログファイル出力**であり、WebSocketによるブラウザへのリアルタイム通知ではありません。

**注意点**:
- NablarchはWebSocketを直接サポートしていないため、WebSocketを用いたリアルタイム通知はNablarchのフレームワーク機能として実現できません
- バッチ進捗のリアルタイム通知が必要な場合は、進捗状況をデータベースに書き込み、別途ポーリングAPIをRESTで提供するなどの設計が現実的ですが、これはNablarchの知識ファイルに記載された方式ではありません
- ChunkステップでRetrying Exceptionsを設定している場合、進捗ログリスナーが正しく機能しなくなります

参照: `processing-pattern/jakarta-batch/jakarta-batch-progress-log.json#s1`, `#s3`, `#s4`
この情報は知識ファイルに含まれていません。

Nablarch 6の知識ファイルを検索した結果、**WebSocketのサポートはNablarchには含まれていません**。

`about-nablarch-platform.json#s1` によると、Nablarchフレームワークが対応しているJakarta EE仕様は以下の通りです：

- Jakarta Standard Tag Library 3.0
- Jakarta Activation 2.1
- Jakarta Server Pages 3.1
- Jakarta Servlet 6.0
- Jakarta Mail 2.1
- Jakarta Messaging 3.1
- Jakarta Persistence 3.1
- Jakarta Batch 2.1
- Jakarta Bean Validation 3.0
- Jakarta RESTful Web Services 3.1

**Jakarta WebSocket はこのリストに含まれていません。** NablarchはWebSocketを公式にサポートしておらず、NablarchのAPIやフレームワーク機能としてWebSocketを利用する方法は提供されていません。

バッチ進捗のリアルタイム通知について、`jakarta-batch-progress-log.json#s1` によると、Nablarchのバッチ処理には進捗ログ出力機能（`ProgressManager`）がありますが、これはログファイルへの出力を目的としており、ブラウザへのリアルタイム通知には対応していません。

参照: `about/about-nablarch/about-nablarch-platform.json#s1`, `processing-pattern/jakarta-batch/jakarta-batch-progress-log.json#s1`
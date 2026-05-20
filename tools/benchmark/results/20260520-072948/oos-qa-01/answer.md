**結論**: NablarchにはWebSocketのサポートはありません。バッチ処理の進捗をブラウザへリアルタイム通知する手段としてNablarchが提供するのは、「テーブルをキューとして使ったメッセージング」を介した非同期連携パターンのみです。WebSocketによるプッシュ通知の実装方法は知識ファイルの対象範囲外です。

**根拠**:

Nablarchの知識ファイル全体を検索した結果、WebSocketに関する記述は「Java EE/Jakarta EEの仕様名対応表」（`Jakarta WebSocket`という仕様名の列挙）のみで、実装方法やNablarchとの統合方法は一切記載されていません。

Nablarchで時間のかかる処理を非同期に実行する公式パターンは以下の通りです：

> Webアプリはリクエストを受け付けて後続処理に必要なデータをDBに登録し、レスポンスを返却する。テーブルをキューとして使ったメッセージングがDBへのデータ登録を検知し、当該データの処理を行う。

つまり、Nablarchが提供する非同期パターンは「DBをキューとして使うポーリング型」であり、WebSocketによるサーバープッシュではありません。

**注意点**:

- WebSocketを使いたい場合は、Nablarchのハンドラ機構の外側でServletコンテナ（TomcatなどのJakarta WebSocket対応コンテナ）の機能を直接利用することになりますが、その方法はNablarchの知識ファイルの対象範囲外です。
- バッチ進捗のリアルタイム通知をNablarchの範囲内で実現したい場合は、クライアント側のポーリング（定期的にAjaxでDB上の進捗レコードを問い合わせる）と「テーブルをキューとして使ったメッセージング」パターンの組み合わせが現実的な代替手段です。

参照: `guide/nablarch-patterns/nablarch-patterns-Nablarchでの非同期処理.json:s1`, `about/migration/migration-migration.json:s33`
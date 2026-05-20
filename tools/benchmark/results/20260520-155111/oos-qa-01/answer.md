**結論**: NablarchにはWebSocketの組み込みサポートに関する記載はなく、バッチ処理の進捗をリアルタイムでブラウザへ通知するNablarch固有のWebSocket機能は提供されていません。Nablarchが文書化している代替アプローチは、テーブルキューメッセージング＋定期ポーリングの組み合わせです。

**根拠**: Nablarchのウェブアプリケーション向け非同期処理パターンとして、以下の構成が文書化されています：

1. ウェブアプリはリクエストを受け付け、後続処理に必要なデータをDBに登録してレスポンスを返す
2. テーブルをキューとして使ったメッセージングがDBへのデータ登録を検知し、バッチ処理を実行する
3. ブラウザはHTTPポーリングで定期的にサーバへ進捗を問い合わせる

また、Nablarchの基本方針として「OSSは使用しない」が明記されており（プロダクションコードにOSSを含めないポリシー）、外部ライブラリを使ったWebSocket統合ガイドラインは知識ファイルの対象範囲外です。

**注意点**: Jakarta EE 10（Nablarch 6の基盤）にはJakarta WebSocket仕様が含まれており、技術的にWebSocketを実装すること自体は可能ですが、NablarchフレームワークとしてのWebSocket統合方法（ハンドラ構成、ライフサイクル管理等）はこの情報は知識ファイルの対象範囲外です。進捗通知の実装としては、上記のポーリング方式が文書化されたパターンです。

参照: guide/nablarch-patterns/nablarch-patterns-Nablarchでの非同期処理.json, about/about-nablarch/about-nablarch-policy.json:s6
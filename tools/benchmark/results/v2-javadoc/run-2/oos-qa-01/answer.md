知識ファイルの検索結果を整理します。WebSocketに関する実装ガイドは知識ファイルに存在しないことを確認しました。回答を生成します。

---

**結論**: NablarchはWebSocketをフレームワークとして提供していません。WebSocketの実装は知識ファイルの対象範囲外です。

**根拠**:

Nablarchの知識ファイルを検索した結果、WebSocketに関する実装ガイドは存在しません。

Nablarchのウェブアプリケーション機能詳細（`processing-pattern/web-application/web-application-feature-details.json`）に列挙されている機能にWebSocketは含まれておらず、バッチ進捗をリアルタイム通知するための組み込みWebSocketサポートは提供されていません。

また、Nablarchの基本方針（`about/about-nablarch/about-nablarch-policy.json` s6）として「OSSは使用しない」が定められており、外部ライブラリを介した機能はアダプタとして別途提供されますが、WebSocketアダプタは提供されていません。

**注意点**:

バッチ処理の進捗をブラウザへ通知したい場合、Nablarchが提供する非同期パターンとして「テーブルをキューとして使ったメッセージング」と組み合わせたポーリング方式が文書化されています。ただし、WebSocketを使ったプッシュ通知については知識ファイルの対象範囲外です。Jakarta EE 10（Nablarch 6が動作する環境）にはJakarta WebSocketの仕様が含まれているため、アプリケーションサーバが提供するJakarta WebSocket APIを直接使用することは技術的には可能ですが、その実装方法はNablarchの文書化対象外です。

参照: guide/nablarch-patterns/nablarch-patterns-Nablarchでの非同期処理.json:s1, about/about-nablarch/about-nablarch-policy.json:s6

---
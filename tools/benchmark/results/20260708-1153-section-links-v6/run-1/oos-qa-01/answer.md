**結論**: NablarchにはWebSocketのネイティブサポートはありません。WebSocketを使ったリアルタイム通知の実装方法は知識ファイルの対象範囲外です。

**根拠**: Nablarchの知識ファイルにはWebSocket実装に関するドキュメントが存在しません。Nablarchのウェブアプリケーション機能詳細（`web-application-feature-details.json`）には、Nablarch初期化・バリデーション・DBアクセス・セッション・ファイル処理・CSRF対策などの機能が列挙されていますが、WebSocketは含まれていません。

**バッチ進捗の非同期通知に関する代替アプローチ（Nablarchが提供するパターン）**:

Nablarchでの非同期処理ガイドによると、Nablarchのウェブアプリケーションで非同期処理を実現する場合は「テーブルをキューとして使ったメッセージング」との組み合わせが推奨されています：

```
Webアプリ:
  1. リクエストを受け付けて後続処理に必要なデータをDBに登録
  2. レスポンスを返却

テーブルをキューとして使ったメッセージング:
  - DBへのデータ登録を検知して当該データの処理を実行
```

ただし、このパターンはバッチ処理の**起動**に関するものであり、WebSocketのようなサーバーからブラウザへのプッシュ通知の仕組みそのものではありません。

**注意点**:
- WebSocketをNablarchアプリで使いたい場合は、Jakarta WebSocket（`jakarta.websocket`）などのJakarta EE標準仕様を直接使用することになりますが、その具体的な実装方法はNablarchの知識ファイルの対象範囲外です
- バッチの進捗をブラウザへ通知する場合、WebSocketの代替として「ブラウザ側からのポーリング（定期的なHTTPリクエスト）」「SSE（Server-Sent Events）」などの方式も一般的ですが、これらもNablarchとしての公式サポートはありません

参照:
- Nablarchでの非同期処理
  .claude/skills/nabledge-6/docs/guide/nablarch-patterns/nablarch-patterns-Nablarchでの非同期処理.md
  メール送信を行う場合
- 機能詳細
  .claude/skills/nabledge-6/docs/processing-pattern/web-application/web-application-feature-details.md
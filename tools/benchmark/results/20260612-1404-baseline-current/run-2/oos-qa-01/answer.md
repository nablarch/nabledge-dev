**結論**: NablarchにはWebSocketのネイティブサポートはありません。Nablarchの設計方針として本番コードにOSSを使用しないため、WebSocket機能は組み込まれていません。

**根拠**:

Nablarchの基本方針（s6）に以下の通り明記されています：

```
Nablarchのプロダクションコードは、致命的な不具合や脆弱性が見つかった際に、
迅速に対応かつリリースすることを目的としてOSSを使用していない。
```

なお、OSSを活用したい場合はアダプタとして提供されるコンポーネントの利用が案内されていますが、WebSocket専用アダプタについては知識ファイルに記載がありません。

**注意点**:
- バッチ処理の進捗をWebSocketでリアルタイムにブラウザへ通知するアーキテクチャはNablarchのスコープ外です
- Jakarta EEのWebSocket仕様（`jakarta.websocket`）はNablarchとは独立した仕様であり、アプリケーションサーバーが提供する機能として利用可能ですが、Nablarchがその実装をサポート・案内している情報は知識ファイルには確認できません
- Nablarchでの非同期処理の代替手段（テーブルをキューとして使ったメッセージング等）については、「[Nablarchでの非同期処理](guide/nablarch-patterns/)」を参照してください

参照: about-nablarch-policy.json:s6
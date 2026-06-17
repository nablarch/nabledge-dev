**結論**: NablarchにはWebSocketのサポートは提供されていません。Nablarchのプロダクションコードはすべて「OSSを使用しない」方針のため、WebSocketライブラリを利用した機能やアダプタは存在しません。

**根拠**: Nablarchの基本方針として以下が定められています：

> Nablarchのプロダクションコードは、致命的な不具合や脆弱性が見つかった際に、迅速に対応かつリリースすることを目的としてOSSを使用していない。なお、OSSを使用することでメリットがあるものは、アダプタとしてOSSを使用できるコンポーネントを提供している。

知識ファイルに含まれるアダプタ一覧（component/adapters/）にはWebSocket用アダプタは存在しません。

**注意点**:
- バッチ処理の進捗状況をブラウザへ通知したい場合、WebSocketではなくHTTPポーリングまたはServer-Sent Eventsをアプリケーション側で独自実装する形になります。ただしこれらの具体的な実装方法はNablarchの知識ファイルの対象範囲外です。
- WebSocketを使いたい場合は、Nablarchのハンドラキューの外側（サーブレットコンテナレベル）でWebSocketエンドポイントを実装する方法が考えられますが、この情報は知識ファイルの対象範囲外です。

参照: about/about-nablarch/about-nablarch-policy.json:s6
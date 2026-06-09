**結論**: NablarchはWebSocketをネイティブにサポートしていません。バッチ処理の進捗をブラウザへリアルタイム通知する場合、Nablarchの標準機能ではWebSocketを直接実装することはできません。

**根拠**:

Nablarchの基本方針として「OSSは使用しない」という原則があり、プロダクションコードはOSSを使用していません。WebSocket対応のサーブレットコンテナ機能（Tomcatなどの Jakarta WebSocket）を組み合わせることは技術的には可能ですが、Nablarchのハンドラキューアーキテクチャはリクエスト/レスポンスの同期モデルを前提としており、長命なWebSocket接続に対応する仕組みは提供されていません。

バッチ処理の進捗管理については、`ProgressManager`を使ったログ出力機能が提供されています：

```java
// Jakarta Batchのバッチlet例
@Inject
public ProgressBatchlet(ProgressManager progressManager) {
    this.progressManager = progressManager;
}

@Override
public String process() throws Exception {
    progressManager.setInputCount(10000);  // 処理対象件数を設定
    long processedCount = 0;
    while (処理対象が存在している間) {
        processedCount++;
        if (processedCount % 1000 == 0) {
            progressManager.outputProgressInfo(processedCount);  // 進捗ログ出力
        }
    }
    return "SUCCESS";
}
```

ただし、これはサーバー側のログファイルへの出力であり、ブラウザへのリアルタイム通知ではありません。

**代替アプローチ（Nablarch知識ファイルの対象範囲外）**:

Nablarchの非同期処理パターンとして「テーブルをキューとして使ったメッセージング」が用意されており、Webアプリとバッチ間でDBを経由したデータ連携が可能です。これと組み合わせて以下のアーキテクチャを検討できます：

1. **ポーリング方式**: ブラウザが定期的にREST APIを呼び出して進捗をDBから取得する（Nablarchの通常のHTTPリクエスト/レスポンスモデルで対応可能）
2. **WebSocket統合**: サーブレットコンテナ（Tomcat等）が提供するJakarta WebSocket APIを直接使用してWebSocket Endpointを実装し、バッチの進捗状態をDBに書き込んでWebSocket経由でプッシュする（NablarchのDI・DBアクセス機能は活用できますが、WebSocket接続管理はNablarch外で実装が必要）

**注意点**: WebSocketをNablarchアプリに組み込む場合、WebSocket接続はNablarchのハンドラキューを経由しないため、スレッドコンテキスト管理やトランザクション管理など、Nablarchが提供するハンドラの恩恵を受けられない点に注意が必要です。

参照: jakarta-batch-progress-log.json:s1, jakarta-batch-progress-log.json:s3, nablarch-patterns-Nablarchでの非同期処理.json:s1, about-nablarch-policy.json:s6
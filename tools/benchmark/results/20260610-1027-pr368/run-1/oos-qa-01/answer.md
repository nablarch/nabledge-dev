**結論**: NablarchにはWebSocketのサポートは提供されていません。NablarchウェブアプリケーションはServletAPIを前提としたアーキテクチャで構成されており、WebSocketに関する機能や設定方法は知識ファイルの対象範囲外です。

**根拠**:

Nablarchウェブアプリケーションの構成はServletAPI前提です。

> Nablarchではウェブアプリケーションを構築する場合、ServletAPIの使用を前提としている。

また、NablarchのプロダクションコードはOSSを使用しない方針を取っています。

> Nablarchのプロダクションコードは、致命的な不具合や脆弱性が見つかった際に、迅速に対応かつリリースすることを目的としてOSSを使用していない。

バッチ処理の進捗状況については、Jakartaバッチ向けに `ProgressManager` を使ったログ出力機能が用意されています。ただしこれはサーバーサイドの**ログファイルへの出力**です。リアルタイムにブラウザへプッシュする仕組みではありません。出力される情報は以下の通りです。

- ジョブ・ステップの開始/終了
- TPS（開始後からのTPS、最新のTPS）
- 未処理件数
- 終了予測時間

```
INFO progress job name: [test-job] step name: [test-step] total tps: [250.00] current tps: [250.00] estimated end time: [2017/02/13 04:02:25.656] remaining count: [15]
```

**注意点**:
- WebSocketを使ったリアルタイムブラウザ通知はNablarchの機能範囲外です。Nablarchの知識ファイルには該当する実装ガイドが含まれていません。
- 代替手段（クライアント側ポーリング、Jakarta EEコンテナ標準のWebSocket API直接利用など）はNablarch機能の対象範囲外のため、この情報は知識ファイルの対象範囲外です。

参照: processing-pattern/jakarta-batch/jakarta-batch-progress-log.json:s1, processing-pattern/web-application/web-application-architecture.json:s1, about/about-nablarch/about-nablarch-policy.json:s6
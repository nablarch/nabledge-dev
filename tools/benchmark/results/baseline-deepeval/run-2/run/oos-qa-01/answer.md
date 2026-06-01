**結論**: NablarchにはWebSocketを直接サポートする機能は提供されていません。

WebSocketによるリアルタイム通知は、Nablarchの知識ファイルの対象範囲外です。

**根拠**:

Nablarchのウェブアプリケーションは、**ServietAPIをベースとしたハンドラキュー**で動作します。すべてのリクエストはWebFrontController（`jakarta.servlet.Filter` の実装）を経由してハンドラキューに委譲される仕組みです。WebSocketの接続確立（HTTPアップグレード）はこのハンドラキューの処理フローの外側で行われるため、Nablarchのフレームワーク機能としては提供されていません。

また、Nablarchの基本方針として以下が明記されています：

> Nablarchのプロダクションコードは、致命的な不具合や脆弱性が見つかった際に、迅速に対応かつリリースすることを目的としてOSSを使用していない。

**バッチ進捗状況の取得について**（知識ファイル内の代替手段）:

Jakarta Batchでは `ProgressManager` を使った**進捗ログのファイル出力**機能が提供されています（カテゴリ名 `progress`）。この機能はログファイルへの出力のみが対象であり、ブラウザへのリアルタイム通知には対応していません。

```properties
# 進捗ログ専用ファイル設定例
writer.progressLog.className=nablarch.core.log.basic.FileLogWriter
writer.progressLog.filePath=./log/progress.log
...
loggers.PROGRESS.nameRegex=progress
loggers.PROGRESS.level=INFO
loggers.PROGRESS.writerNames=progressLog
```

**注意点**:

- Nablarch 6はJakarta EE 10上で動作するため、アプリケーションサーバーが提供するJakarta WebSocket（標準仕様）をNablarchのハンドラキューとは独立した形で使用することは技術的に可能です。ただしこれはNablarchフレームワーク外の実装となり、Nablarchとしてのサポート対象外です。
- WebSocketを使わない代替案として、ブラウザから定期的にRESTエンドポイントをポーリングしてバッチ状態をDBから取得するアプローチがあります。この方法はNablarchのRESTfulウェブサービスで実装可能です。

参照: `processing-pattern/web-application/web-application-architecture.json:s1`, `about/about-nablarch/about-nablarch-policy.json:s6`, `processing-pattern/jakarta-batch/jakarta-batch-progress-log.json:s1`, `processing-pattern/jakarta-batch/jakarta-batch-progress-log.json:s2`

---
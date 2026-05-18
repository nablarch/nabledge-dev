**結論**: NablarchにはWebSocketのサポートは含まれておらず、NablarchのAPIとしてWebSocketを使う方法は知識ファイルに記載されていません。

**根拠**:

NablarchがサポートするJakarta EE仕様の一覧（`about-nablarch-platform.json#s1`）には、Jakarta Servlet 6.0、Jakarta RESTful Web Services 3.1、Jakarta Batch 2.1 など10仕様が含まれていますが、**Jakarta WebSocket はこの一覧に含まれていません。**

移行ガイドの仕様対応表（`migration-migration.json#s33`）では「Java API for WebSocket → Jakarta WebSocket」の対応が記載されていますが、NablarchがJakarta WebSocketをサポートするという記述はありません。

**バッチ進捗をブラウザへ通知する代替手段**（知識ファイルに記載のある方法）:

1. **進捗ログ出力** (`jakarta-batch-progress-log.json#s1`): `ProgressManager` を使ってTPS・残件数・終了予測時刻をログファイルへ出力できます。ブラウザへの直接通知ではありませんが、進捗の記録手段として利用できます。

2. **テーブルをキューとして使ったメッセージング** (`nablarch-patterns-Nablarchでの非同期処理.json`): Nablarchでの非同期/イベント連携の推奨方式。バッチが進捗をDBに書き込み、WebアプリがHTTPポーリングでDBを参照してブラウザへ返す設計が、Nablarchのアーキテクチャに沿ったアプローチです。

**注意点**:
- Jakarta WebSocketはNablarchのサポート対象仕様ではないため、Nablarchフレームワーク機能としてのWebSocketエンドポイント構築方法は知識ファイルに存在しません。
- アプリケーションサーバがJakarta WebSocketを提供している場合に直接APIを使うことは技術的には可能ですが、Nablarchとしての統合サポートに関する情報は知識ファイルにはありません。
- Nablarchのアーキテクチャに沿った現実的な代替案は、進捗をDBに書き込みHTTPポーリングで参照する設計です。

参照: `about-nablarch-platform.json#s1`, `migration-migration.json#s33`, `nablarch-patterns-Nablarchでの非同期処理.json`, `jakarta-batch-progress-log.json#s1`
**結論**: NablarchはWebSocketを直接サポートしていません。バッチ処理の進捗をリアルタイムでブラウザへ通知したい場合、Nablarchの機能だけでは実現できないため、Jakarta EEが提供するWebSocket API（`jakarta.websocket`）をアプリケーションサーバーの仕組みを利用して独自実装するか、代替アプローチを検討する必要があります。

**根拠**:

Nablarchのウェブアプリケーションは **ServletAPI** を前提に構築されており、アーキテクチャはServletフィルタ（WebFrontController）とハンドラキューで構成されています。知識ファイル全体を検索した結果、WebSocketはNablarchがサポートする機能として記載されておらず、Nablarch 5→6移行ガイドのJava EE/Jakarta EE仕様対応表（`javax.websocket` → `jakarta.websocket` のパッケージ名変更）で言及されているのみです。

また、Nablarchには非同期処理パターンとして「テーブルをキューとして使ったメッセージング」が提供されていますが、これはWebアプリからバックエンドへ処理を非同期委譲するパターンであり、ブラウザへのリアルタイムプッシュ通知には対応していません。

```
# Nablarchが提供している非同期処理のアプローチ（WebSocket通知とは別）
1. Webアプリはリクエストを受け付けてDBに処理データを登録し、即座にレスポンスを返却する
2. テーブルをキューとして使ったメッセージングがDBへのデータ登録を検知し、バッチ処理を実行する
※ ブラウザへのリアルタイム通知はこのパターンでは提供されない
```

**注意点**:

- WebSocketを実装したい場合は、アプリケーションサーバー（Tomcat、WildFlyなど）が提供するJakarta WebSocket API（`jakarta.websocket`）を直接利用することになります。WebSocketエンドポイントはNablarchのハンドラキューではなく、サーブレットコンテナの仕組みで動作するため、Nablarchとは独立した実装になります。
- Nablarchの基本方針として、フレームワーク本体はOSSを使用せずServletAPIの範囲で設計されており、WebSocketサポートはその設計範囲外です。
- 代替アプローチとして以下の方法があります（いずれもNablarch標準外の独自実装が必要）:
  - **ポーリング**: ブラウザから定期的にNablarchアクションへHTTP GETして進捗を取得する
  - **Server-Sent Events (SSE)**: サーブレットコンテナのSSE機能を利用する
  - **WebSocket**: `jakarta.websocket` APIを直接利用した独自エンドポイントを実装する

参照: guide/nablarch-patterns/nablarch-patterns-Nablarchでの非同期処理.json:s1、about/about-nablarch/about-nablarch-policy.json:s6、processing-pattern/web-application/web-application-architecture.json:s1

---
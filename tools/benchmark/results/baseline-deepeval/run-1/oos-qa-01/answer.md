知識ファイルへのWebSocket実装記述がないことが確認できました。Step 5の回答を生成します。

---

**結論**: NablarchにはWebSocketをサポートする機能はありません。

NablarchのウェブアプリケーションはServletAPIを前提に構築されており（`web-application-architecture.json:s1`）、WebSocket通信はNablarchのハンドラキューの管理対象外です。また、NablarchはOSSを使用しない方針のため、WebSocket向けのアダプタも提供されていません（`about-nablarch-policy.json:s6`）。

---

**verify Step 6**: 抽出するNablarch固有の主張：
1. 「NablarchのウェブアプリはServletAPIを前提」→ web-application-architecture.json:s1 に明記 → **supported**
2. 「OSSは使用しないポリシー、WebSocketアダプタも提供されていない」→ `about-nablarch-policy.json:s6` に明記 → **supported**

`verify_result = PASS`

---

**結論**: NablarchにはWebSocketをネイティブにサポートする機能は提供されていません。

---

## 回答

**結論**: NablarchはWebSocketを直接サポートしていません。バッチ処理の進捗をブラウザへリアルタイム通知する場合、Nablarchフレームワーク側の機能では実現できません。

**根拠**:

NablarchのウェブアプリケーションはServletAPIの使用を前提としており、WebSocketはこのアーキテクチャの管理外です。Nablarchのプロダクションコードはセキュリティ対応の迅速性を理由にOSSを使用しない方針のため、WebSocket向けのアダプタも提供されていません。

**注意点**:

WebSocketを使いたい場合は以下の選択肢があります（いずれもNablarchフレームワークの対象外）：

- **Jakarta WebSocket仕様を直接使用**: アプリケーションサーバーが Jakarta WebSocket（`jakarta.ee/specifications/websocket/`）をサポートしていれば、`@ServerEndpoint` アノテーション等でNablarchとは独立したWebSocketエンドポイントを実装できます。ただし、Nablarchのハンドラキューやコンポーネント設定は適用されません。

- **ポーリング方式での代替**: バッチ側はNablarchのバッチ進捗ログ機能（`ProgressManager`）や状態保持をDBに書き込み、ブラウザから定期的にRESTエンドポイントへポーリングして進捗を取得する方式が、Nablarch標準機能の範囲で実現できます。

この情報は知識ファイルの対象範囲外のため、WebSocketの実装詳細についてはアプリケーションサーバーのドキュメントをご参照ください。

参照: `processing-pattern/web-application/web-application-architecture.json:s1`, `about/about-nablarch/about-nablarch-policy.json:s6`

---
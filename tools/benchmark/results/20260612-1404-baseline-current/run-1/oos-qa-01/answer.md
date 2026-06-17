**結論**: NablarchはWebSocketをネイティブサポートしていません。NablarchのウェブアプリケーションはServlet APIベースのハンドラキューアーキテクチャで構築されており、WebSocketハンドラは標準提供されていません。バッチ進捗のブラウザ通知には、**DBを介したポーリング**（ブラウザが定期的にREST APIで進捗を問い合わせる）が現実的な代替手段です。

**根拠**:

NablarchウェブアプリケーションはServlet APIの使用を前提としており、WebFrontControllerがリクエストをハンドラキューに委譲するリクエスト・レスポンス型のアーキテクチャを採用しています。

```
1. WebFrontController (jakarta.servlet.Filter) がrequestを受信
2. ハンドラキューに委譲
3. DispatchHandlerがURIからアクションクラスを特定
4. アクションクラスがHttpResponseを返却
5. HTTPレスポンスハンドラがクライアントへレスポンスを返却
```

標準で提供されているハンドラ一覧にはWebSocketハンドラは含まれておらず、HTTP文字エンコード制御ハンドラ、HTTPレスポンスハンドラ、セッション変数保存ハンドラ、トランザクション制御ハンドラ等のHTTPリクエスト・レスポンス処理を前提とするもののみです。

また、Nablarchの基本方針として「プロダクションコードはOSSを使用しない」とされています。WebSocketはOSSの実装ライブラリに依存するケースが多く、Nablarchが直接サポートしない理由の一つです。なお、OSSを使用する機能はアダプタとして提供する方針があるため、WebSocketアダプタが将来提供される可能性はありますが、現時点では存在しません。

**代替アプローチ（ポーリング）**:

バッチ処理側でDBやファイルに進捗情報を書き込み（Nablarchバッチは`ExecutionContext`や`AtomicInteger`での状態保持をサポート）、ウェブアプリ側が定期的にREST APIで問い合わせる構成が現実的です：

```
バッチ処理 → 進捗をDB/テーブルに書き込み
ウェブ側   → ブラウザからJS setInterval でポーリング
           → REST APIが進捗情報をJSONで返却
```

**注意点**:
- WebSocketを独自実装する場合は、Jakarta EEのWebSocket API（`@ServerEndpoint`等）をNablarchのハンドラキューの外側で直接使用する形になりますが、Nablarchのリクエスト処理パイプラインとは切り離した実装となります。この場合のNablarchとの統合方法はドキュメントに記載がなく、サポート対象外の構成となります。
- この情報は知識ファイルの対象範囲外です（WebSocketアダプタ・代替手段の具体的実装方法について）。

参照: web-application-architecture.json:s1, web-application-architecture.json:s2, web-application-architecture.json:s3, about-nablarch-policy.json:s6
**結論**: NablarchはWebSocketを標準サポートしていないため、NablarchのAPIやハンドラ機能としてWebSocketを使う方法はありません。

**根拠**:

Nablarchのウェブアプリケーション基盤はServlet APIを前提としており、処理の流れは「HTTPリクエスト受信 → ハンドラキュー → アクション → HttpResponse返却」という同期的なモデルです。

```
クライアント → WebFrontController (Servlet Filter)
             → ハンドラキュー
             → アクションクラス
             → HttpResponse返却
```

Nablarchの環境要件（`about-nablarch-platform.json`）に含まれる仕様一覧:

| 仕様 | バージョン |
|------|-----------|
| Jakarta Servlet | 6.0 |
| Jakarta Server Pages | 3.1 |
| Jakarta RESTful Web Services | 3.1 |
| ... | ... |

**Jakarta WebSocket はこの一覧に含まれていません。**

また、「Nablarchでの非同期処理」のガイドでは、非同期通知のパターンとしてメール送信（常駐バッチ経由）のみが示されており、WebSocket等によるブラウザへのプッシュ通知については記載がありません。

**注意点**:

バッチ進捗をブラウザにリアルタイム通知する代替手法として、Nablarchの知識ファイルの対象範囲では以下が考えられます:

- **ポーリング方式**: ブラウザが一定間隔でNablarchの通常HTTPエンドポイントに進捗確認リクエストを送る（Nablarchの標準機能で実現可能）
- **Jakarta WebSocketをNablarch外で併用**: アプリケーションサーバの機能として`web.xml`にWebSocketエンドポイントを登録するアプローチは、Nablarchのハンドラキューを経由しない独自実装になります。この方式の詳細はこの知識ファイルの対象範囲外です。

参照: processing-pattern/web-application/web-application-architecture.json:s1, about/about-nablarch/about-nablarch-platform.json:s1, guide/nablarch-patterns/nablarch-patterns-Nablarchでの非同期処理.json:s1, about/about-nablarch/about-nablarch-policy.json:s6

---
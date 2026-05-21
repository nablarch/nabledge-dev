セクション内容を確認しました。Step 5で回答を生成します。

**結論**: NablarchにはWebSocketのネイティブサポートはありません。NablarchのウェブアプリケーションフレームワークはServlet APIを基盤としており、WebSocketハンドラは提供されていません。バッチ処理の状態をブラウザへ通知する非同期パターンとしては、**テーブルをキューとして使ったメッセージング**によるポーリング方式が推奨されます。

**根拠**:

Nablarchのウェブアプリケーションは`WebFrontController`（サーブレットフィルタ）を中心に構成されており、提供されているハンドラ一覧にはWebSocket関連のものがありません（HTTP文字エンコード制御・HTTPレスポンス・データベース接続管理・CSRFトークン検証など）。

**Nablarch推奨の非同期パターン（テーブルキュー方式）**:

```
Webアプリ → リクエストを受け付け、後続処理に必要なデータをDBに登録 → レスポンス返却
テーブルをキューとして使ったメッセージング → DBへのデータ登録を検知 → 当該データの処理を実行
```

バッチの進捗状況をブラウザへ届けるには、この方式を応用して次のような設計が考えられます：
1. バッチ処理側が進捗データをDBテーブルに書き込む
2. ブラウザ側がポーリング（定期的なREST APIコール）で進捗テーブルを参照する

**バッチ側で取得できる進捗情報（Jakarta Batch）**:

`ProgressManager`を使ってBatchletから進捗ログを出力可能です：

```java
@Named
@Dependent
public class ProgressBatchlet extends AbstractBatchlet {

    private final ProgressManager progressManager;
    private static final int PROGRESS_LOG_INTERVAL = 1000;

    @Inject
    public ProgressBatchlet(ProgressManager progressManager) {
      this.progressManager = progressManager;
    }

    @Override
    public String process() throws Exception {
      progressManager.setInputCount(10000);
      long processedCount = 0;

      while (処理対象が存在している間) {
          processedCount++;
          if (processedCount % PROGRESS_LOG_INTERVAL == 0) {
            progressManager.outputProgressInfo(processedCount);
          }
      }
      return "SUCCESS";
    }
}
```

進捗ログには以下の情報が含まれます：
- 開始後からのTPS・最新TPS
- 未処理件数
- 終了予測時間

**注意点**:

- NablarchはWebSocketを直接サポートしないため、WebSocketが必要な場合はアプリケーションサーバーのWebSocket機能を直接利用することになりますが、その実装はNablarchの知識範囲外です
- テーブルキュー方式はポーリングベースであり、厳密なリアルタイム通知ではなくポーリング間隔分の遅延が発生します

参照: `processing-pattern/web-application/web-application-architecture.json:s1`, `processing-pattern/web-application/web-application-architecture.json:s3`, `guide/nablarch-patterns/nablarch-patterns-Nablarchでの非同期処理.json:s1`, `processing-pattern/jakarta-batch/jakarta-batch-progress-log.json:s1`, `processing-pattern/jakarta-batch/jakarta-batch-progress-log.json:s3`

---
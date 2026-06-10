**結論**: DBからデータを読み込んで集計し、別テーブルへ書き込む定期処理は、Nablarchバッチの「都度起動バッチ」＋「DB to DB」パターンで実装します。`DatabaseRecordReader` で入力データを1件ずつ読み込み、`BatchAction` の `handle` メソッドで集計・書き込み処理を行う構成が基本です。

---

**根拠**:

### 全体構成（DB to DBパターン）

| 要素 | 説明 |
|------|------|
| 起動方法 | 都度起動バッチ（日次・月次など定期実行） |
| データリーダ | `DatabaseRecordReader`（SELECT結果を1件ずつ提供） |
| アクション | `BatchAction` を継承して実装 |
| DBアクセス | ユニバーサルDAO（または JDBCラッパー） |

---

### ハンドラ構成（最小構成）

都度起動バッチ（DB接続有り）の最小ハンドラキューは以下の順で設定します：

| No. | ハンドラ | 役割 |
|-----|----------|------|
| 1 | ステータスコード→プロセス終了コード変換ハンドラ | 終了コード変換 |
| 2 | グローバルエラーハンドラ | 例外ログ出力 |
| 3 | データベース接続管理ハンドラ（初期処理用） | DB接続確保 |
| 4 | トランザクション制御ハンドラ（初期処理用） | 初期トランザクション |
| 5 | リクエストディスパッチハンドラ | アクションの決定 |
| 6 | マルチスレッド実行制御ハンドラ | サブスレッド起動 |
| 7 | データベース接続管理ハンドラ（業務処理用） | 業務用DB接続 |
| 8 | **トランザクションループ制御ハンドラ** | コミット間隔制御＋ループ |
| 9 | データリードハンドラ | 1件読み込み |

---

### 実装例

**アクションクラス（BatchActionを継承）**:

```java
public class AggregationBatchAction extends BatchAction<AggregationInputForm> {

    @Override
    public Result handle(AggregationInputForm inputData, ExecutionContext ctx) {
        // 集計結果エンティティを生成
        AggregationResult result = new AggregationResult();
        result.setKey(inputData.getKey());
        result.setAmount(inputData.getAmount());

        // 別テーブルへ書き込み
        UniversalDao.insert(result);

        return new Result.Success();
    }

    @Override
    public DataReader<AggregationInputForm> createReader(ExecutionContext ctx) {
        // DatabaseRecordReader を使用
        DatabaseRecordReader reader = new DatabaseRecordReader();
        reader.setStatement(/* SQLIDを設定 */);
        return reader;
    }
}
```

---

### 大量データの場合：遅延ロードを使用

入力データが大量の場合、全件をメモリに展開するとメモリ不足になります。`UniversalDao.defer()` を使い、サーバサイドカーソルで1件ずつ処理します：

```java
try (DeferredEntityList<InputData> list =
        (DeferredEntityList<InputData>) UniversalDao.defer()
            .findAllBySqlFile(InputData.class, "SEARCH_INPUT")) {
    for (InputData data : list) {
        // 処理
    }
}
```

> `DeferredEntityList#close` を必ず呼ぶ必要があります（try-with-resources推奨）。

---

**注意点**:
- トランザクションループ制御ハンドラのコミット間隔を適切に設定してください。コミット間隔が大きすぎると1トランザクションが長大になり、小さすぎるとオーバーヘッドが増えます。
- 遅延ロード使用中にトランザクション制御（コミット）が発生すると、RDBMSによってはカーソルがクローズされエラーになる場合があります。その場合はページング等で回避してください。
- 起動は `javaコマンド` から直接実行し、コマンドライン引数 `-requestPath=アクションクラス名/リクエストID` でアクションを指定します。

参照: nablarch-batch-architecture.json:s3, nablarch-batch-architecture.json:s5, nablarch-batch-architecture.json:s7, nablarch-batch-architecture.json:s8, nablarch-patterns-Nablarchバッチ処理パターン.json:s1, nablarch-patterns-Nablarchバッチ処理パターン.json:s2, nablarch-patterns-Nablarchバッチ処理パターン.json:s4, nablarch-batch-getting-started-nablarch-batch.json:s3, libraries-universal-dao.json:s9
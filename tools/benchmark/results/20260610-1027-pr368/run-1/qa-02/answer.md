**結論**: 定期的にDBからデータを読み込んで別テーブルへ書き込む処理は「DB to DB パターンの都度起動バッチ」として実装します。`DatabaseRecordReader` で入力テーブルをSELECTし、`BatchAction` の `handle` メソッドで集計ロジックを実行し、`UniversalDao` で結果テーブルへ書き込む構成が標準です。

---

**根拠**:

**起動方式の選択**

日次・月次などの定期処理には「都度起動バッチ」を使用します（毎回プロセスを起動して処理を実行）。

**DB to DB パターンの特性**

- 入力はSELECT文の結果セットの各レコード
- 1レコード分のデータを受け取ってDBを更新
- 1レコードの処理中に行われる更新は全て同一トランザクション下で実行されるため、障害発生時でも不整合が発生しない

**ハンドラキュー構成（都度起動バッチ、DB接続有り）**

| No. | ハンドラ | スレッド |
|---|---|---|
| 1 | ステータスコード→プロセス終了コード変換ハンドラ | メイン |
| 2 | グローバルエラーハンドラ | メイン |
| 3 | データベース接続管理ハンドラ（初期処理/終了処理用） | メイン |
| 4 | トランザクション制御ハンドラ（初期処理/終了処理用） | メイン |
| 5 | リクエストディスパッチハンドラ | メイン |
| 6 | マルチスレッド実行制御ハンドラ | メイン |
| 7 | データベース接続管理ハンドラ（業務処理用） | サブ |
| 8 | トランザクションループ制御ハンドラ | サブ |
| 9 | データリードハンドラ | サブ |

**実装の要点**

`BatchAction` を継承して業務アクションクラスを作成します。

```java
public class AggregationBatchAction extends BatchAction<SqlRow> {

    @Override
    public Result handle(SqlRow inputData, ExecutionContext ctx) {
        // 集計ロジックを実行し、結果テーブルへ書き込む
        AggregationResult result = BeanUtil.createAndCopy(AggregationResult.class, inputData);
        // 集計処理（Javaコードで計算）
        UniversalDao.insert(result);
        return new Result.Success();
    }

    @Override
    public DataReader<SqlRow> createReader(ExecutionContext ctx) {
        // DatabaseRecordReader で入力テーブルを読み込む
        DatabaseRecordReader reader = new DatabaseRecordReader();
        reader.setStatement(
            AppDbConnection.find("YOUR_SQL_ID")
        );
        return reader;
    }
}
```

- `createReader` メソッドで `DatabaseRecordReader` のインスタンスを返却する
- `handle` メソッドにデータリーダから渡された1レコード分のデータに対する処理を実装する
- `UniversalDao.insert` で結果テーブルへ書き込む

**起動コマンド**

```bash
java -jar app.jar \
  -requestPath=com.example.AggregationBatchAction/BATCH001 \
  -diConfig=classpath:batch-config.xml \
  -userId=batch_user
```

---

**注意点**:

- `トランザクションループ制御ハンドラ` のコミット間隔（`commitInterval`）を適切に設定すること。デフォルトでは入力レコード全件をまとめてコミットする。大量データの場合はコミット間隔を設定して分割コミットを検討する。
- `DatabaseRecordReader` を使用する場合、ループ処理はハンドラキューのフレームワーク制御下（トランザクションループ制御ハンドラ）で行われる。フレームワーク制御外でループを書くアンチパターンに注意すること。

参照: nablarch-patterns-Nablarchバッチ処理パターン.json:s1, nablarch-patterns-Nablarchバッチ処理パターン.json:s2, nablarch-patterns-Nablarchバッチ処理パターン.json:s4, nablarch-batch-architecture.json:s3, nablarch-batch-architecture.json:s5, nablarch-batch-architecture.json:s7, nablarch-batch-architecture.json:s8, nablarch-batch-getting-started-nablarch-batch.json:s3
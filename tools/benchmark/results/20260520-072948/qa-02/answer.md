**結論**: 定期実行でDBからデータを読み込んで別テーブルに書き込む処理は、**都度起動バッチの DB to DB パターン**で実装します。`BatchAction` を継承したアクションクラスと `DatabaseRecordReader` を組み合わせ、フレームワークのループ制御に乗せることで、トランザクション管理も自動化されます。

**根拠**:

**① 処理パターンの選択**

Nablarchバッチには入出力パターンによる分類があります。

| パターン | 説明 |
|---------|------|
| DB to DB | 入力：SELECT結果セット、出力：DBへの更新 ← **今回のケース** |
| FILE to DB | ファイルを読み込んでDBへ登録 |
| DB to FILE | DBを読み込んでファイルへ出力 |

日次・月次などの定期実行には**都度起動バッチ**を使います（プロセスを都度起動して処理を実行する形式）。

**② 実装構成**

```
起動コマンド例
mvn exec:java -Dexec.mainClass=nablarch.fw.launcher.Main \
  -Dexec.args="'-requestPath' 'SampleAggregationAction/BATCH001' '-diConfig' 'classpath:batch.xml' '-userId' '000'"
```

**データリーダ（createReader）**: 読み込み元テーブルを SELECT するリーダを実装します。

**アクションクラス（handle）**: 1レコードごとに集計処理と書き込みを行います。

```java
public class SampleAggregationAction extends BatchAction<SqlRow> {

    @Override
    public Result handle(SqlRow inputData, ExecutionContext ctx) {
        // 1レコードに対する集計・加工処理
        ResultEntity result = aggregate(inputData);
        // 別テーブルへの書き込み
        UniversalDao.insert(result);
        return new Result.Success();
    }

    @Override
    public DataReader<SqlRow> createReader(ExecutionContext ctx) {
        DatabaseRecordReader reader = new DatabaseRecordReader();
        ParameterizedSqlPStatement stmt = DbConnectionContext
            .getConnection()
            .prepareParameterizedSqlStatementBySqlId(
                "com.example.SampleAggregationAction#SELECT_INPUT");
        reader.setStatement(stmt);
        return reader;
    }
}
```

**③ ハンドラ構成（都度起動バッチ DB接続有り）**

| No. | ハンドラ | 役割 |
|-----|---------|------|
| 1 | ステータスコード→プロセス終了コード変換ハンドラ | 終了コード変換 |
| 2 | グローバルエラーハンドラ | 例外ログ出力 |
| 3 | データベース接続管理ハンドラ（初期処理用） | DB接続管理 |
| 4 | トランザクション制御ハンドラ（初期処理用） | 初期処理トランザクション |
| 5 | リクエストディスパッチハンドラ | アクションクラス特定 |
| 6 | マルチスレッド実行制御ハンドラ | サブスレッド生成 |
| 7 | データベース接続管理ハンドラ（業務処理用） | 業務DBセッション |
| 8 | **トランザクションループ制御ハンドラ** | **コミット間隔制御＋ループ** |
| 9 | データリードハンドラ | 1件ずつ読み込み |

トランザクションループ制御ハンドラがコミット間隔を自動制御するため、大量データ処理でもトランザクションログが逼迫しません。

**注意点**:

- **N+1問題を避ける**: `handle` メソッド内で追加の SELECT を発行してはいけません。集計に必要なデータは `createReader` の SQL に JOIN で含めてください

  ```sql
  -- OK: createReaderのSQLでJOINして必要なデータを一括取得
  SELECT a.id, a.amount, b.category
  FROM sales a
  INNER JOIN sales_detail b ON a.id = b.sales_id
  WHERE a.sales_date = ?
  ```

- **自前ループ禁止**: `handle` 内で `for` ループを書いてはいけません。フレームワークのループ制御を使うことでコミットが一定間隔で実行されます。`NoInputDataBatchAction` で手動ループするのは典型的なアンチパターンです

参照: nablarch-patterns-Nablarchバッチ処理パターン.json:s1, nablarch-patterns-Nablarchバッチ処理パターン.json:s2, nablarch-patterns-Nablarchバッチ処理パターン.json:s4, nablarch-batch-architecture.json:s1, nablarch-batch-architecture.json:s3, nablarch-batch-architecture.json:s5, nablarch-batch-architecture.json:s7, nablarch-batch-architecture.json:s8, nablarch-patterns-Nablarchアンチパターン.json:s3, nablarch-patterns-Nablarchアンチパターン.json:s4, nablarch-patterns-Nablarchアンチパターン.json:s9, nablarch-patterns-Nablarchアンチパターン.json:s11
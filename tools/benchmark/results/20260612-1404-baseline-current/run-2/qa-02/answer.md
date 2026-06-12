**結論**: DBからデータを読み込んで集計し別テーブルに書き込む定期処理は、**都度起動バッチ（DB to DB パターン）**で実装します。`DatabaseRecordReader` で入力テーブルの各レコードを1件ずつ読み込み、`BatchAction` の `handle` メソッドで集計・書き込みを行い、`UniversalDao` で出力テーブルに登録します。

---

**根拠**:

### 1. バッチ種別の選択

日次・月次など定期起動するバッチは **都度起動バッチ** を使用します。入出力パターンとしては **DB to DB** が該当し、1レコードの処理中に行われる更新は全て同一トランザクション下で実行されるため、障害発生時でも不整合が発生しません。

### 2. ハンドラ構成（都度起動バッチ＋DB接続有り）

必要最小限のハンドラキューは以下の通りです：

| No. | ハンドラ | スレッド |
|-----|----------|----------|
| 1 | ステータスコード→プロセス終了コード変換ハンドラ | メイン |
| 2 | グローバルエラーハンドラ | メイン |
| 3 | データベース接続管理ハンドラ（初期処理/終了処理用） | メイン |
| 4 | トランザクション制御ハンドラ（初期処理/終了処理用） | メイン |
| 5 | リクエストディスパッチハンドラ | メイン |
| 6 | マルチスレッド実行制御ハンドラ | メイン |
| 7 | データベース接続管理ハンドラ（業務処理用） | サブ |
| 8 | トランザクションループ制御ハンドラ | サブ（コミット間隔制御） |
| 9 | データリードハンドラ | サブ |

### 3. データリーダの選択

DBからデータを読み込む場合は標準提供の **`DatabaseRecordReader`** を使用します。

### 4. アクションクラスの実装

`BatchAction` を継承し、`createReader` でリーダを返し、`handle` に集計・書き込みロジックを実装します：

```java
public class SampleAggregationAction extends BatchAction<SomeBeanForm> {

    @Override
    public DataReader<SomeBeanForm> createReader(ExecutionContext ctx) {
        // DatabaseRecordReader で入力テーブルを SELECT する
        return new SomeDbRecordReader();
    }

    @Override
    public Result handle(SomeBeanForm inputData, ExecutionContext ctx) {
        // 集計処理を実行し、結果テーブルに書き込む
        ResultEntity result = aggregate(inputData);
        UniversalDao.insert(result);
        return new Result.Success();
    }
}
```

`UniversalDao.insert()` で出力テーブルへの登録が行えます。大量データを一括登録する場合は `UniversalDao.batchInsert()` によりラウンドトリップ回数を削減できます。

### 5. 大量データの注意点

入力データが大量の場合は遅延ロード（`UniversalDao.defer()`）も検討できますが、RDBMSによってはカーソルオープン中のトランザクション制御でカーソルがクローズされる場合があります。バッチの場合は `DatabaseRecordReader` 経由でフレームワークが1件ずつ処理するため、通常はこの問題を回避できます。

**注意点**:
- トランザクションループ制御ハンドラのコミット間隔は要件に応じて設定してください（デフォルトは1件ごとコミット）
- 起動は `javaコマンド` から `-requestPath=アクションクラス名/リクエストID` を指定して行います

参照: nablarch-batch-architecture.json:s3, nablarch-batch-architecture.json:s5, nablarch-batch-architecture.json:s7, nablarch-batch-architecture.json:s8, nablarch-patterns-Nablarchバッチ処理パターン.json:s4, nablarch-patterns-Nablarchバッチ処理パターン.json:s2, nablarch-batch-getting-started-nablarch-batch.json:s3, libraries-universal-dao.json:s9, libraries-universal-dao.json:s14
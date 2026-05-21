これで十分な情報が揃いました。回答を生成します。

---

**結論**: 「DB to DB」パターンの都度起動バッチとして実装する。`DatabaseRecordReader` で入力テーブルを1件ずつ読み込み、`BatchAction` の `handle` メソッドで集計処理を実行し、`UniversalDao` で結果テーブルに書き込む構成が基本形。

**根拠**:

**全体構成（DB to DBパターン）**

```
入力テーブル → DatabaseRecordReader → BatchAction#handle（集計ロジック） → UniversalDao.insert/update → 結果テーブル
```

ハンドラキュー（都度起動バッチ、DB接続あり）:

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

**アクションクラスの実装例**

```java
public class AggregationBatchAction extends BatchAction<SalesEntity> {

    @Override
    public Result handle(SalesEntity inputData, ExecutionContext ctx) {
        // 集計ロジックを実行
        SummaryEntity summary = aggregate(inputData);
        // 結果テーブルに書き込み
        UniversalDao.insert(summary);
        return new Result.Success();
    }

    @Override
    public DataReader<SalesEntity> createReader(ExecutionContext ctx) {
        // DatabaseRecordReader を使用して入力テーブルを読み込む
        return new DatabaseRecordReader();
    }
}
```

**大量データの場合のDB読み込み（遅延ロード）**

大量データを処理する場合、`UniversalDao.defer()` を使用してメモリ消費を抑えられる:

```java
try (DeferredEntityList<SalesEntity> records
        = (DeferredEntityList<SalesEntity>) UniversalDao.defer()
                                            .findAllBySqlFile(SalesEntity.class, "FIND_TARGET")) {
    for (SalesEntity record : records) {
        // 処理
    }
}
```

**注意点**:
- DB to DBパターンでは、1レコードの処理中に行われる更新は全て同一トランザクション下で実行されるため、障害発生時でも不整合が発生しない
- 遅延ロードを使用する場合、カーソルオープン中にトランザクション制御が行われるとカーソルがクローズされる可能性がある。使用するRDBMSのマニュアルを確認すること
- バッチの起動は `javaコマンド` から `-requestPath` でアクションとリクエストIDを指定する:
  ```
  -requestPath=com.example.AggregationBatchAction/BATCH0001
  ```

参照: nablarch-batch-architecture.json:s3, nablarch-batch-architecture.json:s5, nablarch-batch-architecture.json:s7, nablarch-batch-architecture.json:s8, nablarch-patterns-Nablarchバッチ処理パターン.json:s1, nablarch-patterns-Nablarchバッチ処理パターン.json:s2, nablarch-patterns-Nablarchバッチ処理パターン.json:s4, libraries-universal-dao.json:s9, libraries-universal-dao.json:s7

---
**結論**: DBから読み込んで集計し別テーブルに書き込む処理は、Nablarchバッチの **DB to DB パターン（都度起動バッチ）** で実装します。`BatchAction` を継承したアクションクラスと `DatabaseRecordReader` を使い、`handle` メソッド内で集計・書き込みを行う構成が基本形です。

---

**根拠**:

**① 処理パターンの選択**

定期実行（日次・月次）なら都度起動バッチを選びます。DBを読んでDBに書く処理は「DB to DB」パターンに該当します。

- 入力: SELECT文の結果セット（レコード1件ずつ）
- 出力: DB更新
- 1レコードの処理中の更新は全て同一トランザクション下で実行されるため、障害発生時でも不整合が発生しません

**② アクションクラスの実装**

`BatchAction` を継承し、`createReader` でリーダを返し、`handle` で1レコード分の業務ロジックを実装します。

```java
public class AggregationBatchAction extends BatchAction<AggregationForm> {

    @Override
    public Result handle(AggregationForm inputData, ExecutionContext ctx) {
        // 集計処理（inputDataを元に集計結果Entityを組み立て）
        AggregationResult result = buildResult(inputData);
        // 結果テーブルへの書き込み（INSERT or UPDATE）
        UniversalDao.insert(result);
        return new Result.Success();
    }

    @Override
    public DataReader<AggregationForm> createReader(ExecutionContext ctx) {
        // DatabaseRecordReaderを使用してDBから読み込む
        return new DatabaseRecordReader();
    }
}
```

**③ 最小ハンドラ構成（DB接続あり 都度起動バッチ）**

| No. | ハンドラ | スレッド |
|---|---|---|
| 1 | ステータスコード→プロセス終了コード変換ハンドラ | メイン |
| 2 | グローバルエラーハンドラ | メイン |
| 3 | データベース接続管理ハンドラ（初期処理/終了処理用） | メイン |
| 4 | トランザクション制御ハンドラ（初期処理/終了処理用） | メイン |
| 5 | リクエストディスパッチハンドラ | メイン |
| 6 | マルチスレッド実行制御ハンドラ | メイン |
| 7 | データベース接続管理ハンドラ（業務処理用） | サブ |
| 8 | トランザクションループ制御ハンドラ（LoopHandler） | サブ |
| 9 | データリードハンドラ | サブ |

**④ コミット間隔の設定**

大量データ処理時はトランザクションログ逼迫を防ぐため、`LoopHandler` の `commitInterval` を設定します。

```xml
<component class="nablarch.fw.handler.LoopHandler">
  <property name="commitInterval" value="1000" />
</component>
```

---

**注意点**:

- **N+1問題に注意**: `handle` メソッド内で追加の SELECT を発行すると処理件数 N に比例してSQLが増加します。集計に必要なデータは `createReader` のSQLで JOIN して1回で取得し、`handle` 内ではSELECTを発行しないようにしてください。
- **自前ループは禁止**: `handle` 内で SELECT + for ループを自前実装すると、フレームワークのコミット制御が効かず、トランザクションログを逼迫します。ループ処理は必ずフレームワーク（LoopHandler）に委ねてください。
- **起動コマンド**: `java` コマンドから `nablarch.fw.launcher.Main` をメインクラスとして起動し、`-requestPath` でアクションクラスとリクエストIDを指定します。

参照: nablarch-batch-architecture.json:s3, nablarch-batch-architecture.json:s5, nablarch-batch-architecture.json:s7, nablarch-batch-architecture.json:s8, nablarch-patterns-Nablarchバッチ処理パターン.json:s1, nablarch-patterns-Nablarchバッチ処理パターン.json:s2, nablarch-patterns-Nablarchバッチ処理パターン.json:s4, nablarch-patterns-Nablarchアンチパターン.json:s4, nablarch-patterns-Nablarchアンチパターン.json:s9, nablarch-patterns-Nablarchアンチパターン.json:s11, nablarch-batch-getting-started-nablarch-batch.json:s3, handlers-loop-handler.json:s5

---
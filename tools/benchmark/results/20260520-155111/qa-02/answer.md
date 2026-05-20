**結論**: DBからデータを読んで集計し別テーブルに書き込む定期処理は、**DB to DB パターンの都度起動バッチ**で実装します。`createReader` でSELECT（GROUP BYによる集計も可）、`handle` で結果テーブルへの書き込みを行う構成が基本です。

**根拠**:

**① 起動方式：都度起動バッチ**

定期処理（日次・月次など）には都度起動バッチを使います。コマンドライン引数 `-requestPath` でアクションを指定して起動します。

```bash
java nablarch.fw.launcher.Main \
  -requestPath com.example.AggregationBatchAction/BATCH001 \
  -diConfig classpath:aggregation-batch.xml \
  -userId system
```

**② ハンドラ構成（DB接続有り・都度起動）**

コンポーネント設定ファイルに以下の最小ハンドラ構成を記述します：

| No. | ハンドラ |
|-----|---------|
| 1 | ステータスコード→プロセス終了コード変換ハンドラ |
| 2 | グローバルエラーハンドラ |
| 3 | データベース接続管理ハンドラ（初期処理用） |
| 4 | トランザクション制御ハンドラ（初期処理用） |
| 5 | リクエストディスパッチハンドラ |
| 6 | マルチスレッド実行制御ハンドラ |
| 7 | データベース接続管理ハンドラ（業務処理用） |
| 8 | トランザクションループ制御ハンドラ |
| 9 | データリードハンドラ |

**③ アクションクラス実装**

```java
public class AggregationBatchAction extends BatchAction<SalesEntity> {

    @Override
    public Result handle(SalesEntity inputData, ExecutionContext ctx) {
        // 集計結果をエンティティにセットして書き込む
        AggregationResult result = new AggregationResult();
        result.setKey(inputData.getKey());
        result.setTotal(inputData.getTotal());
        UniversalDao.insert(result);
        return new Result.Success();
    }

    @Override
    public DataReader<SalesEntity> createReader(ExecutionContext ctx) {
        return new DatabaseRecordReader()
            .setStatement(createQuery())
            .setBeanClass(SalesEntity.class);
    }
}
```

**④ 集計SQLはcreateReaderで発行（重要）**

集計処理はSQLの `GROUP BY` で実現し、`createReader` 側でSELECT + 集計を完結させます。

```sql
-- SalesEntity.sql
SELECT
  dept_id AS key,
  SUM(amount) AS total
FROM sales
WHERE sale_date = :saleDate
GROUP BY dept_id
```

**注意点**:
- `handle` メソッド内で再度SELECTを発行すると **N+1問題** が発生し、大量データで深刻な性能劣化を招きます。集計に必要なデータはすべて `createReader` のSQLで取得してください
- `handle` 内で自前のループ処理（`for`でSQLを繰り返し発行）を実装すると、フレームワークのコミット制御が効かずトランザクションログが逼迫します。ループはフレームワーク（トランザクションループ制御ハンドラ）に任せてください
- `UniversalDao` は主キー以外の条件での更新/削除ができません。その場合はデータベースアクセス（JDBCラッパー）を使用してください

参照: nablarch-patterns-Nablarchバッチ処理パターン.json:s1, s2, s4, nablarch-batch-architecture.json:s3, s5, s7, s8, nablarch-patterns-Nablarchアンチパターン.json:s4, s9, s11, libraries-universal-dao.json:s9, s14
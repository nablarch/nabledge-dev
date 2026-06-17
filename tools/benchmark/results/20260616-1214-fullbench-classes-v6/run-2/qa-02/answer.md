**結論**: DB to DB パターンの**都度起動バッチ**として実装します。`DatabaseRecordReader` で入力テーブルを1レコードずつ読み込み、`BatchAction` を継承した業務アクションで集計処理を行い、`UniversalDao` で結果テーブルに書き込む構成です。

---

**根拠**

#### 全体構成（役割分担）

| 役割 | クラス/ハンドラ |
|------|---------------|
| 起動 | `nablarch.fw.launcher.Main`（`-requestPath`引数で指定） |
| DB読み込み | `DatabaseRecordReader`（データリーダ） |
| 業務処理・DB書き込み | `BatchAction` を継承した業務アクション |
| トランザクション制御 | `トランザクションループ制御ハンドラ` |

#### ハンドラ構成（都度起動バッチ DB接続有り）

```
メインスレッド:
  1. ステータスコード→プロセス終了コード変換ハンドラ
  2. グローバルエラーハンドラ
  3. データベース接続管理ハンドラ（初期処理/終了処理用）
  4. トランザクション制御ハンドラ（初期処理/終了処理用）
  5. リクエストディスパッチハンドラ
  6. マルチスレッド実行制御ハンドラ

サブスレッド:
  7. データベース接続管理ハンドラ（業務処理用）
  8. トランザクションループ制御ハンドラ   ← コミット間隔ごとにコミット
  9. データリードハンドラ               ← 1レコードずつ読み込み
```

#### 業務アクションの実装例

```java
public class AggregationBatchAction extends BatchAction<SqlRow> {

    @Override
    public Result handle(SqlRow inputData, ExecutionContext ctx) {
        // 1. 入力レコードから集計処理
        AggregationResult result = aggregate(inputData);

        // 2. 結果テーブルへ書き込み
        UniversalDao.insert(result);

        return new Result.Success();
    }

    @Override
    public DataReader<SqlRow> createReader(ExecutionContext ctx) {
        // DatabaseRecordReader で入力テーブルを読み込む
        DatabaseRecordReader reader = new DatabaseRecordReader();
        // ... SQL設定
        return reader;
    }
}
```

#### DB to DB パターンの特徴

- 入力はSELECT文の結果セットの各レコード
- 1レコードの処理中に行われる更新は全て同一トランザクション下で実行されるため、障害発生時でも不整合が発生しない

#### 起動方法

```bash
java nablarch.fw.launcher.Main \
  -requestPath=com.example.AggregationBatchAction/BATCH0001 \
  -diConfig classpath:aggregation-batch.xml \
  -userId batch-user
```

---

**注意点**:
- `トランザクションループ制御ハンドラ` の `commitInterval` でコミット間隔を設定することで、大量データ処理時のメモリ使用量を制御できる。
- `DatabaseRecordReader` でデータを読み込む場合は、`DataReader` インタフェースを実装するか、`BatchAction.createReader` でリーダを返す。

参照: nablarch-batch-architecture.json:s3, nablarch-batch-architecture.json:s5, nablarch-batch-architecture.json:s7, nablarch-batch-architecture.json:s8, nablarch-patterns-Nablarchバッチ処理パターン.json:s2, nablarch-patterns-Nablarchバッチ処理パターン.json:s4, nablarch-batch-getting-started-nablarch-batch.json:s3
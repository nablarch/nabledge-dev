Step 5: セクション内容をもとに回答を生成します。

---

**結論**: 「DB to DB」パターンの**都度起動バッチ**で実装する。入力テーブルのデータを `DatabaseRecordReader` で1件ずつ読み込み、`BatchAction` の `handle` メソッドで集計・書き込みを行う構成になる。

---

**根拠**:

### 1. 処理パターンの選択

DBから読んでDBへ書く → **DB to DB パターン（都度起動バッチ）**

定期的（日次・月次）にプロセスを起動して実行するため「都度起動」を選択する。  
DB to DB の特性として、1レコードの処理中に行われる更新は全て同一トランザクション下で実行されるため、障害発生時でも不整合が発生しない。

### 2. ハンドラ構成（都度起動バッチ DB接続有り）

コンポーネント設定ファイルに以下の順でハンドラを設定する：

| No | ハンドラ | スレッド |
|----|---------|---------|
| 1 | ステータスコード→プロセス終了コード変換ハンドラ | メイン |
| 2 | グローバルエラーハンドラ | メイン |
| 3 | データベース接続管理ハンドラ（初期処理/終了処理用） | メイン |
| 4 | トランザクション制御ハンドラ（初期処理/終了処理用） | メイン |
| 5 | リクエストディスパッチハンドラ | メイン |
| 6 | マルチスレッド実行制御ハンドラ | メイン |
| 7 | データベース接続管理ハンドラ（業務処理用） | サブ |
| 8 | トランザクションループ制御ハンドラ | サブ |
| 9 | データリードハンドラ | サブ |

### 3. データリーダ

入力テーブルの読み込みには `DatabaseRecordReader` を使用する。アクションクラスの `createReader` メソッドでこのリーダーを生成して返す。

### 4. アクションクラス

`BatchAction` を継承して業務アクションクラスを作成する。

```java
public class AggregationBatchAction extends BatchAction<SqlRow> {

    @Override
    public DataReader<SqlRow> createReader(ExecutionContext ctx) {
        // DatabaseRecordReader を使ってSELECT結果を1件ずつ提供する
        DatabaseRecordReader reader = new DatabaseRecordReader();
        // ...SQLの設定...
        return reader;
    }

    @Override
    public Result handle(SqlRow inputData, ExecutionContext ctx) {
        // 集計処理を実行し、結果エンティティを生成する
        AggregationResult result = aggregate(inputData);
        // 結果テーブルへの書き込み
        UniversalDao.insert(result);

        return new Result.Success();
    }
}
```

実装のポイント：
- `createReader` メソッドで `DatabaseRecordReader` のインスタンスを返す
- `handle` メソッドにデータリーダから1件ずつ渡されるレコードに対する業務ロジック（集計・書き込み）を実装する
- `UniversalDao.insert` で結果テーブルへの書き込みを行う

### 5. 起動方法

```bash
java nablarch.fw.launcher.Main \
  -requestPath AggregationBatchAction/BATCH0001 \
  -diConfig classpath:aggregation-batch.xml \
  -userId system
```

**注意点**: トランザクションループ制御ハンドラのコミット間隔はデフォルトで1件ごとのコミットとなる。大量データ処理の場合はコミット間隔の設定を検討すること。

参照: nablarch-batch-architecture.json:s3, nablarch-batch-architecture.json:s5, nablarch-batch-architecture.json:s7, nablarch-batch-architecture.json:s8, nablarch-patterns-Nablarchバッチ処理パターン.json:s2, nablarch-patterns-Nablarchバッチ処理パターン.json:s4, nablarch-batch-getting-started-nablarch-batch.json:s3

---
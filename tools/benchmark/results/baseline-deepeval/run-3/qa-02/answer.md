セクションの読み込みが完了しました。回答を生成します。

---

**結論**: Nablarchバッチの **DB to DB パターン（都度起動バッチ）** として実装する。`DatabaseRecordReader` でSELECT結果（集計SQLを含む）をレコード単位に読み込み、`BatchAction` の `handle()` メソッドで1件ずつ書き込みテーブルに登録する構成が基本形。

---

**根拠**:

### 全体構成

```
Main（共通起動ランチャ）
  → ハンドラキュー
      → BatchAction#handle()（1レコードごと呼び出し）
          → UniversalDao.insert() / batchInsert()（書き込みテーブルへ）
```

### ハンドラ構成（都度起動バッチ・DB接続有りの最小構成）

| No | ハンドラ（スレッド） | 役割 |
|---|---|---|
| 1 | StatusCodeConvertHandler（メイン） | 終了コード変換 |
| 2 | GlobalErrorHandler（メイン） | 例外ログ出力 |
| 3 | DatabaseConnectionManagementHandler（メイン） | 初期化用DB接続 |
| 4 | TransactionManagementHandler（メイン） | 初期化用トランザクション |
| 5 | RequestPathJavaPackageMappingHandler（メイン） | アクション振り分け |
| 6 | MultiThreadExecutionHandler（メイン） | サブスレッド生成 |
| 7 | DatabaseConnectionManagementHandler（サブ） | 業務処理用DB接続 |
| 8 | LoopHandler（サブ） | トランザクションループ制御（コミット間隔制御） |
| 9 | DataReadHandler（サブ） | 1件ずつレコードをアクションへ渡す |

### データリーダ

DBから読み込む場合は `DatabaseRecordReader` を使用する。集計処理をSQLで行う場合は、GROUP BYを含むSQLをデータリーダのSQLとして記述し、集計済みレコードを1件ずつアクションに渡す。

### アクションクラスの実装

```java
public class AggregationBatchAction extends BatchAction<AggregationForm> {

    @Override
    public Result handle(AggregationForm inputData, ExecutionContext ctx) {
        // 集計結果エンティティを生成して書き込みテーブルへ登録
        ResultEntity result = BeanUtil.createAndCopy(ResultEntity.class, inputData);
        UniversalDao.insert(result);
        return new Result.Success();
    }

    @Override
    public DataReader<AggregationForm> createReader(ExecutionContext ctx) {
        // DatabaseRecordReaderを返す（集計SQLはSQLファイルで管理）
        return new DatabaseRecordReader();
    }
}
```

### 大量件数の場合の注意

書き込みが大量になる場合は `UniversalDao.batchInsert(list)` を使用するとラウンドトリップ回数を削減できる。読み込み側で大量データを扱う場合は `UniversalDao.defer().findAllBySqlFile()` で遅延ロードし、必ず `DeferredEntityList#close()` を呼び出すこと。

```java
try (DeferredEntityList<AggregationForm> rows
        = (DeferredEntityList<AggregationForm>) UniversalDao.defer()
                .findAllBySqlFile(AggregationForm.class, "AGGREGATE_SQL")) {
    for (AggregationForm row : rows) {
        // 処理
    }
}
```

---

**注意点**:

- 1レコードの処理中に行われる更新はすべて同一トランザクション下で実行されるため、障害発生時でも不整合は発生しない
- `UniversalDao.batchUpdate` による一括更新では排他制御が行われない。排他制御が必要な更新は1件ごとの更新処理を使うこと
- 遅延ロード使用中にトランザクション制御（LoopHandlerによるコミット等）が行われると、RDBMSによってはカーソルがクローズされてエラーになる場合がある

参照: nablarch-batch-architecture.json:s3, nablarch-batch-architecture.json:s5, nablarch-batch-architecture.json:s7, nablarch-batch-architecture.json:s8, nablarch-patterns-Nablarchバッチ処理パターン.json:s4, nablarch-batch-getting-started-nablarch-batch.json:s3, libraries-universal-dao.json:s9, libraries-universal-dao.json:s14

---
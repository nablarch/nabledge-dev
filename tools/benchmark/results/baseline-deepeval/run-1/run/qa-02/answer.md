**結論**: DBからデータを読み込んで集計し別テーブルに書き込む定期処理は、Nablarchバッチの**都度起動バッチ**（DB to DBパターン）で実装します。`BatchAction` を継承したアクションクラス、`DatabaseRecordReader` でデータを読み込み、`UniversalDao` で結果テーブルに書き込む構成が基本です。

**根拠**:

**全体構成（DB to DBパターン）**

Nablarchバッチの入出力パターンとして「DB to DB」が定義されており、入力がSELECT文の結果セット、出力がDBへの更新になります。1レコードの処理中に行われる更新は全て同一トランザクション下で実行されるため、障害発生時でも不整合が発生しません。

| 役割 | クラス/コンポーネント |
|---|---|
| エントリポイント | `nablarch.fw.launcher.Main` (共通起動ランチャ) |
| データ読み込み | `DatabaseRecordReader` (DBからレコードを1件ずつ提供) |
| 業務ロジック | `BatchAction` を継承したアクションクラス |
| DB書き込み | `UniversalDao` または データベースアクセス(JDBCラッパー) |

**ハンドラ構成（都度起動バッチ、DB接続あり）**

| No. | ハンドラ |
|---|---|
| 1 | ステータスコード→プロセス終了コード変換ハンドラ |
| 2 | グローバルエラーハンドラ |
| 3 | データベース接続管理ハンドラ（初期処理/終了処理用） |
| 4 | トランザクション制御ハンドラ（初期処理/終了処理用） |
| 5 | リクエストディスパッチハンドラ |
| 6 | マルチスレッド実行制御ハンドラ |
| 7 | データベース接続管理ハンドラ（業務処理用） |
| 8 | トランザクションループ制御ハンドラ（コミット間隔制御） |
| 9 | データリードハンドラ |

**アクションクラスの実装例**

```java
public class AggregationBatchAction extends BatchAction<SourceEntity> {

    @Override
    public Result handle(SourceEntity inputData, ExecutionContext ctx) {
        // 集計ロジック
        ResultEntity result = aggregate(inputData);
        // 結果テーブルへの書き込み
        UniversalDao.insert(result);
        return new Result.Success();
    }

    @Override
    public DataReader<SourceEntity> createReader(ExecutionContext ctx) {
        return new DatabaseRecordReader();
    }
}
```

**UniversalDAOで任意SQLを使う場合（集計クエリ）**

集計にSQLが必要な場合は、SQLファイルを作成してSQL IDを指定して実行します：

```java
UniversalDao.findAllBySqlFile(SourceEntity.class, "AGGREGATE_DATA");
```

**起動コマンド例**

```bash
java nablarch.fw.launcher.Main \
  -requestPath=com.example.AggregationBatchAction/BATCH001 \
  -diConfig=classpath:batch-config.xml \
  -userId=batch
```

**注意点**:
- 集計結果の書き込み先テーブルへのINSERT/UPDATEで主キー以外の条件指定が必要な場合は、`UniversalDao` ではなくデータベースアクセス(JDBCラッパー)を使用すること（`UniversalDao` は主キー以外の条件を指定した更新/削除は行えない）
- 大量データを処理する場合、`UniversalDao#defer()` による遅延ロードを使用してメモリ枯渇を防ぐこと（`DeferredEntityList#close()` の呼び出しが必須）
- 常駐バッチよりも都度起動バッチが推奨。新規開発ではマルチスレッド時の処理遅延問題のない都度起動バッチを使用すること

参照: nablarch-batch-architecture.json:s1, nablarch-batch-architecture.json:s3, nablarch-batch-architecture.json:s5, nablarch-batch-architecture.json:s7, nablarch-batch-architecture.json:s8, nablarch-patterns-Nablarchバッチ処理パターン.json:s2, nablarch-patterns-Nablarchバッチ処理パターン.json:s4, libraries-universal-dao.json:s7, libraries-universal-dao.json:s9

---
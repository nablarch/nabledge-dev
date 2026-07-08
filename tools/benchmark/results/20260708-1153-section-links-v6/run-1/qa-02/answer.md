**結論**: DBからデータを読み込んで集計し別テーブルに書き込む定期処理は、「DB to DB」パターンの**都度起動バッチ**として実装します。`BatchAction` を継承したアクションクラスと、`DatabaseRecordReader` を使うデータリーダで構成し、1レコードずつ集計・書き込みを行います。

**根拠**:

**全体構成**

```
Main（共通起動ランチャ）
  └─ ハンドラキュー（都度起動バッチ最小構成）
       ├─ ステータスコード→プロセス終了コード変換ハンドラ
       ├─ グローバルエラーハンドラ
       ├─ データベース接続管理ハンドラ（初期処理/終了処理用）
       ├─ トランザクション制御ハンドラ（初期処理/終了処理用）
       ├─ リクエストディスパッチハンドラ
       ├─ マルチスレッド実行制御ハンドラ
       ├─ データベース接続管理ハンドラ（業務処理用）
       ├─ トランザクションループ制御ハンドラ  ← コミット間隔もここで制御
       └─ データリードハンドラ
```

**アクションクラスの実装例**

```java
// BatchAction<エンティティクラス> を継承する
public class AggregationBatchAction extends BatchAction<SalesEntity> {

    @Override
    public DataReader<SalesEntity> createReader(ExecutionContext ctx) {
        // DatabaseRecordReader を使ってDBから読み込む
        return new DatabaseRecordReader()
            .setStatement(DbConnectionContext.getConnection()
                .prepareStatementBySqlFile("sql/AggregationBatch/READ_SALES"));
    }

    @Override
    public Result handle(SalesEntity inputData, ExecutionContext ctx) {
        // 集計処理を実行してエンティティを組み立てる
        AggregationEntity aggr = aggregate(inputData);
        UniversalDao.insert(aggr);           // 別テーブルへ書き込む
        return new Result.Success();
    }
}
```

- `DatabaseRecordReader` がSELECT結果を1件ずつ提供し、`handle` メソッドに渡す
- `handle` 内で集計ロジックを実行し、結果を `UniversalDao.insert` で書き込む
- 1レコードの処理中の更新は全て同一トランザクション下で実行されるため、障害発生時でも不整合が発生しない

**起動コマンド**

```bash
java nablarch.fw.launcher.Main \
  -requestPath com.example.AggregationBatchAction/BATCH0001 \
  -diConfig classpath:aggregation-batch.xml \
  -userId batch_user
```

**注意点**:
- 大量データを処理する場合はメモリ枯渇を防ぐため、`UniversalDao.defer()` で遅延ロードを使うか、`トランザクションループ制御ハンドラ` の `commitInterval` でコミット間隔を適切に設定すること
- `UniversalDao` の `batchInsert` を使うと複数件をまとめてINSERTでき、ラウンドトリップを削減できる（ただし一括更新で排他制御が不要な場合のみ）
- 集計処理でSQLのGROUP BYが使える場合は、アクション側で1件ずつ集計するより、SQLで集計した結果をリーダーで読み込む形にした方がシンプルになる

参照:
- アーキテクチャ概要
  .claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-architecture.md
  Nablarchバッチアプリケーションの処理の流れ
  都度起動バッチの最小ハンドラ構成
  Nablarchバッチアプリケーションで使用するデータリーダ
  Nablarchバッチアプリケーションで使用するアクション
- Nablarchバッチ処理パターン
  .claude/skills/nabledge-6/docs/guide/nablarch-patterns/nablarch-patterns-Nablarchバッチ処理パターン.md
  入出力による分類
  DB to DB
- ユニバーサルDAO
  .claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md
  任意のSQL(SQLファイル)で検索する
  検索結果を遅延ロードする
  バッチ実行(一括登録、更新、削除)を行う
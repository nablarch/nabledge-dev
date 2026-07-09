**結論**: DB to DBパターンの**都度起動バッチ**として実装する。`BatchAction`を継承したアクションクラスに業務ロジックを実装し、`DatabaseRecordReader`で読み込みデータを1件ずつ提供、`UniversalDao`で書き込みを行う構成が基本となる。

---

**根拠**:

**① バッチ処理パターンの選択**

DBからデータを読み込んで別テーブルに書き込む処理は **DB to DB** パターン。  
日次・月次など定期的に実行する場合は**都度起動バッチ**を選択する。

```
起動方法  : 都度起動バッチ（javaコマンドで起動）
入出力    : DB to DB
```

**② 実装構成（3クラス）**

| 役割 | 実装 | 内容 |
|------|------|------|
| データリーダ | `DatabaseRecordReader`を使用 | DBから集計元テーブルを1件ずつ読み込む |
| アクションクラス | `BatchAction`を継承して作成 | `handle`メソッドに集計ロジックと結果テーブルへの書き込みを実装 |
| エンティティ | 書き込み先テーブルに対応するEntityクラス | `UniversalDao.batchInsert`等で登録 |

アクションクラスの骨格：
```java
public class AggregationBatchAction extends BatchAction<SqlRow> {

    @Override
    public DataReader<SqlRow> createReader(ExecutionContext ctx) {
        // DatabaseRecordReaderを生成して返す
        DatabaseRecordReader reader = new DatabaseRecordReader();
        // 読み込み用SQLの設定（SQLファイルで管理）
        reader.setStatement(
            DbConnectionContext.getConnection()
                .prepareStatementBySqlId("SELECT_AGGREGATE_SOURCE"));
        return reader;
    }

    @Override
    public Result handle(SqlRow inputData, ExecutionContext ctx) {
        // 集計ロジック → エンティティに変換して書き込み
        AggregationResult entity = new AggregationResult();
        // ... 集計処理 ...
        UniversalDao.insert(entity);
        return new Result.Success();
    }
}
```

**③ 最小ハンドラ構成（都度起動バッチ・DB接続あり）**

| No. | ハンドラ | 役割 |
|-----|---------|------|
| 1 | ステータスコード→プロセス終了コード変換ハンドラ | 終了コードへ変換 |
| 2 | グローバルエラーハンドラ | 例外ログ出力 |
| 3 | データベース接続管理ハンドラ (初期処理用) | DB接続取得・解放 |
| 4 | トランザクション制御ハンドラ (初期処理用) | 初期化トランザクション |
| 5 | リクエストディスパッチハンドラ | アクションクラス決定 |
| 6 | マルチスレッド実行制御ハンドラ | サブスレッド生成 |
| 7 | データベース接続管理ハンドラ (業務処理用) | 業務用DB接続 |
| 8 | **トランザクションループ制御ハンドラ** | 1件ずつループ＋コミット間隔制御 |
| 9 | データリードハンドラ | 1件読み込み |

**④ 大量データの場合のデータ読み込み**

`UniversalDao.defer()` を使うとサーバサイドカーソルで1件ずつメモリに展開でき、大量データでもメモリ不足を防げる。

```java
try (DeferredEntityList<SourceEntity> list =
        (DeferredEntityList<SourceEntity>) UniversalDao.defer()
            .findAllBySqlFile(SourceEntity.class, "SELECT_AGGREGATE_SOURCE")) {
    for (SourceEntity src : list) {
        // 集計処理
    }
}
```

`DeferredEntityList#close` は必ず呼び出す（try-with-resourcesを使用）。

**⑤ 結果テーブルへの一括書き込み（パフォーマンス向上）**

大量データを一括登録する場合は `batchInsert` を使用するとDB往復回数を削減できる。

```java
UniversalDao.batchInsert(resultEntityList);
```

---

**注意点**:

- `UniversalDao.defer()` 使用中にトランザクション制御を行うと、RDBMSによってはカーソルがクローズされエラーになる。コミット間隔との兼ね合いに注意すること。
- 集計処理の中で新たにSELECTするSQLが必要な場合は `UniversalDao.findAllBySqlFile()` でSQLファイルに外出しして管理する。
- 処理起動は `-requestPath=アクションクラス名/リクエストID` で指定する。

---

参照:
- Nablarchバッチ処理パターン
  .claude/skills/nabledge-6/docs/guide/nablarch-patterns/nablarch-patterns-Nablarchバッチ処理パターン.md
  起動方法による分類
  入出力による分類
  DB to DB
- アーキテクチャ概要
  .claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-architecture.md
  Nablarchバッチアプリケーションの処理の流れ
  都度起動バッチの最小ハンドラ構成
  Nablarchバッチアプリケーションで使用するデータリーダ
  Nablarchバッチアプリケーションで使用するアクション
- アプリケーションの責務配置
  .claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-application-design.md
- ユニバーサルDAO
  .claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md
  検索結果を遅延ロードする
  バッチ実行(一括登録、更新、削除)を行う
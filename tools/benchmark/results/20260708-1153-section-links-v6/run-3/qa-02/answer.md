**結論**: DBからデータを読み込んで集計・書き込む定期処理は、Nablarchバッチの「都度起動バッチ」＋「DB to DBパターン」で実装します。`BatchAction`を継承したアクションクラスと、`DatabaseRecordReader`を使ったデータリーダを用意し、1レコード単位で集計→書き込みを行う構成が標準です。

**根拠**:

#### 処理パターンの選択

「DBからデータを読み込んで別テーブルへ書き込む」は **DB to DBパターン**に該当します。入力はSELECT文の結果セット各レコード、出力はDBへの更新です。定期実行（日次・月次など）には **都度起動バッチ** を使います。

```
入力 (DatabaseRecordReader) → BatchAction#handle (集計・書き込み) → UniversalDao.insert/update
```

#### ハンドラ構成（都度起動バッチ・DB接続有り）

コンポーネント設定ファイル（XMLファイル）に以下のハンドラキューを定義します：

| No. | ハンドラ | 役割 |
|-----|----------|------|
| 1 | StatusCodeConvertHandler | プロセス終了コード変換 |
| 2 | GlobalErrorHandler | 例外ログ出力 |
| 3 | DbConnectionManagementHandler (初期/終了処理用) | メインDB接続管理 |
| 4 | TransactionManagementHandler (初期/終了処理用) | 初期トランザクション制御 |
| 5 | RequestPathJavaPackageMapping | アクションへディスパッチ |
| 6 | MultiThreadExecutionHandler | マルチスレッド化 |
| 7 | DbConnectionManagementHandler (業務処理用) | 業務DB接続管理 |
| 8 | LoopHandler | トランザクションループ制御（コミット間隔管理） |
| 9 | DataReadHandler | 1件ずつデータ読み込み |

#### アクションクラスの実装

```java
public class AggregateAction extends BatchAction<SummaryInputEntity> {

    @Override
    public Result handle(SummaryInputEntity inputData, ExecutionContext ctx) {
        // 集計結果エンティティを生成
        SummaryResultEntity result = buildSummary(inputData);
        // 別テーブルへ書き込み
        UniversalDao.insert(result);
        return new Result.Success();
    }

    @Override
    public DataReader<SummaryInputEntity> createReader(ExecutionContext ctx) {
        // DatabaseRecordReader を使って集計対象データを読み込む
        return new DatabaseRecordReader();
    }
}
```

#### データリーダの設定（コンポーネント定義）

```xml
<component class="nablarch.fw.reader.DatabaseRecordReader">
  <!-- SQL IDを指定して読み込み対象レコードを取得 -->
  <property name="query">
    <component class="nablarch.core.db.statement.SqlPStatement">
      <!-- SQLファイルで集計対象データのSELECT文を定義 -->
    </component>
  </property>
</component>
```

大量データを扱う場合は、ユニバーサルDAOの遅延ロード（`UniversalDao.defer().findAllBySqlFile(...)`）を活用するとメモリ効率が向上します：

```java
try (DeferredEntityList<SummaryInputEntity> records =
        (DeferredEntityList<SummaryInputEntity>) UniversalDao.defer()
            .findAllBySqlFile(SummaryInputEntity.class, "FIND_AGGREGATE_TARGET")) {
    for (SummaryInputEntity record : records) {
        // 1件ずつ処理
    }
}
```

#### 起動コマンド

```bash
java nablarch.fw.launcher.Main \
  -requestPath com.example.AggregateAction/AGGREGATE001 \
  -diConfig classpath:aggregate-batch.xml \
  -userId batch_user
```

**注意点**:
- `LoopHandler`の`commitInterval`プロパティでコミット間隔を設定することで、大量データ処理時のメモリ使用量とリカバリ単位を調整できます
- 集計処理でグループ集計（GROUP BY）が必要な場合は、SQLファイルにGROUP BY句を含むSELECT文を定義し、`UniversalDao.findAllBySqlFile`で呼び出す方法が効率的です
- 遅延ロード使用中にトランザクション制御（コミット）が行われるとカーソルが閉じられる場合があるため、RDBMSの仕様を確認してください

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
- ユニバーサルDAO
  .claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md
  任意のSQL(SQLファイル)で検索する
  検索結果を遅延ロードする
  バッチ実行(一括登録、更新、削除)を行う
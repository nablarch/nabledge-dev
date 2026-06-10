**結論**: DBからデータを読み込んで別テーブルに書き込む定期処理は、Nablarchバッチの **都度起動バッチ（DB to DB パターン）** で実装します。`DatabaseRecordReader` で入力テーブルを読み込み、`BatchAction` を継承したアクションクラスで集計処理とDB書き込みを行います。

---

**根拠**:

**① バッチ種別の選択**

日次・月次など定期的に起動する処理は **都度起動バッチ** を使用します。DB to DB パターンは都度起動バッチとの組み合わせが基本です。

```
入力: SELECTの結果レコード（1件ずつ処理）
出力: 別テーブルへINSERT/UPDATE
```

**② ハンドラ構成（都度起動バッチ・DB接続あり最小構成）**

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | ステータスコード→プロセス終了コード変換ハンドラ | 終了コード変換 |
| 2 | グローバルエラーハンドラ | 実行時例外ログ |
| 3 | データベース接続管理ハンドラ（初期処理用） | DB接続（初期化） |
| 4 | トランザクション制御ハンドラ（初期処理用） | トランザクション（初期化） |
| 5 | リクエストディスパッチハンドラ | アクション特定 |
| 6 | マルチスレッド実行制御ハンドラ | サブスレッド起動 |
| 7 | データベース接続管理ハンドラ（業務処理用） | DB接続（業務） |
| 8 | **トランザクションループ制御ハンドラ** | コミット間隔制御・ループ |
| 9 | データリードハンドラ | 1件ずつ読み込み |

**③ データリーダ**

入力テーブルは `DatabaseRecordReader` で読み込みます。大量データの場合は `UniversalDao.defer()` で遅延ロードします。

```java
// アクションクラス内でデータリーダを生成
@Override
public DataReader<SqlRow> createReader(ExecutionContext ctx) {
    // DatabaseRecordReaderを使うか、UniversalDaoのdeferを使ったカスタムリーダを実装
}
```

**④ アクションクラスの実装例**

```java
public class AggregationBatchAction extends BatchAction<SomeForm> {

    @Override
    public Result handle(SomeForm inputData, ExecutionContext ctx) {
        // 1レコード分の集計処理
        ResultEntity result = aggregate(inputData);
        
        // 結果テーブルへ書き込み
        UniversalDao.insert(result);
        
        return new Result.Success();
    }

    @Override
    public DataReader<SomeForm> createReader(ExecutionContext ctx) {
        return new SomeDataReader();  // DatabaseRecordReaderなどを使用
    }
}
```

大量データを読み込む場合は遅延ロードを使います：

```java
// try-with-resourcesでclose必須（サーバサイドカーソルを使用するため）
try (DeferredEntityList<InputEntity> inputs
        = (DeferredEntityList<InputEntity>) UniversalDao.defer()
                .findAllBySqlFile(InputEntity.class, "FIND_TARGET_DATA")) {
    for (InputEntity input : inputs) {
        // 1件ずつ処理
    }
}
```

**⑤ 起動コマンド**

```bash
java nablarch.fw.launcher.Main \
  -requestPath=com.example.AggregationBatchAction/BATCH0001 \
  -diConfig=classpath:batch-config.xml \
  -userId=admin
```

---

**注意点**:
- `DeferredEntityList` を使う場合、トランザクション制御（コミット）を行うとカーソルがクローズされる場合があるため、DBベンダーのマニュアルを確認すること
- `batchUpdate`（一括更新）では楽観的ロックが行われないため、排他制御が必要な更新には1件ずつの更新処理を使うこと
- コミット間隔はトランザクションループ制御ハンドラの `commitInterval` で設定する

参照: nablarch-batch-architecture.json:s3, nablarch-batch-architecture.json:s5, nablarch-batch-architecture.json:s7, nablarch-patterns-Nablarchバッチ処理パターン.json:s4, nablarch-batch-getting-started-nablarch-batch.json:s3, libraries-universal-dao.json:s9, libraries-universal-dao.json:s7
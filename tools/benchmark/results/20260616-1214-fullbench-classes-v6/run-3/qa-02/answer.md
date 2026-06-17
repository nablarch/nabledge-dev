**結論**: 「DBからデータを読み込んで集計し、別テーブルへ書き込む定期処理」は Nablarch バッチの **DB to DB パターン（都度起動バッチ）** で実装します。`DatabaseRecordReader` でデータを1件ずつ読み込み、`BatchAction` を継承したアクションクラスの `handle` メソッドで集計・書き込み処理を行います。

---

**根拠**

### 全体構成（DB to DB パターン）

| 要素 | 内容 |
|---|---|
| データリーダ | `DatabaseRecordReader`（DB からレコードを1件ずつ読み込む） |
| アクションクラス | `BatchAction` を継承して `handle` メソッドに業務ロジックを実装 |
| 起動方式 | 都度起動バッチ（日次・月次の定期処理に適する） |

DB to DB パターンの特徴：入力はSELECT文の結果セット、1レコードの処理中に行われる更新は同一トランザクション下で実行されるため、障害発生時でも不整合が発生しません。

---

### ハンドラ構成（都度起動バッチ DB接続有り 最小構成）

| No. | ハンドラ | スレッド | 役割 |
|---|---|---|---|
| 1 | ステータスコード→プロセス終了コード変換ハンドラ | メイン | 終了コード変換 |
| 2 | グローバルエラーハンドラ | メイン | 実行時例外のログ出力 |
| 3 | データベース接続管理ハンドラ（初期処理用） | メイン | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ（初期処理用） | メイン | トランザクション管理 |
| 5 | リクエストディスパッチハンドラ | メイン | アクションクラスの決定 |
| 6 | マルチスレッド実行制御ハンドラ | メイン | 並列処理制御 |
| 7 | データベース接続管理ハンドラ（業務処理用） | サブ | DB接続の取得・解放 |
| 8 | トランザクションループ制御ハンドラ | サブ | ループとコミット間隔の制御 |
| 9 | データリードハンドラ | サブ | 1件ずつレコードを読み込む |

---

### アクションクラスの実装

`BatchAction` を継承し、`handle` メソッドに集計と書き込み処理を実装します。`createReader` メソッドで `DatabaseRecordReader` を返します。

```java
public class AggregationBatchAction extends BatchAction<InputEntity> {

    @Override
    public Result handle(InputEntity inputData, ExecutionContext ctx) {
        // 集計処理（入力レコードをもとに集計結果を計算）
        ResultEntity result = aggregate(inputData);
        // 結果テーブルへの書き込み
        UniversalDao.insert(result);
        return new Result.Success();
    }

    @Override
    public DataReader<InputEntity> createReader(ExecutionContext ctx) {
        // DatabaseRecordReader はコンポーネント定義で SQLを設定して使用
        return new DatabaseRecordReader();
    }
}
```

---

### 起動方法

バッチはコマンドラインから起動し、`-requestPath` でアクションクラスとリクエストIDを指定します。

```bash
mvn exec:java -Dexec.mainClass=nablarch.fw.launcher.Main \
    -Dexec.args="'-requestPath' 'com.example.AggregationBatchAction/AGGR0001' \
                 '-diConfig' 'classpath:aggregation-batch.xml' \
                 '-userId' 'batch'"
```

---

**注意点**

- **大量データの読み込み**: `handle` 内でさらに大量データをSELECTする場合は `UniversalDao.defer()` を使った遅延ロードを活用してください。ただし、遅延ロード中にトランザクション制御を行うとカーソルがクローズされる場合があるため注意が必要です。
  ```java
  try (DeferredEntityList<InputData> list
          = (DeferredEntityList<InputData>) UniversalDao.defer()
                                              .findAllBySqlFile(InputData.class, "FIND_ALL")) {
      for (InputData data : list) { /* 処理 */ }
  }
  ```
- **集計処理の設計**: 1レコードに対して集計・更新の処理が完結するよう設計するとトランザクション管理がシンプルになります。SQLの GROUP BY を活用してDB側で集計することも検討してください。
- **コミット間隔**: トランザクションループ制御ハンドラの `commitInterval` を適切に設定することで、処理件数に応じたコミットが行われます。

参照: nablarch-batch-architecture.json:s3, nablarch-batch-architecture.json:s5, nablarch-batch-architecture.json:s7, nablarch-batch-architecture.json:s8, nablarch-batch-feature-details.json:s4, nablarch-batch-getting-started-nablarch-batch.json:s3, nablarch-patterns-Nablarchバッチ処理パターン.json:s1, nablarch-patterns-Nablarchバッチ処理パターン.json:s2, nablarch-patterns-Nablarchバッチ処理パターン.json:s4, libraries-universal-dao.json:s6, libraries-universal-dao.json:s9, libraries-universal-dao.json:s14
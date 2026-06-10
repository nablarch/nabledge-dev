**結論**: DB to DBパターンの**都度起動バッチ**として実装する。`DatabaseRecordReader`でSELECT結果を1件ずつ読み込み、`BatchAction`の`handle`メソッドで集計・別テーブルへの書き込みを行うのが基本構成。

---

**根拠**:

### 処理パターンの選択

「DBから読んで別テーブルに書く」は **DB to DB パターン**に該当する。

> 入力はSELECT文の結果セットの各レコードになります。1レコード分のデータを受け取って、DBを更新します。1レコードの処理中に行われる更新は全て同一トランザクション下で実行されるため、障害発生時でも不整合が発生しません。

「定期処理」には**都度起動バッチ**（日次・月次などでプロセスをその都度起動する）を使用する。

---

### ハンドラキューの構成

都度起動バッチ（DB接続有り）の最小ハンドラ構成を基本にする：

| No. | ハンドラ | スレッド |
|---|---|---|
| 1 | ステータスコード→プロセス終了コード変換ハンドラ | メイン |
| 2 | グローバルエラーハンドラ | メイン |
| 3 | データベース接続管理ハンドラ（初期処理用） | メイン |
| 4 | トランザクション制御ハンドラ（初期処理用） | メイン |
| 5 | リクエストディスパッチハンドラ | メイン |
| 6 | マルチスレッド実行制御ハンドラ | メイン |
| 7 | データベース接続管理ハンドラ（業務処理用） | サブ |
| 8 | **トランザクションループ制御ハンドラ** | サブ |
| 9 | データリードハンドラ | サブ |

コミット間隔はトランザクションループ制御ハンドラの `commitInterval` プロパティで指定する：

```xml
<component class="nablarch.fw.handler.LoopHandler">
  <!-- コミット間隔に1000を指定 -->
  <property name="commitInterval" value="1000" />
</component>
```

---

### データリーダ

DBからデータを読み込むには標準提供の **`DatabaseRecordReader`** を使用する。

---

### アクションクラスの実装

**`BatchAction`** を継承し、`handle` メソッドに集計・書き込みロジックを実装する。`createReader` メソッドで `DatabaseRecordReader` のインスタンスを返す。

```java
public class AggregationBatchAction extends BatchAction<SomeEntity> {

    @Override
    public Result handle(SomeEntity inputData, ExecutionContext ctx) {
        // inputData が1件分のレコード
        // 集計してResultテーブルに書き込む
        ResultEntity result = aggregate(inputData);
        UniversalDao.insert(result);
        return new Result.Success();
    }

    @Override
    public DataReader<SomeEntity> createReader(ExecutionContext ctx) {
        return new DatabaseRecordReader(); // SQLで読み込む設定を行う
    }
}
```

---

### 任意のSQLで集計入力を読む場合

集計用のSQLが複雑な場合は `UniversalDao.findAllBySqlFile` でSQLファイルを使う方法もある：

```java
UniversalDao.findAllBySqlFile(SomeEntity.class, "AGGREGATION_QUERY");
```

大量データを扱う場合は**遅延ロード**で全件メモリ展開を避ける：

```java
try (DeferredEntityList<SomeEntity> rows
        = (DeferredEntityList<SomeEntity>) UniversalDao.defer()
                                            .findAllBySqlFile(SomeEntity.class, "AGGREGATION_QUERY")) {
    for (SomeEntity row : rows) {
        // 集計処理
    }
}
```

> **注意**: 使用するRDBMSによっては、カーソルオープン中にトランザクション制御が行われるとカーソルがクローズされる場合があるため、遅延ロードと途中コミットの組み合わせには注意すること。

---

**注意点**:
- 集計処理が重い場合は `commitInterval` を適切に設定してスループットを調整する
- 処理の再実行（リラン）を考慮し、書き込み先テーブルのクリア・冪等性を設計段階で検討すること

参照: nablarch-patterns-Nablarchバッチ処理パターン.json:s2, nablarch-patterns-Nablarchバッチ処理パターン.json:s4, nablarch-batch-architecture.json:s3, nablarch-batch-architecture.json:s5, nablarch-batch-architecture.json:s7, nablarch-batch-architecture.json:s8, libraries-universal-dao.json:s7, libraries-universal-dao.json:s9, handlers-loop-handler.json:s5

---
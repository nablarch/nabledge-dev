**結論**: DBからデータを読み込んで集計し別テーブルに書き込む定期処理は、Nablarchバッチの**都度起動バッチ（DB to DBパターン）**として実装します。`BatchAction`を継承したアクションクラスと`DatabaseRecordReader`を使ったデータリーダを組み合わせ、`handle`メソッド内でSELECT結果1件ずつを処理して`UniversalDao.insert`で書き込みます。

---

**根拠**:

**1. アーキテクチャ構成**

Nablarchバッチは「都度起動バッチ」と「常駐バッチ」の2種類があります。日次・月次などの定期処理には**都度起動バッチ**を使います。

入出力パターンとしては**DB to DB**がまさに今回のケースで、「入力はSELECT文の結果セットの各レコード、1レコード分のデータを受け取ってDBを更新する」形式です。1レコードの処理中に行われる更新は全て同一トランザクション下で実行されるため、障害発生時でも不整合が発生しません。

**2. 最小ハンドラ構成（DB接続あり）**

コンポーネント定義XMLには以下のハンドラをキューに設定します:

| No | ハンドラ | 役割 |
|---|---|---|
| 1 | StatusCodeConvertHandler | 終了コード変換 |
| 2 | GlobalErrorHandler | 例外ログ |
| 3 | DbConnectionManagementHandler（初期処理用） | DB接続確立 |
| 4 | TransactionManagementHandler（初期処理用） | 初期化トランザクション |
| 5 | RequestPathJavaPackageMapping | アクション特定 |
| 6 | MultiThreadExecutionHandler | サブスレッド制御 |
| 7 | DbConnectionManagementHandler（業務処理用） | 業務DB接続 |
| 8 | LoopHandler（トランザクションループ制御） | コミット間隔制御 |
| 9 | DataReadHandler | レコード1件読み込み |

**3. アクションクラスとデータリーダの実装**

```java
public class AggregationBatchAction extends BatchAction<AggregationForm> {

    @Override
    public Result handle(AggregationForm inputData, ExecutionContext ctx) {
        // 集計ロジック（inputDataは1レコード分）
        AggregationResult result = aggregate(inputData);
        // 結果を別テーブルに書き込む
        UniversalDao.insert(result);
        return new Result.Success();
    }

    @Override
    public DataReader<AggregationForm> createReader(ExecutionContext ctx) {
        return new DatabaseRecordReader(); // または独自のDataReader実装
    }
}
```

**4. 大量データ処理時は遅延ロードを使用する**

バッチで大量データを処理する場合、`UniversalDao.defer()`を使って遅延ロードします。これにより検索結果全件をメモリに展開せずに処理できます:

```java
try (DeferredEntityList<SourceEntity> records
        = (DeferredEntityList<SourceEntity>) UniversalDao.defer()
                .findAllBySqlFile(SourceEntity.class, "FIND_TARGET")) {
    for (SourceEntity record : records) {
        // 処理
    }
}
```

**5. コミット間隔の設定**

`LoopHandler`の`commitInterval`プロパティでコミット間隔を調整できます（スループット向上）:

```xml
<component class="nablarch.fw.handler.LoopHandler">
  <property name="commitInterval" value="1000" />
</component>
```

**注意点**:
- **N+1問題を避ける**: `handle`メソッド内で再度SELECTを発行するN+1問題が起きやすい。集計に必要なデータは`createReader`のSQL（JOIN等）で一度に取得する設計にすること
- **自前ループは禁止**: `handle`メソッド内で`SqlResultSet`を取得してforループを回すと、フレームワークのコミット制御が効かずトランザクションログが逼迫する。必ずフレームワークのループ（DataReader → handle）を使うこと
- 集計SQLのような複雑なSELECTはSQLファイルで管理し、`UniversalDao.findAllBySqlFile`で呼び出す

参照: nablarch-patterns-Nablarchバッチ処理パターン.json:s1, s2, s4, nablarch-batch-architecture.json:s3, s5, s7, s8, nablarch-batch-getting-started-nablarch-batch.json:s3, nablarch-patterns-Nablarchアンチパターン.json:s4, s9, s11, libraries-universal-dao.json:s9, handlers-loop-handler.json:s5

---
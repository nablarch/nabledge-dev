**結論**: 定期バッチは**都度起動バッチ**として実装します。`DatabaseRecordReader` でDBからデータを1件ずつ読み込み、`BatchAction` の `handle` メソッドで集計処理と `UniversalDao.insert` による別テーブルへの書き込みを行います。

**根拠**:

**1. 処理パターンの選択**

都度起動バッチは「日次や月次など、定期的にバッチ処理を実行するような場合に使用」するパターンです。今回の要件は「定期処理」なのでこれが適合します。

DB to DBパターンの特徴:
- 入力は SELECT 文の結果セットの各レコード
- 1レコード分のデータを受け取って DB を更新する
- 1レコードの処理中に行われる更新は全て同一トランザクション下で実行されるため、障害発生時でも不整合が発生しない

**2. ハンドラ構成（DB接続あり）**

都度起動バッチでDB接続ありの最小ハンドラ構成は以下の通りです（コンポーネント定義ファイルに設定）:

| No. | ハンドラ | 役割 |
|-----|---------|------|
| 1 | ステータスコード→プロセス終了コード変換ハンドラ | 終了コード変換 |
| 2 | グローバルエラーハンドラ | 例外ログ出力 |
| 3 | データベース接続管理ハンドラ（初期処理/終了処理用） | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ（初期処理/終了処理用） | 初期処理のトランザクション制御 |
| 5 | リクエストディスパッチハンドラ | アクションクラスを特定 |
| 6 | マルチスレッド実行制御ハンドラ | サブスレッド作成 |
| 7 | データベース接続管理ハンドラ（業務処理用） | 業務用DB接続 |
| 8 | **トランザクションループ制御ハンドラ** | コミット間隔ごとにコミット・ループ継続 |
| 9 | データリードハンドラ | データリーダから1件取得 |

コミット間隔は `commitInterval` プロパティで設定します:

```xml
<component class="nablarch.fw.handler.LoopHandler">
  <!-- コミット間隔に1000を指定 -->
  <property name="commitInterval" value="1000" />
</component>
```

**3. アクションクラスの実装**

`BatchAction` を継承して業務アクションクラスを作成します。

```java
public class AggregationBatchAction extends BatchAction<AggregationForm> {

    @Override
    public Result handle(AggregationForm inputData, ExecutionContext ctx) {
        // 集計結果エンティティを作成して別テーブルに書き込む
        AggregationResult result = BeanUtil.createAndCopy(AggregationResult.class, inputData);
        UniversalDao.insert(result);

        return new Result.Success();
    }

    @Override
    public DataReader<AggregationForm> createReader(ExecutionContext ctx) {
        // DatabaseRecordReader を返す（集計SQLは reader の SQL ファイルに定義）
        return new DatabaseRecordReader();
    }
}
```

処理の流れ:
1. `createReader` でデータリーダのインスタンスを返す。`DatabaseRecordReader` が DB からデータを1件ずつ取得する
2. `handle` メソッドでデータリーダから渡された1件分のデータに対する業務ロジックを実装する
3. `UniversalDao.insert` を使用して集計結果エンティティを別テーブルに登録する

**4. 集計SQLはcreateReaderのSQL（JOIN）で取得**

集計に必要なデータはすべて `createReader` のSQLファイルに JOIN で記述し、`handle` 内で追加 SELECT を発行しないようにします（N+1問題の回避）:

```sql
-- OK例: createReader の SQL（JOINで1回で取得）
SELECT
  売上.売上ID,
  売上.売上日,
  売上明細.売上明細ID,
  売上明細.金額
FROM 売上
INNER JOIN 売上明細 ON 売上.売上ID = 売上明細.売上ID
WHERE 売上.売上日 = ?
```

`handle` 内で入力データを元に再度 SELECT を発行すると、処理対象件数が N 件の場合に N+1 回の SQL が発行され、深刻な性能劣化を引き起こします。

**5. 大量データの場合は遅延ロード**

大量データを扱う場合は `UniversalDao.defer()` を使用してメモリ不足を防ぎます:

```java
try (DeferredEntityList<AggregationForm> records
        = (DeferredEntityList<AggregationForm>) UniversalDao.defer()
                .findAllBySqlFile(AggregationForm.class, "FIND_TARGET_DATA")) {
    for (AggregationForm record : records) {
        // recordを使った処理
    }
}
```

遅延ロードは内部でサーバサイドカーソルを使用しているため、`DeferredEntityList#close` を必ず呼び出す必要があります（try-with-resources を使用）。

**注意点**:

- **N+1問題**: 集計に必要なデータはすべて `createReader` の SQL ファイルに JOIN で記述する。`handle` 内で追加の SELECT を発行しない
- **遅延ロード時のトランザクション**: `UniversalDao.defer()` 使用時、カーソルオープン中にトランザクション制御が行われるとカーソルがクローズされる可能性がある。DBベンダのマニュアルに従い挙動を確認する
- **commitInterval の調整**: スループット向上のため、適切なコミット間隔を設定する

参照: nablarch-batch-architecture.json:s3, nablarch-batch-architecture.json:s5, nablarch-batch-architecture.json:s7, nablarch-batch-architecture.json:s8, nablarch-batch-getting-started-nablarch-batch.json:s3, nablarch-patterns-Nablarchバッチ処理パターン.json:s1, nablarch-patterns-Nablarchバッチ処理パターン.json:s4, nablarch-patterns-Nablarchアンチパターン.json:s4, libraries-universal-dao.json:s9, handlers-loop-handler.json:s5
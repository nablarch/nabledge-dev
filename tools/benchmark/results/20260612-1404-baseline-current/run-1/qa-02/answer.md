**結論**: DB to DBパターンのNablarchバッチは `BatchAction` を継承したアクションクラスで実装する。`createReader()` で `DatabaseRecordReader` を生成・返却し、`handle()` で1レコードごとに集計ロジックを実行して書き込み先テーブルに登録する。

**根拠**:

**1. DB to DB パターンの特性**

Nablarchバッチには「入出力による分類」があり、今回のケースは **DB to DB** パターンに該当する。

- 入力はSELECT文の結果セットの各レコード
- 1レコード分のデータを受け取ってDBを更新する
- 1レコードの処理中に行われる更新は全て同一トランザクション下で実行されるため、障害発生時でも不整合が発生しない

**2. アクションクラスの実装**

`BatchAction` を継承し、以下2つのメソッドを実装する。

```java
public class AggregationBatchAction extends BatchAction<SalesData> {

    // 読み込み元テーブルのSELECTを設定したDataReaderを返す
    @Override
    public DataReader<SalesData> createReader(ExecutionContext ctx) {
        DatabaseRecordReader reader = new DatabaseRecordReader();
        // ... SQLPStatementをセット
        return reader;
    }

    // 1レコードごとに呼ばれる業務処理（集計・書き込み）
    @Override
    public Result handle(SalesData inputData, ExecutionContext ctx) {
        // 集計ロジックを実行し、結果テーブルにinsert/update
        AggregationResult result = // ... 集計処理
        UniversalDao.insert(result);
        return new Result.Success();
    }
}
```

`handle()` メソッドは「ここで実行される業務処理は原子性を保証される」。

**3. ハンドラキュー構成（DB接続有り）**

DB接続有りの最小ハンドラ構成には以下が必要（主要なもの）：

| No. | ハンドラ | 役割 |
|-----|----------|------|
| 3 | データベース接続管理ハンドラ（初期処理/終了処理用） | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ（初期処理/終了処理用） | 初期/終了処理のトランザクション管理 |
| 7 | データベース接続管理ハンドラ（業務処理用） | サブスレッドでのDB接続管理 |
| 8 | トランザクションループ制御ハンドラ | コミット間隔ごとに業務トランザクションをコミット、ループ継続制御 |
| 9 | データリードハンドラ | `DatabaseRecordReader` でレコードを1件読み込み後続ハンドラへ渡す |

**4. データリーダの選択**

Nablarchが標準提供するデータリーダのうち、DBから読み込む場合は `DatabaseRecordReader` を使用する。

**注意点**:

- DBからの入力データは「安全な入力」として扱えるため、フォームクラスは省略してデータレコードから直接エンティティクラスを作成して業務ロジックを実行してよい
- プロジェクト要件に応じて、最小ハンドラ構成にNablarch標準ハンドラやカスタムハンドラを追加する

参照: nablarch-patterns-Nablarchバッチ処理パターン.json:s2, nablarch-patterns-Nablarchバッチ処理パターン.json:s4, nablarch-batch-architecture.json:s5, nablarch-batch-architecture.json:s7, javadoc-nablarch-fw-action-BatchAction.json:s4, javadoc-nablarch-fw-action-BatchAction.json:s5, nablarch-batch-application-design.json:s1, nablarch-batch-getting-started-nablarch-batch.json:s3
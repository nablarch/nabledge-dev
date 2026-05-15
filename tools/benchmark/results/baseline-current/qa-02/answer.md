**結論**: DB to DBパターンの都度起動バッチとして実装する。`DatabaseRecordReader`で入力テーブルをSELECT読み込みし、`BatchAction`のhandleメソッド内で集計ロジックを実装して結果テーブルにUniversalDaoで書き込む。

**根拠**:

**1. 処理パターンの選択**

この処理は「DB to DB」パターン × 「都度起動バッチ」の組み合わせとなる（日次・月次など定期実行 → 都度起動、入力テーブルから出力テーブルへ → DB to DB）。

- 入力: SELECT文の結果セットの各レコード
- 出力: 1レコード分のデータを受け取ってDBを更新
- トランザクション: 1レコードの処理中に行われる更新は全て同一トランザクション下で実行されるため、障害発生時でも不整合が発生しない

**2. ハンドラ構成（DB接続あり最小構成）**

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | ステータスコード→プロセス終了コード変換ハンドラ | 終了コード変換 |
| 2 | グローバルエラーハンドラ | 例外ログ出力 |
| 3 | データベース接続管理ハンドラ（初期処理用） | DB接続取得・解放 |
| 4 | トランザクション制御ハンドラ（初期処理用） | 初期化トランザクション制御 |
| 5 | リクエストディスパッチハンドラ | アクションクラス特定 |
| 6 | マルチスレッド実行制御ハンドラ | サブスレッド管理 |
| 7 | データベース接続管理ハンドラ（業務処理用） | 業務DB接続取得・解放 |
| 8 | トランザクションループ制御ハンドラ | ループ・コミット間隔制御 |
| 9 | データリードハンドラ | 1レコード読み込み→handleへ渡す |

**3. データリーダ**

DBから読み込む場合は `DatabaseRecordReader` を使用する。

**4. アクションクラス実装例**

```java
public class AggregateAction extends BatchAction<InputEntity> {

    @Override
    public Result handle(InputEntity inputData, ExecutionContext ctx) {
        // 集計ロジックをここに実装
        ResultEntity result = aggregate(inputData);
        // 結果テーブルへ書き込み（insert または update）
        UniversalDao.insert(result);
        return new Result.Success();
    }

    @Override
    public DataReader<InputEntity> createReader(ExecutionContext ctx) {
        // DatabaseRecordReader で入力テーブルをSELECT
        return new DatabaseRecordReader();
    }
}
```

**5. 大量データの場合（任意）**

入力データが大量の場合は `UniversalDao.defer()` による遅延ロードを検討する。ただし、遅延ロード中にトランザクション制御を行うとカーソルがクローズされる場合があるため、DBベンダーのマニュアルを確認すること。

```java
try (DeferredEntityList<InputEntity> records
        = (DeferredEntityList<InputEntity>) UniversalDao.defer()
                                            .findAllBySqlFile(InputEntity.class, "SELECT_INPUT")) {
    for (InputEntity record : records) {
        // 処理
    }
}
```

**6. コミット間隔の調整（任意）**

トランザクションループ制御ハンドラ（LoopHandler）の `commitInterval` プロパティでコミット間隔を調整できる。

```xml
<component class="nablarch.fw.handler.LoopHandler">
  <property name="commitInterval" value="1000" />
</component>
```

**注意点**:
- `BatchAction` の `handle` メソッドは1レコードずつ呼ばれる。集計結果を複数レコード分まとめてから書き込みたい場合は、アクション内で状態を保持する設計が必要（ただしメモリ管理・障害時の整合性に注意）
- 遅延ロード（`UniversalDao.defer()`）使用中にコミット間隔によるトランザクション制御が走ると、DBMSによってはカーソルがクローズされてエラーになる場合がある
- 都度起動バッチのスケジューリング自体（cronなど）はNablarch外の仕組みで行う

参照: `guide/nablarch-patterns/nablarch-patterns-Nablarchバッチ処理パターン.json#s1`, `guide/nablarch-patterns/nablarch-patterns-Nablarchバッチ処理パターン.json#s2`, `guide/nablarch-patterns/nablarch-patterns-Nablarchバッチ処理パターン.json#s4`, `processing-pattern/nablarch-batch/nablarch-batch-architecture.json#s5`, `processing-pattern/nablarch-batch/nablarch-batch-architecture.json#s7`, `processing-pattern/nablarch-batch/nablarch-batch-architecture.json#s8`, `component/libraries/libraries-universal-dao.json#s9`, `component/handlers/handlers-loop-handler.json#s5`
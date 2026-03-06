**結論**: バッチアクションは `BatchAction<T>` を継承したクラスを作成し、`handle` メソッドと `createReader` メソッドを実装することで実現します。入力データの種類によって使用するアクションクラスを選択します。

**根拠**:

### 1. 標準アクションクラスの選択

Nablarchバッチでは以下の標準アクションクラスが提供されています:

| クラス | 用途 |
|---|---|
| `BatchAction<T>` | 汎用バッチアクションテンプレート |
| `FileBatchAction<T>` | ファイル入力バッチ（`data_format` を使用） |
| `NoInputDataBatchAction` | 入力データ不要のバッチ |
| `AsyncMessageSendAction` | 応答不要メッセージ送信 |

> **注意**: `FileBatchAction` は `data_format` を使用する。`data_bind` を使用する場合は他のアクションクラスを使用すること。

### 2. アクションクラスの責務

アクションクラスは以下の処理を担います:
- `DataReader<T>` を生成（`createReader` メソッド）
- 読み込んだデータレコードを元に業務ロジックを実行
- `Result`（通常は `Result.Success`）を返却

### 3. 実装例（悲観的ロックを使用した例）

```java
public class SampleAction extends BatchAction<SqlRow> {

    @Override
    public DataReader<SqlRow> createReader(final ExecutionContext ctx) {
        final DatabaseRecordReader reader = new DatabaseRecordReader();
        final SqlPStatement statement = DbConnectionContext.getConnection()
                .prepareParameterizedSqlStatementBySqlId(
                        Project.class.getName() + "#GET_ID");
        // 検索条件の取得処理は省略
        reader.setStatement(statement, condition);
        return reader;
    }

    @Override
    public Result handle(final SqlRow inputData, final ExecutionContext ctx) {
        final Project project =
                UniversalDao.findBySqlFile(Project.class, "FIND_BY_ID_WITH_LOCK", inputData);
        // 業務処理のため省略
        UniversalDao.update(project);
        return new Success();
    }
}
```

### 4. アクション内での状態保持

マルチスレッドバッチでアクション内に状態を保持する場合は、スレッドセーフなクラスを使用します:

```java
public class BatchActionSample extends BatchAction<Object> {
    /** 登録件数 */
    private AtomicInteger insertedCount = new AtomicInteger(0);

    @Override
    public Result handle(final Object inputData, final ExecutionContext ctx) {
        // 業務処理
        insertedCount.incrementAndGet();
        return new Result.Success();
    }
}
```

> **重要**: マルチスレッドバッチでは、アプリケーション側でスレッドセーフを保証すること。

### 5. アクションの起動方法

コマンドライン引数 `-requestPath` でアクションを指定します:

```properties
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

書式: `-requestPath=アクションのクラス名/リクエストID`

### 6. アクションクラスの設計指針

- **バリデーション**: データが安全でない場合（外部ファイル等）はフォームクラスでバリデーションを実施
- **エンティティクラス**: テーブルと1対1対応。`DataReader` が読み込んだデータレコードをマッピングして使用
- **フォームクラスのプロパティ**: 全て `String` で定義（バイナリ項目はバイト配列）

**注意点**:
- マルチスレッドバッチではスレッドセーフを自前で保証する必要がある（`AtomicInteger` 等を使用）
- `FileBatchAction` を使用する場合は `data_format` の設定が必要。`data_bind` を使用する場合は他のアクションクラスを選ぶこと
- 都度起動バッチと常駐バッチで実装方法は同一。差異はハンドラキュー構成のみ
- 状態保持に `ExecutionContext` のスコープを使用することも可能だが、保持値が分かりづらいため非推奨。アクション側フィールドでの状態保持を推奨

参照: `nablarch-batch-architecture.json#actions`, `nablarch-batch-application_design.json#overview`, `nablarch-batch-nablarch_batch_pessimistic_lock.json#implementation-example`, `nablarch-batch-nablarch_batch_retention_state.json#overview`, `nablarch-batch-architecture.json#request-path-action-request-id`

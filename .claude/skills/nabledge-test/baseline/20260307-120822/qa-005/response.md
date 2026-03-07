**結論**: バッチアクションは `BatchAction` クラス（またはその派生クラス）を継承し、`createReader` メソッドと `handle` メソッドを実装することで実現します。

---

**根拠**:

## 標準アクションクラスの種類

Nablarchバッチアプリケーションでは、以下の標準アクションクラスが提供されています。

| クラス | 用途 |
|---|---|
| `BatchAction` | 汎用バッチアクションテンプレート |
| `FileBatchAction` | ファイル入力バッチアクションテンプレート（`data_format` 使用時） |
| `NoInputDataBatchAction` | 入力データ不要なバッチアクションテンプレート |
| `AsyncMessageSendAction` | 応答不要メッセージ送信 |

> **重要**: `FileBatchAction` は `:ref:data_format` を使用します。`:ref:data_bind` を使用する場合は他のアクションクラスを使用してください。

---

## 基本的な実装方法（BatchActionの場合）

`BatchAction<T>` を継承し、以下の2つのメソッドを実装します。

```java
public class SampleAction extends BatchAction<SqlRow> {

    /**
     * データリーダを生成するメソッド
     * （DataReadHandlerから呼び出される）
     */
    @Override
    public DataReader<SqlRow> createReader(final ExecutionContext ctx) {
        final DatabaseRecordReader reader = new DatabaseRecordReader();
        final SqlPStatement statement = DbConnectionContext.getConnection()
                .prepareParameterizedSqlStatementBySqlId(
                        Project.class.getName() + "#GET_ID");
        // 検索条件の設定
        reader.setStatement(statement, condition);
        return reader;
    }

    /**
     * 1レコードごとの業務処理
     */
    @Override
    public Result handle(final SqlRow inputData, final ExecutionContext ctx) {
        final Project project =
                UniversalDao.findBySqlFile(Project.class, "FIND_BY_ID_WITH_LOCK", inputData);

        // 業務処理
        UniversalDao.update(project);
        return new Result.Success();
    }
}
```

**標準データリーダ**:
- `FileDataReader` : ファイル読み込み
- `DatabaseRecordReader` : DB読み込み
- `ValidatableFileDataReader` : バリデーション付きファイル読み込み

---

## アクションの起動方法

コマンドライン引数 `-requestPath` でアクションクラスとリクエストIDを指定します。

**書式**:
```
-requestPath=アクションのクラス名/リクエストID
```

**例**:
```
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

リクエストIDは各バッチプロセスの識別子です。同一の業務アクションクラスを実行するプロセスを複数起動する場合、このリクエストIDで識別します。

---

## 状態保持が必要な場合

バッチアクション内でフィールドとして状態を保持できます。マルチスレッドバッチでは `AtomicInteger` 等のスレッドセーフなクラスを使用してください。

```java
public class BatchActionSample extends BatchAction<Object> {
    /** 登録件数（スレッドセーフ） */
    private AtomicInteger insertedCount = new AtomicInteger(0);

    @Override
    public Result handle(final Object inputData, final ExecutionContext ctx) {
        // 業務処理
        insertedCount.incrementAndGet();
        return new Result.Success();
    }
}
```

> **重要**: マルチスレッドバッチでは、アプリケーション側でスレッドセーフを保証すること。`ExecutionContext` のスコープでも同等実装は可能ですが、保持値が分かりづらいためバッチアクション側での状態保持を推奨します。

---

**注意点**:
- `FileBatchAction` は `data_format` 専用。`data_bind` 使用時は `BatchAction` など他クラスを使用すること
- マルチスレッドバッチでのフィールド変数はスレッドセーフを保証すること（`AtomicInteger` 等を使用）
- 常駐バッチは新規開発では非推奨。`db_messaging` を推奨

参照: `nablarch-batch-architecture.json#actions`, `nablarch-batch-architecture.json#request-path-action-request-id`, `nablarch-batch-nablarch_batch_pessimistic_lock.json#implementation-example`, `nablarch-batch-nablarch_batch_retention_state.json#overview`, `handlers-data_read_handler.json#overview`

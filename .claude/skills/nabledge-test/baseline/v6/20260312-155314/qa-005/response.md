**結論**: バッチアクションを実装するには、目的に応じたテンプレートクラス（`BatchAction`、`FileBatchAction`、`NoInputDataBatchAction` など）を継承し、`createReader` メソッドと `handle` メソッドを実装します。

**根拠**:

### 利用可能なバッチアクションのテンプレートクラス

| クラス | 用途 |
|---|---|
| `BatchAction` | 汎用的なバッチアクション |
| `FileBatchAction` | ファイル入力のバッチアクション（`data_format` 使用）※`data_bind` を使う場合は他クラスを選ぶこと |
| `NoInputDataBatchAction` | 入力データを使用しないバッチアクション |
| `AsyncMessageSendAction` | 応答不要メッセージ送信用 |

### 基本的な実装パターン

`BatchAction<T>` を継承し、以下の2つのメソッドを実装します。

```java
public class ImportZipCodeFileAction extends BatchAction<ZipCodeFileReader> {

    /** データリーダのインスタンスを返す */
    @Override
    public DataReader<ZipCodeFileReader> createReader(ExecutionContext ctx) {
        return new ZipCodeFileReader();
    }

    /** データリーダから渡された1件分のデータを処理する */
    @Override
    public Result handle(ZipCodeFileReader inputData, ExecutionContext ctx) {
        ZipCodeData entity = BeanUtil.createAndCopy(ZipCodeData.class, inputData);
        UniversalDao.insert(entity);
        return new Result.Success();
    }
}
```

- `createReader`: 使用するデータリーダクラスのインスタンスを返す
- `handle`: データリーダから渡された1件分のデータに対する処理を実装する。正常終了時は `return new Result.Success();` を返す
- `@ValidateData` インターセプタを使うと、`handle` にはバリデーション済みデータが渡される

### マルチスレッド時の状態保持

マルチスレッド実行時はスレッドセーフを保証する必要があります。状態を保持する場合は `AtomicInteger` を使用します。

```java
public class BatchActionSample extends BatchAction<Object> {

    private AtomicInteger insertedCount = new AtomicInteger(0);

    @Override
    public Result handle(Object inputData, ExecutionContext ctx) {
        insertedCount.incrementAndGet();
        return new Result.Success();
    }
}
```

> `ExecutionContext` のスコープ（リクエストスコープ: スレッドごと、セッションスコープ: バッチ全体）でも状態保持できますが、バッチアクション側で保持することを推奨。

### アクションクラスの起動方法

コマンドライン引数 `-requestPath` でアクションクラスとリクエストIDを指定します。

```properties
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

**注意点**:

- `FileBatchAction` は `data_format` を使用する。`data_bind` を使う場合は `BatchAction` など他のクラスを使用すること
- `handle` メソッド内でループ処理（`for` 文など）は行わないこと。フレームワークによる一定間隔のコミットが行われず、トランザクションログを逼迫する（`NoInputDataBatchAction` での `handle` 内ループは典型的な誤り）
- `handle` 内で再度 SELECT を発行すると N+1 問題が発生する。必要なデータは `createReader` の SQL に JOIN を使って一度に取得すること
- 悲観的ロックが必要な場合は、`createReader` で主キーのみ取得し、`handle` 内でロックを行う

参照: `nablarch-batch-architecture.json#action-list`, `nablarch-batch-getting-started-nablarch-batch.json#execute-business-logic`, `nablarch-batch-nablarch_batch_retention_state.json#retention-state`, `nablarch-batch-architecture.json#resolve-action`, `nablarch-patterns-Nablarchアンチパターン.json#nablarch-batch`

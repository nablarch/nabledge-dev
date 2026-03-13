**結論**: `BatchAction` を継承したクラスを作成し、`handle()` メソッドと `createReader()` メソッドを実装することでバッチアクションを実装します。

---

**根拠**:

#### バッチアクションの基本実装

`BatchAction<T>` を継承し、以下の2メソッドを実装します。

- `handle(T inputData, ExecutionContext ctx)`: データリーダから渡された1件分のデータを処理する
- `createReader(ExecutionContext ctx)`: 使用するデータリーダのインスタンスを返す

```java
public class ImportZipCodeFileAction extends BatchAction<ZipCodeForm> {

    @Override
    @ValidateData
    public Result handle(ZipCodeForm inputData, ExecutionContext ctx) {
        ZipCodeData data = BeanUtil.createAndCopy(ZipCodeData.class, inputData);
        UniversalDao.insert(data);
        return new Result.Success();
    }

    @Override
    public DataReader<ZipCodeForm> createReader(ExecutionContext ctx) {
        return new ZipCodeFileReader();
    }
}
```

#### 標準提供のアクションクラス

用途に応じて以下のテンプレートクラスを使い分けます。

| クラス | 用途 |
|---|---|
| `BatchAction` | 汎用的なバッチアクション |
| `FileBatchAction` | ファイル入力のバッチアクション（data_format使用） |
| `NoInputDataBatchAction` | 入力データを使用しないバッチアクション |
| `AsyncMessageSendAction` | 応答不要メッセージ送信用 |

> **重要**: `FileBatchAction` はデータアクセスに `data_format` を使用します。`data_bind` を使用する場合は `BatchAction` など他のクラスを選択してください。

#### 処理フロー

1. 共通起動ランチャ（Main）がハンドラキューを実行する
2. `DataReader` が入力データを1件ずつ提供する
3. `DispatchHandler` がコマンドライン引数 `-requestPath` に基づきアクションクラスを特定する
4. アクションクラスが1件ごとの業務ロジックを実行し、`Result` を返す
5. 処理対象データがなくなるまで繰り返す

#### バッチアクション内での状態保持

バッチアクション内でフィールドとして状態（登録件数など）を保持できます。マルチスレッドで実行する場合は `AtomicInteger` などスレッドセーフな実装が必要です。

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

---

**注意点**:
- `data_bind` を使用する場合、`FileBatchAction` および `ValidatableFileDataReader` / `FileDataReader` は使用しないこと
- マルチスレッドバッチではバッチアクションのフィールドのスレッドセーフを保証すること（`AtomicInteger` 等を使用）
- `ExecutionContext` でも状態保持は可能だが、バッチアクションのフィールドで管理する方が可読性が高いため推奨
- 標準データリーダで要件を満たせない場合は `DataReader` インタフェースを実装したカスタムクラスを作成すること

参照:
- `nablarch-batch-getting-started-nablarch-batch.json#s1`
- `nablarch-batch-nablarch_batch_retention_state.json#s1`
- `nablarch-batch-architecture.json#s3`
- `nablarch-batch-architecture.json#s2`

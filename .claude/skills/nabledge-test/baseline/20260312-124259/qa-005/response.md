**結論**: Nablarchバッチのバッチアクションは、用途に応じた4種類のテンプレートクラスを継承して実装します。`handle` メソッドに1件分の業務処理を実装し、`createReader` でデータリーダを返す構成が基本です。

**根拠**:

### バッチアクションの種類

用途に応じて以下のテンプレートクラスを選択します:

| クラス | 用途 |
|---|---|
| `BatchAction` | 汎用的なバッチアクション |
| `FileBatchAction` | ファイル入力バッチ（データフォーマット使用） |
| `NoInputDataBatchAction` | 入力データを使用しないバッチ |
| `AsyncMessageSendAction` | 応答不要メッセージ送信 |

> **注意**: `FileBatchAction` はデータアクセスに `data_format` を使用します。`data_bind` を使う場合は他のクラスを選択してください。

### 基本的な実装方法

`BatchAction` を継承し、`handle` と `createReader` を実装します:

```java
// 例: ZIPコードファイルをDBにインポートするバッチ
public class ImportZipCodeFileAction extends BatchAction<ZipCodeForm> {

    @Override
    @ValidateData  // バリデーション共通化インターセプタ
    public Result handle(ZipCodeForm inputData, ExecutionContext ctx) {
        ZipCodeData zipCode = BeanUtil.createAndCopy(ZipCodeData.class, inputData);
        UniversalDao.insert(zipCode);
        return new Result.Success();
    }

    @Override
    public DataReader<ZipCodeForm> createReader(ExecutionContext ctx) {
        return new ZipCodeFileReader();
    }
}
```

- `handle`: データリーダから渡された1件分のデータを処理する。成功時は `new Result.Success()` を返す
- `createReader`: 使用するデータリーダのインスタンスを返す

### 状態を保持するバッチアクション

マルチスレッド実行時はスレッドセーフを保証する必要があります。`AtomicInteger` などスレッドセーフなクラスを使用してください:

```java
public class BatchActionSample extends BatchAction<Object> {

    /** 登録件数（スレッドセーフ） */
    private AtomicInteger insertedCount = new AtomicInteger(0);

    @Override
    public Result handle(final Object inputData, final ExecutionContext ctx) {
        insertedCount.incrementAndGet();
        return new Result.Success();
    }
}
```

### バッチの起動方法

コマンドライン引数 `-requestPath` でアクションクラスとリクエストIDを指定します:

```properties
# 書式
-requestPath=アクションのクラス名/リクエストID

# 例
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

リクエストIDはバッチプロセスの識別子です。同一アクションクラスを複数プロセスで起動する場合に識別子として機能します。

**注意点**:

### よくある実装ミス（アンチパターン）

1. **N+1問題**: `handle` 内で入力データをもとに再度 `SELECT` を発行しない。必要なデータは `createReader` の SQL に JOIN して1回で取得する
2. **フレームワーク制御外のループ処理**: `handle` 内で自前のループを書かない。特に `NoInputDataBatchAction` で `handle` 内にループを書くのは典型的な誤り。ループ処理は `createReader` + フレームワーク管理のループで実現する

   NG:
   ```java
   public Result handle(ExecutionContext context) {
       SqlResultSet rows = search("SEARCH");
       for (SqlRow row : rows) { // フレームワーク管理外のループ
           // 更新処理
       }
   }
   ```

   OK: `createReader` でデータを渡し、`handle` で1件処理する

参照: `nablarch-batch-architecture.json#action-list`, `nablarch-batch-getting-started-nablarch-batch.json#execute-business-logic`, `nablarch-batch-nablarch_batch_retention_state.json#retention-state`, `nablarch-batch-architecture.json#resolve-action`, `nablarch-patterns-Nablarchアンチパターン.json#nablarch-batch`

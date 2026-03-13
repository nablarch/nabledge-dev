**結論**: データリードハンドラ（`DataReadHandler`）は `DataReader` インタフェースを実装したクラス（データリーダ）と組み合わせて使用します。ファイルを読み込む場合は、標準提供の `FileDataReader` を使用するか、`DataReader` を独自実装します。

**根拠**:

### DataReadHandler の役割

`nablarch.fw.handler.DataReadHandler` はデータリーダを使用して入力データを1件ずつ読み込み、後続ハンドラに処理を委譲するハンドラです。`DataReader` の終端到達時は後続ハンドラを実行せず `NoMoreRecord` を返却します。

### 標準提供のファイル読み込み用データリーダ

Nablarch バッチでは以下のデータリーダが標準提供されています：

| クラス名 | 説明 |
|---|---|
| `FileDataReader` | ファイル読み込み |
| `ValidatableFileDataReader` | バリデーション機能付きファイル読み込み |
| `ResumeDataReader` | レジューム機能付き読み込み |

> **重要**: `FileDataReader` および `ValidatableFileDataReader` はデータアクセスに `data_format` を使用します。`data_bind` を使用する場合はこれらのデータリーダを使用しないでください。

### DataReader を独自実装する方法（data_bind 使用の場合）

`data_bind` を使ってCSVファイルを読み込む場合は、`DataReader<T>` を実装して `read()`・`hasNext()`・`close()` の3メソッドを実装します：

```java
public class ZipCodeFileReader implements DataReader<ZipCodeForm> {
    private static final String FILE_NAME = "importZipCode";
    private ObjectMapperIterator<ZipCodeForm> iterator;

    @Override
    public ZipCodeForm read(ExecutionContext ctx) {
        if (iterator == null) initialize();
        return iterator.next();
    }

    @Override
    public boolean hasNext(ExecutionContext ctx) {
        if (iterator == null) initialize();
        return iterator.hasNext();
    }

    @Override
    public void close(ExecutionContext ctx) { iterator.close(); }

    private void initialize() {
        File zipCodeFile = FilePathSetting.getInstance()
            .getFileWithoutCreate("csv-input", FILE_NAME);
        try {
            iterator = new ObjectMapperIterator<>(
                ObjectMapperFactory.create(ZipCodeForm.class,
                    new FileInputStream(zipCodeFile)));
        } catch (FileNotFoundException e) {
            throw new IllegalStateException(e);
        }
    }
}
```

データリーダはバッチアクションの `createReader()` で返却します：

```java
public class ImportZipCodeFileAction extends BatchAction<ZipCodeForm> {
    @Override
    public DataReader<ZipCodeForm> createReader(ExecutionContext ctx) {
        return new ZipCodeFileReader();
    }

    @Override
    @ValidateData
    public Result handle(ZipCodeForm inputData, ExecutionContext ctx) {
        ZipCodeData data = BeanUtil.createAndCopy(ZipCodeData.class, inputData);
        UniversalDao.insert(data);
        return new Result.Success();
    }
}
```

**注意点**:
- `FileDataReader` / `ValidatableFileDataReader` と `data_bind` は併用不可。`data_bind`（`ObjectMapperIterator` 等）を使う場合は `DataReader` を独自実装すること
- `DataReadHandler` は処理フロー上でデータリーダを呼び出すハンドラであり、ハンドラキューに含める必要がある

参照: `component/handlers/handlers-data_read_handler.json#s1`, `processing-pattern/nablarch-batch/nablarch-batch-architecture.json#s2`, `processing-pattern/nablarch-batch/nablarch-batch-feature_details.json#s5`, `processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.json#s1`

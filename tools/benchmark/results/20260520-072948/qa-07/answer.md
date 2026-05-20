**結論**: Nablarchバッチでは、フォームクラスに `@Csv` / `@CsvFormat` アノテーションでCSVフォーマットを定義し、`DataReader<T>` を実装して `ObjectMapperFactory` でファイルを1行ずつ読み込む。アクションクラスは `BatchAction` を継承して実装する。

**根拠**:

**1. フォームクラスの定義（`@Csv` / `@CsvFormat`）**

```java
@Csv(properties = {"localGovernmentCode", "zipCode5digit", ...}, type = CsvType.CUSTOM)
@CsvFormat(charset = "UTF-8", fieldSeparator = ',',
        ignoreEmptyLine = true, lineSeparator = "\r\n", quote = '"',
        quoteMode = QuoteMode.NORMAL, requiredHeader = false, emptyToNull = true)
public class ZipCodeForm {

    @Domain("localGovernmentCode")
    @Required
    private String localGovernmentCode;

    // 行番号を取得したい場合はLineNumberを付与
    private Long lineNumber;

    @LineNumber
    public Long getLineNumber() {
        return lineNumber;
    }
    // getter/setter省略
}
```

**2. データリーダの実装（`DataReader<T>`）**

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
    public void close(ExecutionContext ctx) {
        iterator.close();
    }

    private void initialize() {
        File file = FilePathSetting.getInstance()
                        .getFileWithoutCreate("csv-input", FILE_NAME);
        try {
            iterator = new ObjectMapperIterator<>(
                ObjectMapperFactory.create(ZipCodeForm.class, new FileInputStream(file)));
        } catch (FileNotFoundException e) {
            throw new IllegalStateException(e);
        }
    }
}
```

**3. アクションクラスの実装（`BatchAction` を継承）**

```java
public class ImportZipCodeFileAction extends BatchAction<ZipCodeForm> {

    @Override
    public Result handle(ZipCodeForm inputData, ExecutionContext ctx) {
        // 1件ずつのデータに対する業務ロジック
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

**注意点**:
- 標準提供の `FileDataReader` / `FileBatchAction` はデータアクセスに汎用データフォーマットを使用している。データバインドを使う場合はこれらを使用せず、上記のように `DataReader<T>` を自前実装し `BatchAction` を継承すること。
- `ObjectMapper` はスレッドアンセーフのため、複数スレッドで共有しないこと。
- リソースリークを防ぐため、`ObjectMapper` は `try-with-resources` またはクローズ処理が必要。ただしデータリーダでは `close()` メソッド内で `iterator.close()` を呼ぶことでフレームワークが自動的に解放する。

参照: component/libraries/libraries-data-bind.json:s7, s15, processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.json:s2, s3, processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s7, s8
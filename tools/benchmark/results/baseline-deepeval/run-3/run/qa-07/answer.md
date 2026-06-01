**結論**: NablarchバッチでCSVの各行をJava Beansオブジェクトとして1件ずつ読み込むには、**データバインド**機能（`ObjectMapperFactory` + `ObjectMapper`）を使い、`DataReader` インタフェースを実装したカスタムリーダークラスで1行ずつアクションに渡します。

**根拠**:

#### 1. フォームクラス（CSVバインド定義）

`@Csv` と `@CsvFormat` アノテーションでCSVフォーマットを定義します。プロパティは全て `String` 型で定義します。

```java
@Csv(properties = {"localGovernmentCode", "zipCode5digit"}, type = CsvType.CUSTOM)
@CsvFormat(charset = "UTF-8", fieldSeparator = ',',
        ignoreEmptyLine = true, lineSeparator = "\r\n", quote = '"',
        quoteMode = QuoteMode.NORMAL, requiredHeader = false, emptyToNull = true)
public class ZipCodeForm {

    @Domain("localGovernmentCode")
    @Required
    private String localGovernmentCode;

    private String zipCode5digit;

    // 行番号を取得したい場合
    private Long lineNumber;

    @LineNumber
    public Long getLineNumber() {
        return lineNumber;
    }

    // getter、setter省略
}
```

#### 2. データリーダの実装

`DataReader<T>` を実装し、`ObjectMapperIterator` で1行ずつ返します。

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
        FilePathSetting filePathSetting = FilePathSetting.getInstance();
        File zipCodeFile = filePathSetting.getFileWithoutCreate("csv-input", FILE_NAME);
        try {
            iterator = new ObjectMapperIterator<>(
                ObjectMapperFactory.create(ZipCodeForm.class, new FileInputStream(zipCodeFile)));
        } catch (FileNotFoundException e) {
            throw new IllegalStateException(e);
        }
    }
}
```

#### 3. アクションクラスの実装

`BatchAction<T>` を継承し、`createReader` で上記リーダーを返します。

```java
public class ImportZipCodeFileAction extends BatchAction<ZipCodeForm> {

    @Override
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

**注意点**:
- 標準の `FileDataReader` / `ValidatableFileDataReader` は**汎用データフォーマット**用であり、データバインドを使う場合は使用しません。代わりに `BatchAction`（`FileBatchAction` ではなく）と自作リーダーを使います。
- `ObjectMapper` の読み込み・書き込みはスレッドアンセーフです。複数スレッドから共有する場合は呼び出し元で同期制御が必要です。
- 全データの読み込み完了後は `ObjectMapper#close`（または `try-with-resources`）でリソースを解放してください。

参照: libraries-data-bind.json:s7, libraries-data-bind.json:s15, libraries-data-bind.json:s2, nablarch-batch-getting-started-nablarch-batch.json:s2, nablarch-batch-getting-started-nablarch-batch.json:s3, nablarch-batch-architecture.json:s7, nablarch-batch-architecture.json:s8
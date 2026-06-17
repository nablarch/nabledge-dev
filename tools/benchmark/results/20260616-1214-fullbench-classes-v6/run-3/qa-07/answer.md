**結論**: データバインド機能の`ObjectMapperFactory`で生成した`ObjectMapper`を使い、`@Csv`アノテーションを付与したJava BeansクラスにCSV行をバインドしながら1件ずつ読み込む。独自の`DataReader`実装クラスを作成し、`BatchAction`の`handle`メソッドで1件ずつ処理する。

**根拠**:

**1. フォームクラスの作成（CSVフォーマット定義）**

`@Csv`と`@CsvFormat`アノテーションでCSVフォーマットを定義したJava Beansクラスを作成する。

```java
@Csv(properties = {"localGovernmentCode", "zipCode"}, type = CsvType.CUSTOM)
@CsvFormat(charset = "UTF-8", fieldSeparator = ',',
        ignoreEmptyLine = true, lineSeparator = "\r\n", quote = '"',
        quoteMode = QuoteMode.NORMAL, requiredHeader = false, emptyToNull = true)
public class ZipCodeForm {

    @Required
    private String localGovernmentCode;
    private String zipCode;

    // 行番号を取得したい場合はこのように定義
    private Long lineNumber;
    @LineNumber
    public Long getLineNumber() { return lineNumber; }

    // getter/setter省略
}
```

`@Csv(type = Csv.CsvType.DEFAULT)` で標準のCSVフォーマット（カンマ区切り、ヘッダあり、UTF-8）を使うこともできる。

**2. データリーダの作成**

`DataReader<フォームクラス>`インタフェースを実装し、`ObjectMapperFactory.create`で`ObjectMapper`を生成してCSVを1行ずつ提供する。

```java
public class ZipCodeFileReader implements DataReader<ZipCodeForm> {

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
        File csvFile = FilePathSetting.getInstance()
                .getFileWithoutCreate("csv-input", "importZipCode");
        try {
            iterator = new ObjectMapperIterator<>(
                ObjectMapperFactory.create(ZipCodeForm.class,
                    new FileInputStream(csvFile)));
        } catch (FileNotFoundException e) {
            throw new IllegalStateException(e);
        }
    }
}
```

**3. 業務アクションの作成**

`BatchAction<フォームクラス>`を継承し、`handle`メソッドで1件ずつ処理する。`createReader`でデータリーダを返す。

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
- 標準提供の`FileDataReader`・`ValidatableFileDataReader`は内部で汎用データフォーマットを使用するため、データバインドと組み合わせて使用してはならない。CSVをデータバインドで読む場合は上記のように独自`DataReader`を実装すること。
- 全データ読み込み後は`ObjectMapper#close`でリソースを解放すること（`try-with-resources`推奨）。
- アップロードファイルなど外部から受け付けるデータを読み込む場合は、Java Beansクラスのプロパティを**全てString型**で定義しなければならない（型変換失敗時に異常終了させないため）。

参照: `component/libraries/libraries-data-bind.json:s7`, `component/libraries/libraries-data-bind.json:s15`, `processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.json:s2`, `processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.json:s3`, `processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s7`
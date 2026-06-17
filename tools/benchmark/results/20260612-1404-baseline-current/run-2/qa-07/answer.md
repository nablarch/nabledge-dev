**結論**: NablarchバッチでCSVファイルを1行ずつJava Beansとして読み込むには、データバインド機能（`nablarch-common-databind`）を使い、フォームクラスに`@Csv`/`@CsvFormat`アノテーションを付与した上で、`DataReader<T>`実装クラスと`BatchAction<T>`を組み合わせて実装します。

**根拠**:

**① フォームクラスの作成（CSVバインド定義）**

`@Csv` と `@CsvFormat` を付与してCSVフォーマットを指定します。

```java
@Csv(properties = {"localGovernmentCode", "zipCode5digit", /* 他フィールド */},
     type = CsvType.CUSTOM)
@CsvFormat(charset = "UTF-8", fieldSeparator = ',',
        ignoreEmptyLine = true, lineSeparator = "\r\n", quote = '"',
        quoteMode = QuoteMode.NORMAL, requiredHeader = false, emptyToNull = true)
public class ZipCodeForm {

    @Domain("localGovernmentCode")
    @Required
    private String localGovernmentCode;

    private String zipCode5digit;

    private Long lineNumber;

    @LineNumber
    public Long getLineNumber() {
        return lineNumber;
    }
    // getter/setter省略
}
```

ヘッダ行ありの標準CSVであれば `@Csv(type = Csv.CsvType.DEFAULT, ...)` を使うとより簡潔です。

**② DataReader の実装**

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
                ObjectMapperFactory.create(ZipCodeForm.class,
                                           new FileInputStream(file)));
        } catch (FileNotFoundException e) {
            throw new IllegalStateException(e);
        }
    }
}
```

**③ BatchAction の実装**

```java
public class ImportZipCodeFileAction extends BatchAction<ZipCodeForm> {

    @Override
    public Result handle(ZipCodeForm inputData, ExecutionContext ctx) {
        // 1行分のデータをBeanとして受け取り、業務処理を実行する
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
- 外部から受け付けたCSVファイルの場合、**フォームのプロパティは全てString型で定義**すること。型変換に失敗すると例外が発生してJava Beansが生成されないため、不正データは業務エラーとして別途ハンドリングする必要があります。
- `ObjectMapper` は使用後に必ず `close()` でリソースを解放すること（`try-with-resources` が利用可能）。
- `ObjectMapper` はスレッドアンセーフのため、複数スレッドでの共有はできません。

参照: libraries-data-bind.json:s7, libraries-data-bind.json:s15, libraries-data-bind.json:s2, nablarch-batch-getting-started-nablarch-batch.json:s2, nablarch-batch-getting-started-nablarch-batch.json:s3
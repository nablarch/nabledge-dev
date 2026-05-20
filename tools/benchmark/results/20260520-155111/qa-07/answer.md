**結論**: `@Csv` アノテーションでフォーマットを定義したフォームクラスと、`ObjectMapperFactory` を使った `DataReader` 実装を組み合わせることで、CSVの各行を Java Beans として1件ずつ読み込める。

**根拠**:

**① フォームクラスの作成（CSVフォーマット定義）**

`@Csv` および `@CsvFormat` アノテーションでフォーマットを指定する。

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

    private Long lineNumber;

    @LineNumber
    public Long getLineNumber() { return lineNumber; }

    // getter/setter は省略
}
```

**② DataReader の実装**

`DataReader<T>` を実装し、`ObjectMapperFactory` で生成した `ObjectMapper` を使って1行ずつ読み込む。

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
        File file = FilePathSetting.getInstance().getFileWithoutCreate("csv-input", "importZipCode");
        try {
            iterator = new ObjectMapperIterator<>(
                ObjectMapperFactory.create(ZipCodeForm.class, new FileInputStream(file)));
        } catch (FileNotFoundException e) {
            throw new IllegalStateException(e);
        }
    }
}
```

**③ BatchAction に組み込む**

`BatchAction` を継承したアクションクラスの `createReader` で上記リーダーを返す。

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
- `ObjectMapper` は必ず `close` でリソースを解放すること（`try-with-resources` 推奨）
- `ObjectMapper` はスレッドアンセーフのため、複数スレッドでの共有は不可
- 外部から受け付けたデータをフォームに読み込む場合、型変換エラーを業務エラーとして扱うため、プロパティは全て `String` 型で定義すること

参照: `libraries-data-bind.json:s7`, `libraries-data-bind.json:s15`, `nablarch-batch-getting-started-nablarch-batch.json:s2`, `nablarch-batch-getting-started-nablarch-batch.json:s3`
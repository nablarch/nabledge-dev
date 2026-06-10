**結論**: NablarchバッチでCSVファイルの各行をJava Beansとして1件ずつ読み込むには、`@Csv`/`@CsvFormat`アノテーションを付与したフォームクラスを作成し、`DataReader`の実装クラス内で`ObjectMapperFactory.create()`が生成する`ObjectMapper`を使って1行ずつ読み込みます。

**根拠**:

**① フォームクラスの作成（CSVフォーマット定義）**

```java
@Csv(
    properties = {"localGovernmentCode", "zipCode5digit", /* ...その他フィールド... */},
    type = CsvType.CUSTOM
)
@CsvFormat(
    charset = "UTF-8",
    fieldSeparator = ',',
    ignoreEmptyLine = true,
    lineSeparator = "\r\n",
    quote = '"',
    quoteMode = QuoteMode.NORMAL,
    requiredHeader = false,
    emptyToNull = true
)
public class ZipCodeForm {

    private String localGovernmentCode;
    // ... 他のフィールド ...

    private Long lineNumber;

    @LineNumber  // 行番号を自動設定するアノテーション
    public Long getLineNumber() {
        return lineNumber;
    }

    // getter/setter は省略
}
```

**② DataReaderの実装（1行ずつ読み込み）**

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
        File file = FilePathSetting.getInstance()
                        .getFileWithoutCreate("csv-input", "importZipCode");
        try {
            iterator = new ObjectMapperIterator<>(
                ObjectMapperFactory.create(ZipCodeForm.class, new FileInputStream(file))
            );
        } catch (FileNotFoundException e) {
            throw new IllegalStateException(e);
        }
    }
}
```

**③ BatchActionでの処理**

```java
public class ImportZipCodeFileAction extends BatchAction<ZipCodeForm> {

    @Override
    public Result handle(ZipCodeForm inputData, ExecutionContext ctx) {
        // inputData に1行分のデータが格納されている
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
- `ObjectMapper` はリソース解放が必要なため、`DataReader#close`で`ObjectMapper`（またはそれをラップしたイテレータ）の`close()`を必ず呼び出すこと。
- 標準提供の`FileDataReader`は汎用データフォーマットを使用するため、データバインド（`@Csv`/`@CsvFormat`）を使用する場合は使用せず、上記のようにカスタム`DataReader`を実装すること。
- CSVフォーマットが事前定義のフォーマットセットに合致する場合は`@Csv(type = Csv.CsvType.DEFAULT)`を使用でき、`@CsvFormat`は省略可能。

参照:
- `component/libraries/libraries-data-bind.json:s7`
- `component/libraries/libraries-data-bind.json:s15`
- `processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.json:s2`
- `processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.json:s3`
- `processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s7`
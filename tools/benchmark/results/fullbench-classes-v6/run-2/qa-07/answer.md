**結論**: NablarchバッチでCSVを1行ずつJava Beansとして読み込むには、**データバインド機能**を使用する。Formクラスに `@Csv` / `@CsvFormat` アノテーションを付与し、`DataReader` 実装クラス内で `ObjectMapperFactory.create()` が生成した `ObjectMapper` の `read()` を呼び出す。

**根拠**:

**① Formクラスの作成（CSVフォーマット定義）**

```java
@Csv(type = Csv.CsvType.CUSTOM, properties = {"localGovernmentCode", "zipCode5digit"})
@CsvFormat(charset = "UTF-8", fieldSeparator = ',',
        ignoreEmptyLine = true, lineSeparator = "\r\n", quote = '"',
        quoteMode = QuoteMode.NORMAL, requiredHeader = false, emptyToNull = true)
public class ZipCodeForm {

    @Domain("localGovernmentCode")
    @Required
    private String localGovernmentCode;  // プロパティは全てString型

    private String zipCode5digit;

    private Long lineNumber;

    @LineNumber  // 行番号を自動設定
    public Long getLineNumber() { return lineNumber; }

    // getter/setter省略
}
```

**② DataReader実装クラスの作成**

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
        FilePathSetting filePathSetting = FilePathSetting.getInstance();
        File csvFile = filePathSetting.getFileWithoutCreate("csv-input", "importZipCode");
        try {
            iterator = new ObjectMapperIterator<>(
                ObjectMapperFactory.create(ZipCodeForm.class, new FileInputStream(csvFile)));
        } catch (FileNotFoundException e) {
            throw new IllegalStateException(e);
        }
    }
}
```

**③ BatchActionの作成**

```java
public class ImportZipCodeFileAction extends BatchAction<ZipCodeForm> {

    @Override
    public Result handle(ZipCodeForm inputData, ExecutionContext ctx) {
        // inputDataに1行分のデータが渡される
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

`ObjectMapper` を直接使う場合（DataReader不要の場合）は次のように書ける：

```java
try (ObjectMapper<Person> mapper = ObjectMapperFactory.create(Person.class, inputStream)) {
    Person person;
    while ((person = mapper.read()) != null) {
        // 1件ずつ処理
    }
} catch (InvalidDataFormatException e) {
    // フォーマット不正時の処理
}
```

**注意点**:
- 外部から受け付けたデータ（CSVファイル）を読み込む場合、Formのプロパティは**全てString型**で定義すること。型変換失敗時に異常終了ではなく業務エラーとして通知するため。
- `ObjectMapper` のリソース解放を忘れないよう、`try-with-resources` を使用すること。

参照: libraries-data-bind.json:s7, libraries-data-bind.json:s15, libraries-data-bind.json:s2, nablarch-batch-getting-started-nablarch-batch.json:s2, nablarch-batch-getting-started-nablarch-batch.json:s3
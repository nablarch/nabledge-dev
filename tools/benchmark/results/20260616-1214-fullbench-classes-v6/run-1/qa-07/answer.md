**結論**: NablarchバッチでCSVの各行をJava Beansとして1件ずつ読み込むには、`@Csv`/`@CsvFormat` アノテーションでフォーマットを定義したフォームクラスと、`ObjectMapperFactory`・`DataReader` を使ったリーダクラスを作成し、`BatchAction` の `createReader` メソッドで返却します。

**根拠**:

**① フォームクラスの作成（CSVフォーマット定義）**

```java
@Csv(properties = {"localGovernmentCode", "zipCode5digit"}, type = CsvType.CUSTOM)
@CsvFormat(charset = "UTF-8", fieldSeparator = ',',
        ignoreEmptyLine = true, lineSeparator = "\r\n", quote = '"',
        quoteMode = QuoteMode.NORMAL, requiredHeader = false, emptyToNull = true)
public class ZipCodeForm {

    @Domain("localGovernmentCode")
    @Required
    private String localGovernmentCode;

    // 行番号を取得したい場合
    private Long lineNumber;

    @LineNumber
    public Long getLineNumber() {
        return lineNumber;
    }

    // getter/setter省略
}
```

ポイント：
- `@Csv` と `@CsvFormat` でCSVのフォーマットをアノテーションで指定
- 外部から受け付けるデータのため、**プロパティは全てString型**で定義すること（型変換失敗時の異常終了を防ぐため）
- `@LineNumber` を付与したgetterを定義すると論理行番号を自動取得可能

**② データリーダの作成**

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
        iterator.close();  // リソース解放
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

ポイント：
- `DataReader<T>` を実装し、`read` で1件、`hasNext` で次行有無、`close` でリソース解放
- `ObjectMapperFactory.create(フォームクラス, InputStream)` でObjectMapperを生成
- `hasNext` が `false` を返すと読み込み終了

**③ 業務アクションの作成**

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

**直接ObjectMapperを使う場合（DataReader不要のシンプルなケース）**

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
- `ObjectMapper` はスレッドアンセーフのため、複数スレッドから共有して呼び出す場合は呼び出し元で同期すること
- 読み込み完了後は必ず `ObjectMapper#close` でリソースを解放すること（`try-with-resources` 推奨）
- フォームのプロパティを全てString型にしておかないと、不正データで型変換失敗時に異常終了になる

参照: nablarch-batch-getting-started-nablarch-batch.json:s2, nablarch-batch-getting-started-nablarch-batch.json:s3, libraries-data-bind.json:s7, libraries-data-bind.json:s15, libraries-data-bind.json:s2
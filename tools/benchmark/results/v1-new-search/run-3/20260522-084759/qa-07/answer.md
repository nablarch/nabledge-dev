**結論**: NablarchバッチでCSVファイルの各行をJava Beansオブジェクトとして1件ずつ読み込むには、データバインド機能（`ObjectMapperFactory` + `ObjectMapper`）を使い、`DataReader` インタフェースを実装したカスタムデータリーダと、`BatchAction` を継承したアクションクラスを作成する。

**根拠**:

**① Java Beansクラスの定義（CSVフォーマットをアノテーションで指定）**

```java
@Csv(type = Csv.CsvType.DEFAULT, properties = {"age", "name"}, headers = {"年齢", "氏名"})
public class PersonForm {
    private String age;   // 外部入力はString型で定義する
    private String name;

    // getter、setterは省略。
}
```

カスタムフォーマットが必要な場合は `@CsvFormat` を追加する。

```java
@Csv(type = Csv.CsvType.CUSTOM, properties = {"localGovernmentCode", "zipCode5digit"})
@CsvFormat(charset = "UTF-8", fieldSeparator = ',',
        ignoreEmptyLine = true, lineSeparator = "\r\n", quote = '"',
        quoteMode = QuoteMode.NORMAL, requiredHeader = false, emptyToNull = true)
public class ZipCodeForm {
    private String localGovernmentCode;
    private String zipCode5digit;
    // ...
}
```

**② DataReaderの実装**

`DataReader` インタフェースを実装し、`ObjectMapperFactory.create` で生成した `ObjectMapper` を使用してCSVを1行ずつ読み込む。`ObjectMapperIterator` を活用すると実装をシンプルにできる。

```java
public class ZipCodeFileReader implements DataReader<ZipCodeForm> {

    private ObjectMapperIterator<ZipCodeForm> iterator;

    @Override
    public ZipCodeForm read(ExecutionContext ctx) {
        if (iterator == null) { initialize(); }
        return iterator.next();
    }

    @Override
    public boolean hasNext(ExecutionContext ctx) {
        if (iterator == null) { initialize(); }
        return iterator.hasNext();
    }

    @Override
    public void close(ExecutionContext ctx) {
        iterator.close();
    }

    private void initialize() {
        FilePathSetting filePathSetting = FilePathSetting.getInstance();
        File zipCodeFile = filePathSetting.getFileWithoutCreate("csv-input", "importZipCode");
        try {
            iterator = new ObjectMapperIterator<>(
                ObjectMapperFactory.create(ZipCodeForm.class, new FileInputStream(zipCodeFile)));
        } catch (FileNotFoundException e) {
            throw new IllegalStateException(e);
        }
    }
}
```

**③ BatchActionの実装**

`BatchAction` を継承してアクションクラスを作成する。`createReader` メソッドで上記のデータリーダを返す。

```java
public class ImportZipCodeFileAction extends BatchAction<ZipCodeForm> {

    @Override
    public Result handle(ZipCodeForm inputData, ExecutionContext ctx) {
        // 1行分のデータに対する業務処理を実装する
        return new Result.Success();
    }

    @Override
    public DataReader<ZipCodeForm> createReader(ExecutionContext ctx) {
        return new ZipCodeFileReader();
    }
}
```

`ObjectMapper` でデータを直接ループして読み込む場合のシンプルな例:

```java
try (ObjectMapper<PersonForm> mapper = ObjectMapperFactory.create(PersonForm.class, inputStream)) {
    PersonForm person;
    while ((person = mapper.read()) != null) {
        // Java Beansオブジェクトごとの処理
    }
} catch (InvalidDataFormatException e) {
    // フォーマット不正時の処理
}
```

**注意点**:
- 外部から受け付けたファイルを読み込む場合、Java Beansクラスのプロパティは**全てString型**で定義しなければならない（不正なデータでも業務エラーとして通知するため）。
- 標準の `FileDataReader` および `FileBatchAction` は汎用データフォーマットを使用するため、データバインドを使う場合は**これらを使用しないこと**。`DataReader` インタフェースを自分で実装し、アクションは `BatchAction` を継承すること。
- `ObjectMapper` は読み込み完了後に必ずクローズすること（`try-with-resources` で省略可能）。

参照: libraries-data-bind.json:s7, libraries-data-bind.json:s2, libraries-data-bind.json:s15, nablarch-batch-getting-started-nablarch-batch.json:s2, nablarch-batch-getting-started-nablarch-batch.json:s3, nablarch-batch-architecture.json:s7, nablarch-batch-architecture.json:s8

---
**結論**: NablarchバッチでCSVファイルの各行をJava Beansオブジェクトとして読み込むには、**データバインド**機能の`ObjectMapper`を使用したカスタム`DataReader`を実装します。標準提供の`FileDataReader`はデータバインドと併用できないため、`DataReader`インターフェースを自分で実装します。

**根拠**:

**① フォームクラス（Java Beans）を作成する**

`@Csv`と`@CsvFormat`アノテーションでCSVフォーマットを指定します。

```java
@Csv(properties = {"name", "age", "address"}, type = CsvType.CUSTOM)
@CsvFormat(charset = "UTF-8", fieldSeparator = ',',
        ignoreEmptyLine = true, lineSeparator = "\r\n", quote = '"',
        quoteMode = QuoteMode.NORMAL, requiredHeader = false, emptyToNull = true)
public class SampleForm {

    /** バリデーションのため全プロパティはString型で定義する */
    private String name;
    private String age;
    private String address;

    // getter、setter は省略
}
```

> **重要**: 外部から受け付けたデータを読み込む場合、Java BeansクラスのプロパティはすべてString型で定義しなければならない。型変換失敗で異常終了とせず、業務エラーとして通知するため。

**② DataReaderを実装する**

`ObjectMapper`を使ってCSVを1行ずつ読み込むDataReaderを作成します。

```java
public class SampleCsvReader implements DataReader<SampleForm> {

    private ObjectMapperIterator<SampleForm> iterator;

    @Override
    public SampleForm read(ExecutionContext ctx) {
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
        iterator.close();  // リソースを必ず解放すること
    }

    private void initialize() {
        File file = FilePathSetting.getInstance()
                .getFileWithoutCreate("csv-input", "inputFileName");
        try {
            iterator = new ObjectMapperIterator<>(
                ObjectMapperFactory.create(SampleForm.class, new FileInputStream(file)));
        } catch (FileNotFoundException e) {
            throw new IllegalStateException(e);
        }
    }
}
```

> **Tip**: `ObjectMapper`にはhasNextがないため、`ObjectMapperIterator`を使うとDataReaderの実装がシンプルになります（Exampleアプリケーションの実装を参照）。

**③ BatchActionで使用する**

```java
public class SampleBatchAction extends BatchAction<SampleForm> {

    @Override
    public Result handle(SampleForm inputData, ExecutionContext ctx) {
        // inputData が1行分のデータ（Java Beansオブジェクト）
        // バリデーション、業務ロジックなど
        return new Result.Success();
    }

    @Override
    public DataReader<SampleForm> createReader(ExecutionContext ctx) {
        return new SampleCsvReader();
    }
}
```

**ObjectMapperを直接使う場合（DataReaderを使わないシンプルな例）**:

```java
try (ObjectMapper<SampleForm> mapper = ObjectMapperFactory.create(SampleForm.class, inputStream)) {
    SampleForm form;
    while ((form = mapper.read()) != null) {
        // 1行ずつJava Beansオブジェクトとして処理
    }
} catch (InvalidDataFormatException e) {
    // フォーマット不正時の処理
}
```

**注意点**:
- 標準の`FileDataReader`・`ValidatableFileDataReader`はデータバインドと**併用不可**。DataReader実装が必要。
- `ObjectMapper`はtry-with-resources で囲み、必ず`close()`してリソースを解放すること。
- `ObjectMapper`はスレッドアンセーフのため、複数スレッドからの同時呼び出しは不可。

参照: libraries-data-bind.json:s7, libraries-data-bind.json:s15, libraries-data-bind.json:s2, nablarch-batch-getting-started-nablarch-batch.json:s2, nablarch-batch-getting-started-nablarch-batch.json:s3, nablarch-batch-architecture.json:s7
**結論**: NablarchバッチでCSVの各行をJava Beansオブジェクトとして1件ずつ読み込むには、データバインド機能の `ObjectMapperFactory`/`ObjectMapper` と、`DataReader` を独自実装したカスタムリーダを組み合わせる。

**根拠**:

**1. フォームクラス（Java Beans）の作成**

CSVをバインドするフォームクラスに `@Csv` および `@CsvFormat` アノテーションを付与してフォーマットを定義する。

```java
@Csv(properties = {"field1", "field2"}, type = CsvType.CUSTOM)
@CsvFormat(charset = "UTF-8", fieldSeparator = ',',
        ignoreEmptyLine = true, lineSeparator = "\r\n", quote = '"',
        quoteMode = QuoteMode.NORMAL, requiredHeader = false, emptyToNull = true)
public class MyForm {
    private String field1;
    private String field2;
    // getter、setter省略
}
```

標準のフォーマットセット（DEFAULT / RFC4180 / EXCEL / TSV）を使う場合は `type = Csv.CsvType.DEFAULT` と指定し、`@CsvFormat` を省略できる。

**2. DataReaderの実装**

`DataReader<MyForm>` を実装し、`ObjectMapperFactory.create()` で生成した `ObjectMapper` を使って1行ずつ読み込む。`ObjectMapperIterator` でラップすると `hasNext()` / `next()` が使えてシンプルになる。

```java
public class MyFileReader implements DataReader<MyForm> {

    private ObjectMapperIterator<MyForm> iterator;

    @Override
    public MyForm read(ExecutionContext ctx) {
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
        iterator.close();  // 必ずcloseしてリソース解放
    }

    private void initialize() {
        File csvFile = FilePathSetting.getInstance()
                .getFileWithoutCreate("csv-input", "myFile");
        try {
            iterator = new ObjectMapperIterator<>(
                    ObjectMapperFactory.create(MyForm.class, new FileInputStream(csvFile)));
        } catch (FileNotFoundException e) {
            throw new IllegalStateException(e);
        }
    }
}
```

**3. BatchActionの実装**

`BatchAction<MyForm>` を継承し、`createReader` でリーダを返却、`handle` で1件分のデータを処理する。

```java
public class MyBatchAction extends BatchAction<MyForm> {

    @Override
    public Result handle(MyForm inputData, ExecutionContext ctx) {
        // 1件分の業務処理
        return new Result.Success();
    }

    @Override
    public DataReader<MyForm> createReader(ExecutionContext ctx) {
        return new MyFileReader();
    }
}
```

**注意点**:
- データバインドを使う場合、標準提供の `FileDataReader` および `FileBatchAction` は使用できない（汎用データフォーマットを前提としているため）。`DataReader` インタフェースを実装したカスタムリーダを作成すること。
- 外部から受け取るCSVの場合、型変換エラーを業務エラーとして通知できるよう、フォームクラスのプロパティは全て `String` 型で定義すること。

参照: libraries-data-bind.json:s7, libraries-data-bind.json:s15, nablarch-batch-getting-started-nablarch-batch.json:s2, nablarch-batch-getting-started-nablarch-batch.json:s3, nablarch-batch-architecture.json:s7, nablarch-batch-architecture.json:s8

---
Step 5〜8: 回答を生成し、検証します。

**結論**: NablarchバッチでCSVファイルの各行をJava Beansオブジェクトとして読み込むには、データバインド機能（`ObjectMapperFactory` + `ObjectMapper`）と`DataReader`の実装を組み合わせて使います。

**根拠**:

**① Formクラスの作成（CSVフォーマット定義）**

`@Csv` / `@CsvFormat` アノテーションでCSVのフォーマットを定義したフォームクラスを作成します。

```java
@Csv(properties = {"code", "name", "address"}, type = CsvType.CUSTOM)
@CsvFormat(charset = "UTF-8", fieldSeparator = ',',
        ignoreEmptyLine = true, lineSeparator = "\r\n", quote = '"',
        quoteMode = QuoteMode.NORMAL, requiredHeader = false, emptyToNull = true)
public class ZipCodeForm {

    private String code;
    private String name;
    private String address;

    // getter、setter

    /** 行番号（@LineNumberで自動セット） */
    private Long lineNumber;

    @LineNumber
    public Long getLineNumber() {
        return lineNumber;
    }
}
```

**② DataReaderの作成（1行ずつ返す）**

`DataReader<T>` を実装し、`ObjectMapperFactory.create()` で生成した `ObjectMapper` を使って1行ずつフォームオブジェクトを返します。

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
                ObjectMapperFactory.create(ZipCodeForm.class, new FileInputStream(file)));
        } catch (FileNotFoundException e) {
            throw new IllegalStateException(e);
        }
    }
}
```

**③ BatchActionの作成（1件ずつ処理）**

`BatchAction<ZipCodeForm>` を継承し、`handle` メソッドで1行分のデータを処理します。

```java
public class ImportZipCodeFileAction extends BatchAction<ZipCodeForm> {

    @Override
    public Result handle(ZipCodeForm inputData, ExecutionContext ctx) {
        // inputData に1行分のデータがZipCodeFormオブジェクトとして渡される
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

`ObjectMapper` から直接 `while ((obj = mapper.read()) != null)` でループすることも可能ですが、バッチでは `DataReader` + `BatchAction` の構成が推奨パターンです。

**注意点**:
- **プロパティは全てString型で定義すること**: 外部から受け付けたデータを読み込む場合、型変換失敗時に異常終了せず業務エラーとして通知できるよう、Formクラスのプロパティは全て `String` 型で定義する必要があります。
- **`close()` の呼び出し**: `ObjectMapper` はリソースを保持するため、使用後に必ず `close()` を呼び出すこと（`try-with-resources` で省略可能）。

参照: libraries-data-bind.json:s7, libraries-data-bind.json:s15, libraries-data-bind.json:s2, nablarch-batch-getting-started-nablarch-batch.json:s2, nablarch-batch-getting-started-nablarch-batch.json:s3

---
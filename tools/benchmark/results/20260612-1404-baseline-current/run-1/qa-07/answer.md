**結論**: NablarchバッチでCSVの各行をJava Beansオブジェクトとして1件ずつ読み込むには、データバインド機能（`ObjectMapper`）を使ったカスタム`DataReader`を実装し、`BatchAction`の`createReader`メソッドで登録する。

**根拠**:

**1. Formクラスに `@Csv` / `@CsvFormat` でフォーマットを定義**

```java
@Csv(properties = {"localGovernmentCode", "zipCode5digit"}, type = CsvType.CUSTOM)
@CsvFormat(charset = "UTF-8", fieldSeparator = ',',
        ignoreEmptyLine = true, lineSeparator = "\r\n", quote = '"',
        quoteMode = QuoteMode.NORMAL, requiredHeader = false, emptyToNull = true)
public class ZipCodeForm {
    private String localGovernmentCode;
    private String zipCode5digit;
    // getter, setter
}
```

- 外部ファイルのデータを受け付ける場合、プロパティは全て`String`型で定義すること（不正データを業務エラーとして通知するため）。
- フォーマットセット（`DEFAULT`/`RFC4180`/`EXCEL`/`TSV`）にマッチする場合は `@CsvFormat` を省略して `type = Csv.CsvType.DEFAULT` 等で指定できる。

**2. `DataReader` 実装クラスを作成**（`ObjectMapperFactory.create()` でマッパーを生成）

```java
public class ZipCodeFileReader implements DataReader<ZipCodeForm> {
    private ObjectMapperIterator<ZipCodeForm> iterator;

    @Override
    public ZipCodeForm read(ExecutionContext ctx) {
        if (iterator == null) initialize();
        return iterator.next();  // 1件返す
    }

    @Override
    public boolean hasNext(ExecutionContext ctx) {
        if (iterator == null) initialize();
        return iterator.hasNext();  // false になるとループ終了
    }

    @Override
    public void close(ExecutionContext ctx) {
        iterator.close();  // ストリームを解放
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

**3. `BatchAction` で `createReader` にリーダを登録**

```java
public class ImportZipCodeFileAction extends BatchAction<ZipCodeForm> {

    @Override
    public Result handle(ZipCodeForm inputData, ExecutionContext ctx) {
        // inputData に1行分のデータが渡される
        return new Result.Success();
    }

    @Override
    public DataReader<ZipCodeForm> createReader(ExecutionContext ctx) {
        return new ZipCodeFileReader();
    }
}
```

**注意点**:
- 標準の `FileDataReader` や `FileBatchAction` は汎用データフォーマット（フォーマット定義ファイル）を使用するため、データバインドを使う場合は使用しないこと。代わりに `BatchAction` を継承し、カスタム `DataReader` を組み合わせる。
- `ObjectMapper` はスレッドアンセーフなため、複数スレッドで共有しないこと。
- ファイルパス管理には `FilePathSetting` を使い、論理名（例：`"csv-input"`）でディレクトリを管理する。

参照: libraries-data-bind.json:s7, libraries-data-bind.json:s15, libraries-data-bind.json:s2, nablarch-batch-getting-started-nablarch-batch.json:s2, nablarch-batch-getting-started-nablarch-batch.json:s3, nablarch-batch-architecture.json:s7, nablarch-batch-architecture.json:s8
**結論**: データバインドライブラリ（`nablarch-common-databind`）を使用し、`@Csv`/`@CsvFormat` アノテーション付き Java Beans クラスと `DataReader` の実装（`ObjectMapperIterator` を利用）を組み合わせて実現する。標準の `FileDataReader` は使用しない。

**根拠**:

**1. Maven依存関係の追加**

```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-common-databind</artifactId>
</dependency>
```

**2. フォームクラス（Java Beans）の作成**

`@Csv` と `@CsvFormat` でCSVフォーマットを指定する。外部ファイルの場合、プロパティはすべて `String` 型で定義する。

```java
@Csv(properties = {"zipCode", "address"}, type = CsvType.CUSTOM)
@CsvFormat(charset = "UTF-8", fieldSeparator = ',',
        ignoreEmptyLine = true, lineSeparator = "\r\n", quote = '"',
        quoteMode = QuoteMode.NORMAL, requiredHeader = false, emptyToNull = true)
public class ZipCodeForm {

    private String zipCode;
    private String address;

    private Long lineNumber;

    @LineNumber
    public Long getLineNumber() {
        return lineNumber;
    }
    // getter/setter省略
}
```

**3. DataReader の実装**

`DataReader<ZipCodeForm>` を実装し、`ObjectMapperIterator` を使って1件ずつ読み込む。

```java
public class ZipCodeFileReader implements DataReader<ZipCodeForm> {

    private static final String FILE_NAME = "importZipCode";
    private ObjectMapperIterator<ZipCodeForm> iterator;

    @Override
    public ZipCodeForm read(ExecutionContext ctx) {
        if (iterator == null) {
            initialize();
        }
        return iterator.next();
    }

    @Override
    public boolean hasNext(ExecutionContext ctx) {
        if (iterator == null) {
            initialize();
        }
        return iterator.hasNext();
    }

    @Override
    public void close(ExecutionContext ctx) {
        iterator.close();
    }

    private void initialize() {
        FilePathSetting filePathSetting = FilePathSetting.getInstance();
        File zipCodeFile = filePathSetting.getFileWithoutCreate("csv-input", FILE_NAME);
        try {
            iterator = new ObjectMapperIterator<>(ObjectMapperFactory.create(ZipCodeForm.class,
                    new FileInputStream(zipCodeFile)));
        } catch (FileNotFoundException e) {
            throw new IllegalStateException(e);
        }
    }
}
```

**4. バッチアクションの実装**

`BatchAction` を継承し、`createReader` で上記 DataReader を返す。

```java
public class ImportZipCodeFileAction extends BatchAction<ZipCodeForm> {

    @Override
    public Result handle(ZipCodeForm inputData, ExecutionContext ctx) {
        // 1件ずつ業務処理を実装
        return new Result.Success();
    }

    @Override
    public DataReader<ZipCodeForm> createReader(ExecutionContext ctx) {
        return new ZipCodeFileReader();
    }
}
```

**注意点**:
- 標準の `FileDataReader` / `ValidatableFileDataReader` は汎用データフォーマットを使用するため、データバインドを使う場合は使用してはならない。同様に `FileBatchAction` も使用不可（`BatchAction` を使用すること）。
- 外部ファイルのデータを読み込む場合、バリデーションエラーを業務エラーとして扱うため、フォームのプロパティはすべて `String` 型で定義すること。
- `ObjectMapper` はスレッドアンセーフ。複数スレッドで共有する場合は呼び出し元で同期処理が必要。
- `close` メソッドで必ずストリームを解放すること（`try-with-resources` 使用を推奨）。

参照: `libraries-data-bind.json:s7`, `libraries-data-bind.json:s15`, `libraries-data-bind.json:s2`, `nablarch-batch-getting-started-nablarch-batch.json:s2`, `nablarch-batch-getting-started-nablarch-batch.json:s3`, `nablarch-batch-architecture.json:s7`, `nablarch-batch-architecture.json:s8`
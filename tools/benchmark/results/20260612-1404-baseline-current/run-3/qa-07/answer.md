**結論**: データバインド機能（`ObjectMapperFactory` + `ObjectMapperIterator`）を使い、`DataReader<T>` を独自実装する。アクションは `BatchAction<T>` を継承する。標準の `FileDataReader` や `FileBatchAction` はデータバインドと併用できないため使用しない。

---

**根拠**:

#### 1. Formクラス（Beanクラス）の作成

CSVをバインドするFormクラスに `@Csv` と `@CsvFormat` を付与する。

```java
@Csv(properties = {"localGovernmentCode", "zipCode5digit"}, type = Csv.CsvType.DEFAULT)
public class ZipCodeForm {

    /** 全国地方公共団体コード */
    @Domain("localGovernmentCode")
    @Required
    private String localGovernmentCode;

    private String zipCode5digit;

    // 行番号を取得したい場合はプロパティを定義してゲッタに@LineNumberを付与
    private Long lineNumber;

    @LineNumber
    public Long getLineNumber() {
        return lineNumber;
    }

    // getter/setter 省略
}
```

デフォルトフォーマット (`CsvType.DEFAULT`) がカンマ区切り・UTF-8・ヘッダ行ありに対応している。カスタムフォーマットが必要な場合は `type = CsvType.CUSTOM` + `@CsvFormat` を組み合わせる。

```java
@Csv(type = Csv.CsvType.CUSTOM, properties = {"age", "name"})
@CsvFormat(
    fieldSeparator = ',', lineSeparator = "\r\n", quote = '"',
    ignoreEmptyLine = true, requiredHeader = false, charset = "UTF-8",
    quoteMode = CsvDataBindConfig.QuoteMode.NORMAL, emptyToNull = true)
public class Person { ... }
```

#### 2. DataReaderの実装

`DataReader<T>` を実装し、`ObjectMapperIterator` でCSVを1行ずつ返す。

```java
public class ZipCodeFileReader implements DataReader<ZipCodeForm> {

    private static final String FILE_NAME = "importZipCode";
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
            .getFileWithoutCreate("csv-input", FILE_NAME);
        try {
            iterator = new ObjectMapperIterator<>(
                ObjectMapperFactory.create(ZipCodeForm.class, new FileInputStream(file)));
        } catch (FileNotFoundException e) {
            throw new IllegalStateException(e);
        }
    }
}
```

- `read()` で1行分のBeanを返す。これが業務アクションに引き渡される。
- `hasNext()` が `false` を返すと読み込み終了。
- `close()` で `ObjectMapperIterator` のリソースを解放する。

#### 3. BatchActionの実装

`BatchAction<T>` を継承し、`createReader()` で上記のDataReaderを返す。

```java
public class ImportZipCodeFileAction extends BatchAction<ZipCodeForm> {

    @Override
    public Result handle(ZipCodeForm inputData, ExecutionContext ctx) {
        // 1件分の処理（例: DBへの登録）
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

---

**注意点**:
- 外部ファイルを読み込む場合、Formクラスのプロパティは**全て `String` 型**で定義する（不正データを業務エラーとして扱うため）
- 標準の `FileDataReader`・`ValidatableFileDataReader` は**汎用データフォーマット**を使用するため、データバインドと組み合わせる場合は使用しない
- 同様に `FileBatchAction` も汎用データフォーマット前提のため使用しない。`BatchAction` を使うこと
- `ObjectMapper` はスレッドアンセーフのため、複数スレッドで共有しないこと

参照: `processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.json:s2`, `processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.json:s3`, `component/libraries/libraries-data-bind.json:s7`, `component/libraries/libraries-data-bind.json:s15`, `component/libraries/libraries-data-bind.json:s2`, `processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s7`, `processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s8`
Step 5: 回答を生成します。

---

**結論**: NablarchバッチでCSVファイルの各行をJava Beansとして1件ずつ読み込むには、**データバインド**機能（`nablarch-common-databind`）を使用します。具体的には、`@Csv`アノテーションを付与したFormクラスと`DataReader`実装クラスを作成し、`ObjectMapperFactory`経由で行単位に読み込みます。

---

**根拠**:

**① Formクラス（CSVバインド定義）**

CSVの列構成をアノテーションで定義します。

```java
@Csv(properties = {"code", "name", "zipCode"}, type = CsvType.CUSTOM)
@CsvFormat(
        charset = "UTF-8",
        fieldSeparator = ',',
        ignoreEmptyLine = true,
        lineSeparator = "\r\n",
        quote = '"',
        quoteMode = QuoteMode.NORMAL,
        requiredHeader = false,
        emptyToNull = true)
public class MyRecordForm {

    private String code;
    private String name;
    private String zipCode;

    // getter/setter（省略）

    private Long lineNumber;

    @LineNumber
    public Long getLineNumber() {
        return lineNumber;
    }
}
```

- `@Csv` の `properties` にCSVの列順に対応するプロパティ名を定義する
- `@LineNumber` を付与したgetterを用意すると、何行目のデータかが自動設定される
- 外部ファイルを受け付けるため、**プロパティは原則 `String` 型**で定義する

**② DataReader実装クラス**

```java
public class MyFileReader implements DataReader<MyRecordForm> {

    private ObjectMapperIterator<MyRecordForm> iterator;

    @Override
    public MyRecordForm read(ExecutionContext ctx) {
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
                .getFileWithoutCreate("csv-input", "myFile");
        try {
            iterator = new ObjectMapperIterator<>(
                    ObjectMapperFactory.create(MyRecordForm.class,
                            new FileInputStream(file)));
        } catch (FileNotFoundException e) {
            throw new IllegalStateException(e);
        }
    }
}
```

**③ 業務アクションクラス**

```java
public class MyBatchAction extends BatchAction<MyRecordForm> {

    @Override
    public Result handle(MyRecordForm inputData, ExecutionContext ctx) {
        // inputData に1行分のデータが入っている
        MyEntity entity = BeanUtil.createAndCopy(MyEntity.class, inputData);
        UniversalDao.insert(entity);
        return new Result.Success();
    }

    @Override
    public DataReader<MyRecordForm> createReader(ExecutionContext ctx) {
        return new MyFileReader();
    }
}
```

**④ モジュール依存**

```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-common-databind</artifactId>
</dependency>
```

---

**注意点**:
- `ObjectMapper`（イテレータ経由の場合は`ObjectMapperIterator`）は `close` 必須。`try-with-resources` またはDataReaderの `close` メソッドで確実に解放すること。
- `ObjectMapper`はスレッドアンセーフなため、複数スレッドで共有しないこと。
- フォーマットが標準の `DEFAULT`（カンマ区切り・ヘッダあり・UTF-8）に合致する場合は `@Csv(type = CsvType.DEFAULT, ...)` のみで `@CsvFormat` を省略できる。

参照: `component/libraries/libraries-data-bind.json:s7`, `component/libraries/libraries-data-bind.json:s15`, `processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.json:s2`, `processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.json:s3`

---
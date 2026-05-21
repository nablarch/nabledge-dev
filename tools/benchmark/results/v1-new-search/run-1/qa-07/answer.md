**結論**: NablarchバッチでCSVファイルの各行をJava Beansオブジェクトとして読み込むには、**データバインド**機能（`ObjectMapperFactory` / `ObjectMapper`）を使用し、`DataReader` インタフェースを自作して `BatchAction` に組み込む。

**根拠**:

**1. フォームクラスの作成（@Csv / @CsvFormat アノテーション）**

CSVのフォーマットをアノテーションで定義したフォームクラスを作成する。

```java
@Csv(type = Csv.CsvType.DEFAULT, properties = {"age", "name"}, headers = {"年齢", "氏名"})
public class PersonForm {
    private Integer age;
    private String name;
    // getter、setter省略
}
```

フォーマットセットに合わない場合は `@CsvFormat` で個別に指定する：

```java
@Csv(type = Csv.CsvType.CUSTOM, properties = {"localGovernmentCode", ...})
@CsvFormat(charset = "UTF-8", fieldSeparator = ',',
        ignoreEmptyLine = true, lineSeparator = "\r\n", quote = '"',
        quoteMode = QuoteMode.NORMAL, requiredHeader = false, emptyToNull = true)
public class ZipCodeForm {
    @Required
    private String localGovernmentCode;

    private Long lineNumber;

    @LineNumber
    public Long getLineNumber() { return lineNumber; }
    // その他getter/setter省略
}
```

標準で用意されているフォーマットセット（`@Csv`の`type`属性）：

| フォーマット | ヘッダ行 | 列区切り | 空行を無視 |
|---|---|---|---|
| DEFAULT | あり | カンマ | true |
| RFC4180 | なし | カンマ | false |
| EXCEL | なし | カンマ | false |
| TSV | なし | タブ | false |

**2. DataReader の作成**

`DataReader<T>` インタフェースを実装し、`ObjectMapperFactory.create` で生成したイテレータ経由で1行ずつ読み込む：

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

`ObjectMapper` を直接使う場合（DataReader外）：

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

**3. BatchAction の作成**

`BatchAction<フォームクラス>` を継承し、`createReader` で上記リーダを返す：

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

**注意点**:
- 標準提供の `FileDataReader` / `ValidatableFileDataReader` は汎用データフォーマットを使用するため、データバインドと**併用不可**。`DataReader` を自作すること。
- 同様に `FileBatchAction` も汎用データフォーマットを使用するため、データバインド使用時は `BatchAction` を使うこと。
- 外部から受け付けたファイルを読み込む場合は、型変換失敗時の異常終了を避けるため、フォームのプロパティは**全てString型**で定義すること。
- 依存モジュールに `nablarch-common-databind` の追加が必要：
  ```xml
  <dependency>
    <groupId>com.nablarch.framework</groupId>
    <artifactId>nablarch-common-databind</artifactId>
  </dependency>
  ```

参照: libraries-data-bind.json:s2, libraries-data-bind.json:s7, libraries-data-bind.json:s15, libraries-data-bind.json:s21, libraries-data-bind.json:s5, nablarch-batch-getting-started-nablarch-batch.json:s2, nablarch-batch-getting-started-nablarch-batch.json:s3, nablarch-batch-architecture.json:s7, nablarch-batch-architecture.json:s8

---
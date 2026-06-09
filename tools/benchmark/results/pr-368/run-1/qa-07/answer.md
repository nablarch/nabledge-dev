**結論**: NablarchバッチでCSVファイルの各行をJava Beansオブジェクトとして1件ずつ読み込むには、**データバインド機能**（`ObjectMapper` + `@Csv` / `@CsvFormat` アノテーション）を使い、`DataReader` 実装クラスから1行ずつ業務アクションへ渡す。

---

**根拠**:

**1. Java Beansフォームにアノテーションでフォーマットを指定する**

```java
@Csv(properties = {"age", "name"}, type = CsvType.DEFAULT)
public class PersonForm {
    private String age;   // 外部入力なので String 型で定義
    private String name;
    // getter/setter
}
```

カスタムフォーマットが必要な場合は `@CsvFormat` を追加する:

```java
@Csv(properties = {"age", "name"}, type = CsvType.CUSTOM)
@CsvFormat(charset = "UTF-8", fieldSeparator = ',',
        ignoreEmptyLine = true, lineSeparator = "\r\n", quote = '"',
        quoteMode = QuoteMode.NORMAL, requiredHeader = false, emptyToNull = true)
public class PersonForm { ... }
```

**2. `DataReader` 実装クラスを作成する**

`DataReader<PersonForm>` を実装し、`ObjectMapperFactory.create()` で生成した `ObjectMapper` から1行ずつ返す:

```java
public class PersonFileReader implements DataReader<PersonForm> {

    private ObjectMapperIterator<PersonForm> iterator;

    @Override
    public PersonForm read(ExecutionContext ctx) {
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
                        .getFileWithoutCreate("csv-input", "personFile");
        try {
            iterator = new ObjectMapperIterator<>(
                ObjectMapperFactory.create(PersonForm.class, new FileInputStream(file)));
        } catch (FileNotFoundException e) {
            throw new IllegalStateException(e);
        }
    }
}
```

**3. `BatchAction` で `DataReader` を返す**

```java
public class PersonBatchAction extends BatchAction<PersonForm> {

    @Override
    public Result handle(PersonForm inputData, ExecutionContext ctx) {
        // inputData に1行分のデータが入っている
        // 例: BeanUtil.createAndCopy でエンティティへコピーしてDBに登録
        PersonEntity entity = BeanUtil.createAndCopy(PersonEntity.class, inputData);
        UniversalDao.insert(entity);
        return new Result.Success();
    }

    @Override
    public DataReader<PersonForm> createReader(ExecutionContext ctx) {
        return new PersonFileReader();
    }
}
```

---

**注意点**:
- 外部から受け付けたCSVファイルを処理する場合、Java Beansクラスのプロパティは**全て `String` 型**で定義すること（型変換失敗による異常終了を防ぐため）
- `ObjectMapper` は使い終わったら必ず `close()` すること（`try-with-resources` 推奨）
- 標準提供の `FileDataReader` / `ValidatableFileDataReader` は**汎用データフォーマット**を使用するため、データバインドを利用する場合はこれらを使わず、独自の `DataReader` を実装すること

参照: libraries-data-bind.json:s7, libraries-data-bind.json:s15, libraries-data-bind.json:s2, nablarch-batch-getting-started-nablarch-batch.json:s2, nablarch-batch-getting-started-nablarch-batch.json:s3, nablarch-batch-architecture.json:s7
**結論**: `ObjectMapperFactory.create()` で `ObjectMapper` を生成し、`mapper.read()` を繰り返し呼び出すことで、CSVの各行をJava Beansオブジェクトとして1件ずつ読み込めます。

**根拠**:

**1. Java BeansクラスにCSVフォーマットを定義する**

`@Csv` と `@CsvFormat` アノテーションをクラスに付与してフォーマットを指定します。

```java
@Csv(type = Csv.CsvType.DEFAULT, properties = {"age", "name"}, headers = {"年齢", "氏名"})
public class Person {
    private Integer age;
    private String name;
    // getter、setter
}
```

カスタムフォーマット（文字コード・区切り文字等を細かく指定する場合）:

```java
@Csv(type = Csv.CsvType.CUSTOM, properties = {"age", "name"})
@CsvFormat(
    fieldSeparator = ',',
    lineSeparator = "\r\n",
    quote = '"',
    charset = "UTF-8",
    ignoreEmptyLine = true,
    quoteMode = CsvDataBindConfig.QuoteMode.NORMAL,
    requiredHeader = false,
    emptyToNull = true)
public class Person {
    private Integer age;
    private String name;
}
```

**2. `ObjectMapper` で1行ずつ読み込む**

```java
try (ObjectMapper<Person> mapper = ObjectMapperFactory.create(Person.class, inputStream)) {
    Person person;
    while ((person = mapper.read()) != null) {
        // 1行分のJava Beansオブジェクトに対する処理
    }
} catch (InvalidDataFormatException e) {
    // フォーマット不正時の処理
}
```

`mapper.read()` は全データを読み終えると `null` を返します。`try-with-resources` を使うことでクローズ処理が自動化されます。

**3. Nablarchバッチで使う場合（`DataReader` の実装）**

`ObjectMapperIterator` を使うと `DataReader<T>` の実装をシンプルにできます。

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
        File file = FilePathSetting.getInstance().getFileWithoutCreate("csv-input", "importZipCode");
        try {
            iterator = new ObjectMapperIterator<>(
                ObjectMapperFactory.create(ZipCodeForm.class, new FileInputStream(file)));
        } catch (FileNotFoundException e) {
            throw new IllegalStateException(e);
        }
    }
}
```

**4. 必要なMavenモジュール**

```xml
<dependency>
    <groupId>com.nablarch.framework</groupId>
    <artifactId>nablarch-common-databind</artifactId>
</dependency>
```

**注意点**:
- 外部から受け付けたファイル（アップロード等）を読み込む場合、不正データでも業務エラーとして扱うため、**Java BeansクラスのプロパティはすべてString型**で定義する必要があります
- Java Beansクラスにバインドする場合、フォーマット指定はアノテーションで行うため、`ObjectMapper` 生成時に `DataBindConfig` を渡すことはできません（Mapクラスにバインドする場合のみ `DataBindConfig` を使用できます）
- 行番号を取得する必要がある場合は、`@LineNumber` アノテーションを `Long` 型プロパティのgetterに付与します
- 入力値チェックが必要な場合は、`mapper.read()` 後に `ValidatorUtil.validate(person)` を呼び出します

参照: `component/libraries/libraries-data-bind.json#s7`, `component/libraries/libraries-data-bind.json#s15`, `processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.json#s2`
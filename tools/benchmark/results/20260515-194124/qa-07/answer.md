**結論**: NablarchのデータバインドAPIを使用して、`@Csv`アノテーションをJava Beansクラスに付与し、`ObjectMapperFactory.create()`で`ObjectMapper`を生成後、`mapper.read()`をループ内で呼び出すことでCSVの各行を1件ずつJava Beansオブジェクトとして読み込めます。

**根拠**:

**1. Mavenモジュールの追加**

```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-common-databind</artifactId>
</dependency>
```

**2. Java BeansクラスにCSVフォーマットをアノテーションで定義する**

```java
@Csv(type = Csv.CsvType.DEFAULT, properties = {"age", "name"}, headers = {"年齢", "氏名"})
public class Person {
    private Integer age;
    private String name;
    // getter、setterは省略。
}
```

`type`にはフォーマットセットを指定します。`DEFAULT`はカンマ区切り・UTF-8・ヘッダ行ありです。他に`RFC4180`、`EXCEL`、`TSV`が選択可能です。

**3. ObjectMapperを使って1件ずつ読み込む**

```java
try (ObjectMapper<Person> mapper = ObjectMapperFactory.create(Person.class, inputStream)) {
    Person person;
    while ((person = mapper.read()) != null) {
        // Java Beansオブジェクトごとの処理を記述（バリデーション、DB登録など）
    }
} catch (InvalidDataFormatException e) {
    // 読み込んだデータのフォーマットが不正な場合の処理を記述
}
```

`ObjectMapper`は`AutoCloseable`を実装しているため、`try-with-resources`でクローズ処理を省略できます。

**フォーマットをカスタマイズする場合**（例：タブ区切り、ヘッダなしなど）:

```java
@Csv(type = Csv.CsvType.CUSTOM, properties = {"age", "name"})
@CsvFormat(
        fieldSeparator = '\t',
        lineSeparator = "\r\n",
        quote = '"',
        ignoreEmptyLine = false,
        requiredHeader = false,
        charset = "UTF-8",
        quoteMode = CsvDataBindConfig.QuoteMode.NORMAL,
        emptyToNull = true)
public class Person {
    private Integer age;
    private String name;
}
```

**注意点**:

- **アップロードファイルなど外部入力の場合**: 不正なデータでも異常終了させずに業務エラーとして通知できるよう、Java BeansクラスのプロパティはすべてString型で定義しなければならない。型変換に失敗した場合は例外が発生する。
- **Bean Validationによる入力チェックを行う場合**: `mapper.read()`で取得した各オブジェクトに対して`ValidatorUtil.validate(person)`を呼び出す。
- **行番号の取得**: Java BeansクラスのLong型プロパティに`@LineNumber`アノテーションを付与することで、論理行番号を取得できる（Mapオブジェクトとして取得する場合は行番号取得不可）。
- **スレッドセーフではない**: `ObjectMapper`のインスタンスは複数スレッドで共有不可。複数スレッドから呼び出す場合は呼び出し元で同期処理を行うこと。
- Java BeansクラスにバインドするとDataBindConfigは使用できない（フォーマット指定はアノテーションのみ）。

参照: `libraries-data-bind.json#s7`, `libraries-data-bind.json#s15`, `libraries-data-bind.json#s2`, `libraries-data-bind.json#s21`, `libraries-data-bind.json#s5`
**結論**: NablarchのデータバインドライブラリとObjectMapperFactoryを使用する。`@Csv`アノテーションを付与したJava BeansクラスをObjectMapperFactory.create()に渡し、mapper.read()をループで呼び出すことでCSVを1件ずつJava Beansとして読み込める。

**根拠**:

**Step 1: Maven依存の追加**

```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-common-databind</artifactId>
</dependency>
```

**Step 2: Java Beansクラスに@Csvアノテーションを定義**

```java
@Csv(type = Csv.CsvType.DEFAULT, properties = {"age", "name"}, headers = {"年齢", "氏名"})
public class Person {
    private Integer age;
    private String name;

    // getter、setterは省略。
}
```

`Csv.CsvType.DEFAULT`以外のフォーマットが必要な場合は、`@CsvFormat`を併用して個別に指定できる（文字コード・区切り文字・クォートモードなど）。

**Step 3: ObjectMapperでCSVを1件ずつ読み込む**

```java
try (ObjectMapper<Person> mapper = ObjectMapperFactory.create(Person.class, inputStream)) {
    Person person;
    while ((person = mapper.read()) != null) {
        // Java Beansオブジェクトごとの処理を記述
    }
} catch (InvalidDataFormatException e) {
    // 読み込んだデータのフォーマットが不正な場合の処理を記述
}
```

**注意点**:
- 外部から受け付けたCSVを読み込む場合、不正なデータを業務エラーとして通知するためにJava Beansのプロパティは**全てString型**で定義すること。
- ObjectMapperは必ずclose（またはtry-with-resources）すること。閉じないとリソースリークが発生する。

参照: libraries-data-bind.json:s5, libraries-data-bind.json:s7, libraries-data-bind.json:s15
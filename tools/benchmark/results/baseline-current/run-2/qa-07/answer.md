**結論**: `ObjectMapperFactory#create` で生成した `ObjectMapper` を使用し、`mapper.read()` を呼び出してCSVの各行を1件ずつJava Beansオブジェクトとして読み込む。

**根拠**:

**1. Maven依存関係の追加**

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

`@Csv` の `type` には `DEFAULT`、`RFC4180`、`EXCEL`、`TSV` のいずれかのフォーマットセットを指定する（`DEFAULT` はヘッダ行あり・UTF-8・カンマ区切り）。

**3. ObjectMapperを使用して1件ずつ読み込む**

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
- `ObjectMapper` は `AutoCloseable` を実装しているため、`try-with-resources` でリソースを解放すること。
- アップロードファイルなど外部からの入力を読み込む場合は、Java BeansクラスのプロパティをすべてString型で定義しなければならない（型変換失敗時に例外が発生し業務エラーとして通知できないため）。
- `ObjectMapper` の読み込み・書き込みはスレッドアンセーフ。複数スレッドから共有する場合は呼び出し元で同期処理を行うこと。
- Java Beansクラスにバインドする場合、`ObjectMapper` 生成時に `DataBindConfig` でのフォーマット指定はできない（アノテーション指定のみ）。

参照: `libraries-data-bind.json#s7` `libraries-data-bind.json#s15`
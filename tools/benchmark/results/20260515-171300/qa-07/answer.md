**結論**: `ObjectMapperFactory.create()` で生成した `ObjectMapper` を使い、`mapper.read()` を `while` ループで呼び出すことで、CSVの各行を1件ずつ Java Beans オブジェクトとして読み込めます。

**根拠**:

**ステップ1: Maven 依存関係の追加**

```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-common-databind</artifactId>
</dependency>
```

**ステップ2: Java Beans クラスに `@Csv` アノテーションを付与**

```java
@Csv(type = Csv.CsvType.DEFAULT, properties = {"age", "name"}, headers = {"年齢", "氏名"})
public class Person {
    private Integer age;
    private String name;
    // getter、setter
}
```

`Csv.CsvType.DEFAULT` はカンマ区切り・ヘッダ行あり・UTF-8 のフォーマットです（他に `RFC4180`、`EXCEL`、`TSV` が選択可能）。

**ステップ3: `ObjectMapper` で1件ずつ読み込む**

```java
try (ObjectMapper<Person> mapper = ObjectMapperFactory.create(Person.class, inputStream)) {
    Person person;
    while ((person = mapper.read()) != null) {
        // 1件ずつの処理をここに記述
    }
} catch (InvalidDataFormatException e) {
    // フォーマット不正時の処理
}
```

`mapper.read()` はファイル末尾に達すると `null` を返します。`try-with-resources` を使うことでクローズ処理が自動化されます。

**フォーマットのカスタマイズが必要な場合**: `@CsvFormat` アノテーションで区切り文字・改行コード・クォート文字などを個別指定できます。

```java
@Csv(type = Csv.CsvType.CUSTOM, properties = {"age", "name"})
@CsvFormat(fieldSeparator = '\t', charset = "UTF-8", requiredHeader = false, ...)
public class Person { ... }
```

**注意点**:
- アップロードファイルなど外部入力を読み込む場合、型変換失敗が業務エラーとなるため、**Bean のプロパティはすべて `String` 型で定義**すること
- `ObjectMapper` はスレッドアンセーフのため、複数スレッドで共有する場合は呼び出し元で同期処理が必要
- `@LineNumber` アノテーション付きの `Long` プロパティを定義することで論理行番号も取得可能

参照: `libraries-data-bind.json#s7`, `libraries-data-bind.json#s15`, `libraries-data-bind.json#s2`, `libraries-data-bind.json#s21`
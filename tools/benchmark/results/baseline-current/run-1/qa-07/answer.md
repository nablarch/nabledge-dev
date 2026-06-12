**結論**: NablarchのデータバインドAPIを使い、`@Csv`アノテーションを付けたJava Beansクラスと`ObjectMapperFactory`を組み合わせることで、CSVファイルを1行ずつJava Beansオブジェクトとして読み込めます。

**根拠**:

### 1. Java Beansクラスの定義（フォーマット指定）

`@Csv`アノテーションでCSVのフォーマットとプロパティマッピングを指定します。

```java
@Csv(type = Csv.CsvType.DEFAULT, properties = {"age", "name"}, headers = {"年齢", "氏名"})
public class Person {
    private Integer age;
    private String name;

    // getter、setter
}
```

フォーマットセットは`Csv.CsvType`で選択します（DEFAULT / RFC4180 / EXCEL / TSV）。  
DEFAULTはカンマ区切り、UTF-8、ヘッダ行ありの設定です。

### 2. 読み込み実装

`ObjectMapperFactory#create`で`ObjectMapper`を生成し、`mapper.read()`でnullが返るまでループします。

```java
try (ObjectMapper<Person> mapper = ObjectMapperFactory.create(Person.class, inputStream)) {
    Person person;
    while ((person = mapper.read()) != null) {
        // Java Beansオブジェクトごとの処理
    }
} catch (InvalidDataFormatException e) {
    // フォーマット不正時の処理
}
```

`try-with-resources`を使うことでクローズ処理（`ObjectMapper#close`）を自動化できます。

### 3. 依存モジュール

```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-common-databind</artifactId>
</dependency>
```

**注意点**:

- **アップロードファイル等の外部入力の場合**: 型変換失敗時に例外が発生して異常終了するため、Java BeansクラスのプロパティはすべてString型で定義し、Bean Validationで入力値チェックを行うこと
- **スレッドセーフ非対応**: `ObjectMapper`のインスタンスは複数スレッドで共有してはいけない
- **フォーマットが標準に合わない場合**: `@CsvFormat`アノテーションで区切り文字・引用符・文字コード等を個別指定できる

参照: libraries-data-bind.json#s7, libraries-data-bind.json#s15, libraries-data-bind.json#s2, libraries-data-bind.json#s5
**結論**: `ObjectMapperFactory#create` で `ObjectMapper` を生成し、`mapper.read()` が `null` を返すまでループすることで、CSVの各行をJava Beansオブジェクトとして1件ずつ読み込めます。

**根拠**:

**① Java BeansクラスにCSVフォーマットをアノテーションで定義する**

```java
@Csv(type = Csv.CsvType.DEFAULT, properties = {"age", "name"}, headers = {"年齢", "氏名"})
public class Person {
    private Integer age;
    private String name;
    // getter、setter は省略
}
```

`@Csv` の `type` には事前定義されたフォーマットセットを指定します。

| フォーマットセット | 列区切り | ヘッダ行 | 空行無視 |
|---|---|---|---|
| DEFAULT | カンマ | あり (true) | true |
| RFC4180 | カンマ | なし (false) | false |
| EXCEL | カンマ | なし (false) | false |
| TSV | タブ | なし (false) | false |

カスタムフォーマットが必要な場合は `@CsvFormat` を組み合わせて使用できます。

**② `ObjectMapper` で1件ずつ読み込む**

```java
try (ObjectMapper<Person> mapper = ObjectMapperFactory.create(Person.class, inputStream)) {
    Person person;
    while ((person = mapper.read()) != null) {
        // Java Beansオブジェクトごとの処理を記述
    }
} catch (InvalidDataFormatException e) {
    // フォーマット不正時の処理
}
```

- `ObjectMapperFactory.create(Person.class, inputStream)` で `ObjectMapper` を生成
- `mapper.read()` を `null` になるまでループして1行ずつ処理
- `try-with-resources` を使用すると `close()` 処理が自動化される

**注意点**:

- **外部ファイル（アップロードデータなど）を扱う場合**: 型変換失敗でも業務エラーとして通知できるよう、Java BeansクラスのプロパティはすべてString型で定義すること
- **Java Beansクラスにバインドする場合**: フォーマット指定はアノテーション（`@Csv`/`@CsvFormat`）のみ。`ObjectMapper` 生成時に `DataBindConfig` を渡すことはできない（`DataBindConfig` はMapバインド時のみ使用可能）
- **スレッドアンセーフ**: `ObjectMapper` は複数スレッドで共有しないこと。共有する場合は呼び出し元で同期処理が必要

参照: `component/libraries/libraries-data-bind.json#s7`, `component/libraries/libraries-data-bind.json#s15`, `component/libraries/libraries-data-bind.json#s21`
### Answer

NablarchバッチでCSVファイルの各行をJava Beansオブジェクトとして1件ずつ読み込む実装は、以下の2ステップで行います。

---

## 1. フォームクラスの作成

CSVをバインドするJava Beansクラスに `@Csv` / `@CsvFormat` アノテーションでフォーマットを指定します。

```java
@Csv(
    properties = {"age", "name"},
    headers = {"年齢", "氏名"},
    type = Csv.CsvType.DEFAULT
)
public class PersonForm {
    private String age;   // 外部入力はすべてString型で定義すること
    private String name;

    // getter / setter 省略

    private Long lineNumber;

    @LineNumber  // 行番号を自動設定したい場合に付与
    public Long getLineNumber() {
        return lineNumber;
    }
}
```

**ポイント:**
- アップロードファイル等の外部入力データは、型変換エラーを業務エラーとして扱えるよう、プロパティは**すべて `String` 型**で定義すること
- `@LineNumber` をgetterに付与することで、何行目のデータかを自動取得できる

フォーマットが標準セット以外の場合は `type = Csv.CsvType.CUSTOM` と `@CsvFormat` を組み合わせて個別指定します（文字コード、区切り文字、改行コード等）。

---

## 2. DataReaderの作成

`DataReader<PersonForm>` を実装し、`ObjectMapperFactory` で生成した `ObjectMapper` を使って1行ずつ読み込みます。

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
                        .getFileWithoutCreate("csv-input", "importPerson");
        try {
            iterator = new ObjectMapperIterator<>(
                ObjectMapperFactory.create(PersonForm.class, new FileInputStream(file))
            );
        } catch (FileNotFoundException e) {
            throw new IllegalStateException(e);
        }
    }
}
```

**ポイント:**
- `read()` が返したデータが業務アクションハンドラへ1件ずつ引き渡される
- `hasNext()` が `false` を返すと読み込み処理が終了する
- `close()` で `ObjectMapperIterator#close()` を呼び出してリソースを解放する
- `ObjectMapper` は `try-with-resources` でも使用可能（直接ループする場合）

---

## 直接ループする場合（参考）

DataReaderを使わず直接ループ処理する場合はこちら：

```java
try (ObjectMapper<PersonForm> mapper =
        ObjectMapperFactory.create(PersonForm.class, inputStream)) {
    PersonForm person;
    while ((person = mapper.read()) != null) {
        // 1件ずつ処理
    }
} catch (InvalidDataFormatException e) {
    // フォーマット不正時の処理
}
```
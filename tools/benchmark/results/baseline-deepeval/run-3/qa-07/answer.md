十分な情報が集まりました。回答を生成します。

**Step 5: 回答生成**

セクション内容を確認し、ユーザーの質問（NablarchバッチでCSVファイルの各行をJava Beansオブジェクトとして1件ずつ読み込む実装方法）に回答します。

**Step 6: 回答検証**

抽出したNablarch固有の主張：
1. `@Csv`/`@CsvFormat`アノテーションをJava Beansクラスに付与 → s15に直接記述あり ✅
2. `ObjectMapperFactory#create`で`ObjectMapper`を生成 → s7に直接記述あり ✅
3. `ObjectMapper#read()`で1件ずつ読み込み → s7に直接記述あり ✅
4. `DataReader`インタフェースを実装する → s2に直接記述あり ✅
5. `ObjectMapperIterator`を使ってイテレータ化できる → s2に記述あり ✅
6. `FilePathSetting`でファイルパスを取得 → s2に記述あり ✅
7. `close`でリソースを解放すること → s7の Important に記述あり ✅

verify_result = PASS

---

**結論**: `@Csv`（または`@CsvFormat`）アノテーションを付けたフォームクラスを定義し、`DataReader<T>`を実装して`ObjectMapperFactory.create()`で生成した`ObjectMapper`を使って`read()`で1行ずつ読み込みます。

**根拠**:

#### 1. フォームクラス（Java Beans）の作成

`@Csv`と`@CsvFormat`でCSVフォーマットを指定します。

```java
@Csv(properties = {"localGovernmentCode", "zipCode5digit", /* ...他の項目 */},
     type = CsvType.CUSTOM)
@CsvFormat(charset = "UTF-8", fieldSeparator = ',',
        ignoreEmptyLine = true, lineSeparator = "\r\n", quote = '"',
        quoteMode = QuoteMode.NORMAL, requiredHeader = false, emptyToNull = true)
public class ZipCodeForm {

    @Domain("localGovernmentCode")
    @Required
    private String localGovernmentCode;

    // 行番号を自動設定したい場合
    private Long lineNumber;

    @LineNumber
    public Long getLineNumber() {
        return lineNumber;
    }

    // その他のgetter/setterは省略
}
```

フォーマットセット（`Csv.CsvType`）を使う場合は`@CsvFormat`不要です。

| 定数 | 特徴 |
|------|------|
| `DEFAULT` | カンマ区切り、ヘッダ行あり、UTF-8 |
| `RFC4180` | カンマ区切り、ヘッダなし |
| `EXCEL` | Excel互換 |
| `TSV` | タブ区切り |

#### 2. DataReader の実装

```java
public class ZipCodeFileReader implements DataReader<ZipCodeForm> {

    private ObjectMapperIterator<ZipCodeForm> iterator;

    @Override
    public ZipCodeForm read(ExecutionContext ctx) {
        if (iterator == null) {
            initialize();
        }
        return iterator.next();
    }

    @Override
    public boolean hasNext(ExecutionContext ctx) {
        if (iterator == null) {
            initialize();
        }
        return iterator.hasNext();
    }

    @Override
    public void close(ExecutionContext ctx) {
        iterator.close();  // 必ずリソースを解放すること
    }

    private void initialize() {
        File file = FilePathSetting.getInstance()
                        .getFileWithoutCreate("csv-input", "importZipCode");
        try {
            iterator = new ObjectMapperIterator<>(
                ObjectMapperFactory.create(ZipCodeForm.class,
                                          new FileInputStream(file)));
        } catch (FileNotFoundException e) {
            throw new IllegalStateException(e);
        }
    }
}
```

`ObjectMapperIterator`を使わず`ObjectMapper`を直接使う場合のシンプルな読み込みパターン：

```java
try (ObjectMapper<ZipCodeForm> mapper =
         ObjectMapperFactory.create(ZipCodeForm.class, inputStream)) {
    ZipCodeForm form;
    while ((form = mapper.read()) != null) {
        // 1件ずつ処理
    }
} catch (InvalidDataFormatException e) {
    // フォーマット不正時の処理
}
```

**注意点**:
- `ObjectMapper`のインスタンスはスレッドアンセーフです。複数スレッドで共有する場合は同期処理が必要です。
- 外部から受け取るファイル（アップロード等）の場合、バリデーション異常を業務エラーとして通知するため、フォームのプロパティは**全てString型**で定義してください。
- `close()`を忘れるとリソースリークが発生します。`try-with-resources`の使用を推奨します。

参照: `component/libraries/libraries-data-bind.json:s7`, `component/libraries/libraries-data-bind.json:s15`, `component/libraries/libraries-data-bind.json:s21`, `processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.json:s2`

---
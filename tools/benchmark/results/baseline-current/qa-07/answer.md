**結論**: `DataReader` を実装し、`ObjectMapperIterator` を使って CSVファイルを1行ずつ Java Beans オブジェクトとして読み込む。

**根拠**:

**1. Java Beans クラスにアノテーションを付与する**

CSVフォーマットを指定するため、`@Csv` と `@CsvFormat` をクラスに付与する。

```java
// 定義済みフォーマットセット（DEFAULT/RFC4180/EXCEL/TSV）を使う場合
@Csv(type = Csv.CsvType.DEFAULT, properties = {"localGovernmentCode", "zipCode5digit"}, headers = {"団体コード", "郵便番号"})
public class ZipCodeForm {
    private String localGovernmentCode;
    private String zipCode5digit;
    // getter/setter 省略
}
```

カスタムフォーマット（ヘッダなし、文字コード指定など）の場合は `CsvType.CUSTOM` + `@CsvFormat` を組み合わせる：

```java
@Csv(properties = {"localGovernmentCode", "zipCode5digit"}, type = CsvType.CUSTOM)
@CsvFormat(charset = "UTF-8", fieldSeparator = ',',
        ignoreEmptyLine = true, lineSeparator = "\r\n", quote = '"',
        quoteMode = QuoteMode.NORMAL, requiredHeader = false, emptyToNull = true)
public class ZipCodeForm {
    @Domain("localGovernmentCode")
    @Required
    private String localGovernmentCode;

    private Long lineNumber;

    @LineNumber  // 行番号を自動セット
    public Long getLineNumber() { return lineNumber; }
    // その他 getter/setter 省略
}
```

**2. `DataReader` を実装する**

`ObjectMapperIterator` を使って、`read()` で1件ずつ返す：

```java
public class ZipCodeFileReader implements DataReader<ZipCodeForm> {

    private static final String FILE_NAME = "importZipCode";
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
        File csvFile = FilePathSetting.getInstance()
                .getFileWithoutCreate("csv-input", FILE_NAME);
        try {
            iterator = new ObjectMapperIterator<>(
                    ObjectMapperFactory.create(ZipCodeForm.class,
                            new FileInputStream(csvFile)));
        } catch (FileNotFoundException e) {
            throw new IllegalStateException(e);
        }
    }
}
```

**3. 主要クラスの役割まとめ**

| クラス | 役割 |
|--------|------|
| `@Csv` / `@CsvFormat` | CSVフォーマットをBean に定義 |
| `ObjectMapperFactory#create` | `ObjectMapper` を生成 |
| `ObjectMapperIterator` | `hasNext()` / `next()` で1件ずつ取得 |
| `DataReader<T>` | バッチフレームワークへのデータ供給インタフェース |

**注意点**:

- 外部入力ファイル（アップロードなど不正データが入りうる場合）は、Bean の全プロパティを **`String` 型**で定義すること。型変換失敗時に例外が発生し、Bean が生成されなくなるため。
- `ObjectMapper` はスレッドアンセーフ。複数スレッドで共有する場合は呼び出し元で同期処理が必要。
- 読み込み完了後は `ObjectMapper#close`（または `try-with-resources`）でリソースを解放すること。
- 利用可能な定義済みフォーマットセット: `DEFAULT`（ヘッダあり・空行無視）、`RFC4180`、`EXCEL`、`TSV`。いずれにも合わない場合は `CsvType.CUSTOM` + `@CsvFormat` で個別指定。

参照: `processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.json#s2`、`component/libraries/libraries-data-bind.json#s7`、`component/libraries/libraries-data-bind.json#s15`
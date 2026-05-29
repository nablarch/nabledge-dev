十分な情報が得られました。回答を生成します。

**Step 5: 回答生成**

**結論**: Nablarchバッチでは、`@Csv` アノテーションを付与したフォームクラスに `ObjectMapper` を使ってCSVを1行ずつバインドし、`DataReader` 実装でフレームワークに渡す。

**Step 6: 検証**

主なNablarch固有の主張を確認:
- `@Csv` アノテーション → s15に明示的に記載 ✅
- `@CsvFormat` アノテーション → s15に明示的に記載 ✅
- `ObjectMapperFactory.create()` → s7に記載 ✅
- `ObjectMapper#read()` → s7に記載 ✅
- `DataReader` インタフェース、`read`/`hasNext`/`close` メソッド → s2に記載 ✅
- `ObjectMapperIterator` → s2に記載（Exampleの実装として） ✅
- `BatchAction` の `createReader` メソッド → s3に記載 ✅
- `try-with-resources` でクローズ → s7に記載 ✅

verify_result = PASS

**結論**: **`@Csv` アノテーションを付与したフォームクラスと `ObjectMapper` を使ってCSVを1行ずつ読み込み、`DataReader` 実装でバッチフレームワークに渡す。**

---

**根拠**:

**① フォームクラスの作成（CSVフォーマットをアノテーションで指定）**

```java
@Csv(properties = {"localGovernmentCode", "zipCode5digit"}, type = Csv.CsvType.CUSTOM)
@CsvFormat(charset = "UTF-8", fieldSeparator = ',',
        ignoreEmptyLine = true, lineSeparator = "\r\n", quote = '"',
        quoteMode = CsvDataBindConfig.QuoteMode.NORMAL, requiredHeader = false, emptyToNull = true)
public class ZipCodeForm {

    @Required
    private String localGovernmentCode;

    private String zipCode5digit;

    /** 行番号を自動設定 */
    private Long lineNumber;

    @LineNumber
    public Long getLineNumber() { return lineNumber; }

    // getter/setter省略
}
```

標準フォーマット（`CsvType.DEFAULT` など）を使う場合は `@CsvFormat` を省略できる。DEFAULTはカンマ区切り・ヘッダあり・UTF-8。

**② DataReader の実装（1行ずつフォームに読み込む）**

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

**③ BatchAction でリーダを組み込む**

```java
public class ImportZipCodeFileAction extends BatchAction<ZipCodeForm> {

    @Override
    public Result handle(ZipCodeForm inputData, ExecutionContext ctx) {
        // 読み込んだ1行分のデータを処理
        ZipCodeData data = BeanUtil.createAndCopy(ZipCodeData.class, inputData);
        UniversalDao.insert(data);
        return new Result.Success();
    }

    @Override
    public DataReader<ZipCodeForm> createReader(ExecutionContext ctx) {
        return new ZipCodeFileReader();
    }
}
```

**注意点**:
- 外部から受け付けたCSVの場合（アップロードファイル等）、フォームのプロパティは全て `String` 型で定義すること（不正データでも業務エラーとして通知できるようにするため）
- `ObjectMapper` はスレッドアンセーフのため、複数スレッドからの共有不可
- `ObjectMapper`（または `ObjectMapperIterator`）は必ず `close` すること（リソースリーク防止のため `try-with-resources` 推奨）

参照: `libraries-data-bind.json:s7`, `libraries-data-bind.json:s15`, `libraries-data-bind.json:s21`, `nablarch-batch-getting-started-nablarch-batch.json:s2`, `nablarch-batch-getting-started-nablarch-batch.json:s3`

---
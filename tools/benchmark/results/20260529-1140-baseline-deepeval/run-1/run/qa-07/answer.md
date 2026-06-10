**結論**: NablarchバッチでCSVファイルを1行ずつJava Beansオブジェクトとして読み込むには、**データバインド**機能を使い、`DataReader`実装クラス内で`ObjectMapperFactory`と`ObjectMapper`（または`ObjectMapperIterator`）を使用します。

**根拠**:

**1. フォームクラスの作成（`@Csv`アノテーションでフォーマット指定）**

```java
@Csv(properties = {"field1", "field2"}, type = CsvType.CUSTOM)
@CsvFormat(
    charset = "UTF-8",
    fieldSeparator = ',',
    ignoreEmptyLine = true,
    lineSeparator = "\r\n",
    quote = '"',
    quoteMode = QuoteMode.NORMAL,
    requiredHeader = false,
    emptyToNull = true)
public class ZipCodeForm {

    private String field1;
    private String field2;

    /** 行番号を自動設定する場合はゲッタに@LineNumberを付与 */
    private Long lineNumber;

    @LineNumber
    public Long getLineNumber() {
        return lineNumber;
    }

    // getter、setter省略
}
```

**2. DataReaderの実装（`ObjectMapperIterator`を使用）**

```java
public class ZipCodeFileReader implements DataReader<ZipCodeForm> {

    private ObjectMapperIterator<ZipCodeForm> iterator;

    @Override
    public ZipCodeForm read(ExecutionContext ctx) {
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
        FilePathSetting filePathSetting = FilePathSetting.getInstance();
        File file = filePathSetting.getFileWithoutCreate("csv-input", "importZipCode");
        try {
            iterator = new ObjectMapperIterator<>(
                ObjectMapperFactory.create(ZipCodeForm.class, new FileInputStream(file)));
        } catch (FileNotFoundException e) {
            throw new IllegalStateException(e);
        }
    }
}
```

**CSVフォーマットセット**（`Csv.CsvType.DEFAULT`を使用する場合のデフォルト設定）:

| 設定項目 | DEFAULT |
|---------|---------|
| 列区切り | カンマ(,) |
| 行区切り | `\r\n` |
| フィールド囲み文字 | `"` |
| 空行を無視 | true |
| ヘッダ行あり | true |
| 文字コード | UTF-8 |

**注意点**:
- 外部ファイル（アップロードファイルなど）を読み込む場合、フォームのプロパティは**すべて`String`型**で定義すること（不正データを業務エラーとして通知するため）
- `ObjectMapper`はtry-with-resourcesを使い、処理完了後は必ず`close()`してリソースを解放すること
- 標準提供の`FileDataReader`や`ValidatableFileDataReader`は**汎用データフォーマット**を使うため、データバインドを使う場合はこれらを使用せず、`DataReader`インタフェースを独自実装すること
- `ObjectMapper`はスレッドアンセーフなため、複数スレッドで共有しないこと

参照: `component/libraries/libraries-data-bind.json:s7`, `component/libraries/libraries-data-bind.json:s15`, `component/libraries/libraries-data-bind.json:s2`, `processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.json:s2`, `processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s7`, `component/libraries/libraries-data-bind.json:s21`
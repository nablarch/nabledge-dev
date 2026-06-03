十分な情報を取得できました。Step 5でAnswerを生成します。

**セクション選定まとめ（Step 3）：**

- `libraries-data-bind.json:s7` **high** — ObjectMapperでCSVをJava Beansに1件ずつ読む主要実装
- `libraries-data-bind.json:s15` **high** — @Csv/@CsvFormatアノテーションでフォーマット指定
- `libraries-data-bind.json:s2` **partial** — Java Beansプロパティ全String制約
- `libraries-data-bind.json:s11` **partial** — @LineNumberで行番号取得
- `nablarch-batch-getting-started-nablarch-batch.json:s2` **high** — DataReader実装例（ZipCodeFileReader）
- `nablarch-batch-getting-started-nablarch-batch.json:s3` **high** — BatchAction実装例
- `nablarch-batch-architecture.json:s7` **partial** — FileDataReaderはデータバインドと非互換の注意
- `nablarch-batch-architecture.json:s8` **partial** — FileBatchActionもデータバインドと非互換の注意
- `javadoc/javadoc-nablarch-common-databind-ObjectMapper.json:s3` **partial** — read()メソッドAPI
- `javadoc/javadoc-nablarch-common-databind-ObjectMapperFactory.json:s4` **partial** — create()メソッドAPI

read_sections:
- `component/libraries/libraries-data-bind.json:s7`
- `component/libraries/libraries-data-bind.json:s15`
- `component/libraries/libraries-data-bind.json:s2`
- `component/libraries/libraries-data-bind.json:s11`
- `processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.json:s2`
- `processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.json:s3`
- `processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s7`
- `processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s8`
- `javadoc/javadoc-nablarch-common-databind-ObjectMapper.json:s3`
- `javadoc/javadoc-nablarch-common-databind-ObjectMapperFactory.json:s4`

---

**Step 5: 回答生成 → Step 6: 検証 → Step 7-8: 出力**

**結論**: NablarchバッチでCSVの各行をJava Beansとして読み込むには、**データバインド機能**（`@Csv`アノテーション + `ObjectMapper`）を使った独自`DataReader`を実装し、`BatchAction`の`createReader`で返す。

**根拠**:

### 1. Beanクラスにアノテーションを定義する

```java
@Csv(properties = {"code", "name"}, type = CsvType.CUSTOM)
@CsvFormat(charset = "UTF-8", fieldSeparator = ',',
        ignoreEmptyLine = true, lineSeparator = "\r\n", quote = '"',
        quoteMode = QuoteMode.NORMAL, requiredHeader = false, emptyToNull = true)
public class ZipCodeForm {
    private String code;
    private String name;

    // getter/setter

    private Long lineNumber;

    @LineNumber
    public Long getLineNumber() {
        return lineNumber;
    }
}
```

- `@Csv`：バインド対象プロパティとCSV型を指定
- `@CsvFormat`：文字コード・区切り文字など詳細フォーマットを指定（DEFAULTやRFC4180など定義済みセットを使う場合は省略可）
- `@LineNumber`：行番号を自動設定したい場合に`Long`型プロパティのgetterに付与

### 2. DataReaderを実装する

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
        File file = filePathSetting.getFileWithoutCreate("csv-input", "inputFileName");
        try {
            iterator = new ObjectMapperIterator<>(
                ObjectMapperFactory.create(ZipCodeForm.class, new FileInputStream(file)));
        } catch (FileNotFoundException e) {
            throw new IllegalStateException(e);
        }
    }
}
```

- `ObjectMapperFactory.create(ZipCodeForm.class, inputStream)` でObjectMapperを生成
- `ObjectMapperIterator`を使うことで`hasNext()`/`next()`インタフェースに変換（Exampleの`ObjectMapperIterator.java`を参照）
- `close`で必ずリソースを解放する

### 3. BatchActionに組み込む

```java
public class ImportZipCodeFileAction extends BatchAction<ZipCodeForm> {

    @Override
    public Result handle(ZipCodeForm inputData, ExecutionContext ctx) {
        // 1行分のデータに対する業務処理
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
- 外部から受け取るファイルの場合、Beanのプロパティは**全てString型**で定義すること（型変換失敗時に異常終了させないため）
- `FileDataReader` / `FileBatchAction`（標準提供）はデータバインドと非互換のため使用しないこと（これらは汎用データフォーマットを使用）
- `ObjectMapper`はスレッドアンセーフなため、複数スレッドでの共有は不可

参照: libraries-data-bind.json:s7, libraries-data-bind.json:s15, nablarch-batch-getting-started-nablarch-batch.json:s2, nablarch-batch-getting-started-nablarch-batch.json:s3

---

**Verify（Step 6）**

Nablarch固有クレーム確認：
1. `@Csv`アノテーション → s15で明示 ✅
2. `@CsvFormat`アノテーション → s15で明示 ✅
3. `ObjectMapperFactory.create` → s7, Javadoc s4で明示 ✅
4. `ObjectMapper#read()` → s7で明示 ✅
5. `ObjectMapperIterator` → s2（DataReader実装例）で明示 ✅
6. `@LineNumber` → s11で明示 ✅
7. `FilePathSetting.getInstance()` / `getFileWithoutCreate` → s2で明示 ✅
8. `FileDataReader`/`FileBatchAction`がデータバインドと非互換 → architecture s7, s8で明示 ✅
9. プロパティは全String型（外部入力の場合） → s2で明示 ✅
10. `ObjectMapper`はスレッドアンセーフ → s21（CSVフォーマットセット）に「ObjectMapperの読み込み及び書き込みは、スレッドアンセーフ」と記載 ✅

verify_result = PASS

---

**結論**: NablarchバッチでCSVの各行をJava Beansとして読み込むには、**データバインド機能**（`@Csv`アノテーション + `ObjectMapperFactory`）を使った独自`DataReader`を実装し、`BatchAction.createReader`で返す。

**根拠**:

**ステップ1: Beanクラスの定義**

```java
@Csv(properties = {"code", "name"}, type = CsvType.CUSTOM)
@CsvFormat(charset = "UTF-8", fieldSeparator = ',',
        ignoreEmptyLine = true, lineSeparator = "\r\n", quote = '"',
        quoteMode = QuoteMode.NORMAL, requiredHeader = false, emptyToNull = true)
public class ZipCodeForm {
    private String code;  // 外部入力のため全てString型で定義
    private String name;

    // getter/setter

    private Long lineNumber;

    @LineNumber  // 行番号を自動設定したい場合
    public Long getLineNumber() { return lineNumber; }
}
```

`@Csv`でバインド対象プロパティとCSV型を、`@CsvFormat`でフォーマット詳細を指定する。標準フォーマット（`DEFAULT`/`RFC4180`/`EXCEL`/`TSV`）を使う場合は`@CsvFormat`を省略できる。

**ステップ2: DataReader の実装**

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
        File file = filePathSetting.getFileWithoutCreate("csv-input", "inputFileName");
        try {
            iterator = new ObjectMapperIterator<>(
                ObjectMapperFactory.create(ZipCodeForm.class, new FileInputStream(file)));
        } catch (FileNotFoundException e) {
            throw new IllegalStateException(e);
        }
    }
}
```

`ObjectMapperFactory.create(ZipCodeForm.class, inputStream)` でObjectMapperを生成し、`ObjectMapperIterator`（Exampleの実装を参照）でhasNext/nextインタフェースに変換する。

**ステップ3: BatchAction への組み込み**

```java
public class ImportZipCodeFileAction extends BatchAction<ZipCodeForm> {

    @Override
    public Result handle(ZipCodeForm inputData, ExecutionContext ctx) {
        // 1行分のデータに対する業務処理
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
- 外部ファイルの場合、Beanのプロパティは**全てString型**で定義すること（型変換失敗で異常終了しないため）
- 標準提供の`FileDataReader`・`FileBatchAction`は**データバインドと非互換**なので使用しないこと（これらは汎用データフォーマットを使用）
- `ObjectMapper`はスレッドアンセーフなため複数スレッドでの共有は不可

参照: libraries-data-bind.json:s7, libraries-data-bind.json:s15, nablarch-batch-getting-started-nablarch-batch.json:s2, nablarch-batch-getting-started-nablarch-batch.json:s3

---
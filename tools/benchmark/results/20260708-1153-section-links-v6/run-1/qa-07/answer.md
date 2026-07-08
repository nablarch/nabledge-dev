**結論:** データバインド機能（`@Csv` / `@CsvFormat` アノテーション + `ObjectMapperFactory`）を使い、`DataReader<T>` の実装クラスを作成する。`ObjectMapperFactory.create` でCSVを読み込み、1行ずつJava Beansとして `read` メソッドから返す。バッチアクション（`BatchAction` を継承）の `createReader` メソッドでそのリーダーを返すように実装する。

**根拠:**

**① フォームクラスに `@Csv` / `@CsvFormat` を付与する**

```java
@Csv(properties = {/** プロパティ定義 **/}, type = CsvType.CUSTOM)
@CsvFormat(charset = "UTF-8", fieldSeparator = ',',
        ignoreEmptyLine = true, lineSeparator = "\r\n", quote = '"',
        quoteMode = QuoteMode.NORMAL, requiredHeader = false, emptyToNull = true)
public class ZipCodeForm {

    @Domain("localGovernmentCode")
    @Required
    private String localGovernmentCode;

    private Long lineNumber;

    @LineNumber
    public Long getLineNumber() {
        return lineNumber;
    }
    // 他のセッタ・ゲッタは省略
}
```

ポイント：
- `@Csv` と `@CsvFormat` でCSVフォーマットを指定する
- `@LineNumber` をゲッタに付与すると行番号が自動セットされる
- バリデーション用アノテーション（`@Domain`, `@Required` など）を付与してBean Validationを実施できる

**② `DataReader<T>` を実装したリーダークラスを作成する**

```java
public class ZipCodeFileReader implements DataReader<ZipCodeForm> {

    private static final String FILE_NAME = "importZipCode";
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
        File file = filePathSetting.getFileWithoutCreate("csv-input", FILE_NAME);
        try {
            iterator = new ObjectMapperIterator<>(
                ObjectMapperFactory.create(ZipCodeForm.class, new FileInputStream(file)));
        } catch (FileNotFoundException e) {
            throw new IllegalStateException(e);
        }
    }
}
```

ポイント：
- `read` メソッドで1行分のJava Beansを返す（これが業務アクションに渡される）
- `hasNext` が `false` を返すとファイル読み込みが終了する
- `close` メソッドでストリームを閉じる

**③ `BatchAction` を継承したアクションクラスを作成する**

```java
public class ImportZipCodeFileAction extends BatchAction<ZipCodeForm> {

    @Override
    public Result handle(ZipCodeForm inputData, ExecutionContext ctx) {
        // 1行分のJava Beansに対する業務処理
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

また、`ObjectMapperFactory` を直接使う場合は次のパターンでも読み込み可能：

```java
try (ObjectMapper<Person> mapper = ObjectMapperFactory.create(Person.class, inputStream)) {
    Person person;
    while ((person = mapper.read()) != null) {
        // 1件ずつ処理
    }
}
```

**注意点:**
- 外部から受け付けたCSVデータを読み込む場合、フォームのプロパティは**全てString型**で定義しなければならない（不正な値でも異常終了させず業務エラーとして通知するため）
- 標準提供の `FileDataReader` および `FileBatchAction` は**汎用データフォーマットを使用しており、データバインドと併用できない**。データバインドを使う場合は `DataReader<T>` の独自実装と `BatchAction` を使うこと
- ストリームは必ず `close` メソッドでクローズすること（リソースリーク防止）

参照:
- ファイルをDBに登録するバッチの作成
  .claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.md
  入力データソースからデータを読み込む
  業務ロジックを実行する
- アーキテクチャ概要
  .claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-architecture.md
  Nablarchバッチアプリケーションで使用するデータリーダ
  Nablarchバッチアプリケーションで使用するアクション
- データバインド
  .claude/skills/nabledge-6/docs/component/libraries/libraries-data-bind.md
  データをJava Beansオブジェクトとして扱うことができる
  データをJava Beansオブジェクトとして読み込む
  CSVファイルのフォーマットを指定する
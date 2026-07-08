**結論**: NablarchバッチでCSVの各行をJava Beansとして1件ずつ読み込むには、`@Csv`/`@CsvFormat`アノテーションを付けたFormクラスを作成し、`DataReader<FormClass>`を実装して`ObjectMapperFactory.create()`でCSVを読み込む。

**根拠**:

**1. Formクラスの作成**（`@Csv`と`@CsvFormat`でフォーマットを指定）

```java
@Csv(properties = {"field1", "field2"}, type = CsvType.DEFAULT)
// フォーマットが標準セットに合わない場合は @CsvFormat で個別指定
@CsvFormat(charset = "UTF-8", fieldSeparator = ',',
        ignoreEmptyLine = true, lineSeparator = "\r\n", quote = '"',
        quoteMode = QuoteMode.NORMAL, requiredHeader = false, emptyToNull = true)
public class MyForm {
    @Required
    private String field1;
    private String field2;

    // getter/setter省略
}
```

**2. DataReaderの実装**（`ObjectMapperFactory.create()`でObjectMapperを生成し1行ずつ返す）

```java
public class MyFileReader implements DataReader<MyForm> {
    private ObjectMapperIterator<MyForm> iterator;

    @Override
    public MyForm read(ExecutionContext ctx) {
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
        File file = FilePathSetting.getInstance().getFileWithoutCreate("csv-input", "myFile");
        try {
            iterator = new ObjectMapperIterator<>(
                ObjectMapperFactory.create(MyForm.class, new FileInputStream(file)));
        } catch (FileNotFoundException e) {
            throw new IllegalStateException(e);
        }
    }
}
```

または、バッチ内でシンプルに全件読み込む場合のコード例:

```java
try (ObjectMapper<MyForm> mapper = ObjectMapperFactory.create(MyForm.class, inputStream)) {
    MyForm form;
    while ((form = mapper.read()) != null) {
        // 1件ずつ処理
    }
} catch (InvalidDataFormatException e) {
    // フォーマット不正時の処理
}
```

**3. BatchActionクラスの作成**

```java
public class MyBatchAction extends BatchAction<MyForm> {

    @Override
    public Result handle(MyForm inputData, ExecutionContext ctx) {
        // 1件分の業務処理を記述
        return new Result.Success();
    }

    @Override
    public DataReader<MyForm> createReader(ExecutionContext ctx) {
        return new MyFileReader();
    }
}
```

**注意点**:
- 標準の`FileDataReader`/`ValidatableFileDataReader`は汎用データフォーマットを使用するため、**データバインドを使う場合は使用しないこと**。`DataReader`インタフェースを直接実装すること。
- `ObjectMapper`は読み込み完了後に必ず`close()`すること（`try-with-resources`推奨）。
- 外部ファイルを読み込む場合、バリデーションエラーを業務エラーとして通知するためFormのプロパティは**全てString型**で定義すること。

参照:
- ファイルをDBに登録するバッチの作成
  .claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.md
  入力データソースからデータを読み込む
  業務ロジックを実行する
- データバインド
  .claude/skills/nabledge-6/docs/component/libraries/libraries-data-bind.md
  データをJava Beansオブジェクトとして読み込む
  CSVファイルのフォーマットを指定する
- アーキテクチャ概要
  .claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-architecture.md
  Nablarchバッチアプリケーションで使用するデータリーダ
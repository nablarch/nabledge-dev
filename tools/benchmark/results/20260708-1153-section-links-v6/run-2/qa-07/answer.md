**結論**: NablarchバッチでCSVファイルの各行をJava Beansとして読み込むには、データバインド機能を使い、①`@Csv`/`@CsvFormat`アノテーション付きのフォームクラス、②`DataReader<T>`実装のリーダークラス、③`BatchAction<T>`を継承したアクションクラスの3つを実装します。

**根拠**:

**①フォームクラス（CSVフォーマット定義）**

Java Beansクラスに `@Csv` と `@CsvFormat` を付与してCSVのフォーマットを指定します。バリデーション用アノテーションも付与できます。外部から受け付けるデータはプロパティをすべて `String` 型で定義してください。

```java
@Csv(type = Csv.CsvType.DEFAULT, properties = {"code", "name"}, headers = {"コード", "名前"})
public class MyDataForm {
    @Required
    private String code;
    private String name;

    // getter/setter は省略
}
```

カスタムフォーマット（文字コード・区切り文字など）が必要な場合は `@CsvFormat` を追加します：

```java
@Csv(type = Csv.CsvType.CUSTOM, properties = {"code", "name"})
@CsvFormat(charset = "UTF-8", fieldSeparator = ',',
        ignoreEmptyLine = true, lineSeparator = "\r\n", quote = '"',
        quoteMode = QuoteMode.NORMAL, requiredHeader = false, emptyToNull = true)
public class MyDataForm { ... }
```

**②データリーダークラス**

`DataReader<T>` を実装し、`ObjectMapperFactory.create()` で生成した `ObjectMapper` を使って1行ずつ読み込みます。

```java
public class MyDataReader implements DataReader<MyDataForm> {

    private ObjectMapperIterator<MyDataForm> iterator;

    @Override
    public MyDataForm read(ExecutionContext ctx) {
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
        iterator.close();  // リソース解放を必ず行う
    }

    private void initialize() {
        File file = FilePathSetting.getInstance()
                        .getFileWithoutCreate("csv-input", "myDataFile");
        try {
            iterator = new ObjectMapperIterator<>(
                ObjectMapperFactory.create(MyDataForm.class,
                    new FileInputStream(file)));
        } catch (FileNotFoundException e) {
            throw new IllegalStateException(e);
        }
    }
}
```

**③アクションクラス**

`BatchAction<T>` を継承し、`createReader()` でリーダーを返し、`handle()` で1行分のデータを処理します。

```java
public class MyBatchAction extends BatchAction<MyDataForm> {

    @Override
    public Result handle(MyDataForm inputData, ExecutionContext ctx) {
        // 1行分のデータに対する処理
        MyEntity entity = BeanUtil.createAndCopy(MyEntity.class, inputData);
        UniversalDao.insert(entity);
        return new Result.Success();
    }

    @Override
    public DataReader<MyDataForm> createReader(ExecutionContext ctx) {
        return new MyDataReader();
    }
}
```

**注意点**:
- `ObjectMapper#close()` を必ず呼び出してリソースを解放すること（`try-with-resources` 推奨）
- 外部から受け付けるデータのフォームプロパティはすべて `String` 型で定義すること（型変換失敗による異常終了を防ぐため）
- `ObjectMapper` はスレッドアンセーフのため、複数スレッドで共有しないこと

参照:
- ファイルをDBに登録するバッチの作成
  .claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.md
  入力データソースからデータを読み込む
  業務ロジックを実行する
- データバインド
  .claude/skills/nabledge-6/docs/component/libraries/libraries-data-bind.md
  データをJava Beansオブジェクトとして扱うことができる
  データをJava Beansオブジェクトとして読み込む
  CSVファイルのフォーマットを指定する
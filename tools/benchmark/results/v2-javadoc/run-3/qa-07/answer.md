セクション内容の読み込みが完了しました。回答に必要な情報が揃ったので、Step 5に進みます。

---

**結論**: NablarchのデータバインドライブラリとDataReader実装を組み合わせて実現します。Java BeanクラスにCSVフォーマットのアノテーションを定義し、`ObjectMapperFactory`で生成した`ObjectMapper`（または`ObjectMapperIterator`）で1行ずつ読み込みます。

**根拠**:

**① フォームクラス（Java Beans）を作成**

`@Csv`アノテーションでCSVフォーマットを指定します。

```java
@Csv(type = Csv.CsvType.CUSTOM, properties = {"field1", "field2"}, headers = {"フィールド1", "フィールド2"})
@CsvFormat(
    charset = "UTF-8",
    fieldSeparator = ',',
    ignoreEmptyLine = true,
    lineSeparator = "\r\n",
    quote = '"',
    quoteMode = CsvDataBindConfig.QuoteMode.NORMAL,
    requiredHeader = false,
    emptyToNull = true)
public class ZipCodeForm {
    private String field1;
    private String field2;

    // getter、setter省略
}
```

**② DataReader を実装してバッチへ渡す**

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
        File file = FilePathSetting.getInstance().getFileWithoutCreate("csv-input", "inputFile");
        try {
            iterator = new ObjectMapperIterator<>(
                ObjectMapperFactory.create(ZipCodeForm.class, new FileInputStream(file)));
        } catch (FileNotFoundException e) {
            throw new IllegalStateException(e);
        }
    }
}
```

**③ 業務アクションで1件ずつ処理**

```java
public class ImportAction extends BatchAction<ZipCodeForm> {

    @Override
    public Result handle(ZipCodeForm inputData, ExecutionContext ctx) {
        // inputData に1行分のデータが入っている
        MyEntity entity = BeanUtil.createAndCopy(MyEntity.class, inputData);
        UniversalDao.insert(entity);
        return new Result.Success();
    }

    @Override
    public DataReader<ZipCodeForm> createReader(ExecutionContext ctx) {
        return new ZipCodeFileReader();
    }
}
```

**注意点**:
- `ObjectMapper`のクローズ忘れに注意。`DataReader#close`内で`iterator.close()`を確実に呼ぶこと
- 外部から受け取るCSVファイルの場合、フォームのプロパティは**全てString型**で定義しなければならない（不正データでも業務エラーとして通知するため）
- `ObjectMapper`はスレッドアンセーフのため、複数スレッドからの共有は不可

参照: `libraries-data-bind.json:s7`, `libraries-data-bind.json:s15`, `nablarch-batch-getting-started-nablarch-batch.json:s2`, `nablarch-batch-getting-started-nablarch-batch.json:s3`

---
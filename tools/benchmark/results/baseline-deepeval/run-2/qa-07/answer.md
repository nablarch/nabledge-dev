Step 5〜8: 回答を生成し、検証します。

**結論の検証:**
- `ObjectMapperFactory#create` → s7に明記
- `ObjectMapper#read()` → s7に明記
- `@Csv` / `@CsvFormat` → s15に明記
- `DataReader<T>` / `read()` / `hasNext()` / `close()` → s2に明記
- `BatchAction<T>` の継承 → s3に明記
- `ObjectMapperIterator` → s2に明記
- プロパティを全てString型 → s2（外部ファイルの場合）に明記

全クレームはsections_contentで裏付けられており、verify_result = PASS。

---

**結論**: NablarchバッチでCSVをJava Beansオブジェクトとして1行ずつ読み込むには、データバインド機能（`@Csv`アノテーション + `ObjectMapper`）を使ったフォームクラスと`DataReader`実装クラスを作成し、`BatchAction`に連携させます。

**根拠**:

**① フォームクラス（Beansオブジェクト）を作成する**

```java
@Csv(type = Csv.CsvType.DEFAULT, properties = {"age", "name"}, headers = {"年齢", "氏名"})
public class PersonForm {
    private String age;   // 外部入力はString型で定義
    private String name;

    // getter、setterは省略
}
```

CSVフォーマットが標準形式（ヘッダあり、カンマ区切り、UTF-8）なら `CsvType.DEFAULT` を指定するだけでよい。独自フォーマットの場合は `CsvType.CUSTOM` + `@CsvFormat` で個別指定する。

**② DataReaderを実装する**

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
                        .getFileWithoutCreate("csv-input", "inputFile");
        try {
            iterator = new ObjectMapperIterator<>(
                ObjectMapperFactory.create(PersonForm.class, new FileInputStream(file)));
        } catch (FileNotFoundException e) {
            throw new IllegalStateException(e);
        }
    }
}
```

**③ BatchActionを作成する**

```java
public class PersonBatchAction extends BatchAction<PersonForm> {

    @Override
    public Result handle(PersonForm inputData, ExecutionContext ctx) {
        // inputData に1行分のデータがセットされている
        return new Result.Success();
    }

    @Override
    public DataReader<PersonForm> createReader(ExecutionContext ctx) {
        return new PersonFileReader();
    }
}
```

`read()` が呼ばれるたびに1行分のBeansオブジェクトが `handle()` へ渡される。`hasNext()` が `false` を返すと処理が終了する。

**注意点**:
- 外部から受け付けたCSVファイルを読み込む場合、Beansクラスのプロパティは**全てString型**で定義しなければならない（型変換失敗時に異常終了させないため）
- `ObjectMapper` はスレッドアンセーフなため、複数スレッドでインスタンスを共有しないこと
- `ObjectMapper` の使用後は必ずクローズすること（`try-with-resources` 推奨）
- モジュール `nablarch-common-databind` への依存が必要

参照: libraries-data-bind.json:s7, libraries-data-bind.json:s15, nablarch-batch-getting-started-nablarch-batch.json:s2, nablarch-batch-getting-started-nablarch-batch.json:s3, libraries-data-bind.json:s2

---
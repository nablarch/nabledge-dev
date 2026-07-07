# qa-07 — run-2

## 質問

CSVファイルの各行をJava Beansオブジェクトとして1件ずつ読み込みたい。どう実装する？

## 回答

**結論**: NablarchバッチでCSVを1行ずつJava Beansとして読み込むには、**データバインド機能**を使用する。Formクラスに `@Csv` / `@CsvFormat` アノテーションを付与し、`DataReader` 実装クラス内で `ObjectMapperFactory.create()` が生成した `ObjectMapper` の `read()` を呼び出す。

**根拠**:

**① Formクラスの作成（CSVフォーマット定義）**

```java
@Csv(type = Csv.CsvType.CUSTOM, properties = {"localGovernmentCode", "zipCode5digit"})
@CsvFormat(charset = "UTF-8", fieldSeparator = ',',
        ignoreEmptyLine = true, lineSeparator = "\r\n", quote = '"',
        quoteMode = QuoteMode.NORMAL, requiredHeader = false, emptyToNull = true)
public class ZipCodeForm {

    @Domain("localGovernmentCode")
    @Required
    private String localGovernmentCode;  // プロパティは全てString型

    private String zipCode5digit;

    private Long lineNumber;

    @LineNumber  // 行番号を自動設定
    public Long getLineNumber() { return lineNumber; }

    // getter/setter省略
}
```

**② DataReader実装クラスの作成**

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
        File csvFile = filePathSetting.getFileWithoutCreate("csv-input", "importZipCode");
        try {
            iterator = new ObjectMapperIterator<>(
                ObjectMapperFactory.create(ZipCodeForm.class, new FileInputStream(csvFile)));
        } catch (FileNotFoundException e) {
            throw new IllegalStateException(e);
        }
    }
}
```

**③ BatchActionの作成**

```java
public class ImportZipCodeFileAction extends BatchAction<ZipCodeForm> {

    @Override
    public Result handle(ZipCodeForm inputData, ExecutionContext ctx) {
        // inputDataに1行分のデータが渡される
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

`ObjectMapper` を直接使う場合（DataReader不要の場合）は次のように書ける：

```java
try (ObjectMapper<Person> mapper = ObjectMapperFactory.create(Person.class, inputStream)) {
    Person person;
    while ((person = mapper.read()) != null) {
        // 1件ずつ処理
    }
} catch (InvalidDataFormatException e) {
    // フォーマット不正時の処理
}
```

**注意点**:
- 外部から受け付けたデータ（CSVファイル）を読み込む場合、Formのプロパティは**全てString型**で定義すること。型変換失敗時に異常終了ではなく業務エラーとして通知するため。
- `ObjectMapper` のリソース解放を忘れないよう、`try-with-resources` を使用すること。

参照: libraries-data-bind.json:s7, libraries-data-bind.json:s15, libraries-data-bind.json:s2, nablarch-batch-getting-started-nablarch-batch.json:s2, nablarch-batch-getting-started-nablarch-batch.json:s3

## 参照ナレッジ

- [データをJava Beansオブジェクトとして読み込む](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-data-bind.md#データをjava-beansオブジェクトとして読み込む) (s7)
- [CSVファイルのフォーマットを指定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-data-bind.md#csvファイルのフォーマットを指定する) (s15)
- [データをJava Beansオブジェクトとして扱うことができる](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-data-bind.md#データをjava-beansオブジェクトとして扱うことができる) (s2)
- [入力データソースからデータを読み込む](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.md#入力データソースからデータを読み込む) (s2)
- [業務ロジックを実行する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.md#業務ロジックを実行する) (s3)
- [ファイル入出力](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-feature-details.md#ファイル入出力) (s5)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output explicitly mentions using `ObjectMapperFactory.create()` to generate an `ObjectMapper` and calling its `read()` method to read data, which directly corresponds to the Expected Output's fact about using `ObjectMapperFactory#create` to generate an `ObjectMapper` for reading data. The key fact is fully covered. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant, directly addressing how to read each row of a CSV file as Java Beans objects one by one. No irrelevant statements were detected! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「ObjectMapperFactory#createで生成したObjectMapperを使用してデータを読み込む」は回答の「`ObjectMapperFactory.create()` が生成した `ObjectMapper` の `read()` を呼び出す」および②のコード例に含まれている |
| answer_relevancy | — | —
| faithfulness | — | —

### 参照事実（expected_facts）

- ObjectMapperFactory#createで生成したObjectMapperを使用してデータを読み込む

# qa-07 — run-3

## 質問

CSVファイルの各行をJava Beansオブジェクトとして1件ずつ読み込みたい。どう実装する？

## 回答

**結論**: データバインド機能の`ObjectMapperFactory`で生成した`ObjectMapper`を使い、`@Csv`アノテーションを付与したJava BeansクラスにCSV行をバインドしながら1件ずつ読み込む。独自の`DataReader`実装クラスを作成し、`BatchAction`の`handle`メソッドで1件ずつ処理する。

**根拠**:

**1. フォームクラスの作成（CSVフォーマット定義）**

`@Csv`と`@CsvFormat`アノテーションでCSVフォーマットを定義したJava Beansクラスを作成する。

```java
@Csv(properties = {"localGovernmentCode", "zipCode"}, type = CsvType.CUSTOM)
@CsvFormat(charset = "UTF-8", fieldSeparator = ',',
        ignoreEmptyLine = true, lineSeparator = "\r\n", quote = '"',
        quoteMode = QuoteMode.NORMAL, requiredHeader = false, emptyToNull = true)
public class ZipCodeForm {

    @Required
    private String localGovernmentCode;
    private String zipCode;

    // 行番号を取得したい場合はこのように定義
    private Long lineNumber;
    @LineNumber
    public Long getLineNumber() { return lineNumber; }

    // getter/setter省略
}
```

`@Csv(type = Csv.CsvType.DEFAULT)` で標準のCSVフォーマット（カンマ区切り、ヘッダあり、UTF-8）を使うこともできる。

**2. データリーダの作成**

`DataReader<フォームクラス>`インタフェースを実装し、`ObjectMapperFactory.create`で`ObjectMapper`を生成してCSVを1行ずつ提供する。

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
        File csvFile = FilePathSetting.getInstance()
                .getFileWithoutCreate("csv-input", "importZipCode");
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

**3. 業務アクションの作成**

`BatchAction<フォームクラス>`を継承し、`handle`メソッドで1件ずつ処理する。`createReader`でデータリーダを返す。

```java
public class ImportZipCodeFileAction extends BatchAction<ZipCodeForm> {

    @Override
    public Result handle(ZipCodeForm inputData, ExecutionContext ctx) {
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
- 標準提供の`FileDataReader`・`ValidatableFileDataReader`は内部で汎用データフォーマットを使用するため、データバインドと組み合わせて使用してはならない。CSVをデータバインドで読む場合は上記のように独自`DataReader`を実装すること。
- 全データ読み込み後は`ObjectMapper#close`でリソースを解放すること（`try-with-resources`推奨）。
- アップロードファイルなど外部から受け付けるデータを読み込む場合は、Java Beansクラスのプロパティを**全てString型**で定義しなければならない（型変換失敗時に異常終了させないため）。

参照: `component/libraries/libraries-data-bind.json:s7`, `component/libraries/libraries-data-bind.json:s15`, `processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.json:s2`, `processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.json:s3`, `processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s7`

## 参照ナレッジ

- [データをJava Beansオブジェクトとして読み込む](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-data-bind.md#データをjava-beansオブジェクトとして読み込む) (s7)
- [CSVファイルのフォーマットを指定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-data-bind.md#csvファイルのフォーマットを指定する) (s15)
- [入力データソースからデータを読み込む](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.md#入力データソースからデータを読み込む) (s2)
- [業務ロジックを実行する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.md#業務ロジックを実行する) (s3)
- [Nablarchバッチアプリケーションで使用するデータリーダ](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-architecture.md#nablarchバッチアプリケーションで使用するデータリーダ) (s7)
- [ファイルのデータの論理行番号を取得する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-data-bind.md#ファイルのデータの論理行番号を取得する) (s11)
- [データをJava Beansオブジェクトとして扱うことができる](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-data-bind.md#データをjava-beansオブジェクトとして扱うことができる) (s2)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output explicitly mentions using `ObjectMapperFactory.create` to generate an `ObjectMapper` for reading data, which directly corresponds to the Expected Output's fact about using `ObjectMapperFactory#create` to generate an `ObjectMapper` for data reading. The fact is covered clearly and with equivalent meaning in the Actual Output. |
| answer_relevancy | 0.95 | 0.96 | OK | The score is 0.96 because the response is highly relevant to explaining how to read CSV rows as Java Beans objects, with only a minor detraction where it briefly describes specific business logic involving data copying and insertion via UniversalDao, which goes slightly beyond the scope of the question. Overall, the response addresses the implementation question well. |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「ObjectMapperFactory#createで生成したObjectMapperを使用してデータを読み込む」は回答の「`ObjectMapperFactory.create`で`ObjectMapper`を生成してCSVを1行ずつ提供する」および`iterator = new ObjectMapperIterator<>(ObjectMapperFactory.create(ZipCodeForm.class, new FileInputStream(csvFile))))`のコード例に含まれている |
| answer_relevancy | OK | 回答はCSVファイルの各行をJava Beansオブジェクトとして1件ずつ読み込む実装方法に直接答えており、フォームクラスの作成・DataReaderの実装・BatchActionの作成という3ステップで構成されている。handleメソッド内のBeanUtil.createAndCopyやUniversalDao.insertは純粋なCSV読み込みの範囲をわずかに超えるが、バッチ処理の完全な動作例として文脈上適切であり、的外れな内容とは言えない。 |
| faithfulness | OK | 回答の内容はナレッジMDの記述と矛盾していない。ObjectMapperFactory#createでObjectMapperを生成してデータを読み込む方法（s7）、@Csvと@CsvFormatアノテーションによるフォーマット指定（s15）、全データ読み込み後のObjectMapper#closeによるリソース解放、try-with-resourcesの推奨、外部から受け付けるデータの場合にプロパティを全てString型で定義する必要性（ナレッジのImportantノート）、いずれもナレッジの内容と一致している。ObjectMapperIteratorはナレッジに明示されていないが、ナレッジの記述と矛盾するものではない。 |

### 参照事実（expected_facts）

- ObjectMapperFactory#createで生成したObjectMapperを使用してデータを読み込む

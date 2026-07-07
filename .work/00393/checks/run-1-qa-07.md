# qa-07 — run-1

## 質問

CSVファイルの各行をJava Beansオブジェクトとして1件ずつ読み込みたい。どう実装する？

## 回答

**結論**: NablarchバッチでCSVの各行をJava Beansとして1件ずつ読み込むには、`@Csv`/`@CsvFormat` アノテーションでフォーマットを定義したフォームクラスと、`ObjectMapperFactory`・`DataReader` を使ったリーダクラスを作成し、`BatchAction` の `createReader` メソッドで返却します。

**根拠**:

**① フォームクラスの作成（CSVフォーマット定義）**

```java
@Csv(properties = {"localGovernmentCode", "zipCode5digit"}, type = CsvType.CUSTOM)
@CsvFormat(charset = "UTF-8", fieldSeparator = ',',
        ignoreEmptyLine = true, lineSeparator = "\r\n", quote = '"',
        quoteMode = QuoteMode.NORMAL, requiredHeader = false, emptyToNull = true)
public class ZipCodeForm {

    @Domain("localGovernmentCode")
    @Required
    private String localGovernmentCode;

    // 行番号を取得したい場合
    private Long lineNumber;

    @LineNumber
    public Long getLineNumber() {
        return lineNumber;
    }

    // getter/setter省略
}
```

ポイント：
- `@Csv` と `@CsvFormat` でCSVのフォーマットをアノテーションで指定
- 外部から受け付けるデータのため、**プロパティは全てString型**で定義すること（型変換失敗時の異常終了を防ぐため）
- `@LineNumber` を付与したgetterを定義すると論理行番号を自動取得可能

**② データリーダの作成**

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
        iterator.close();  // リソース解放
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

ポイント：
- `DataReader<T>` を実装し、`read` で1件、`hasNext` で次行有無、`close` でリソース解放
- `ObjectMapperFactory.create(フォームクラス, InputStream)` でObjectMapperを生成
- `hasNext` が `false` を返すと読み込み終了

**③ 業務アクションの作成**

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

**直接ObjectMapperを使う場合（DataReader不要のシンプルなケース）**

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
- `ObjectMapper` はスレッドアンセーフのため、複数スレッドから共有して呼び出す場合は呼び出し元で同期すること
- 読み込み完了後は必ず `ObjectMapper#close` でリソースを解放すること（`try-with-resources` 推奨）
- フォームのプロパティを全てString型にしておかないと、不正データで型変換失敗時に異常終了になる

参照: nablarch-batch-getting-started-nablarch-batch.json:s2, nablarch-batch-getting-started-nablarch-batch.json:s3, libraries-data-bind.json:s7, libraries-data-bind.json:s15, libraries-data-bind.json:s2

## 参照ナレッジ

- [入力データソースからデータを読み込む](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.md#入力データソースからデータを読み込む) (s2)
- [業務ロジックを実行する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.md#業務ロジックを実行する) (s3)
- [データをJava Beansオブジェクトとして読み込む](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-data-bind.md#データをjava-beansオブジェクトとして読み込む) (s7)
- [CSVファイルのフォーマットを指定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-data-bind.md#csvファイルのフォーマットを指定する) (s15)
- [データをJava Beansオブジェクトとして扱うことができる](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-data-bind.md#データをjava-beansオブジェクトとして扱うことができる) (s2)
- [ファイル入出力](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-feature-details.md#ファイル入出力) (s5)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output explicitly covers the key fact from the Expected Output: using ObjectMapperFactory#create to generate an ObjectMapper for reading data. This is shown in the code example with `ObjectMapperFactory.create(ZipCodeForm.class, new FileInputStream(csvFile))` and the direct usage example `ObjectMapperFactory.create(Person.class, inputStream)`. The expected fact is fully addressed. |
| answer_relevancy | 0.95 | 0.95 | NG | The score is 0.95 because the response is largely relevant and effectively addresses how to read CSV rows as Java Bean objects. However, it loses a small amount of points for including an unrelated mention of inserting data with UniversalDao, which is a post-processing step that goes beyond the scope of the question asked. |
| faithfulness | 0.99 | 0.95 | NG | The score is 0.95 because the actual output incorrectly suggests calling mapper.read() until it returns null as a simpler alternative for DataReader implementation, whereas the retrieval context states that ObjectMapper does not have a hasNext method and recommends using ObjectMapperIterator to simplify the implementation instead. |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「ObjectMapperFactory#createで生成したObjectMapperを使用してデータを読み込む」は回答の「ObjectMapperFactory.create(ZipCodeForm.class, new FileInputStream(csvFile))」および「ObjectMapperFactory.create(Person.class, inputStream)」に明示されている |
| answer_relevancy | NG | 回答末尾に「参照: nablarch-batch-getting-started-nablarch-batch.json:s2, nablarch-batch-getting-started-nablarch-batch.json:s3, libraries-data-bind.json:s7, libraries-data-bind.json:s15, libraries-data-bind.json:s2」という内部参照記法がユーザー向け回答に含まれており不適切 |
| faithfulness | OK | 回答の「直接ObjectMapperを使う場合」セクションで示す `while ((person = mapper.read()) != null)` パターンはナレッジ s7（データをJava Beansオブジェクトとして読み込む）に明示されており矛盾なし。DataReader実装ではObjectMapperIteratorを正しく使用しており、ナレッジのTip（ObjectMapperはhasNextを持たないためイテレータ推奨）とも整合している |

### 参照事実（expected_facts）

- ObjectMapperFactory#createで生成したObjectMapperを使用してデータを読み込む

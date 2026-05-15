**結論**: DBからデータを読み込んで集計し、別テーブルに書き込む定期処理は、**Jakarta Batchの Chunk タイプ**で実装します。`ItemReader`（DB読み込み）→ `ItemProcessor`（集計ロジック）→ `ItemWriter`（DB書き込み）の3コンポーネント構成が基本形です。

**根拠**:

### 全体構成

```
ItemReader           ItemProcessor         ItemWriter
(DBからSELECT)  →   (集計・計算ロジック)  →  (別テーブルにINSERT)
UniversalDao.defer()                         UniversalDao.batchInsert()
```

Jakarta Batch の仕様上、「DBなどの入力データソースからレコードを読み込み業務処理を実行する場合」はChunkタイプが適切です。

### 1. ItemReader（DB読み込み）

`AbstractItemReader` を継承し、`UniversalDao.defer()` で遅延ロードします。大量データ処理でもメモリを逼迫させないために `defer()` は必須です。

```java
@Dependent
@Named
public class MyDataReader extends AbstractItemReader {
    private DeferredEntityList<InputForm> list;
    private Iterator<InputForm> iterator;

    @Override
    public void open(Serializable checkpoint) throws Exception {
        list = (DeferredEntityList<InputForm>) UniversalDao.defer()
                .findAllBySqlFile(InputForm.class, "SELECT_TARGET_DATA");
        iterator = list.iterator();
    }

    @Override
    public Object readItem() {
        if (iterator.hasNext()) return iterator.next();
        return null;
    }

    @Override
    public void close() throws Exception {
        list.close();
    }
}
```

### 2. ItemProcessor（集計ロジック）

`ItemProcessor` を実装します。永続化処理はここに書かず、集計結果エンティティを返すだけにします。

```java
@Dependent
@Named
public class AggregateProcessor implements ItemProcessor {
    @Override
    public Object processItem(Object item) {
        InputForm form = (InputForm) item;
        ResultEntity result = new ResultEntity();
        result.setSummaryValue(calculateSummary(form));
        return result;
    }
}
```

### 3. ItemWriter（別テーブルへの書き込み）

`AbstractItemWriter` を継承し、`UniversalDao.batchInsert()` で一括登録します。

```java
@Dependent
@Named
public class ResultWriter extends AbstractItemWriter {
    @Override
    public void writeItems(List<Object> items) {
        UniversalDao.batchInsert(items);
    }
}
```

`writeItems` 実行後にトランザクションがコミットされ、次の `readItem` から処理が繰り返されます。

### 4. JOB設定ファイル

`/src/main/resources/META-INF/batch-jobs/` 配下に配置します。

```xml
<job id="aggregate-job" xmlns="https://jakarta.ee/xml/ns/jakartaee" version="2.0">
  <listeners>
    <listener ref="nablarchJobListenerExecutor" />
  </listeners>
  <step id="step1">
    <listeners>
      <listener ref="nablarchStepListenerExecutor" />
      <listener ref="nablarchItemWriteListenerExecutor" />
    </listeners>
    <chunk item-count="1000">
      <reader ref="myDataReader" />
      <processor ref="aggregateProcessor" />
      <writer ref="resultWriter" />
    </chunk>
  </step>
</job>
```

`item-count` で `writeItems` 一回あたりの処理件数を設定します（例: 1000件ごとにコミット）。

### 起動方法（定期処理）

**都度起動バッチ**を使用します。日次・月次などの定期実行はジョブスケジューラ（cronなど）からプロセスを都度起動する方式です。

**注意点**:

- `UniversalDao.defer()` でサーバサイドカーソルを使用するため、**`DeferredEntityList.close()` を必ず呼び出す**こと（`try-with-resources` 推奨）
- RDBMSによっては、**カーソルオープン中のトランザクション制御でカーソルがクローズされる**場合がある。中間コミットが必要な場合はDBベンダーのマニュアルを確認するか、ページングで回避すること
- `batchUpdate` による一括更新は**排他制御が行われない**。バージョン不一致のレコードは更新されずに正常終了するため、排他制御が必要な場合は1レコードずつ更新すること

参照: `guide/nablarch-patterns/nablarch-patterns-Nablarchバッチ処理パターン.json#s4`, `processing-pattern/jakarta-batch/jakarta-batch-getting-started-chunk.json#s1`, `processing-pattern/jakarta-batch/jakarta-batch-getting-started-chunk.json#s2`, `processing-pattern/jakarta-batch/jakarta-batch-getting-started-chunk.json#s3`, `processing-pattern/jakarta-batch/jakarta-batch-getting-started-chunk.json#s4`, `processing-pattern/jakarta-batch/jakarta-batch-getting-started-chunk.json#s5`, `component/libraries/libraries-universal-dao.json#s9`, `component/libraries/libraries-universal-dao.json#s14`
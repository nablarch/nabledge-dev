**結論**: DBからデータを読み込んで集計し別テーブルに書き込む定期処理は、**Jakarta BatchのChunkステップ方式**（DB to DBパターン）で実装する。`ItemReader`でDB読み込み、`ItemProcessor`で集計ロジック、`ItemWriter`でDB書き込みの3クラスに責務を分割する。

**根拠**:

**処理方式の選択**

Jakarta Batchには `Batchlet`（タスク指向）と `Chunk`（レコード反復処理）の2種類がある。DBからレコードを読み込んで業務処理を実行する場合は **Chunk** を使用する。日次・月次など定期起動には **都度起動バッチ** が適合する。

**クラス構成（DB to DBパターン）**

| クラス | 責務 |
|---|---|
| `ItemReader` | DBから処理対象データを遅延ロードして1件ずつ返す |
| `ItemProcessor` | 読み込んだデータで集計ロジックを実行し出力エンティティを生成する |
| `ItemWriter` | エンティティのリストを書き込み先テーブルに一括登録する |

**実装例（賞与計算バッチの例）**

```java
// ItemReader — BaseDatabaseItemReaderを継承（DB入力時はこちらを使用）
@Dependent @Named
public class EmployeeSearchReader extends BaseDatabaseItemReader {
    private DeferredEntityList<EmployeeForm> list;
    private Iterator<EmployeeForm> iterator;

    @Override
    public void doOpen(Serializable checkpoint) throws Exception {
        list = (DeferredEntityList<EmployeeForm>) UniversalDao.defer()
                .findAllBySqlFile(EmployeeForm.class, "SELECT_EMPLOYEE");
        iterator = list.iterator();
    }
    @Override
    public Object readItem() {
        return iterator.hasNext() ? iterator.next() : null;
    }
    @Override
    public void doClose() throws Exception { list.close(); }
}

// ItemProcessor — 集計ロジックを実行してエンティティを返す
@Dependent @Named
public class BonusCalculateProcessor implements ItemProcessor {
    @Override
    public Object processItem(Object item) {
        EmployeeForm form = (EmployeeForm) item;
        Bonus bonus = new Bonus();
        bonus.setEmployeeId(form.getEmployeeId());
        bonus.setPayments(calculateBonus(form));
        return bonus;
    }
}

// ItemWriter — UniversalDao.batchInsertで一括登録
@Dependent @Named
public class BonusWriter extends AbstractItemWriter {
    @Override
    public void writeItems(List<Object> items) {
        UniversalDao.batchInsert(items);
    }
}
```

**JOB定義ファイル**

```xml
<job id="bonus-calculate" xmlns="https://jakarta.ee/xml/ns/jakartaee" version="2.0">
  <listeners>
    <listener ref="nablarchJobListenerExecutor" />
  </listeners>
  <step id="step1">
    <listeners>
      <listener ref="nablarchStepListenerExecutor" />
      <listener ref="nablarchItemWriteListenerExecutor" />
    </listeners>
    <chunk item-count="1000">
      <reader ref="employeeSearchReader" />
      <processor ref="bonusCalculateProcessor" />
      <writer ref="bonusWriter" />
    </chunk>
  </step>
</job>
```

**注意点**:
1. DB入力時は `BaseDatabaseItemReader` を継承すること。
2. 大量データは `UniversalDao.defer()` で遅延ロードすること。
3. `ItemProcessor` 内でDB書き込みを行わないこと。
4. DB to DBパターンでは1レコードの処理中の更新が全て同一トランザクション下で実行される。
5. リスナー構成として最低限、`DbConnectionManagementListener`、`StepTransactionManagementListener`、`ItemWriteTransactionManagementListener` が必要。

参照: `processing-pattern/jakarta-batch/jakarta-batch-getting-started-chunk.json#s1`, `#s2`, `#s3`, `#s4`, `#s5`, `processing-pattern/jakarta-batch/jakarta-batch-database-reader.json`, `processing-pattern/jakarta-batch/jakarta-batch-architecture.json#s2`, `#s9`, `#s10`, `guide/nablarch-patterns/nablarch-patterns-Nablarchバッチ処理パターン.json#s4`
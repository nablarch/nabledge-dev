**結論**: DBからデータを集計して別テーブルに書き込む定期処理は、Jakarta Batch の **Chunkステップ**（都度起動バッチ）で実装するのが標準的な構成です。

**根拠**:

Jakarta Batch の Chunkステップは、ItemReader・ItemProcessor・ItemWriter の3役割で構成されます。

**実装クラスの構成**

| クラス | 役割 |
|--------|------|
| `BaseDatabaseItemReader` を継承した ItemReader | DBから集計対象データを読み込む |
| ItemProcessor | レコード単位の集計ロジックを実行 |
| ItemWriter | 集計結果を別テーブルに書き込む |

**ItemReader の実装例**（`BaseDatabaseItemReader` を使用）:

```java
@Dependent
@Named
public class SalesDataReader extends BaseDatabaseItemReader {

    private DeferredEntityList<SalesForm> list;
    private Iterator<SalesForm> iterator;
    private final ProgressManager progressManager;

    @Inject
    public SalesDataReader(ProgressManager progressManager) {
        this.progressManager = progressManager;
    }

    @Override
    public void doOpen(Serializable checkpoint) throws Exception {
        // 処理件数を進捗管理に設定（大量データは遅延ロードを使用）
        progressManager.setInputCount(
            UniversalDao.countBySqlFile(SalesForm.class, "SELECT_SALES"));

        list = (DeferredEntityList<SalesForm>) UniversalDao.defer()
                .findAllBySqlFile(SalesForm.class, "SELECT_SALES");
        iterator = list.iterator();
    }

    @Override
    public Object readItem() {
        if (iterator.hasNext()) {
            return iterator.next();
        }
        return null;  // データ終端でnullを返す
    }

    @Override
    public void doClose() throws Exception {
        list.close();
    }
}
```

**注意点**:
- DBを入力とする場合、Jakarta Batch 標準のリーダではなく **`BaseDatabaseItemReader`** を実装すること。これにより、トランザクション制御時にカーソルが自動クローズされるDBでも Chunkステップを安定動作させられる
- 大量データ取得時はヒープ圧迫を防ぐため `UniversalDao.defer()` で**遅延ロード**を使用すること
- 定期実行（日次・月次など）の場合は**都度起動バッチ**として構成する。常駐バッチは推奨されない（マルチスレッド時に処理遅延スレッドが他スレッドをブロックする問題があるため）

**バッチ起動方法**:

```bash
mvn exec:java -Dexec.mainClass=nablarch.fw.batch.ee.Main \
    -Dexec.args=your-job-name
```

参照: `processing-pattern/jakarta-batch/jakarta-batch-database-reader.json`、`processing-pattern/jakarta-batch/jakarta-batch-getting-started-chunk.json`、`processing-pattern/nablarch-batch/nablarch-batch-architecture.json`
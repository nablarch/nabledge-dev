**結論**: Jakarta Batch の **Chunk型バッチ（都度起動）** で実装します。DB to DB パターンに該当し、`ItemReader` でDB読み込み、`ItemProcessor` で集計ロジック、`ItemWriter` で別テーブルへの書き込みを担当します。

**根拠**:

### 起動方式の選択

定期処理（日次・月次など）には **都度起動バッチ** を使用します。プロセスをその都度起動して処理するため、定期スケジューラ（cronなど）との組み合わせに適しています。

### 処理パターン

入力がDB、出力が別テーブル（DB）なので **DB to DB パターン** に該当します。

> 1レコードの処理中に行われる更新は全て同一トランザクション下で実行されるため、障害発生時でも不整合が発生しません

### クラス構成（Chunkステップ）

| クラス | 役割 |
|--------|------|
| `ItemReader` | SELECT文でDBからレコードを1件ずつ読み込む |
| `ItemProcessor` | 業務ロジック（集計処理）を実行し、エンティティに変換する |
| `ItemWriter` | 集計結果を別テーブルに一括登録する |
| フォーム | ItemReader→ItemProcessor 間のデータ受け渡し用 |
| エンティティ | 書き込み先テーブルとの1対1マッピング |

### ItemReader の実装例

```java
@Dependent
@Named
public class SourceDataReader extends AbstractItemReader {
    private DeferredEntityList<SourceForm> list;
    private Iterator<SourceForm> iterator;

    @Override
    public void open(Serializable checkpoint) throws Exception {
        // 大量データはdeferで遅延ロードしてメモリ逼迫を防ぐ
        list = (DeferredEntityList<SourceForm>) UniversalDao.defer()
                .findAllBySqlFile(SourceForm.class, "SELECT_SOURCE");
        iterator = list.iterator();
    }

    @Override
    public Object readItem() {
        if (iterator.hasNext()) { return iterator.next(); }
        return null;
    }

    @Override
    public void close() throws Exception { list.close(); }
}
```

### ItemWriter の実装例

```java
@Dependent
@Named
public class ResultWriter extends AbstractItemWriter {
    @Override
    public void writeItems(List<Object> items) {
        // エンティティのリストを別テーブルへ一括登録
        UniversalDao.batchInsert(items);
    }
}
```

> `writeItems` メソッド実行後にトランザクションがコミットされ、新たなトランザクションが開始されます。

### 処理フロー

Chunk型の処理は次のように繰り返されます:
1. `ItemReader#readItem` → 1レコード読み込み
2. `ItemProcessor#processItem` → 集計ロジック実行・エンティティ変換
3. チャンクサイズ分たまったら `ItemWriter#writeItems` → DB書き込み＋コミット
4. 入力データが終わるまで1〜3を繰り返す

**注意点**:
- 大量データを読み込む場合は `UniversalDao.defer()` で遅延ロードを使用してください。通常の `findAll` だと全件をメモリに展開してOOMになる危険があります
- `ItemProcessor` 内でDBへの書き込み・更新を行わないでください。書き込みは必ず `ItemWriter` で行います（Chunkのトランザクション境界を守るため）
- Batchlet型（タスク指向）はSQL1本で完結するような処理向けです。レコードを1件ずつ読み込んで処理する場合は Chunk型を選択してください

参照: `guide/nablarch-patterns/nablarch-patterns-Nablarchバッチ処理パターン.json#s1`, `guide/nablarch-patterns/nablarch-patterns-Nablarchバッチ処理パターン.json#s2`, `guide/nablarch-patterns/nablarch-patterns-Nablarchバッチ処理パターン.json#s4`, `processing-pattern/jakarta-batch/jakarta-batch-getting-started-chunk.json#s1`, `processing-pattern/jakarta-batch/jakarta-batch-getting-started-chunk.json#s2`, `processing-pattern/jakarta-batch/jakarta-batch-getting-started-chunk.json#s4`, `processing-pattern/jakarta-batch/jakarta-batch-application-design.json#s2`, `processing-pattern/jakarta-batch/jakarta-batch-architecture.json#s2`, `processing-pattern/jakarta-batch/jakarta-batch-architecture.json#s5`
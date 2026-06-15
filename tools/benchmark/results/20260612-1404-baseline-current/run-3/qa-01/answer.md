**結論**: NablarchバッチのデフォルトデータリーダーであるDatabaseRecordReader は初回読み込み時に全レコードをキャッシュするため、大量データではメモリ不足になり得ます。メモリ効率を上げるには、`createReader` で主キーのみ取得し、`handle` メソッド内で1件ずつ完全なレコードを取得するパターンを使います。

**根拠**:

DatabaseRecordReader の `read` メソッドの仕様（Javadoc）:
> 初回読み込み時にデータベースからレコードを取得し、キャッシュする。レコードはそのキャッシュから返却する。

つまり、全件がメモリ上にキャッシュされます。

**推奨パターン（主キーのみリーダー）**:

悲観的ロックのドキュメントに示されているパターンが、大量データ処理でも有効です。

```java
public class SampleAction extends BatchAction<SqlRow> {

    @Override
    public DataReader<SqlRow> createReader(final ExecutionContext ctx) {
        final DatabaseRecordReader reader = new DatabaseRecordReader();
        final SqlPStatement statement = DbConnectionContext.getConnection()
                .prepareParameterizedSqlStatementBySqlId(
                        Project.class.getName() + "#GET_ID");  // 主キーのみ取得するSQL

        reader.setStatement(statement, condition);
        return reader;
    }

    @Override
    public Result handle(final SqlRow inputData, final ExecutionContext ctx) {
        // handle 内で主キーを使って1件ずつ完全なレコードを取得
        final Project project =
                UniversalDao.findBySqlFile(Project.class, "FIND_BY_ID", inputData);

        // 業務処理
        UniversalDao.update(project);
        return new Success();
    }
}
```

**ポイント**:
- `createReader` の SQL は主キーのみを返すようにする（キャッシュするデータ量を最小化）
- `handle` 内で主キーを使って1件ずつ完全なレコードを取得して処理する

**注意点**:
- 標準の `DatabaseRecordReader` では真のカーソルストリーミングはできません。主キーのみ取得パターンでもキャッシュ自体は発生しますが、データ量が大幅に減ります。
- 標準データリーダーで要件を満たせない場合は、`DataReader` インタフェースを実装したカスタムクラスをプロジェクトで作成して対応することも可能です。

参照: nablarch-batch-architecture.json:s7, javadoc-nablarch-fw-reader-DatabaseRecordReader.json:s10, nablarch-batch-nablarch-batch-pessimistic-lock.json
**結論**: NablarchバッチアクションはBatchActionクラスを継承し、`createReader`メソッドと`handle`メソッドを実装することで作成する。

**根拠**:

### 標準アクションクラスの種類

Nablarchバッチでは用途に応じて以下の標準アクションクラスを選択する:

| クラス | 用途 |
|---|---|
| `BatchAction` | 汎用バッチアクションテンプレート |
| `FileBatchAction` | ファイル入力バッチアクションテンプレート（`data_format`使用時） |
| `NoInputDataBatchAction` | 入力データ不要なバッチアクションテンプレート |
| `AsyncMessageSendAction` | 応答不要メッセージ送信 |

> `FileBatchAction`は`data_format`を使用する。`data_bind`を使用する場合は他のアクションクラスを使用すること。

### アクションクラスの責務

アクションクラスは以下を実装する:
1. `DataReader`を生成（`createReader`メソッド）
2. 読み込んだデータレコードを元に業務ロジックを実行
3. 処理結果として`Result`を返却

業務ロジックの典型的な処理内容（例: ファイル取り込みバッチ）:
- データレコードからフォームクラスを作成してバリデーション実行
- フォームクラスからエンティティクラスを作成してデータベースに追加
- 処理結果として`Result.Success`を返す

### 実装例（基本的なバッチアクション）

```java
public class SampleAction extends BatchAction<SqlRow> {

    @Override
    public DataReader<SqlRow> createReader(final ExecutionContext ctx) {
        final DatabaseRecordReader reader = new DatabaseRecordReader();
        final SqlPStatement statement = DbConnectionContext.getConnection()
                .prepareParameterizedSqlStatementBySqlId(
                        Project.class.getName() + "#GET_ID");

        reader.setStatement(statement, condition);
        return reader;
    }

    @Override
    public Result handle(final SqlRow inputData, final ExecutionContext ctx) {
        final Project project =
                UniversalDao.findBySqlFile(Project.class, "FIND_BY_ID_WITH_LOCK", inputData);

        // 業務処理

        UniversalDao.update(project);
        return new Success();
    }
}
```

### 状態保持が必要な場合

バッチアクション内でフィールドとして状態（例: 処理件数カウンタ）を保持できる:

```java
public class BatchActionSample extends BatchAction<Object> {
    /** 登録件数（スレッドセーフなカウンタ） */
    private AtomicInteger insertedCount = new AtomicInteger(0);

    @Override
    public Result handle(final Object inputData, final ExecutionContext ctx) {
        // 業務処理
        insertedCount.incrementAndGet();
        return new Result.Success();
    }
}
```

### アクションの起動方法

コマンドライン引数`-requestPath`でアクションクラスとリクエストIDを指定する:

```properties
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

### 関連クラスの責務

| クラス | 責務 |
|---|---|
| フォームクラス | `DataReader`が読み込んだデータレコードをマッピング。バリデーション用アノテーションと相関バリデーションのロジックを持つ。プロパティは全て`String`で定義（バイナリはバイト配列） |
| エンティティクラス | テーブルと1対1対応。カラムに対応するプロパティを持つ |

**注意点**:
- マルチスレッドバッチでは、アクションクラスのフィールドに状態を保持する場合、アプリケーション側でスレッドセーフを保証すること（`AtomicInteger`等を使用）
- `FileBatchAction`は`data_format`専用。`data_bind`を使用する場合は別のアクションクラスを選択すること
- 外部ファイル等で入力データが安全でない場合のみフォームクラスでバリデーション。データベース等で安全なデータの場合はフォームクラスを省略して直接エンティティクラスを作成可能

参照: `nablarch-batch-architecture.json#actions`, `nablarch-batch-application_design.json#overview`, `nablarch-batch-nablarch_batch_pessimistic_lock.json#implementation-example`, `nablarch-batch-nablarch_batch_retention_state.json#overview`

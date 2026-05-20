**結論**: はい、可能です。`SimpleDbTransactionManager` を使って業務トランザクションとは独立した別トランザクションでSQLを実行できます。ユニバーサルDAOを使う場合は `UniversalDao.Transaction`、JDBCラッパーを使う場合は `SimpleDbTransactionExecutor` を使用します。業務トランザクション（`LoopHandler` が制御するトランザクション）がロールバックされても、別トランザクションでコミット済みの更新は残ります。

**根拠**:

コンポーネント設定ファイルに `SimpleDbTransactionManager` を定義します。

```xml
<component name="separate-transaction"
    class="nablarch.core.db.transaction.SimpleDbTransactionManager">
  <property name="connectionFactory" ref="connectionFactory" />
  <property name="transactionFactory" ref="transactionFactory" />
  <property name="dbTransactionName" value="separate-transaction" />
</component>
```

**ユニバーサルDAOを使う場合** (`UniversalDao.Transaction` を継承):

```java
private static final class InsertLogTransaction extends UniversalDao.Transaction {

    InsertLogTransaction() {
        // コンポーネント定義で指定した名前を指定する
        super("separate-transaction");
    }

    @Override
    protected void execute() {
        // このメソッドが自動的に別のトランザクションで実行される
        // 正常終了でコミット、例外・エラーでロールバック
        UniversalDao.insert(logEntity);
    }
}

// 呼び出し
new InsertLogTransaction();
```

**JDBCラッパーを使う場合** (`SimpleDbTransactionExecutor` を使用):

```java
SimpleDbTransactionManager dbTransactionManager =
    SystemRepository.get("separate-transaction");

new SimpleDbTransactionExecutor<Void>(dbTransactionManager) {
    @Override
    public Void execute(AppDbConnection connection) {
        SqlPStatement statement = connection.prepareStatementBySqlId(
            "jp.co.example.Action#INSERT_LOG");
        statement.executeUpdate();
        return null;
    }
}.doTransaction();
```

**注意点**:
- `SimpleDbTransactionManager` を直接使わず、必ず `SimpleDbTransactionExecutor`（JDBCラッパー）または `UniversalDao.Transaction`（ユニバーサルDAO）を使うこと。
- `execute()` メソッド内で例外が発生した場合、その別トランザクションはロールバックされる。業務トランザクションのロールバックとは独立している。

参照: `component/libraries/libraries-database.json:s29`, `component/libraries/libraries-universal-dao.json:s20`
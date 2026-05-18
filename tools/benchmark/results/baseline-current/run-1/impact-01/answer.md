**結論**: はい、業務トランザクションとは別のトランザクションでSQLを実行する方法があります。`SimpleDbTransactionManager` と `SimpleDbTransactionExecutor`（または `UniversalDao.Transaction`）を使用することで、現在のトランザクションとは独立したトランザクションでSQLを実行できます。業務処理がロールバックされても、別トランザクションでコミットした更新は残ります。

**根拠**:

#### JDBCラッパー（`SimpleDbTransactionExecutor`）を使う場合

**Step 1: コンポーネント設定ファイルで `SimpleDbTransactionManager` を定義する**

```xml
<component name="update-login-failed-count-transaction"
    class="nablarch.core.db.transaction.SimpleDbTransactionManager">
  <property name="connectionFactory" ref="connectionFactory" />
  <property name="transactionFactory" ref="transactionFactory" />
  <property name="dbTransactionName" value="update-login-failed-count-transaction" />
</component>
```

**Step 2: `SimpleDbTransactionExecutor` を使って実行する**

```java
SimpleDbTransactionManager dbTransactionManager =
    SystemRepository.get("update-login-failed-count-transaction");

SqlResultSet resultSet = new SimpleDbTransactionExecutor<SqlResultSet>(dbTransactionManager) {
    @Override
    public SqlResultSet execute(AppDbConnection connection) {
        SqlPStatement statement = connection.prepareStatementBySqlId(
            "jp.co.tis.sample.action.SampleAction#findUser");
        statement.setLong(1, userId);
        return statement.retrieve();
    }
}.doTransaction();
```

#### UniversalDAO を使う場合

```java
private static final class FindPersonsTransaction extends UniversalDao.Transaction {
    private EntityList<Person> persons;

    FindPersonsTransaction() {
        super("find-persons-transaction");
    }

    @Override
    protected void execute() {
        persons = UniversalDao.findAllBySqlFile(Person.class, "FIND_PERSONS");
    }

    public EntityList<Person> getPersons() {
        return persons;
    }
}
```

**注意点**:
- `SimpleDbTransactionManager` を直接使わず、必ず `SimpleDbTransactionExecutor`（JDBCラッパー）または `UniversalDao.Transaction`（UniversalDAO）を経由してトランザクションを制御すること
- 別トランザクション内で正常終了した場合はコミット、例外発生時はロールバック
- `connectionFactory` と `transactionFactory` の設定が前提

参照: `component/libraries/libraries-database.json#s29`, `component/libraries/libraries-universal-dao.json#s20`, `component/libraries/libraries-transaction.json#s5`
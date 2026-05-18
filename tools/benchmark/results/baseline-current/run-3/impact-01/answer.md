**結論**: 業務トランザクションとは別の独立したトランザクションでSQLを実行する方法があります。`SimpleDbTransactionManager` と `SimpleDbTransactionExecutor`（JDBCラッパーの場合）または `UniversalDao.Transaction`（UniversalDAOの場合）を使用することで、現在のトランザクションがロールバックされても更新が残る別トランザクションを実現できます。

**根拠**:

### JDBCラッパー（`SimpleDbTransactionExecutor`）を使う場合

コンポーネント設定ファイルに `SimpleDbTransactionManager` を定義します：

```xml
<component name="update-login-failed-count-transaction"
    class="nablarch.core.db.transaction.SimpleDbTransactionManager">
  <property name="connectionFactory" ref="connectionFactory" />
  <property name="transactionFactory" ref="transactionFactory" />
  <property name="dbTransactionName" value="update-login-failed-count-transaction" />
</component>
```

実装例：

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

### UniversalDAOを使う場合

同じ `SimpleDbTransactionManager` の定義を行い、`UniversalDao.Transaction` を継承したクラスを作成します：

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

呼び出し側：

```java
FindPersonsTransaction findPersonsTransaction = new FindPersonsTransaction();
EntityList<Person> persons = findPersonsTransaction.getPersons();
```

**注意点**:
- `SimpleDbTransactionManager` を直接使わず、必ずラッパークラス（`SimpleDbTransactionExecutor` または `UniversalDao.Transaction`）を使用すること
- `SimpleDbTransactionManager` には `connectionFactory`・`transactionFactory`・`dbTransactionName` の3プロパティ設定が必要
- 複数の独立トランザクションを使う場合は `dbTransactionName` にそれぞれ別名を設定する
- システムリポジトリからの取得だけでなく、`SimpleDbTransactionManager` をDIして使用することも可能

参照: `component/libraries/libraries-database.json#s29`, `component/libraries/libraries-universal-dao.json#s20`
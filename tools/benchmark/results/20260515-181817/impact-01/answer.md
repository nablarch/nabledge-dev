**結論**: 業務トランザクションとは別の独立したトランザクションでSQLを実行するには、`SimpleDbTransactionManager` を使用します。これにより、業務トランザクションがロールバックされても、別トランザクション内での変更はコミット済みとして残ります。

**根拠**:

**方法1: JDBCラッパーを使う場合（`SimpleDbTransactionExecutor`）**

① コンポーネント設定ファイルに `SimpleDbTransactionManager` を定義します。

```xml
<component name="update-login-failed-count-transaction"
    class="nablarch.core.db.transaction.SimpleDbTransactionManager">
  <property name="connectionFactory" ref="connectionFactory" />
  <property name="transactionFactory" ref="transactionFactory" />
  <property name="dbTransactionName" value="update-login-failed-count-transaction" />
</component>
```

② システムリポジトリから取得し、`SimpleDbTransactionExecutor` で実行します。

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

**方法2: UniversalDAOを使う場合（`UniversalDao.Transaction`）**

① 同様に `SimpleDbTransactionManager` をコンポーネント設定に定義します。

② `UniversalDao.Transaction` を継承したクラスを作成して使用します。

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

// 呼び出し
FindPersonsTransaction findPersonsTransaction = new FindPersonsTransaction();
EntityList<Person> persons = findPersonsTransaction.getPersons();
```

**注意点**:
- `dbTransactionName` プロパティには、このトランザクション固有の名前を設定してください（他のトランザクションと重複させないこと）。
- `connectionFactory` と `transactionFactory` は既存のデータベース接続設定を参照します（`JdbcTransactionFactory` 含む既存設定が前提）。
- `SimpleDbTransactionExecutor.doTransaction()` の実行中にコミット/ロールバックは自動的に行われます。業務トランザクションとは完全に独立しているため、業務トランザクションがロールバックされても、`doTransaction()` 内でコミット済みの変更は残ります。

参照: `component/libraries/libraries-database.json#s29`、`component/libraries/libraries-universal-dao.json#s20`
**結論**: Nablarchバッチで業務トランザクションとは別のトランザクションでSQLを実行するには、`SimpleDbTransactionManager` を使用します。`SimpleDbTransactionExecutor`（JDBCラッパー使用時）または `UniversalDao.Transaction`（ユニバーサルDAO使用時）でラップした処理は独立したトランザクションでコミットされるため、業務トランザクションがロールバックされても更新が残ります。

---

**根拠**:

**JDBCラッパー（`SimpleDbTransactionExecutor`）を使う場合**:

1. コンポーネント設定ファイルに `SimpleDbTransactionManager` を定義:

```xml
<component name="update-login-failed-count-transaction"
    class="nablarch.core.db.transaction.SimpleDbTransactionManager">
  <property name="connectionFactory" ref="connectionFactory" />
  <property name="transactionFactory" ref="transactionFactory" />
  <property name="dbTransactionName" value="update-login-failed-count-transaction" />
</component>
```

2. アクション内で `SimpleDbTransactionExecutor` を使って実行:

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

**ユニバーサルDAOを使う場合**:

同様に `SimpleDbTransactionManager` を定義したうえで、`UniversalDao.Transaction` を継承したクラスを使用:

```java
private static final class FindPersonsTransaction extends UniversalDao.Transaction {

    private EntityList<Person> persons;

    FindPersonsTransaction() {
        // コンポーネント定義の名前またはSimpleDbTransactionManagerオブジェクトを指定
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

呼び出し側:

```java
FindPersonsTransaction findPersonsTransaction = new FindPersonsTransaction();
EntityList<Person> persons = findPersonsTransaction.getPersons();
```

`execute()` メソッドが正常終了すればコミット、例外・エラーが発生した場合はロールバックされます。業務トランザクションとは独立しているため、業務側がロールバックされても別トランザクションの更新は残ります。

**注意点**:
- `SimpleDbTransactionManager` を直接操作するのではなく、必ず `SimpleDbTransactionExecutor`（JDBCラッパー）または `UniversalDao.Transaction`（ユニバーサルDAO）を通じてトランザクションを制御してください。
- `dbTransactionName` の値はスレッド内で一意となるよう設定してください。

参照: `component/libraries/libraries-database.json:s29`, `component/libraries/libraries-universal-dao.json:s20`
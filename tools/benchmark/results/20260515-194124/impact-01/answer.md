**結論**: `SimpleDbTransactionManager` と `SimpleDbTransactionExecutor`（または `UniversalDao.Transaction`）を使用することで、業務トランザクションとは独立した別トランザクションでSQLを実行できます。業務処理がロールバックされても、別トランザクション側のコミットは保持されます。

**根拠**:

### 方法1: JDBCラッパーを使う場合

**① コンポーネント設定ファイルに `SimpleDbTransactionManager` を定義する**

```xml
<component name="update-login-failed-count-transaction"
    class="nablarch.core.db.transaction.SimpleDbTransactionManager">
  <property name="connectionFactory" ref="connectionFactory" />
  <property name="transactionFactory" ref="transactionFactory" />
  <property name="dbTransactionName" value="update-login-failed-count-transaction" />
</component>
```

**② `SimpleDbTransactionExecutor` を使ってSQLを実行する**

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

- `SimpleDbTransactionManager` は直接使わず、必ず `SimpleDbTransactionExecutor` 経由で使用すること。

### 方法2: ユニバーサルDAOを使う場合

**① 同様に `SimpleDbTransactionManager` をコンポーネント設定ファイルに定義する**（方法1と同じ）

**② `UniversalDao.Transaction` を継承したクラスを作成し、呼び出す**

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

```java
FindPersonsTransaction findPersonsTransaction = new FindPersonsTransaction();
EntityList<Person> persons = findPersonsTransaction.getPersons();
```

**注意点**:
- `SimpleDbTransactionManager` を直接操作するのではなく、必ず `SimpleDbTransactionExecutor`（JDBCラッパー）または `UniversalDao.Transaction`（ユニバーサルDAO）を使うこと
- `execute()` メソッド内で例外・エラーが発生した場合は、別トランザクション側もロールバックされます（業務トランザクションとは独立しているため、業務側のロールバックの影響は受けない）
- `connectionFactory` と `transactionFactory` の設定が前提となる

参照: component/libraries/libraries-database.json#s29, component/libraries/libraries-universal-dao.json#s20
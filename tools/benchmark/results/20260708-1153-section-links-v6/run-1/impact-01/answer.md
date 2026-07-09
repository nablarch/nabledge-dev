**結論**: 業務トランザクションとは別のトランザクションでSQLを実行できる。`SimpleDbTransactionManager` をコンポーネント定義に追加し、`SimpleDbTransactionExecutor`（JDBCラッパー使用時）または `UniversalDao.Transaction`（ユニバーサルDAO使用時）でラップして実行する。この場合、業務トランザクションがロールバックされても、別トランザクション内のコミット済み更新は残る。

**根拠**:

**JDBCラッパーを使う場合**

コンポーネント設定ファイルに `SimpleDbTransactionManager` を定義する：

```xml
<component name="update-login-failed-count-transaction"
    class="nablarch.core.db.transaction.SimpleDbTransactionManager">
  <property name="connectionFactory" ref="connectionFactory" />
  <property name="transactionFactory" ref="transactionFactory" />
  <property name="dbTransactionName" value="update-login-failed-count-transaction" />
</component>
```

実装例（`SimpleDbTransactionExecutor` を使う）：

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

**ユニバーサルDAOを使う場合**

コンポーネント設定は上記と同様。実装は `UniversalDao.Transaction` を継承したクラスを作る：

```java
private static final class FindPersonsTransaction extends UniversalDao.Transaction {

    private EntityList<Person> persons;

    FindPersonsTransaction() {
        // コンポーネント定義で指定した名前を指定する
        super("find-persons-transaction");
    }

    @Override
    protected void execute() {
        // このメソッドが自動的に別トランザクションで実行される
        persons = UniversalDao.findAllBySqlFile(Person.class, "FIND_PERSONS");
    }

    public EntityList<Person> getPersons() {
        return persons;
    }
}
```

呼び出し：

```java
FindPersonsTransaction findPersonsTransaction = new FindPersonsTransaction();
EntityList<Person> persons = findPersonsTransaction.getPersons();
```

正常終了すれば別トランザクションがコミットされ、例外が発生した場合は別トランザクションのみロールバックされる。

**注意点**:
- `SimpleDbTransactionManager` を直接使わず、`SimpleDbTransactionExecutor`（JDBCラッパー）または `UniversalDao.Transaction`（ユニバーサルDAO）を経由すること
- `dbTransactionName` はアプリケーション内で一意な名前を設定すること

参照:
- データベースアクセス(JDBCラッパー)
  .claude/skills/nabledge-6/docs/component/libraries/libraries-database.md
  現在のトランザクションとは異なるトランザクションでSQLを実行する
- ユニバーサルDAO
  .claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md
  現在のトランザクションとは異なるトランザクションで実行する
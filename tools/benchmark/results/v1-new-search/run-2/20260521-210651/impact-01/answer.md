**結論**: 業務トランザクションとは別のトランザクションでSQLを実行するには、`SimpleDbTransactionManager` をコンポーネント設定ファイルに定義し、`SimpleDbTransactionExecutor`（JDBCラッパー使用時）または `UniversalDao.Transaction`（ユニバーサルDAO使用時）を介して操作する。この別トランザクションは業務トランザクションのロールバックとは独立しており、失敗しても変更を確定できる。

**根拠**:

**JDBCラッパーを使う場合（`SimpleDbTransactionExecutor`）**

手順1: コンポーネント設定ファイルに `SimpleDbTransactionManager` を定義する。

```xml
<component name="update-login-failed-count-transaction" class="nablarch.core.db.transaction.SimpleDbTransactionManager">
  <!-- connectionFactoryプロパティにConnectionFactory実装クラスを設定する -->
  <property name="connectionFactory" ref="connectionFactory" />

  <!-- transactionFactoryプロパティにTransactionFactory実装クラスを設定する -->
  <property name="transactionFactory" ref="transactionFactory" />

  <!-- トランザクションを識別するための名前を設定する -->
  <property name="dbTransactionName" value="update-login-failed-count-transaction" />
</component>
```

手順2: `SimpleDbTransactionExecutor` を使って別トランザクションでSQLを実行する。

```java
// システムリポジトリからSimpleDbTransactionManagerを取得する
SimpleDbTransactionManager dbTransactionManager =
    SystemRepository.get("update-login-failed-count-transaction");

// SimpleDbTransactionManagerをコンストラクタに指定して実行する
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

**ユニバーサルDAOを使う場合（`UniversalDao.Transaction`）**

同様に `SimpleDbTransactionManager` をコンポーネント設定ファイルに定義したうえで、`UniversalDao.Transaction` を継承したクラスを作成する。

```java
private static final class FindPersonsTransaction extends UniversalDao.Transaction {

    private EntityList<Person> persons;

    FindPersonsTransaction() {
        // コンポーネント定義で指定した名前を指定する
        super("find-persons-transaction");
    }

    // このメソッドが自動的に別のトランザクションで実行される。
    // 正常に処理が終了した場合はトランザクションがコミットされ、
    // 例外やエラーが送出された場合には、トランザクションがロールバックされる。
    @Override
    protected void execute() {
        persons = UniversalDao.findAllBySqlFile(Person.class, "FIND_PERSONS");
    }

    public EntityList<Person> getPersons() {
        return persons;
    }
}
```

呼び出し:

```java
// 生成すると別のトランザクションで実行される
FindPersonsTransaction findPersonsTransaction = new FindPersonsTransaction();
EntityList<Person> persons = findPersonsTransaction.getPersons();
```

**注意点**: `SimpleDbTransactionManager` を直接使うのではなく、必ず `SimpleDbTransactionExecutor`（JDBCラッパー）または `UniversalDao.Transaction`（ユニバーサルDAO）を経由してトランザクションを制御すること。

参照: libraries-database.json:s29, libraries-universal-dao.json:s20

---
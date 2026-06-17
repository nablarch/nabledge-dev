**結論**: Nablarchバッチでは、業務トランザクションとは別のトランザクションを `SimpleDbTransactionManager` で定義し、`SimpleDbTransactionExecutor`（JDBCラッパー使用時）または `UniversalDao.Transaction`（ユニバーサルDAO使用時）を通じて実行することで、業務トランザクションがロールバックされても別トランザクションの更新を確定させることができます。

**根拠**:

#### JDBCラッパーを使用する場合

**コンポーネント設定ファイル**に `SimpleDbTransactionManager` を定義します:

```xml
<component name="update-login-failed-count-transaction"
    class="nablarch.core.db.transaction.SimpleDbTransactionManager">
  <!-- ConnectionFactory実装クラスを設定する -->
  <property name="connectionFactory" ref="connectionFactory" />
  <!-- TransactionFactory実装クラスを設定する -->
  <property name="transactionFactory" ref="transactionFactory" />
  <!-- トランザクションを識別するための名前を設定する -->
  <property name="dbTransactionName" value="update-login-failed-count-transaction" />
</component>
```

**実装例**（`SimpleDbTransactionExecutor` を使用）:

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

#### ユニバーサルDAOを使用する場合

`UniversalDao.Transaction` を継承したクラスを作成し、`execute()` メソッド内にユニバーサルDAOの処理を実装します:

```java
private static final class FindPersonsTransaction extends UniversalDao.Transaction {
    private EntityList<Person> persons;

    FindPersonsTransaction() {
        // コンポーネント定義で指定した名前を指定する
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

#### Domaアダプタを使用する場合

`DomaConfig#getTransactionManager()` で取得した `TransactionManager` を使って別トランザクションを制御します:

```java
DomaConfig.singleton()
        .getTransactionManager()
        .requiresNew(() ->
                DomaDaoRepository.get(ProjectDao.class).insert(project));
```

**注意点**: `execute()` メソッドが正常終了するとトランザクションがコミットされ、例外やエラーが送出された場合はロールバックされます。業務トランザクションとは独立したトランザクションなので、業務トランザクション側のロールバックによる影響は受けません。

参照: libraries-database.json:s29, libraries-universal-dao.json:s20, adapters-doma-adaptor.json:s8
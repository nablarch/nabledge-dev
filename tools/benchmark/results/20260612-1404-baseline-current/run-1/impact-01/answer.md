**結論**: `SimpleDbTransactionManager` を使うことで、業務トランザクションとは独立した別トランザクションでSQLを実行できます。業務処理がロールバックされても、別トランザクション内でコミットした更新は保持されます。

**根拠**:

**共通の設定**: コンポーネント設定ファイルに `SimpleDbTransactionManager` を定義します。

```xml
<component name="update-login-failed-count-transaction"
    class="nablarch.core.db.transaction.SimpleDbTransactionManager">
  <property name="connectionFactory" ref="connectionFactory" />
  <property name="transactionFactory" ref="transactionFactory" />
  <property name="dbTransactionName" value="update-login-failed-count-transaction" />
</component>
```

---

**アプローチ①: JDBCラッパーを使う場合**

`SimpleDbTransactionExecutor` を使用してトランザクションを実行します。

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

---

**アプローチ②: ユニバーサルDAOを使う場合**

`UniversalDao.Transaction` を継承したクラスを作成して実行します。

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

呼び出し:

```java
FindPersonsTransaction findPersonsTransaction = new FindPersonsTransaction();
EntityList<Person> persons = findPersonsTransaction.getPersons();
```

---

**アプローチ③: Domaアダプタを使っている場合**

`DomaConfig#getTransactionManager` から取得した `TransactionManager` を使用して `requiresNew` で別トランザクション実行できます。

```java
DomaConfig.singleton()
        .getTransactionManager()
        .requiresNew(() ->
                DomaDaoRepository.get(ProjectDao.class).insert(project));
```

**注意点**:
- `SimpleDbTransactionManager` の `dbTransactionName` には一意の名前を設定してください（別のトランザクション管理ハンドラと名前が衝突しないように）。
- `SimpleDbTransactionManager` はシステムリポジトリからの取得の他に、DIで直接インジェクションしても使用できます。

参照: libraries-database.json:s29, libraries-universal-dao.json:s20, adapters-doma-adaptor.json:s8
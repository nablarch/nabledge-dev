業務トランザクションとは別のトランザクションでSQLを実行するには、`SimpleDbTransactionManager` と `SimpleDbTransactionExecutor`（JDBCラッパー使用時）または `UniversalDao.Transaction`（UniversalDAO使用時）を使います。業務トランザクションがロールバックされても、別トランザクションでコミットした更新は保持されます。

---

**方法1: JDBCラッパー (`SimpleDbTransactionExecutor`) を使う場合**

コンポーネント設定ファイルに `SimpleDbTransactionManager` を定義します。

```xml
<component name="update-login-failed-count-transaction"
    class="nablarch.core.db.transaction.SimpleDbTransactionManager">
  <!-- connectionFactoryプロパティにConnectionFactory実装クラスを設定する -->
  <property name="connectionFactory" ref="connectionFactory" />
  <!-- transactionFactoryプロパティにTransactionFactory実装クラスを設定する -->
  <property name="transactionFactory" ref="transactionFactory" />
  <!-- トランザクションを識別するための名前を設定する -->
  <property name="dbTransactionName" value="update-login-failed-count-transaction" />
</component>
```

実装例：

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

---

**方法2: UniversalDAO (`UniversalDao.Transaction`) を使う場合**

コンポーネント設定ファイルに同様に `SimpleDbTransactionManager` を定義し、`UniversalDao.Transaction` を継承したクラスを作成します。

```java
private static final class FindPersonsTransaction extends UniversalDao.Transaction {
    private EntityList<Person> persons;

    FindPersonsTransaction() {
        // SimpleDbTransactionManagerのコンポーネント定義名を指定する
        super("find-persons-transaction");
    }

    // このメソッドが自動的に別のトランザクションで実行される
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

---

**注意点**: `SimpleDbTransactionManager` には `connectionFactory`（DB接続設定）と `transactionFactory`（トランザクション制御）の両方を設定する必要があります。各プロパティの詳細は、データベース接続設定（`libraries-database.json`）およびトランザクション制御（`libraries-transaction.json`）を参照してください。

参照: `libraries-database.json:s29`, `libraries-universal-dao.json:s20`, `libraries-transaction.json:s5`
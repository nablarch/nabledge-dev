**結論**: `SimpleDbTransactionManager` を使って個別トランザクションを開始することで、業務トランザクションとは独立したトランザクションでSQLを実行できる。業務トランザクションがロールバックされても、この別トランザクションでコミットした更新は維持される。

---

**根拠**:

### JDBCラッパー（`SimpleDbTransactionExecutor`）を使う場合

コンポーネント設定ファイルに `SimpleDbTransactionManager` を定義する:

```xml
<component name="update-login-failed-count-transaction"
    class="nablarch.core.db.transaction.SimpleDbTransactionManager">
  <property name="connectionFactory" ref="connectionFactory" />
  <property name="transactionFactory" ref="transactionFactory" />
  <property name="dbTransactionName" value="update-login-failed-count-transaction" />
</component>
```

Java実装例（`SimpleDbTransactionExecutor` を使用）:

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

### ユニバーサルDAO（`UniversalDao.Transaction`）を使う場合

コンポーネント設定ファイルは同様に `SimpleDbTransactionManager` を定義。Java実装は `UniversalDao.Transaction` を継承したクラスを作成する:

```java
private static final class FindPersonsTransaction extends UniversalDao.Transaction {
    private EntityList<Person> persons;

    FindPersonsTransaction() {
        // コンポーネント定義で指定した名前を指定する
        super("find-persons-transaction");
    }

    // このメソッドが自動的に別トランザクションで実行される
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

### Domaアダプタを使う場合

Domaアダプタを利用している場合は `DomaConfig#getTransactionManager()` で取得した `TransactionManager` を使う:

```java
DomaConfig.singleton()
    .getTransactionManager()
    .requiresNew(() ->
        DomaDaoRepository.get(ProjectDao.class).insert(project));
```

---

**注意点**:
- `SimpleDbTransactionManager` を `SimpleDbTransactionExecutor` や `UniversalDao.Transaction` を介さずに直接使用しないこと。トランザクション制御が正しく行われない。
- `execute()` メソッド内で例外/エラーが発生した場合は別トランザクションもロールバックされる。

参照: libraries-database.json:s29, libraries-universal-dao.json:s20, adapters-doma-adaptor.json:s8
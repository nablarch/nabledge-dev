**結論**: `SimpleDbTransactionManager` と `SimpleDbTransactionExecutor`（またはUniversalDAOを使う場合は `UniversalDao.Transaction`）を組み合わせることで、業務トランザクションとは独立した別トランザクションでSQLを実行できる。このトランザクションは業務トランザクションのロールバックとは無関係にコミット・ロールバックされる。

---

**根拠**:

### 方法1: JDBCラッパーで直接SQL実行する場合

**① コンポーネント設定ファイルに `SimpleDbTransactionManager` を定義する**

```xml
<component name="update-login-failed-count-transaction" class="nablarch.core.db.transaction.SimpleDbTransactionManager">
  <!-- ConnectionFactory実装クラスを設定する -->
  <property name="connectionFactory" ref="connectionFactory" />

  <!-- TransactionFactory実装クラスを設定する -->
  <property name="transactionFactory" ref="transactionFactory" />

  <!-- トランザクションを識別するための名前を設定する -->
  <property name="dbTransactionName" value="update-login-failed-count-transaction" />
</component>
```

**② `SimpleDbTransactionExecutor` を使って実行する**

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

### 方法2: UniversalDAOで実行する場合

コンポーネント設定は方法1と同様。Javaコードでは `UniversalDao.Transaction` を継承したクラスを使う。

```java
private static final class FindPersonsTransaction extends UniversalDao.Transaction {

    private EntityList<Person> persons;

    FindPersonsTransaction() {
        // コンポーネント定義で指定した名前をsuper()に指定する
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

// 呼び出し側
FindPersonsTransaction findPersonsTransaction = new FindPersonsTransaction();
EntityList<Person> persons = findPersonsTransaction.getPersons();
```

---

### 方法3: Domaアダプタを使う場合

```java
DomaConfig.singleton()
        .getTransactionManager()
        .requiresNew(() ->
                DomaDaoRepository.get(ProjectDao.class).insert(project));
```

---

**注意点**:
- `SimpleDbTransactionManager` の `transactionFactory` プロパティには、`JdbcTransactionFactory` を設定する（`isolationLevel` や `transactionTimeoutSec` もここで指定）
- `SimpleDbTransactionExecutor` を使うこと（`SimpleDbTransactionManager` を直接操作しない）
- `UniversalDao.Transaction` の `execute()` メソッド内で例外が発生した場合、別トランザクション側がロールバックされる点に注意

参照: libraries-database.json:s29, libraries-universal-dao.json:s20, adapters-doma-adaptor.json:s8, libraries-transaction.json:s5
**結論**: `SimpleDbTransactionManager` を使って業務トランザクションとは独立した別トランザクションでSQLを実行できます。JDBCラッパー使用時は `SimpleDbTransactionExecutor`、ユニバーサルDAO使用時は `UniversalDao.Transaction` を使います。別トランザクションは独立してコミットされるため、業務トランザクションがロールバックされても別トランザクションの更新は残ります。

---

**根拠**:

### JDBCラッパーを使う場合（`SimpleDbTransactionExecutor`）

コンポーネント設定ファイルに `SimpleDbTransactionManager` を定義します：

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

実装例：`SimpleDbTransactionManager` を直接使わず、`SimpleDbTransactionExecutor` 経由で実行します：

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

### ユニバーサルDAOを使う場合（`UniversalDao.Transaction`）

コンポーネント設定は同様。実装では `UniversalDao.Transaction` を継承したクラスを作成します：

```java
private static final class FindPersonsTransaction extends UniversalDao.Transaction {

    // 結果を受け取る入れ物を用意する。
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
        // executeメソッドにUniversalDaoを使った処理を実装する。
        persons = UniversalDao.findAllBySqlFile(Person.class, "FIND_PERSONS");
    }

    // 結果を返すgetterを用意する。
    public EntityList<Person> getPersons() {
        return persons;
    }
}
```

呼び出し：

```java
// 生成すると別のトランザクションで実行される。
FindPersonsTransaction findPersonsTransaction = new FindPersonsTransaction();

// 結果を取得する。
EntityList<Person> persons = findPersonsTransaction.getPersons();
```

---

**注意点**:
- `execute()` メソッド内で例外が発生した場合は、その別トランザクションはロールバックされます（業務トランザクションとは独立）
- Domaアダプタを使用している場合は、`DomaConfig.singleton().getTransactionManager().requiresNew(() -> ...)` でも同様の独立トランザクション実行が可能です

参照: libraries-database.json:s29, libraries-universal-dao.json:s20, adapters-doma-adaptor.json:s8
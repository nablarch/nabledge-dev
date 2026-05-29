Step 5-7: 回答を生成し、検証します。

**結論**: `SimpleDbTransactionManager` + `SimpleDbTransactionExecutor`（または `UniversalDao.Transaction`）を使うことで、業務トランザクションとは独立した別トランザクションでSQLを実行できます。業務処理がロールバックされても、別トランザクションでコミットされた更新は保持されます。

**根拠**:

**アプローチ1: JDBCラッパーを使う場合**

まずコンポーネント設定ファイルに `SimpleDbTransactionManager` を定義します。

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

`SimpleDbTransactionManager` を直接使わず、`SimpleDbTransactionExecutor` でトランザクションを制御します。

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

**アプローチ2: ユニバーサルDAOを使う場合**

コンポーネント設定は同様に `SimpleDbTransactionManager` を定義します。実装では `UniversalDao.Transaction` を継承したクラスを作成します。

```java
private static final class FindPersonsTransaction extends UniversalDao.Transaction {
    private EntityList<Person> persons;

    FindPersonsTransaction() {
        // コンポーネント定義で指定した名前を指定
        super("find-persons-transaction");
    }

    // このメソッドが自動的に別のトランザクションで実行される。
    // 正常終了でコミット、例外・エラーでロールバックされる。
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
// 生成すると別のトランザクションで実行される
FindPersonsTransaction findPersonsTransaction = new FindPersonsTransaction();
EntityList<Person> persons = findPersonsTransaction.getPersons();
```

---

**アプローチ3: Domaアダプタを使う場合**

`DomaConfig#getTransactionManager` で取得した `TransactionManager` の `requiresNew` を使います。

```java
DomaConfig.singleton()
        .getTransactionManager()
        .requiresNew(() ->
                DomaDaoRepository.get(ProjectDao.class).insert(project));
```

**注意点**:
- アプローチ1・2では、コンポーネント設定ファイルへの `SimpleDbTransactionManager` の定義が必須です。`connectionFactory` と `transactionFactory` の両プロパティを設定する必要があります。
- `SimpleDbTransactionManager` を直接使用せず、必ず `SimpleDbTransactionExecutor`（JDBCラッパー）または `UniversalDao.Transaction`（ユニバーサルDAO）経由で使用してください。

参照: `component/libraries/libraries-database.json:s29`, `component/libraries/libraries-universal-dao.json:s20`, `component/adapters/adapters-doma-adaptor.json:s8`

---
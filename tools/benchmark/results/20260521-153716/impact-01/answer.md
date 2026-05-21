**結論**: `SimpleDbTransactionManager` を使用して別トランザクションを定義し、`SimpleDbTransactionExecutor`（JDBCラッパー使用時）または `UniversalDao.Transaction`（ユニバーサルDAO使用時）でSQLを実行することで、業務トランザクションとは独立した別トランザクションでSQLを実行できる。このトランザクションは業務トランザクションのロールバックの影響を受けない。

---

**根拠**:

**JDBCラッパー（データベースアクセス）を使用する場合**

コンポーネント設定ファイルに `SimpleDbTransactionManager` を定義する：

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

実装例（`SimpleDbTransactionExecutor` を使用）：

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

**ユニバーサルDAO を使用する場合**

コンポーネント設定ファイルの定義は同様に `SimpleDbTransactionManager` を使用する。実装は `UniversalDao.Transaction` を継承したクラスを作成して呼び出す：

```java
private static final class FindPersonsTransaction extends UniversalDao.Transaction {

    private EntityList<Person> persons;

    FindPersonsTransaction() {
        // コンポーネント定義で指定した名前を指定する
        super("find-persons-transaction");
    }

    // このメソッドが自動的に別のトランザクションで実行される。
    // 正常終了時はコミット、例外・エラー時はロールバックされる。
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

// 結果を取得する
EntityList<Person> persons = findPersonsTransaction.getPersons();
```

**注意点**: `SimpleDbTransactionManager` を直接使用するのではなく、必ずトランザクション制御クラス（`SimpleDbTransactionExecutor` または `UniversalDao.Transaction`）を経由して実行すること。

参照: libraries-database.json:s29, libraries-universal-dao.json:s20

---
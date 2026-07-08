**結論**: `SimpleDbTransactionManager` を使って個別トランザクションを定義することで、業務トランザクションとは独立したトランザクションでSQLを実行できます。これにより、業務トランザクションがロールバックされても、別トランザクションの更新は確定（コミット）されます。

---

**根拠**:

#### JDBCラッパーを使う場合

**① コンポーネント設定ファイル**に `SimpleDbTransactionManager` を定義します。

```xml
<component name="update-login-failed-count-transaction"
    class="nablarch.core.db.transaction.SimpleDbTransactionManager">

  <!-- 接続ファクトリを設定 -->
  <property name="connectionFactory" ref="connectionFactory" />

  <!-- トランザクションファクトリを設定 -->
  <property name="transactionFactory" ref="transactionFactory" />

  <!-- トランザクションを識別する名前 -->
  <property name="dbTransactionName" value="update-login-failed-count-transaction" />
</component>
```

**② 実装例** — `SimpleDbTransactionExecutor` でトランザクションを制御します。

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

#### ユニバーサルDAOを使う場合

同様に `SimpleDbTransactionManager` を設定した上で、`UniversalDao.Transaction` を継承したクラスを作成します。

```java
private static final class FindPersonsTransaction extends UniversalDao.Transaction {

    private EntityList<Person> persons;

    FindPersonsTransaction() {
        // コンポーネント定義で指定した名前を渡す
        super("find-persons-transaction");
    }

    @Override
    protected void execute() {
        // 別トランザクションで実行される。
        // 正常終了でコミット、例外発生でロールバック。
        persons = UniversalDao.findAllBySqlFile(Person.class, "FIND_PERSONS");
    }

    public EntityList<Person> getPersons() {
        return persons;
    }
}
```

呼び出し側：

```java
FindPersonsTransaction findPersonsTransaction = new FindPersonsTransaction();
EntityList<Person> persons = findPersonsTransaction.getPersons();
```

---

**注意点**:
- `SimpleDbTransactionExecutor` / `UniversalDao.Transaction` の `execute()` メソッド内で正常終了するとコミット、例外が発生するとロールバックされます（業務トランザクションの結果とは無関係）。
- `dbTransactionName` プロパティには一意の名前を設定してください。同じ名前のトランザクションが競合しないよう注意が必要です。

参照:
- データベースアクセス(JDBCラッパー)
  .claude/skills/nabledge-6/docs/component/libraries/libraries-database.md
  現在のトランザクションとは異なるトランザクションでSQLを実行する
- ユニバーサルDAO
  .claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md
  現在のトランザクションとは異なるトランザクションで実行する
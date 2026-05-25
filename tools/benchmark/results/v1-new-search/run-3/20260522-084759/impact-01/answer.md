Step 5: 回答を生成します。

---

**結論**: `SimpleDbTransactionManager` と `SimpleDbTransactionExecutor`（UniversalDAO使用時は `UniversalDao.Transaction`）を使うことで、業務トランザクションとは独立した個別トランザクションでSQLを実行できます。このトランザクションは業務トランザクションのロールバックに影響されず、更新が確定します。

**根拠**:

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

**JDBCラッパーを使う場合**（`SimpleDbTransactionExecutor`）:

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

**UniversalDAOを使う場合**（`UniversalDao.Transaction`）:

```java
private static final class FindPersonsTransaction extends UniversalDao.Transaction {

    private EntityList<Person> persons;

    FindPersonsTransaction() {
        // コンポーネント定義で指定した名前を指定する
        super("find-persons-transaction");
    }

    // このメソッドが自動的に別のトランザクションで実行される。
    // 正常終了した場合はコミット、例外・エラー発生時はロールバックされる。
    @Override
    protected void execute() {
        persons = UniversalDao.findAllBySqlFile(Person.class, "FIND_PERSONS");
    }

    public EntityList<Person> getPersons() {
        return persons;
    }
}

// 生成すると別のトランザクションで実行される
FindPersonsTransaction findPersonsTransaction = new FindPersonsTransaction();
EntityList<Person> persons = findPersonsTransaction.getPersons();
```

**補足 — ロールバック後コールバック**: Nablarchバッチの `LoopHandler`（トランザクションループ制御ハンドラ）では、業務トランザクションがロールバックした場合、`TransactionEventCallback` を実装したハンドラの `transactionAbnormalEnd` が **新しいトランザクション** で実行されコミットされます。「ロールバック後も確実に書き込みたいログや監査情報」はこのコールバックを使う方法もあります。

**注意点**:
- `SimpleDbTransactionExecutor` または `UniversalDao.Transaction` を使い、`SimpleDbTransactionManager` を直接操作しないこと。
- `LoopHandler` のコールバック内でエラーが発生すると、それ以降のハンドラへのコールバックは実行されないため注意が必要です。

参照: `libraries-database.json:s29`, `libraries-universal-dao.json:s20`, `handlers-loop-handler.json:s6`

---
**結論**: `SimpleDbTransactionManager` を使って個別トランザクションを定義することで実現できます。業務トランザクション（ハンドラが管理するトランザクション）とは独立したトランザクションでSQLが実行されるため、業務トランザクションがロールバックされても、個別トランザクションの更新は確定したままになります。

**根拠**:

#### 共通の準備: コンポーネント設定ファイルに `SimpleDbTransactionManager` を定義する

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

#### データベースアクセス(JDBCラッパー)の場合: `SimpleDbTransactionExecutor` を使用

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

#### ユニバーサルDAOの場合: `UniversalDao.Transaction` を使用

```java
private static final class FindPersonsTransaction extends UniversalDao.Transaction {

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
        persons = UniversalDao.findAllBySqlFile(Person.class, "FIND_PERSONS");
    }

    public EntityList<Person> getPersons() {
        return persons;
    }
}

// 利用側
FindPersonsTransaction findPersonsTransaction = new FindPersonsTransaction();
EntityList<Person> persons = findPersonsTransaction.getPersons();
```

**注意点**:
- `SimpleDbTransactionExecutor` / `UniversalDao.Transaction` の `execute` メソッド内で例外が発生した場合、個別トランザクションはロールバックされます。あくまで業務トランザクションとは独立してコミット・ロールバックが制御されます。
- Nablarchバッチのトランザクションループ制御ハンドラが管理する業務トランザクションとは別のDB接続が使われるため、同一DBに対する更新であっても独立して確定できます。

参照: libraries-database.json:s29, libraries-universal-dao.json:s20
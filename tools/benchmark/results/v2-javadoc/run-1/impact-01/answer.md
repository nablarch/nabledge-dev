s29とs20の内容はすでに読み取り済みです。Step 5でanswer_textを生成します。

---

**結論**: `SimpleDbTransactionManager` と `SimpleDbTransactionExecutor`（JDBCラッパー利用の場合）または `UniversalDao.Transaction`（UniversalDAO利用の場合）を使うことで、業務トランザクションとは独立した別トランザクションでSQLを実行できます。業務処理がロールバックされても、別トランザクションで実行したSQLのコミットはそのまま残ります。

---

**根拠**:

JDBCラッパーを使う場合：

**1. コンポーネント定義（XML）**
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

**2. 実装例（JDBCラッパー）**
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

UniversalDAOを使う場合：

**1. コンポーネント定義（XML）**（同上の `SimpleDbTransactionManager`）

**2. 実装例（UniversalDAO）**
```java
private static final class FindPersonsTransaction extends UniversalDao.Transaction {

    private EntityList<Person> persons;

    FindPersonsTransaction() {
        // コンポーネント定義で指定した名前を指定する
        super("find-persons-transaction");
    }

    // このメソッドが自動的に別トランザクションで実行される
    // 正常終了でコミット、例外/エラー発生でロールバック
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

**注意点**:
- `SimpleDbTransactionExecutor`（JDBCラッパー用）または `UniversalDao.Transaction`（UniversalDAO用）を使うこと。`SimpleDbTransactionManager` を直接操作しないこと。
- 別トランザクション内で例外が発生した場合は、そのトランザクションはロールバックされる。
- トランザクション名（`dbTransactionName`）は一意にすること。

参照: libraries-database.json:s29, libraries-universal-dao.json:s20

---
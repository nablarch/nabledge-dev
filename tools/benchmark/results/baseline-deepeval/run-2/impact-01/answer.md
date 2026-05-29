Step 5-7: 回答を生成し、検証します。

---

**結論**: `SimpleDbTransactionManager` と `SimpleDbTransactionExecutor`（JDBCラッパー）または `UniversalDao.Transaction`（ユニバーサルDAO）を使用することで、業務トランザクションとは独立した別トランザクションでSQLを実行できます。業務処理がロールバックされても、別トランザクションでコミット済みの更新はそのまま残ります。

---

**根拠**:

#### 方法1: JDBCラッパーで別トランザクション実行

**① コンポーネント設定ファイルに `SimpleDbTransactionManager` を定義する**

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

#### 方法2: ユニバーサルDAOで別トランザクション実行

コンポーネント設定は方法1と同様に `SimpleDbTransactionManager` を定義します。実装は `UniversalDao.Transaction` を継承したクラスを作成します。

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
```

呼び出し側:

```java
// 生成すると別のトランザクションで実行される
FindPersonsTransaction findPersonsTransaction = new FindPersonsTransaction();

// 結果を取得する
EntityList<Person> persons = findPersonsTransaction.getPersons();
```

---

**注意点**:
- `SimpleDbTransactionManager` を直接使うのではなく、必ず `SimpleDbTransactionExecutor`（JDBCラッパー）または `UniversalDao.Transaction`（ユニバーサルDAO）経由で実行すること。
- `execute()` メソッド内で例外・エラーが発生した場合、別トランザクション側もロールバックされます。ロールバックされず確定させたいのは「業務トランザクションがロールバックされた場合でも」という意味です。

参照: `libraries-database.json:s29`, `libraries-universal-dao.json:s20`

---
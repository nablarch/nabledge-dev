以上のセクション内容をもとに回答を生成します。

---

**結論**: Nablarchバッチで業務トランザクションとは別のトランザクションでSQLを実行するには、`SimpleDbTransactionManager` と `SimpleDbTransactionExecutor`（JDBCラッパー使用時）または `UniversalDao.Transaction`（ユニバーサルDAO使用時）を使います。このトランザクション内の更新は、業務トランザクションがロールバックされても独立してコミットされます。

---

**根拠**:

### JDBCラッパー（`DbConnectionContext`）を使う場合

**1. コンポーネント設定ファイルに `SimpleDbTransactionManager` を定義する**

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

**2. `SimpleDbTransactionExecutor` を使って実行する**

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

### ユニバーサルDAO を使う場合

コンポーネント設定は同様に `SimpleDbTransactionManager` を定義し、`UniversalDao.Transaction` を継承したクラスを使います。

```java
private static final class FindPersonsTransaction extends UniversalDao.Transaction {

    private EntityList<Person> persons;

    FindPersonsTransaction() {
        // コンポーネント定義で指定した名前を指定する
        super("find-persons-transaction");
    }

    // このメソッドが自動的に別のトランザクションで実行される。
    // 正常終了→コミット、例外・エラー→ロールバック
    @Override
    protected void execute() {
        persons = UniversalDao.findAllBySqlFile(Person.class, "FIND_PERSONS");
    }

    public EntityList<Person> getPersons() {
        return persons;
    }
}

// 呼び出し側
FindPersonsTransaction tx = new FindPersonsTransaction();
EntityList<Person> persons = tx.getPersons();
```

---

**注意点**:
- `SimpleDbTransactionManager` を直接使用するのではなく、必ず `SimpleDbTransactionExecutor`（JDBCラッパー）または `UniversalDao.Transaction`（ユニバーサルDAO）を使ってトランザクションを制御すること。
- このトランザクションは業務トランザクションとは完全に独立しているため、業務トランザクションがロールバックされても、`doTransaction()` が正常完了していればその更新はコミットされたまま残る。

参照: libraries-database.json:s29, libraries-universal-dao.json:s20

---
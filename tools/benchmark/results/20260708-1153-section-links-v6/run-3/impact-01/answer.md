**結論**: `SimpleDbTransactionManager` を使って独立したトランザクションを定義することで、業務トランザクションとは切り離された別トランザクションでSQLを実行できます。業務トランザクションがロールバックされても、別トランザクションでコミットされた更新は残ります。

---

**根拠**:

#### JDBCラッパーを使う方法

**コンポーネント設定ファイル**に `SimpleDbTransactionManager` を定義します。

```xml
<component name="update-login-failed-count-transaction"
    class="nablarch.core.db.transaction.SimpleDbTransactionManager">

  <!-- ConnectionFactory実装クラスを設定する -->
  <property name="connectionFactory" ref="connectionFactory" />

  <!-- TransactionFactory実装クラスを設定する -->
  <property name="transactionFactory" ref="transactionFactory" />

  <!-- トランザクションを識別するための名前 -->
  <property name="dbTransactionName" value="update-login-failed-count-transaction" />
</component>
```

**実装例**: `SimpleDbTransactionExecutor` を使ってSQLを実行します。

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

#### ユニバーサルDAOを使う方法

コンポーネント設定は上記と同じです。実装では `UniversalDao.Transaction` を継承したクラスを作成します。

```java
private static final class FindPersonsTransaction extends UniversalDao.Transaction {

    private EntityList<Person> persons;

    FindPersonsTransaction() {
        // コンポーネント定義で指定した名前を指定する
        super("find-persons-transaction");
    }

    // このメソッドが自動的に別のトランザクションで実行される
    // 正常終了 → コミット、例外/エラー → ロールバック
    @Override
    protected void execute() {
        persons = UniversalDao.findAllBySqlFile(Person.class, "FIND_PERSONS");
    }

    public EntityList<Person> getPersons() {
        return persons;
    }
}
```

呼び出し方：

```java
FindPersonsTransaction findPersonsTransaction = new FindPersonsTransaction();
EntityList<Person> persons = findPersonsTransaction.getPersons();
```

---

**注意点**:
- `SimpleDbTransactionManager` には `connectionFactory` と `transactionFactory` の両方の設定が必要です。詳細は「データベースに対する接続設定」および「データベースに対するトランザクション制御」を参照してください。
- 別トランザクション内で例外が発生した場合は、**その別トランザクションのみ**がロールバックされます。

参照:
- データベースアクセス(JDBCラッパー)
  .claude/skills/nabledge-6/docs/component/libraries/libraries-database.md
  現在のトランザクションとは異なるトランザクションでSQLを実行する
- ユニバーサルDAO
  .claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md
  現在のトランザクションとは異なるトランザクションで実行する
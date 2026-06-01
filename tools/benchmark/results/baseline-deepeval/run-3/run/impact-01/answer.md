**結論**: 業務トランザクションとは別のトランザクションでSQLを実行するには、`SimpleDbTransactionManager` を使って個別トランザクションを定義する方法があります。この方法で実行した更新は、業務トランザクションがロールバックされても独立してコミット/ロールバックされます。

---

**根拠**:

#### 方法1: JDBCラッパー（`SimpleDbTransactionExecutor`）

コンポーネント設定ファイルに `SimpleDbTransactionManager` を定義します。

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

実装は `SimpleDbTransactionExecutor` を使います（`SimpleDbTransactionManager` を直接使わないこと）。

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

#### 方法2: ユニバーサルDAO（`UniversalDao.Transaction`）

XMLの設定は方法1と同じ。実装は `UniversalDao.Transaction` を継承したクラスを作ります。

```java
private static final class FindPersonsTransaction extends UniversalDao.Transaction {

    private EntityList<Person> persons;

    FindPersonsTransaction() {
        // コンポーネント定義で設定した名前を指定する
        super("find-persons-transaction");
    }

    // このメソッドが自動的に別のトランザクションで実行される。
    // 正常終了でコミット、例外/エラーでロールバック。
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
// 生成すると別のトランザクションで実行される。
FindPersonsTransaction findPersonsTransaction = new FindPersonsTransaction();

// 結果を取得する。
EntityList<Person> persons = findPersonsTransaction.getPersons();
```

#### 方法3: Domaアダプタ（`requiresNew`）

Domaアダプタを使用している場合は、`DomaConfig#getTransactionManager` から取得した `TransactionManager` を使って別トランザクションで制御できます。

```java
DomaConfig.singleton()
        .getTransactionManager()
        .requiresNew(() ->
                DomaDaoRepository.get(ProjectDao.class).insert(project));
```

---

**注意点**:
- 業務トランザクション（ループハンドラが管理するトランザクション）とは完全に独立したトランザクションになります。別トランザクション内で例外が発生した場合、そのトランザクション自身はロールバックされます。
- `SimpleDbTransactionManager` を直接使わず、必ず `SimpleDbTransactionExecutor`（JDBCラッパーの場合）または `UniversalDao.Transaction`（ユニバーサルDAOの場合）を使ってください。

参照: libraries-database.json:s29, libraries-universal-dao.json:s20, adapters-doma-adaptor.json:s8

---
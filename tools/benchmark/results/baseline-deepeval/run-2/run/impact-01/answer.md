**結論**: Nablarchバッチで業務トランザクションとは別のトランザクションでSQLを実行するには、`SimpleDbTransactionManager`をコンポーネント定義に追加し、`SimpleDbTransactionExecutor`（JDBCラッパー）または`UniversalDao.Transaction`（ユニバーサルDAO）を使って実行する。業務トランザクションがロールバックされても、別トランザクション内でコミットされた更新は残る。

---

**根拠**:

#### アプローチ1: JDBCラッパー（`SimpleDbTransactionExecutor`）

**コンポーネント定義**（`connectionFactory`と`transactionFactory`は既存のものを流用可）:

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

**実装例**:

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

#### アプローチ2: ユニバーサルDAO（`UniversalDao.Transaction`）

コンポーネント定義はアプローチ1と同様。実装は`UniversalDao.Transaction`を継承したクラスを使う:

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

// 呼び出し側
FindPersonsTransaction findPersonsTransaction = new FindPersonsTransaction();
EntityList<Person> persons = findPersonsTransaction.getPersons();
```

#### アプローチ3: Domaアダプタ（`requiresNew`）

Domaアダプタを使っている場合は、`DomaConfig#getTransactionManager`から取得した`TransactionManager`の`requiresNew`で別トランザクションを実行できる:

```java
DomaConfig.singleton()
        .getTransactionManager()
        .requiresNew(() ->
                DomaDaoRepository.get(ProjectDao.class).insert(project));
```

---

**注意点**:
- `SimpleDbTransactionManager`を直接使うのではなく、必ず`SimpleDbTransactionExecutor`または`UniversalDao.Transaction`を介して使うこと。
- `transactionFactory`には`JdbcTransactionFactory`（アイソレーションレベル・タイムアウト設定あり）を指定するのが一般的。

参照: `libraries-database.json:s29`, `libraries-universal-dao.json:s20`, `adapters-doma-adaptor.json:s8`

---
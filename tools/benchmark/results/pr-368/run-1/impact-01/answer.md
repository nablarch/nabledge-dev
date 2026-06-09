これで全セクション内容が揃いました。Step 5 へ進みます。

---

## 回答

Nablarchバッチでは、業務トランザクションとは独立した別トランザクションでSQLを実行する機能が提供されています。業務処理がロールバックされても、別トランザクションの更新を確定できます。

### 方法 1: JDBCラッパーで実行する場合（SimpleDbTransactionExecutor）

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

**② `SimpleDbTransactionExecutor` を使ってSQLを実行する**

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

### 方法 2: ユニバーサルDAOで実行する場合（UniversalDao.Transaction）

**① コンポーネント設定ファイルの定義は方法 1 と同じ**

**② `UniversalDao.Transaction` を継承したクラスを作成する**

```java
private static final class FindPersonsTransaction extends UniversalDao.Transaction {

    private EntityList<Person> persons;

    FindPersonsTransaction() {
        // コンポーネント定義で指定した名前、またはSimpleDbTransactionManagerオブジェクトを指定できる
        super("find-persons-transaction");
    }

    // このメソッドが自動的に別のトランザクションで実行される。
    // 正常終了時はコミット、例外・エラー発生時はロールバックされる。
    @Override
    protected void execute() {
        persons = UniversalDao.findAllBySqlFile(Person.class, "FIND_PERSONS");
    }

    public EntityList<Person> getPersons() {
        return persons;
    }
}
```

**③ 呼び出し側**

```java
// 生成すると別のトランザクションで実行される
FindPersonsTransaction findPersonsTransaction = new FindPersonsTransaction();

// 結果を取得する
EntityList<Person> persons = findPersonsTransaction.getPersons();
```

### 補足：Domaアダプタを使用している場合

Domaを使用している場合は、`DomaConfig#getTransactionManager().requiresNew()` で別トランザクションを制御できます。

```java
DomaConfig.singleton()
    .getTransactionManager()
    .requiresNew(() ->
        DomaDaoRepository.get(ProjectDao.class).insert(project));
```

---

どちらの方法でも、業務トランザクションがロールバックされても、`SimpleDbTransactionManager` 配下で実行した更新はそのまま確定（コミット）されます。
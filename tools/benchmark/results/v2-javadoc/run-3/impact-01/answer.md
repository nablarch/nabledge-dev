セクション内容を読み込みました。回答を生成します。

**Step 5: 回答生成**

3つのセクションすべてが直接この質問に回答できる内容を持っています。Nablarchバッチに焦点を当てて回答を構成します。

**Step 6: Verify**

claims:
- `SimpleDbTransactionManager` をコンポーネント設定に定義する → s29に直接記述あり ✅
- `SimpleDbTransactionExecutor` を使用してSQLを実行する → s29に直接記述あり ✅
- `UniversalDao.Transaction` を継承したクラスを作成する → s20に直接記述あり ✅
- 業務処理が失敗した場合でも必ずデータベースへの変更を確定できる → s29に「業務処理が失敗した場合でも必ずデータベースへの変更を確定したい場合には、現在のトランザクションとは異なるトランザクションを定義してデータベースにアクセスする」と直接記述あり ✅
- Domaを使う場合は `DomaConfig.singleton().getTransactionManager().requiresNew(...)` → s8に直接記述あり ✅
- 正常終了した場合はコミット、例外/エラーの場合はロールバック → s20に直接記述あり ✅

verify_result = PASS

**Step 8: Output**

---

**結論**: `SimpleDbTransactionManager` を使った「個別トランザクション」を定義することで、業務トランザクションとは独立した別トランザクションでSQLを実行できます。業務トランザクションがロールバックされても、別トランザクション内でコミット済みの更新はそのまま残ります。

---

**根拠**:

### JDBCラッパー（低レベルAPI）を使う場合

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

---

### ユニバーサルDAOを使う場合

コンポーネント設定は上記と同じ。実装では `UniversalDao.Transaction` を継承したクラスを作成します。

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

```java
// インスタンス生成と同時に別のトランザクションで実行される
FindPersonsTransaction findPersonsTransaction = new FindPersonsTransaction();
EntityList<Person> persons = findPersonsTransaction.getPersons();
```

---

### Domaアダプタを使う場合

`DomaConfig` の `TransactionManager` を使い、`requiresNew` で別トランザクションを起動します。

```java
DomaConfig.singleton()
        .getTransactionManager()
        .requiresNew(() ->
                DomaDaoRepository.get(ProjectDao.class).insert(project));
```

---

**注意点**:
- いずれの方法も、`SimpleDbTransactionManager`（またはDomaのTransactionManager）で開始した個別トランザクション内で処理が正常終了すれば**その時点でコミット**されます。業務トランザクションが後でロールバックされても、個別トランザクションの更新は残ります。
- 逆に、個別トランザクション内で例外が発生した場合はその個別トランザクションのみロールバックされます。

参照: libraries-database.json:s29, libraries-universal-dao.json:s20, adapters-doma-adaptor.json:s8

---
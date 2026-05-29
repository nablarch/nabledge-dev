必要なセクション情報が揃いました。回答を生成します。

**結論の検証:**
- `SimpleDbTransactionManager` + `SimpleDbTransactionExecutor` (JDBCラッパー) → s29に明記
- `SimpleDbTransactionManager` + `UniversalDao.Transaction` (ユニバーサルDAO) → s20に明記
- `DomaConfig.singleton().getTransactionManager().requiresNew(...)` (Domaアダプタ) → s8に明記
- 「業務処理が失敗した場合でも必ずデータベースへの変更を確定したい場合」という文言 → s29に明記

verify結果: PASS

---

**結論**: `SimpleDbTransactionManager` を使って個別トランザクションを定義し、そのトランザクション内でSQLを実行することで、業務トランザクションのロールバックとは独立してコミットできます。

---

**根拠**:

#### JDBCラッパーを使う場合（`SimpleDbTransactionExecutor`）

コンポーネント設定ファイルに `SimpleDbTransactionManager` を定義します：

```xml
<component name="update-login-failed-count-transaction"
    class="nablarch.core.db.transaction.SimpleDbTransactionManager">
  <property name="connectionFactory" ref="connectionFactory" />
  <property name="transactionFactory" ref="transactionFactory" />
  <property name="dbTransactionName" value="update-login-failed-count-transaction" />
</component>
```

実装例（`SimpleDbTransactionExecutor` でラップして実行）：

```java
SimpleDbTransactionManager dbTransactionManager =
    SystemRepository.get("update-login-failed-count-transaction");

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

#### ユニバーサルDAOを使う場合（`UniversalDao.Transaction`）

同じコンポーネント設定ファイルの定義に加えて、`UniversalDao.Transaction` を継承したクラスを作成します：

```java
private static final class FindPersonsTransaction extends UniversalDao.Transaction {
    private EntityList<Person> persons;

    FindPersonsTransaction() {
        super("find-persons-transaction");  // コンポーネント定義の名前を指定
    }

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

`execute()` メソッドが別トランザクションで実行され、正常終了でコミット、例外発生でロールバックされます。

#### Domaアダプタを使う場合

`DomaConfig#getTransactionManager` の `requiresNew` を使います：

```java
DomaConfig.singleton()
        .getTransactionManager()
        .requiresNew(() ->
                DomaDaoRepository.get(ProjectDao.class).insert(project));
```

**注意点**: `SimpleDbTransactionExecutor` および `UniversalDao.Transaction` の内部で例外が発生した場合は、その個別トランザクションがロールバックされます（業務トランザクションの状態には影響しません）。

参照:
- `libraries-database.json:s29`
- `libraries-universal-dao.json:s20`
- `adapters-doma-adaptor.json:s8`

---
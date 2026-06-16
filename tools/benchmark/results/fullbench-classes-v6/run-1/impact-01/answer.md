**結論**: `SimpleDbTransactionManager` と `SimpleDbTransactionExecutor` を使用することで、業務トランザクションとは独立した別トランザクションでSQLを実行できます。この別トランザクションは独自にコミット・ロールバックするため、業務トランザクションがロールバックされても更新は残ります。

**根拠**:

**1. コンポーネント設定ファイルに `SimpleDbTransactionManager` を定義する**

```xml
<component name="update-login-failed-count-transaction"
    class="nablarch.core.db.transaction.SimpleDbTransactionManager">
  <!-- ConnectionFactory実装クラスを設定 -->
  <property name="connectionFactory" ref="connectionFactory" />
  <!-- TransactionFactory実装クラスを設定 -->
  <property name="transactionFactory" ref="transactionFactory" />
  <!-- トランザクションを識別する名前 -->
  <property name="dbTransactionName" value="update-login-failed-count-transaction" />
</component>
```

**2. `SimpleDbTransactionExecutor` を使って別トランザクションでSQLを実行する（JDBCラッパー使用時）**

```java
// システムリポジトリからSimpleDbTransactionManagerを取得
SimpleDbTransactionManager dbTransactionManager =
    SystemRepository.get("update-login-failed-count-transaction");

// SimpleDbTransactionExecutorを使用してトランザクションを実行
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

**ユニバーサルDAO使用時は `UniversalDao.Transaction` を使う**

```java
// UniversalDao.Transactionを継承したクラスを作成
private static final class MyTransaction extends UniversalDao.Transaction {
    FindPersonsTransaction() {
        super("find-persons-transaction"); // コンポーネント名を指定
    }
    @Override
    protected void execute() {
        // ここが別トランザクションで実行される
        UniversalDao.insert(entity);
    }
}
// インスタンス化すると自動的に別トランザクションで実行される
new MyTransaction();
```

**注意点**:
- `SimpleDbTransactionManager` を直接使うのではなく、必ず `SimpleDbTransactionExecutor`（JDBCラッパー）または `UniversalDao.Transaction`（UniversalDAO）を使うこと。
- `doTransaction()` 呼び出し時点でコミットが確定するため、その後の業務トランザクションのロールバックとは無関係に更新が確定する。

参照: libraries-database.json:s29, libraries-universal-dao.json:s20
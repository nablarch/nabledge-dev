**結論**: 可能です。`SimpleDbTransactionManager` と `SimpleDbTransactionExecutor` を使用することで、業務トランザクションとは独立した別トランザクションでSQLを実行できます。業務処理がロールバックされても、この別トランザクション内の更新はコミット済みとなるため残ります。

**根拠**:

コンポーネント設定ファイルに `SimpleDbTransactionManager` を定義します。

```xml
<component name="update-login-failed-count-transaction"
    class="nablarch.core.db.transaction.SimpleDbTransactionManager">
  <property name="connectionFactory" ref="connectionFactory" />
  <property name="transactionFactory" ref="transactionFactory" />
  <property name="dbTransactionName" value="update-login-failed-count-transaction" />
</component>
```

アプリケーションコードでは、`SimpleDbTransactionExecutor` を使ってSQLを実行します。

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

`SimpleDbTransactionExecutor#doTransaction()` を呼び出すことで、`SimpleDbTransactionManager` が管理する独立したトランザクション内でSQLが実行され、業務処理のトランザクションとは切り離してコミット／ロールバックされます。

**注意点**:
- `SimpleDbTransactionManager` を直接使うのではなく、必ず `SimpleDbTransactionExecutor` を介してトランザクション制御を行うこと。
- `connectionFactory` には `ConnectionFactory` 実装クラス、`transactionFactory` には `TransactionFactory` 実装クラス（例：`JdbcTransactionFactory`）を設定する。
- 典型的なユースケースはログイン失敗カウント更新など、「業務処理失敗時でも必ずDBへの変更を確定したい場合」。

参照: `libraries-database.json#s29`
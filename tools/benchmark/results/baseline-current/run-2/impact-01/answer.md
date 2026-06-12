**結論**: 業務トランザクションとは別の独立したトランザクションでSQLを実行するには、`SimpleDbTransactionManager` と `SimpleDbTransactionExecutor` を使用します。このトランザクションは業務トランザクションのロールバックの影響を受けず、独立してコミット・ロールバックを制御できます。

**根拠**:

コンポーネント設定ファイルに `SimpleDbTransactionManager` を定義します:

```xml
<component name="update-login-failed-count-transaction"
           class="nablarch.core.db.transaction.SimpleDbTransactionManager">
  <property name="connectionFactory" ref="connectionFactory" />
  <property name="transactionFactory" ref="transactionFactory" />
  <property name="dbTransactionName" value="update-login-failed-count-transaction" />
</component>
```

Javaでの実装例:

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

`SimpleDbTransactionExecutor` はトランザクションの開始・コミット・ロールバックを自動制御するラッパーです。業務処理がロールバックされても、このトランザクション内でコミットした更新は独立して残ります。

**注意点**:
- `SimpleDbTransactionManager` を直接操作せず、必ず `SimpleDbTransactionExecutor` を介してトランザクション制御を行うこと。
- `connectionFactory` と `transactionFactory` の設定が前提として必要。
- トランザクションタイムアウトを使用している場合、別トランザクションのタイムアウトは独立してチェックされる。

参照: `libraries-database.json#s29`、`libraries-transaction.json#s5`
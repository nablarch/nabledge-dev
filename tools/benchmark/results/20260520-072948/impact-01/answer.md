**結論**: Nablarchバッチで業務トランザクションとは独立したトランザクションでSQLを実行するには、主に2つの方法がある。

1. **`SimpleDbTransactionManager` + `SimpleDbTransactionExecutor`** を使って、任意のタイミングで別トランザクションでSQLを実行する
2. **`TransactionEventCallback#transactionAbnormalEnd`** を実装したハンドラを使う。これはロールバック後に自動的に新しいトランザクションで実行されるため、エラーログDBへの書き込みに適している

**根拠**:

### 方法1: SimpleDbTransactionManager を使って明示的に別トランザクションで実行

コンポーネント設定ファイルに `SimpleDbTransactionManager` を定義する。

```xml
<component name="update-login-failed-count-transaction" class="nablarch.core.db.transaction.SimpleDbTransactionManager">
  <property name="connectionFactory" ref="connectionFactory" />
  <property name="transactionFactory" ref="transactionFactory" />
  <property name="dbTransactionName" value="update-login-failed-count-transaction" />
</component>
```

実装では `SimpleDbTransactionExecutor` を使ってSQLを実行する（`SimpleDbTransactionManager` を直接使わないこと）。

```java
SimpleDbTransactionManager dbTransactionManager =
    SystemRepository.get("update-login-failed-count-transaction");

new SimpleDbTransactionExecutor<SqlResultSet>(dbTransactionManager) {
  @Override
  public SqlResultSet execute(AppDbConnection connection) {
    SqlPStatement statement = connection.prepareStatementBySqlId(
        "jp.co.tis.sample.action.SampleAction#findUser");
    statement.setLong(1, userId);
    return statement.retrieve();
  }
}.doTransaction();
```

ユニバーサルDAOを使う場合は `UniversalDao.Transaction` を継承したクラスを使う。

### 方法2: TransactionEventCallback を使ってロールバック後に自動実行（エラーログ書き込みに最適）

`LoopHandler`（トランザクションループ制御ハンドラ）は、後続ハンドラで例外・エラーが発生してロールバックした場合、**ロールバック後に新しいトランザクションで** `transactionAbnormalEnd` を呼び出す。コールバックが正常終了するとコミットされる。

```java
public static class ErrorLogHandler
    implements Handler<Object, Object>, TransactionEventCallback<Object> {

  @Override
  public Object handle(Object o, ExecutionContext context) {
    return context.handleNext(o);
  }

  @Override
  public void transactionNormalEnd(Object o, ExecutionContext ctx) {
    // 正常終了時の処理（同一トランザクションで実行）
  }

  @Override
  public void transactionAbnormalEnd(Throwable e, Object o, ExecutionContext ctx) {
    // ロールバック後、新しいトランザクションで実行される
    // ここでエラーログをDBに書き込む
  }
}
```

ハンドラキューの設定:

```xml
<list name="handlerQueue">
  <component class="nablarch.fw.handler.LoopHandler">
    <!-- プロパティへの設定は省略 -->
  </component>

  <!-- LoopHandlerの後続に配置する -->
  <component class="sample.ErrorLogHandler" />
</list>
```

**注意点**:
- 方法2で複数のハンドラが `TransactionEventCallback` を実装している場合、コールバック中に例外が発生すると残りのハンドラのコールバックは実行されない
- 方法1の `SimpleDbTransactionManager` を使う場合は、`SimpleDbTransactionManager` を直接使わず、必ず `SimpleDbTransactionExecutor`（またはUniversalDAO使用時は `UniversalDao.Transaction`）を介すこと

参照: `libraries-database.json:s29`, `libraries-universal-dao.json:s20`, `handlers-loop-handler.json:s6`
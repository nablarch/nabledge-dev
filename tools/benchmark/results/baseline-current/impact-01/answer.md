**結論**: Nablarchバッチで業務ロールバック後もDBにエラーログを書き込む方法は2つあります。バッチ専用の `TransactionEventCallback`（`LoopHandler`のコールバック機能）を使う方法と、`SimpleDbTransactionManager` で個別トランザクションを直接制御する方法です。

---

**根拠**:

### 方法1: LoopHandler の TransactionEventCallback（バッチ向け推奨）

`LoopHandler` は、後続ハンドラで例外/エラーが発生してロールバックした後に、**新しいトランザクション**でコールバック処理を実行します。コールバックが正常終了すると自動的にコミットされます。

```java
public class ErrorLoggingHandler
    implements Handler<Object, Object>, TransactionEventCallback<Object> {

  @Override
  public Object handle(Object o, ExecutionContext context) {
    return context.handleNext(o);
  }

  @Override
  public void transactionNormalEnd(Object o, ExecutionContext ctx) {
    // 正常終了時のコールバック（同一トランザクション内で実行）
  }

  @Override
  public void transactionAbnormalEnd(Throwable e, Object o, ExecutionContext ctx) {
    // ロールバック後に新しいトランザクションで呼ばれる
    // ここでエラーログをDBに書き込む → 自動コミットされる
  }
}
```

ハンドラキューの設定:
```xml
<list name="handlerQueue">
  <component class="nablarch.fw.handler.LoopHandler">
    <!-- 省略 -->
  </component>
  <!-- LoopHandlerより後続に設定する -->
  <component class="sample.ErrorLoggingHandler" />
</list>
```

### 方法2: SimpleDbTransactionManager で個別トランザクション

業務処理の任意の場所（例外ハンドリング箇所）で独立したトランザクションを実行できます。

コンポーネント設定:
```xml
<component name="error-log-transaction"
    class="nablarch.core.db.transaction.SimpleDbTransactionManager">
  <property name="connectionFactory" ref="connectionFactory" />
  <property name="transactionFactory" ref="transactionFactory" />
  <property name="dbTransactionName" value="error-log-transaction" />
</component>
```

実装例:
```java
SimpleDbTransactionManager txManager =
    SystemRepository.get("error-log-transaction");

new SimpleDbTransactionExecutor<Void>(txManager) {
  @Override
  public Void execute(AppDbConnection connection) {
    ParameterizedSqlPStatement stmt =
        connection.prepareParameterizedSqlStatementBySqlId(
            "com.example.ErrorLogAction#insertErrorLog");
    stmt.executeUpdateByObject(errorLog);
    return null;
  }
}.doTransaction(); // このトランザクションは業務トランザクションとは独立してコミットされる
```

---

**注意点**:
- `TransactionEventCallback` で複数ハンドラがコールバックを実装している場合、途中のコールバックで例外が発生すると残りのハンドラのコールバックは実行されません
- `SimpleDbTransactionManager` を使う方法では、コンポーネント設定に `connectionFactory` と `transactionFactory` の両方が必要です
- `SimpleDbTransactionExecutor#doTransaction()` は内部で begin → execute → commit/rollback を自動管理します

参照: `knowledge/component/libraries/libraries-database.json#s29`, `knowledge/component/handlers/handlers-loop-handler.json#s6`
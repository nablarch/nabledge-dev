**質問**: バッチで DB を更新しているんだけど、コミットのタイミングやトランザクションの区切りがどこで決まっているのかよく分からない。Nablarch でトランザクションの境界って何で決まる？

---

**結論**: Nablarch のトランザクション境界は `TransactionManagementHandler`（トランザクション制御ハンドラ）が決定する。本ハンドラの往路でトランザクションを開始し、復路でコミット、例外時にロールバックする。制御対象は `transactionFactory` プロパティに指定した `TransactionFactory` 実装で取得し、スレッド上で管理される。`DatabaseConnectionManagementHandler`（DB 接続管理ハンドラ）より後ろに配置する必要がある。 — `component/handlers/handlers-transaction_management_handler.json#s3`、`component/handlers/handlers-transaction_management_handler.json#s4`

**① ハンドラの役割**
`TransactionManagementHandler` はトランザクション制御対象をスレッド上で管理する。`transactionFactory` プロパティに `TransactionFactory` 実装を設定（DB の場合は `JdbcTransactionFactory`）し、スレッド識別名は `transactionName` プロパティ（デフォルト `transaction`）で指定する。 — `component/handlers/handlers-transaction_management_handler.json#s4`

**② 配置制約**
`DatabaseConnectionManagementHandler` より後ろに配置する。トランザクションを制御する時点で、管理対象の DB 接続がスレッド上に存在している必要があるため。 — `component/handlers/handlers-transaction_management_handler.json#s3`

**③ DB 接続の取得**
`DatabaseConnectionManagementHandler` は `connectionFactory` プロパティに `ConnectionFactory` 実装（例: `BasicDbConnectionFactoryForDataSource`）を設定し、DB 接続を取得・解放する。 — `component/handlers/handlers-database_connection_management_handler.json#s3`

**④ 設定例**
```xml
<component class="nablarch.common.handler.TransactionManagementHandler">
  <property name="transactionFactory" ref="databaseTransactionFactory" />
  <property name="transactionName" value="name" />
</component>

<component name="databaseTransactionFactory"
    class="nablarch.core.db.transaction.JdbcTransactionFactory">
</component>
```

複数トランザクションを扱う場合は `transactionName` 設定が必須。`DbConnectionManagementHandler#connectionName` に設定した値と同じ値を `transactionName` に指定する（`connectionName` 未設定時は `transactionName` も省略可）。 — `component/handlers/handlers-transaction_management_handler.json#s4`

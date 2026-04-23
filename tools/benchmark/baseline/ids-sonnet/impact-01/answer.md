**結論**: Nablarch バッチのトランザクション境界は、主に **`LoopHandler`** の設定によって決まる。コミットのタイミングは `commitInterval`（件数）で制御し、トランザクション制御対象は `transactionFactory` に設定した `TransactionFactory` 実装クラスで決まる。

**根拠**:

1. **トランザクション制御の仕組み**: `LoopHandler` の `transactionFactory` プロパティに `TransactionFactory` 実装クラス（例: `JdbcTransactionFactory`）を設定することで、トランザクション制御対象を取得してスレッド上で管理する。トランザクション識別名のデフォルトは `transaction` で、変更する場合は `transactionName` プロパティに設定する。(`component/handlers/handlers-loop_handler.json:s5`)

2. **コミット間隔の設定**: `LoopHandler` の `commitInterval` プロパティにコミット間隔（件数）を設定する。例えば `value="1000"` とすると 1000 件処理ごとにコミットされる。間隔を大きくするとスループットが向上する。(`component/handlers/handlers-loop_handler.json:s6`)

3. **Web 等との違い**: バッチでなくリクエスト単位のトランザクション制御が必要な場合は `TransactionManagementHandler` を使用する。こちらも同様に `transactionFactory` と `transactionName` で制御対象を設定する。(`component/handlers/handlers-transaction_management_handler.json:s4`)

4. **複数 DB のトランザクション**: 複数 DB を扱う場合は、`TransactionManagementHandler` をハンドラキューに複数設定し、それぞれ異なる `transactionName` を指定する。(`component/handlers/handlers-transaction_management_handler.json:s7`)

**注意点**:
- `DbConnectionManagementHandler` の `connectionName` と `LoopHandler`（または `TransactionManagementHandler`）の `transactionName` は **同じ値を設定する必要がある**。`connectionName` が未設定の場合は `transactionName` の設定も省略可。
- バッチで `commitInterval` を大きくしすぎると、障害時の再処理範囲（ロールバック対象）が広がる点に注意。

参照: component/handlers/handlers-loop_handler.json:s5, component/handlers/handlers-loop_handler.json:s6, component/handlers/handlers-transaction_management_handler.json:s4, component/handlers/handlers-transaction_management_handler.json:s7
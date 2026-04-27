**結論**: `MultiThreadExecutionHandler` で並列化する場合、DBコネクションはスレッドごとに独立して確保し、排他制御は「ロック取得→データ取得→更新」の順で1件ずつ行うことが必須。

**根拠**:

**① スレッド数分のコネクションが必要**
親スレッド・サブスレッドそれぞれに `DatabaseConnectionManagementHandler` を設定し、コネクションを独立して確保する。サブスレッド10本なら合計11コネクションが必要。 (`component/handlers/handlers-multi_thread_execution_handler.json:s7`)

**② ハンドラ配置の位置**
- 親スレッド側でDBアクセスする場合: `MultiThreadExecutionHandler` より**前**に `DatabaseConnectionManagementHandler` を置く
- サブスレッド側でDBアクセスする場合: **後**のサブスレッド用ハンドラ構成に同ハンドラとトランザクション制御ハンドラを置く (`component/handlers/handlers-multi_thread_execution_handler.json:s7`)

**③ スレッドセーフの保証が必須**
後続ハンドラおよびバッチアクションはスレッドセーフな実装が必要。スレッドセーフでない処理を複数スレッドで実行すると、予期せぬ例外やデータ不整合が発生する。 (`component/handlers/handlers-multi_thread_execution_handler.json:s5`)

**④ 悲観ロックはロック時間を最小化する順序で取得**
バッチ処理では、前処理でロック対象の主キーのみを取得し、本処理で1件ずつロックを取得してからデータ取得・更新すること。理由は、(1) データ取得から更新の間に他プロセスによる更新を防ぐ、(2) ロック時間を短くし並列処理への影響を最小化するため。 (`component/libraries/libraries-exclusive_control.json:s4`)

**⑤ マルチプロセス化（常駐バッチ）の実装パターン**
`DatabaseRecordReader` を使う場合、`beforeReadRecords()` コールバックで悲観ロックSQLを別トランザクション（`SimpleDbTransactionExecutor`）で実行し、自身がロックした未処理データだけを抽出する。`processId` は `UUID.randomUUID().toString()` で一意に生成する。 (`processing-pattern/nablarch-batch/nablarch-batch-nablarch_batch_multiple_process.json:s1`)

**⑥ サブスレッド例外時のロールバック**
サブスレッドに `DatabaseConnectionManagementHandler` と `TransactionManagementHandler` を設定している場合、例外が発生したスレッドはロールバックされ、親スレッドが全サブスレッドへ停止要求を送る。`InterruptedException` を捕捉している場合は再スローして異常終了させること。 (`component/handlers/handlers-multi_thread_execution_handler.json:s8`)

**注意点**:
- `LoopHandler` の `transactionName` と `DbConnectionManagementHandler` の `connectionName` は同じ値を設定すること。不一致の場合、トランザクション制御が意図しないDB接続に対して働く。 (`component/handlers/handlers-loop_handler.json:s5`)
- 排他制御には UniversalDao の使用が推奨される。 (`processing-pattern/nablarch-batch/nablarch-batch-feature_details.json:s6`)

参照: component/handlers/handlers-multi_thread_execution_handler.json:s5, component/handlers/handlers-multi_thread_execution_handler.json:s7, component/handlers/handlers-multi_thread_execution_handler.json:s8, component/libraries/libraries-exclusive_control.json:s4, processing-pattern/nablarch-batch/nablarch-batch-nablarch_batch_multiple_process.json:s1, component/handlers/handlers-loop_handler.json:s5, processing-pattern/nablarch-batch/nablarch-batch-feature_details.json:s6
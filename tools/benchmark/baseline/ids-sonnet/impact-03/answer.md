**結論**: `MultiThreadExecutionHandler` を使うとサブスレッドで並列DB更新が可能。各スレッドは独立したDB接続を持ち、1スレッドで例外が発生すると他スレッドは現在の処理を完了してから安全に終了する。

**根拠**:

**スレッド数の設定**: `concurrentNumber` プロパティで並列数を指定する。例として8スレッド並列の場合は以下のように設定する。（`component/handlers/handlers-multi_thread_execution_handler.json:s5`）
```xml
<component class="nablarch.fw.handler.MultiThreadExecutionHandler">
  <property name="concurrentNumber" value="8" />
</component>
```

**DB接続の持ち方**: サブスレッドでDBアクセスが必要な場合、`MultiThreadExecutionHandler` より後のサブスレッド用ハンドラ構成に `DatabaseConnectionManagementHandler`（およびトランザクション制御ハンドラ）を設定する必要がある。コネクション数は「親スレッド分 + サブスレッド数分」が必要。例えばサブスレッド10本なら合計11コネクションが必要。（`component/handlers/handlers-multi_thread_execution_handler.json:s7`）

**例外発生時の挙動**: サブスレッドで予期せぬ例外が発生した場合、`ThreadPoolExecutor#shutdownNow()` が呼ばれ、以下の順序で処理される。（`component/handlers/handlers-multi_thread_execution_handler.json:s8`）
1. 例外が発生したスレッドは処理中断・ロールバック
2. 親スレッドがデータリーダをクローズ
3. 親スレッドが全サブスレッドに停止要求
4. 各サブスレッドはデータリーダがクローズされているため、**現在実行中の処理が終わったタイミングで正常終了**（強制中断ではない）

**注意点**:
- `MultiThreadExecutionHandler` 以降のハンドラ・バッチアクションはスレッドセーフな実装が必須。スレッドセーフでない実装だとデータ不整合が発生する。（`component/handlers/handlers-multi_thread_execution_handler.json:s5`）
- `InterruptedException` を捕捉している場合は、割り込み要求を無視せず例外を再送出するなどして異常終了させること。そうしないと停止要求に応答できなくなる。（`component/handlers/handlers-multi_thread_execution_handler.json:s8`）
- `DatabaseConnectionManagementHandler` の `connectionName` と `LoopHandler` の `transactionName` は値を合わせる必要がある。（`component/handlers/handlers-loop_handler.json:s5`）

参照: component/handlers/handlers-multi_thread_execution_handler.json:s5, component/handlers/handlers-multi_thread_execution_handler.json:s7, component/handlers/handlers-multi_thread_execution_handler.json:s8, component/handlers/handlers-loop_handler.json:s5
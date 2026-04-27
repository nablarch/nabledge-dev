**質問**: 常駐バッチが遅いので複数スレッドで並列実行して速くしたい。各スレッドで DB 更新したいんだけど、接続はどう持つ？ スレッドの 1 つで例外が出たら他はどうなる？

---

**結論**: `MultiThreadExecutionHandler`（マルチスレッド実行制御ハンドラ）の `concurrentNumber` プロパティで並列数を指定し、サブスレッド側のハンドラ構成に `DatabaseConnectionManagementHandler` と `TransactionManagementHandler` を組み込んで各スレッド独自の DB 接続・トランザクションを持たせる。サブスレッドで例外が発生した場合、そのスレッドはロールバックされ、親スレッドが他スレッドに停止要求を出して安全に終了させる。 — `component/handlers/handlers-multi_thread_execution_handler.json#s7`、`component/handlers/handlers-multi_thread_execution_handler.json#s8`

**① DB 接続の持ち方**
- 親スレッドで DB アクセスが必要な場合: 本ハンドラより **前** に `DatabaseConnectionManagementHandler` を配置する。
- サブスレッドで DB アクセスが必要な場合: 本ハンドラより **後** のサブスレッド用ハンドラ構成に `DatabaseConnectionManagementHandler` を配置する（`TransactionManagementHandler` も同様）。
- 親・サブ両方で DB アクセスする場合、最低2つの DB コネクションが必要。サブスレッドが複数の場合はスレッド数分が追加で必要（例: サブスレッド10なら合計11コネクション）。 — `component/handlers/handlers-multi_thread_execution_handler.json#s7`

**② 例外発生時の振る舞い**
サブスレッドで予期せぬ例外が発生すると、`ThreadPoolExecutor#shutdownNow()` が呼ばれ、処理中の他サブスレッドをデータ処理完了後に安全に終了させる。サブスレッドに `DatabaseConnectionManagementHandler` と `TransactionManagementHandler` を設定した場合の詳細動作:
1. 例外発生スレッドは処理が中断されロールバックされる。
2. 親スレッドは各サブスレッドで使用されるデータリーダをクローズする。
3. 親スレッドは全サブスレッドに対し停止要求を行う。
4. 各サブスレッドはデータリーダがクローズされているため、実行中の処理が終わったタイミングで正常終了する。 — `component/handlers/handlers-multi_thread_execution_handler.json#s8`

**③ トランザクション境界**
サブスレッド側のトランザクションは、サブスレッド用ハンドラ構成に設定した `TransactionManagementHandler` が担う。往路で開始、復路でコミット、例外時にロールバック。`DatabaseConnectionManagementHandler` より後ろに配置する必要がある。 — `component/handlers/handlers-transaction_management_handler.json#s3`

**注意点**
- `InterruptedException` を捕捉している場合は、割り込み要求により安全に処理できないことを示すため、例外を送出するなどで処理を異常終了させる。 — `component/handlers/handlers-multi_thread_execution_handler.json#s8`
- 後続のハンドラやバッチアクションはスレッドセーフな実装が必要。スレッドセーフでない処理を並列実行するとデータ不整合・予期せぬ例外が発生する。 — `component/handlers/handlers-multi_thread_execution_handler.json#s5`

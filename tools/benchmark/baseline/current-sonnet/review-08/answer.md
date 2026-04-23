**結論**: 常駐バッチを `MultiThreadExecutionHandler` でマルチスレッド化する場合、①DB接続はスレッドごとに `DbConnectionManagementHandler`（サブスレッド側）で個別取得すること、②バッチアクション内の共有インスタンス変数はスレッドセーフなクラスで保護すること、③常駐バッチ特有の「遅いスレッドが次周回の開始を遅らせる」問題に注意し、新規開発では `db_messaging` への切替えを検討すること。

---

**根拠**:

1. **並列数の設定**
   `MultiThreadExecutionHandler` の `concurrentNumber` プロパティで後続ハンドラの並列実行数を指定できる。（`component/handlers/handlers-multi_thread_execution_handler.json:s5`）
   ```xml
   <component class="nablarch.fw.handler.MultiThreadExecutionHandler">
     <property name="concurrentNumber" value="8" />
   </component>
   ```

2. **DB接続はスレッドごとに分離する**
   `DbConnectionManagementHandler` はスレッド上でDB接続を管理するハンドラ。`MultiThreadExecutionHandler`（No.11）の**後ろ（サブスレッド側）**に別途配置することで、各スレッドが独立した接続を持つ（`processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s1` の常駐バッチ最小構成 No.12 参照）。このハンドラが未設定だとスレッド間で接続が共有されてしまい、データ不整合を引き起こす。

3. **TransactionManagementHandler はDbConnectionManagementHandler の後に置く**
   トランザクション制御ハンドラはスレッド上にDB接続が存在する必要があるため、必ず `DbConnectionManagementHandler` より後に配置すること。また `DbConnectionManagementHandler` を使う場合は `TransactionManagementHandler` をセットで設定しないとDB変更が全て破棄される。（`component/handlers/handlers-database_connection_management_handler.json:s1`、`component/handlers/handlers-transaction_management_handler.json:s3`）

4. **後続ハンドラとバッチアクションはスレッドセーフであること**
   `MultiThreadExecutionHandler` 以降の処理はすべてスレッドセーフな実装が必要。スレッドセーフでない処理を複数スレッドで実行すると、予期せぬ例外やデータ不整合が発生する。（`component/handlers/handlers-multi_thread_execution_handler.json:s5`）

5. **バッチアクション内の状態保持には AtomicInteger 等を使う**
   バッチアクションのインスタンス変数を複数スレッドから更新する場合、`AtomicInteger` などのスレッドセーフなクラスを使用してスレッドセーフを保証すること。（`processing-pattern/nablarch-batch/nablarch-batch-nablarch_batch_retention_state.json:s1`）

6. **悲観ロックによる重複処理防止**
   複数スレッドが同じDBレコードを処理しないよう、`DatabaseRecordListener.beforeReadRecords()` コールバックで悲観ロックSQL を別トランザクション（`SimpleDbTransactionExecutor`）で実行し、各スレッドが処理対象データを排他的に取得する設計が必要。（`processing-pattern/nablarch-batch/nablarch-batch-nablarch_batch_multiple_process.json:s1`）

---

**注意点**:

- **常駐バッチ固有の遅延問題**: 常駐バッチをマルチスレッドで動かすと、遅いスレッドが終了するまで他のスレッドが待機し、次の監視周回の開始が遅れる可能性がある。この問題が発生している（または発生リスクがある）場合は、`db_messaging`（テーブルをキューとしたメッセージング）への移行を検討すること。（`processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s1`）
- **ExeucutionContext のスコープ**: スレッドごとの状態は「リクエストスコープ」、バッチ全体の共有状態は「セッションスコープ」で保持できるが、状態がわかりづらくなるため、バッチアクション側で状態を保持する実装が推奨。（`processing-pattern/nablarch-batch/nablarch-batch-nablarch_batch_retention_state.json:s1`）

参照: component/handlers/handlers-multi_thread_execution_handler.json:s5, processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s1, component/handlers/handlers-database_connection_management_handler.json:s1, component/handlers/handlers-transaction_management_handler.json:s3, processing-pattern/nablarch-batch/nablarch-batch-nablarch_batch_retention_state.json:s1, processing-pattern/nablarch-batch/nablarch-batch-nablarch_batch_multiple_process.json:s1
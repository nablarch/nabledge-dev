**結論**: 常駐バッチを複数スレッドで並列実行するには `MultiThreadExecutionHandler` の `concurrentNumber` を設定する。各サブスレッド用に `DatabaseConnectionManagementHandler`（業務処理用）＋ `TransactionManagementHandler`（業務処理用）をハンドラキューの **MultiThreadExecutionHandler より後ろ**（サブスレッド側）に置くことで、各スレッドが独立したDB接続とトランザクションを持つ。いずれか1スレッドで予期せぬ例外が発生した場合、他のスレッドは現在処理中のレコードを完了させた後に正常終了する。

---

**根拠**:

1. **スレッド数の設定**  
   `MultiThreadExecutionHandler` の `concurrentNumber` プロパティで並列実行数を変更できる。デフォルトは1。  
   `component/handlers/handlers-multi_thread_execution_handler.json:s5`
   ```xml
   <component class="nablarch.fw.handler.MultiThreadExecutionHandler">
     <!-- 後続ハンドラを8多重で実行する -->
     <property name="concurrentNumber" value="8" />
   </component>
   ```

2. **DB接続の持ち方（スレッドごとに独立）**  
   サブスレッド側でDBアクセスが必要な場合は、`MultiThreadExecutionHandler` より後ろのハンドラ構成に `DatabaseConnectionManagementHandler` および `TransactionManagementHandler` を設定する必要がある。  
   `component/handlers/handlers-multi_thread_execution_handler.json:s7`
   > 親スレッド・サブスレッドの両方でDBアクセスする場合、最低2つのDBコネクションが必要。サブスレッドが複数の場合はスレッド数分が追加で必要（例: サブスレッド10の場合、合計11コネクション）。

   常駐バッチのハンドラ構成では、No.12〜13がサブスレッド側に位置している：  
   `processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s1`
   - No.11: `MultiThreadExecutionHandler`（メイン） ← ここを境にサブスレッド
   - No.12: `DatabaseConnectionManagementHandler`（業務処理用）（サブ）
   - No.13: `LoopHandler`（サブ） ← 業務トランザクション管理

3. **例外発生時の他スレッドへの影響**  
   サブスレッドで予期せぬ例外が発生した場合の動作：  
   `component/handlers/handlers-multi_thread_execution_handler.json:s8`
   1. 例外が発生したサブスレッドは処理が中断されロールバックされる
   2. 親スレッドは各サブスレッドで使用されるデータリーダをクローズする
   3. 親スレッドは全サブスレッドに対し停止要求（`ThreadPoolExecutor#shutdownNow()`）を行う
   4. 各サブスレッドはデータリーダがクローズされているため、**実行中の処理が終わったタイミングで正常終了する**

   → つまり「即座に強制終了」ではなく「処理中のレコードを処理し終えてから安全に停止する」。

---

**注意点**:

- **スレッドセーフな実装が必須**: `MultiThreadExecutionHandler` 以降のハンドラおよびバッチアクションはスレッドセーフな実装が必要。スレッドセーフでない処理を複数スレッドで動かすと、予期せぬ例外やデータ不整合が発生する。  
  `component/handlers/handlers-multi_thread_execution_handler.json:s5`

- **常駐バッチのマルチスレッド化には設計上の問題あり**: 並列実行された全スレッドが終了するまで次のデータ登録の監視が始まらないため、処理が遅いスレッドがあると要求データの取り込みが遅延する。新規開発プロジェクトでは常駐バッチより **`db_messaging`（テーブルをキューとして使ったメッセージング）** の使用が推奨されている。  
  `processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s1`、`guide/nablarch-patterns/nablarch-patterns-Nablarchでの非同期処理.json:s2`

- **`InterruptedException` は必ず再送出すること**: 業務コード内で `InterruptedException` を捕捉している場合は、割り込み要求を握りつぶさず例外を送出して処理を異常終了させること。そうしないとスレッド停止シーケンスが正常に動作しない。  
  `component/handlers/handlers-multi_thread_execution_handler.json:s8`

- **コネクション数の確保**: スレッド数分のDB接続が必要。コネクションプールのサイズをスレッド数＋親スレッド分（例: 8スレッドなら最低9コネクション）以上に設定すること。  
  `component/handlers/handlers-multi_thread_execution_handler.json:s7`

---

参照: component/handlers/handlers-multi_thread_execution_handler.json:s1, component/handlers/handlers-multi_thread_execution_handler.json:s5, component/handlers/handlers-multi_thread_execution_handler.json:s7, component/handlers/handlers-multi_thread_execution_handler.json:s8, processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s1, guide/nablarch-patterns/nablarch-patterns-Nablarchでの非同期処理.json:s2
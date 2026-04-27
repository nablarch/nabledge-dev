**質問**: 常駐バッチの処理が遅いので並列実行で速くしたい。複数スレッドで同時に DB を更新することになるが、接続や排他の扱いで注意することは？

---

**結論**: Nablarch の `MultiThreadExecutionHandler` で並列実行数を指定する。後続ハンドラ・バッチアクションはスレッドセーフである必要があり、DB 接続はサブスレッド数＋親スレッド分が追加で必要。サブスレッド側の DB アクセスには `database_connection_management_handler` と `transaction_management_handler` をサブスレッド用ハンドラ構成に組み込む。 — `component/handlers/handlers-multi_thread_execution_handler.json#s5`

**① 並列数の指定**
デフォルトはサブスレッド1つ。`concurrentNumber` プロパティで変更する:

```xml
<component class="nablarch.fw.handler.MultiThreadExecutionHandler">
  <property name="concurrentNumber" value="8" />
</component>
```
後続のハンドラやバッチアクションはスレッドセーフでなければならない。スレッドセーフでない処理を並列実行すると、予期せぬ例外やデータ不整合が発生する。 — `component/handlers/handlers-multi_thread_execution_handler.json#s5`

**② DB 接続の持ち方**
- 親スレッド側で DB アクセスが必要なら、本ハンドラより **前** に `database_connection_management_handler` を配置する。
- サブスレッド側で DB アクセスが必要なら、本ハンドラより **後** のサブスレッド用ハンドラ構成に `database_connection_management_handler` を配置する（`transaction_management_handler` も同様）。
- 親・サブ両方で DB アクセスする場合、最低2つの DB コネクションが必要。サブスレッドが複数の場合はスレッド数分が追加で必要（例: サブスレッド10なら合計11コネクション）。 — `component/handlers/handlers-multi_thread_execution_handler.json#s7`

**③ サブスレッドで例外が出たときの振る舞い**
サブスレッドで予期せぬ例外が発生した場合、`ThreadPoolExecutor#shutdownNow()` を呼び出し、他スレッドをデータ処理完了後に安全に終了させる。`database_connection_management_handler` と `transaction_management_handler` をサブスレッド側に設定した場合の挙動:
1. 例外が発生したサブスレッドは処理が中断されロールバックされる。
2. 親スレッドは各サブスレッドで使用されるデータリーダをクローズする。
3. 親スレッドは全サブスレッドに対し停止要求を行う。
4. 各サブスレッドはデータリーダがクローズされているため、実行中の処理が終わったタイミングで正常終了する。 — `component/handlers/handlers-multi_thread_execution_handler.json#s8`

**注意点**
- `InterruptedException` を捕捉している場合は、割り込み要求により安全に処理できないことを示しているため、例外を送出するなどで処理を異常終了させること。 — `component/handlers/handlers-multi_thread_execution_handler.json#s8`

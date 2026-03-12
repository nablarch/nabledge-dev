**結論**: Nablarch 6バッチのエラーハンドリングは、バッチ種別（都度起動バッチ・常駐バッチ）と例外の種類によって対応が異なります。基本的には `TransactionAbnormalEnd` / `ProcessAbnormalEnd` を送出してハンドラに処理を委譲し、リトライが必要な場合は `RetryHandler` を利用します。

**根拠**:

### 1. バッチ種別による対応の違い

**都度起動バッチ**:
- `TransactionAbnormalEnd` を送出するとバッチ処理が**異常終了**となる
- エラーが発生したら処理を中断するのが基本動作

**常駐バッチ**:
- `TransactionAbnormalEnd` を送出すると、`RetryHandler` により**処理が継続**される
- ただし、バッチ処理がリランできる設計になっている必要がある

### 2. 障害ログの出力方法

`FailureLogUtil` を使用して障害ログを出力する:

```java
// 例外を捕捉してログ出力する場合
try {
    // 業務処理
} catch (UserNotFoundException e) {
    FailureLogUtil.logError(e, inputData, "USER_NOT_FOUND");
}
```

バッチで障害検知時に処理を終了したい場合は、`TransactionAbnormalEnd` または `ProcessAbnormalEnd` を送出し、例外ハンドラ（`global_error_handler` 等）に障害ログ出力を委譲する:

```java
// 自ら例外を生成する場合
if (user == null) {
    throw new TransactionAbnormalEnd(100, "USER_NOT_FOUND");
}

// 例外を捕捉した場合
try {
    // 業務処理
} catch (UserNotFoundException e) {
    throw new ProcessAbnormalEnd(100, e, "USER_NOT_FOUND");
}
```

### 3. リトライハンドラ（RetryHandler）

クラス名: `nablarch.fw.handler.RetryHandler`

デッドロックのように単純リトライでリカバリ可能なエラーに対して自動リトライを制御する。`Retryable` インターフェースを実装した実行時例外をリトライ可能とみなす。

リトライ上限の設定方法:
- **リトライ回数による上限**: `CountingRetryContext`
- **経過時間による上限**: `TimeRetryContext`

### 4. RequestThreadLoopHandler の例外処理（常駐バッチ向け）

| 例外/エラー | 処理内容 |
|---|---|
| `ServiceUnavailable` | 一定時間待機後に後続ハンドラに再委譲 |
| `ProcessStop` | 本ハンドラの処理を終了 |
| `ProcessAbnormalEnd` | 捕捉した例外を再送出 |
| `ServiceError` | ログ出力後、`Retryable` を送出 |
| `RuntimeException` | FATALログ出力後、`Retryable` を送出 |
| `OutOfMemoryError` | 標準エラー出力後にFATALログ出力、`Retryable` を送出 |
| `VirtualMachineError` | そのまま再送出 |

### 5. ProcessResidentHandler の例外処理（常駐バッチ向け）

| 例外の種類 | 処理内容 |
|---|---|
| `ServiceUnavailable` | データ監視間隔分待機後に後続ハンドラを再実行 |
| リトライ可能例外（`RetryUtil#isRetryable()` が真） | 捕捉した例外をそのまま再送出 |
| プロセス異常終了例外（`ProcessAbnormalEnd` など） | 捕捉した例外をそのまま再送出 |
| 上記以外 | ログ記録後、`RetryableException` でラップして再送出 |

**注意点**:
- 都度起動バッチでは「特定の例外を無視して処理継続する（ロールバック後に継続）」機能はサポートされていない（Jakarta Batchとの機能比較より `×`）。この要件が必要な場合はカスタムハンドラを追加して対応すること。
- `RetryHandler` によるリトライは、Jakarta Batchのように例外が発生したデータの単純なリトライや柔軟な例外指定はできない。柔軟なリトライが必要な場合はカスタムハンドラを追加すること。
- 障害コードのコード体系はプロジェクト毎に規定すること。
- DB接続エラー（`DbConnectionException`）は `RetryHandler` により自動処理される。一意制約違反（`DuplicateStatementException`）のハンドリング方法は別途参照のこと。

参照:
- `nablarch-batch-nablarch_batch_error_process.json#continue-on-error`
- `handlers-retry_handler.json#handler-class-name`
- `handlers-request_thread_loop_handler.json#error-handling`
- `handlers-process_resident_handler.json#exception-handling`
- `libraries-failure_log.json#failure-log-logging`
- `nablarch-batch-architecture.json#handler-list`
- `nablarch-batch-functional_comparison.json#functional-comparison`
- `libraries-database.json#database-exception-types`

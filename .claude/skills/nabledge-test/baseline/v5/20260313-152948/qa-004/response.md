**結論**: Nablarchバッチのエラーハンドリングは、バッチの種別（Nablarchバッチ／JSR352準拠バッチ）と、エラー発生時に「処理を継続するか」「異常終了させるか」によって方法が異なります。

---

**根拠**:

## Nablarchバッチの場合

### エラー発生時に処理を継続する（常駐バッチのみ）

エラー発生時の処理継続は **常駐バッチのみ** 対応しており、都度起動バッチは非対応です。

常駐バッチでは `TransactionAbnormalEnd` を送出すると、`RetryHandler` により処理が継続されます。ただし、バッチ処理がリランできるよう設計されている必要があります（処理対象レコードにステータスを持たせ、成功・失敗時にステータスを更新する実装が必要）。

> 補足: 都度起動バッチで `TransactionAbnormalEnd` を送出すると、バッチ処理が異常終了となります。

### バッチ処理を異常終了させる

処理を継続せずに異常終了させたい場合は `ProcessAbnormalEnd` を送出します。プロセス終了コードはこのクラスに指定した値となります。

### リトライ制御（RetryHandler）

`RetryHandler` はデッドロックのような単純リトライでリカバリ可能なエラーを自動リトライ制御するハンドラです。`Retryable` を実装した実行時例外をリトライ可能とみなし、後続ハンドラを再実行します。

- クラス: `nablarch.fw.handler.RetryHandler`
- リトライ上限: リトライ回数による上限設定、または経過時間による上限設定

---

## JSR352準拠バッチの場合

### 例外ハンドリングの方針

NablarchはJSR352準拠バッチにおいて例外を捕捉せず、**JSR352の実装側で例外ハンドリング**を行います。これはWebアプリケーションやNablarchバッチとは異なる特有の振る舞いです。

例外発生時のバッチ状態（batch status、exit status）はJSR352仕様に従い、リトライや継続有無もジョブ定義に従った動作となります。

### 運用担当者向けエラーログの出力と異常終了

```java
@Named
@Dependent
public class SampleBatchlet extends AbstractBatchlet {

    @Override
    public String process() throws Exception {
        try {
            // 省略
        } catch (FileNotFoundException e) {
            OperationLogger.write(
                    LogLevel.ERROR,
                    "ファイルが存在しません。正しく受信できているか確認してください。",
                    e);
            throw e;  // 例外を再送出して異常終了させる
        }
        // 省略
    }
}
```

出力例:
```
ERROR operator ファイルが存在しません。正しく受信できているか確認してください。
```

### 終了コード

| 終了種別 | コード | 条件 |
|---|---|---|
| 正常終了 | 0 | 終了ステータスが"WARNING"以外かつ `BatchStatus.COMPLETED` |
| 異常終了 | 1 | 終了ステータスが"WARNING"以外かつ `BatchStatus.COMPLETED` 以外 |
| 警告終了 | 2 | 終了ステータスが"WARNING" |

警告終了させる場合は chunk または batchlet 内で `JobContext#setExitStatus("WARNING")` を呼び出します。

---

**注意点**:
- Nablarchバッチでエラー継続（`TransactionAbnormalEnd` + `RetryHandler`）が使えるのは **常駐バッチのみ**。都度起動バッチでは使えません。
- バッチ処理をリランできるよう設計するには、フレームワーク機能の提供はなく（ファイル入力の `ResumeDataReader` を除く）、アプリケーション側でレコードのステータス管理を実装する必要があります。
- JSR352準拠バッチではNablarchが例外を捕捉しないため、エラーハンドリングはJSR352の仕組みに委ねる設計となっています。

参照:
- `nablarch-batch-nablarch_batch_error_process.json#s2`
- `nablarch-batch-nablarch_batch_error_process.json#s3`
- `jakarta-batch-architecture.json#s5`
- `jakarta-batch-operator_notice_log.json#s3`
- `handlers-retry_handler.json#s1`
- `jakarta-batch-run_batch_application.json#s2`

**結論**: Nablarchバッチのエラーハンドリングには、「異常終了」「エラー継続（常駐バッチのみ）」「特定例外でのコミット」「リラン設計」の4つのアプローチがあります。

---

#### 1. バッチ処理を異常終了させる

アプリケーションでエラーを検知し、処理を継続せずに異常終了させたい場合は、`ProcessAbnormalEnd` を送出します。このクラスに指定した値がプロセス終了コードとなります。

```java
// 例: プロセス終了コード100で異常終了
throw new ProcessAbnormalEnd(100, "message-id");
```

参照: `nablarch-batch-nablarch_batch_error_process.json#abnormal-termination`

---

#### 2. エラー発生時に処理を継続する（常駐バッチのみ）

**重要**: エラー継続は **常駐バッチのみ** 対応しています。都度起動バッチでは対応していません。

常駐バッチでは、`TransactionAbnormalEnd` を送出すると `retry_handler` により処理が継続されます。ただし、この機能を使う場合はバッチ処理がリランできるようになっている必要があります（次項参照）。

> 補足: 都度起動バッチで `TransactionAbnormalEnd` を送出すると、バッチ処理が異常終了となります。

参照: `nablarch-batch-nablarch_batch_error_process.json#continue-on-error`

---

#### 3. リラン（再実行）設計

Nablarchバッチでは、ファイル入力を除き、リラン機能は提供されていません。そのため、アプリケーション側での設計と実装が必要です。

**推奨設計**: 処理対象レコードにステータスを持たせ、処理成功・失敗時にステータスを変更する（`loop_handler-callback` を参照）。

**ファイル入力の場合**: `ResumeDataReader`（レジューム機能付き読み込み）を使用することで、障害発生ポイントからの再実行が可能です。

参照: `nablarch-batch-nablarch_batch_error_process.json#rerun-batch-processing`

---

#### 4. 特定例外発生時にコミットする

デフォルトでは全エラー・例外がロールバック対象です。特定の例外が発生した場合にロールバックではなくコミットしたい場合は、`TransactionManagementHandler` の `transactionCommitExceptions` プロパティに対象例外クラスを設定します。設定したクラスのサブクラスもコミット対象となります。

```xml
<component class="nablarch.common.handler.TransactionManagementHandler">
  <property name="transactionCommitExceptions">
    <list>
      <value>example.TransactionCommitException</value>
    </list>
  </property>
</component>
```

参照: `handlers-transaction_management_handler.json#commit-on-specific-exceptions`

---

**注意点**:

- エラー継続処理（`TransactionAbnormalEnd` + `retry_handler`）は **常駐バッチのみ** 有効です。都度起動バッチでは使用できません。
- Jakarta Batchのように「特定例外を無視して処理を継続する」機能はNablarchバッチでは標準提供されていません（機能比較表で × と記載）。要件がある場合はカスタムハンドラを追加して対応します。
- Jakarta Batchのような「例外が発生したデータの単純なリトライ」は `retry_handler` では対応できません。柔軟なリトライが必要な場合はカスタムハンドラを追加します。
- DB例外（`DbAccessException`、`SqlStatementException`、`DuplicateStatementException`）はすべて非チェック例外のため、`try-catch` での明示的な捕捉は必須ではありません。ただし、一意制約違反（`DuplicateStatementException`）をハンドリングしたい場合は明示的に捕捉する必要があります。

参照:
- `nablarch-batch-nablarch_batch_error_process.json#abnormal-termination`
- `nablarch-batch-nablarch_batch_error_process.json#continue-on-error`
- `nablarch-batch-nablarch_batch_error_process.json#rerun-batch-processing`
- `handlers-transaction_management_handler.json#commit-on-specific-exceptions`
- `libraries-database.json#exception-types`
- `nablarch-batch-functional_comparison.json#functional-comparison`

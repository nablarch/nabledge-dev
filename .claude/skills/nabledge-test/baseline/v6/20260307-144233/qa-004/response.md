**結論**: Nablarchバッチのエラーハンドリングは、バッチ種別（都度起動 or 常駐）とエラー時の要件（異常終了 / 処理継続 / 特定例外でのコミット）によって方法が異なります。

---

**根拠**:

## 1. バッチを異常終了させたい場合

`ProcessAbnormalEnd` を送出することでバッチ処理を異常終了させられます。送出時に指定した値がプロセス終了コードになります。

```java
// 例：プロセス終了コード 100 で異常終了
throw new ProcessAbnormalEnd(100, "エラーメッセージ");
```

## 2. エラー発生後も処理を継続したい場合（常駐バッチのみ）

**重要な制約**: エラー発生時の処理継続は **常駐バッチのみ** 対応しています。都度起動バッチは非対応です。

常駐バッチでは、`TransactionAbnormalEnd` を送出すると `retry_handler` により処理が継続されます。

```java
// 常駐バッチでエラーを検知して処理継続（retry_handler がリトライ）
throw new TransactionAbnormalEnd(100, "エラーメッセージ");
```

**注意**: 都度起動バッチで `TransactionAbnormalEnd` を送出するとバッチ処理が異常終了になります。

また、機能比較表にあるとおり、Nablarchバッチは「特定の例外を無視して処理を継続する（ロールバック後に処理を継続する）」機能を標準では提供していません（`×`）。この要件がある場合はカスタムハンドラを追加して対応する必要があります。

## 3. 特定の例外発生時にロールバックではなくコミットしたい場合

`TransactionManagementHandler` の `transactionCommitExceptions` プロパティにコミット対象の例外クラスを設定します。デフォルトは全エラー・例外がロールバック対象です。

```xml
<component class="nablarch.common.handler.TransactionManagementHandler">
  <property name="transactionCommitExceptions">
    <list>
      <value>example.TransactionCommitException</value>
    </list>
  </property>
</component>
```

設定した例外クラスのサブクラスもコミット対象になります。

## 4. トランザクション終了時にコールバック処理を実行したい場合

`TransactionEventCallback` インターフェースを実装したハンドラを作成することで、コミット時・ロールバック時にそれぞれコールバック処理を実行できます。

```java
public class SampleHandler
    implements Handler<Object, Object>, TransactionEventCallback<Object> {

  @Override
  public Object handle(Object o, ExecutionContext context) {
    return context.handleNext(o);
  }

  @Override
  public void transactionNormalEnd(Object o, ExecutionContext ctx) {
    // コミット時のコールバック処理
  }

  @Override
  public void transactionAbnormalEnd(Throwable e, Object o, ExecutionContext ctx) {
    // ロールバック時のコールバック処理（新しいトランザクションで実行される）
  }
}
```

ハンドラキューでは `TransactionManagementHandler` の後続に配置します。

## 5. データベースアクセス例外のハンドリング

DBアクセス時の例外は全て非チェック例外のため、`try-catch` で必ず捕捉する必要はありません。主な例外：

| 例外クラス | 発生条件 |
|---|---|
| `DbAccessException` | DBアクセスエラー全般 |
| `DbConnectionException` | DB接続エラー（`retry_handler` が自動処理） |
| `SqlStatementException` | SQL実行エラー |
| `DuplicateStatementException` | 一意制約違反 |

---

**注意点**:

- エラー発生後の処理継続（次レコードへのスキップ）は **常駐バッチのみ** サポート。都度起動バッチは非対応
- Jakarta Batchのように「特定例外を無視して処理継続」する機能はNablarchバッチには標準提供なし。必要な場合はカスタムハンドラで対応
- 特定例外でのリトライは `retry_handler` で対応できるが、例外が発生したデータの単純なリトライや柔軟な例外指定は非対応。これらが必要な場合もカスタムハンドラで対応
- バッチ処理のリラン設計（再実行）はアプリケーション側で処理対象レコードのステータス管理が必要（ファイル入力の場合は `ResumeDataReader` が利用可能）
- トランザクション終了コールバック処理中にエラーが発生すると、残りのハンドラに対するコールバック処理は実行されない

参照:
- `nablarch-batch-nablarch_batch_error_process.json#abnormal-termination`
- `nablarch-batch-nablarch_batch_error_process.json#continue-on-error`
- `handlers-transaction_management_handler.json#commit-on-specific-exceptions`
- `handlers-transaction_management_handler.json#execute-callback-on-transaction-end`
- `libraries-database.json#exception-types`
- `nablarch-batch-functional_comparison.json#functional-comparison`
- `nablarch-batch-nablarch_batch_error_process.json#rerun-batch-processing`

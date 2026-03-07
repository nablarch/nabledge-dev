**結論**: Nablarch 6のバッチでのエラーハンドリングは、バッチの種別（都度起動バッチ／常駐バッチ）とエラーの対処方針（異常終了・継続・コミット）によって使用するハンドラが異なります。

---

**根拠**:

#### 1. エラー発生時の基本動作（ハンドラキュー構成）

バッチのエラー処理は主に以下のハンドラが担います。

| ハンドラ | 役割 |
|---|---|
| `global_error_handler` | 実行時例外・エラーをログ出力 |
| `transaction_management_handler` | 例外時にトランザクションロールバック |
| `loop_handler` | 業務トランザクションのロールバック |
| `retry_handler` | リトライ可能例外を捕捉してリトライ（常駐バッチのみ） |
| `data_read_handler` | 読み込みレコードをログ出力後、元例外を再送出 |

#### 2. エラー継続（常駐バッチのみ）

エラーが発生しても処理を継続したい場合は **常駐バッチ** のみ対応。`TransactionAbnormalEnd` を送出すると、`retry_handler` により処理が継続されます。

> **重要**: エラー継続を使用する場合は、バッチ処理が「リラン可能」な設計になっている必要があります。
> **注意**: 都度起動バッチで `TransactionAbnormalEnd` が送出されると、バッチ処理は異常終了します。

特定例外を無視して処理を継続したい場合は、専用のカスタムハンドラを追加して対応します（標準機能では提供されていません）。

#### 3. 特定例外時にコミットする

デフォルトでは全エラー・例外がロールバック対象ですが、特定例外発生時にコミットしたい場合は `TransactionManagementHandler` の `transactionCommitExceptions` プロパティに例外クラスを設定します。

```xml
<component class="nablarch.common.handler.TransactionManagementHandler">
  <property name="transactionCommitExceptions">
    <list>
      <value>example.TransactionCommitException</value>
    </list>
  </property>
</component>
```

設定した例外クラスのサブクラスもコミット対象となります。

#### 4. トランザクション終了時のコールバック処理

コミット・ロールバック時に追加処理（通知、補償処理など）を実行したい場合は `TransactionEventCallback` インタフェースを実装します。

```java
public static class SampleHandler
    implements Handler<Object, Object>, TransactionEventCallback<Object> {

  @Override
  public void transactionNormalEnd(Object o, ExecutionContext ctx) {
    // トランザクションコミット時のコールバック処理
  }

  @Override
  public void transactionAbnormalEnd(Throwable e, Object o, ExecutionContext ctx) {
    // トランザクションロールバック時のコールバック処理
  }
}
```

ハンドラキューで `TransactionManagementHandler` の後続にこのハンドラを配置します。

> **注意**: 複数ハンドラがコールバックを実装している場合、コールバック処理中にエラーが発生すると残りのコールバックは実行されません。

#### 5. DB例外の種類

データベースアクセス時に発生する例外（全て非チェック例外）:

| 例外クラス | 発生タイミング |
|---|---|
| `DbAccessException` | データベースアクセスエラー全般 |
| `DbConnectionException` | データベース接続エラー（`retry_handler` で処理） |
| `SqlStatementException` | SQL実行時エラー |
| `DuplicateStatementException` | 一意制約違反 |

---

**注意点**:
- エラー継続（処理スキップ）は **常駐バッチのみ** 対応。都度起動バッチには対応していません。
- `retry_handler` でのリトライは、Jakarta Batchのように「例外が発生したデータの単純なリトライ」はできません。柔軟なリトライが必要な場合はカスタムハンドラを追加してください。
- バッチ処理の終了コードやコミット間隔制御など、エラー処理に関連する詳細は `nablarch_batch_error_process` のドキュメントを参照してください。

参照: `nablarch-batch-nablarch_batch_error_process.json#continue-on-error`, `nablarch-batch-architecture.json#handlers`, `handlers-transaction_management_handler.json#commit-on-specific-exceptions`, `handlers-transaction_management_handler.json#execute-callback-on-transaction-end`, `nablarch-batch-feature_details.json#batch-execution-control`, `nablarch-batch-functional_comparison.json#functional-comparison`, `libraries-database.json#exception-types`

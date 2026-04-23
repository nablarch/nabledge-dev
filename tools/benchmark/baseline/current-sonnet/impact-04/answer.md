**結論**: Nablarch には `RetryHandler`（`nablarch.fw.handler.RetryHandler`）という標準ハンドラがあり、DB接続の一時切断のような「単純リトライでリカバリ可能なエラー」を自動で再実行できる。ただし使えるのは **バッチ（常駐バッチ）・MOMメッセージング・DBメッセージング** のハンドラ構成のみで、Webアプリケーション（サーブレット）では標準構成に含まれていない。

**根拠**:

1. **仕組み**: `RetryHandler` は `Retryable` インタフェースを実装した実行時例外をリトライ可能とみなし、後続ハンドラを再実行する。リトライ上限の判定は外部化された `RetryContext` 実装クラスに委ねられており、デフォルトで「リトライ回数による上限設定（`CountingRetryContextFactory`）」と「経過時間による上限設定」の2種類が提供されている。
（`component/handlers/handlers-retry_handler.json:s1`）

2. **設定例（リトライ回数）**: 最大3回リトライ・5秒待機の例:
```xml
<component name="retryHandler" class="nablarch.fw.handler.RetryHandler">
  <property name="retryContextFactory">
    <component class="nablarch.fw.handler.retry.CountingRetryContextFactory">
      <property name="retryCount" value="3" />
      <property name="retryIntervals" value="5000" />
    </component>
  </property>
</component>
```
上限値は「想定する最大復旧時間プラスアルファ」に設定すること（例: DB切り替えに最大5分かかるなら7分等）。複数例外をリトライする場合は最も復旧に時間のかかるものをベースにする。
（`component/handlers/handlers-retry_handler.json:s4`）

3. **常駐バッチでの位置**: `retry_handler` は `process_resident_handler` より **前（外側）** に設置する必要がある。`process_resident_handler` が実行時例外を `RetryableException` でラップして再送出し、プロセス継続制御を `retry_handler` に委譲する設計のため。
（`component/handlers/handlers-process_resident_handler.json:s4`、`processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s1`）

4. **MOM/DBメッセージングでも同様**: MOMメッセージング・DBメッセージングのハンドラ構成でも `retry_handler` が標準で組み込まれている。
（`processing-pattern/mom-messaging/mom-messaging-architecture.json:s4`、`processing-pattern/db-messaging/db-messaging-architecture.json:s5`）

5. **Webアプリ・RESTfulでは非対応**: Webアプリケーションの最小ハンドラ構成には `retry_handler` が含まれていない。DB接続の一時障害に対するリトライが必要な場合はカスタム実装が必要になる。
（`processing-pattern/web-application/web-application-architecture.json:s3`）

**注意点**:
- リトライ上限は必須設定。上限に達しても成功しなければ異常終了する。
- リトライ対象にするには、スローする例外が `Retryable` インタフェースを実装している必要がある。標準外の例外（JDBCドライバが投げる `SQLException` など）をそのまま投げても `RetryHandler` は反応しない。`Retryable` を実装した例外でラップするか、`process_resident_handler` が自動でラップするパスを活用すること。
- 常駐バッチでは `process_resident_handler`（s4）の記述通り、`retry_handler` を `process_resident_handler` より前に置かないとリトライ機構が機能しない。
- 上限値の設計は復旧時間の見積もりに依存するため、インフラチームと連携して設定値を決めること。

参照: component/handlers/handlers-retry_handler.json:s1, component/handlers/handlers-retry_handler.json:s4, component/handlers/handlers-process_resident_handler.json:s4, processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s1, processing-pattern/mom-messaging/mom-messaging-architecture.json:s4, processing-pattern/db-messaging/db-messaging-architecture.json:s5, processing-pattern/web-application/web-application-architecture.json:s3
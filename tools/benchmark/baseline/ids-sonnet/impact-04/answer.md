**結論**: Nablarch には `RetryHandler` という標準のリトライ機構がある。一時的なDB接続断などで発生する例外を対象に、指定回数または経過時間を上限として自動再実行できる。

**根拠**:

`RetryHandler` を使用する際は必ずリトライ上限を設定する必要がある。上限に達しても処理が成功しない場合は異常終了する。上限設定には「リトライ回数による上限」と「経過時間による上限」の2種類があり、プロジェクト要件に合わない場合はプロジェクト側で実装を追加できる。(`component/handlers/handlers-retry_handler.json:s4`)

リトライ回数による設定例（最大3回、5秒待機）:
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
(`component/handlers/handlers-retry_handler.json:s4`)

**注意点**:

1. **ハンドラの順序が重要**: リトライ対象の例外を送出するハンドラ（DBアクセスを行うハンドラなど）は、`RetryHandler` より**後ろ**に設定すること。`RetryHandler` より前に例外が発生した場合は、単に例外として処理されリトライされない。(`component/handlers/handlers-retry_handler.json:s3`)

2. **上限値の設定指針**: 上限値は「想定する最大の復旧時間＋アルファ」に設定すること。例えばDBの切り替えに最大5分かかる場合は7分程度を設定する。複数の例外をリトライ対象とする場合は、最も復旧に時間を要するものをベースに上限値を決める。(`component/handlers/handlers-retry_handler.json:s4`)

参照: component/handlers/handlers-retry_handler.json:s3, component/handlers/handlers-retry_handler.json:s4
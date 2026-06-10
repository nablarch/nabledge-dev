**結論**: RESTfulウェブサービスでは、`JaxRsResponseHandler`がエラー処理の中心を担い、レスポンス生成を`ErrorResponseBuilder`に、ログ出力を`JaxRsErrorLogWriter`に委譲する仕組みになっている。より深刻なエラー（システムエラー等）は`GlobalErrorHandler`が捕捉してFATALログを出力する。

**根拠**:

**1. JaxRsResponseHandler によるエラー処理**

`JaxRsResponseHandler`はハンドラキューで発生した例外を捕捉し、2つのコンポーネントに処理を委譲する。

**レスポンス生成（ErrorResponseBuilder）**:
- 発生した例外が`HttpErrorResponse`の場合 → `HttpErrorResponse#getResponse()`で取得した`HttpResponse`をそのままクライアントに返す
- それ以外 → `errorResponseBuilder`プロパティに設定された`ErrorResponseBuilder`がレスポンスを生成する
- 省略時はデフォルト実装が使用される

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

**ログ出力（JaxRsErrorLogWriter）**:
- `errorLogWriter`プロパティに設定された`JaxRsErrorLogWriter`がログを出力する
- 省略時はデフォルト実装が使用される

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorLogWriter">
    <component class="sample.SampleJaxRsErrorLogWriter" />
  </property>
</component>
```

**2. GlobalErrorHandler による致命的エラーの処理**

`GlobalErrorHandler`は例外・エラーの種類に応じて以下の処理を行う：

| 例外/エラー種別 | 処理内容 |
|---|---|
| `ServiceError`（サブクラス含む） | `ServiceError#writeLog`を呼び出してログ出力（レベルは実装クラス依存）、`ServiceError`を結果として返却 |
| `Result.Error`（サブクラス含む） | FATALレベルのログ出力後、`Result.Error`を返却 |
| その他の例外 | FATALレベルのログ出力後、`InternalError`を生成して返却 |
| `StackOverflowError` / `OutOfMemoryError` | FATALレベルのログ出力後、`InternalError`を生成して返却 |
| `VirtualMachineError`（上記以外） | FATALレベルのログ出力後、エラーをリスロー |

**3. 拡張方法**

バリデーションエラー時にJSONエラーメッセージをボディに返したい場合や、`NoDataException`に404を返したい場合は、`ErrorResponseBuilder`を継承してカスタマイズする（s7, s8参照）。

**注意点**: `ErrorResponseBuilder`内で例外が発生した場合、フレームワークはWARNレベルでログを出力し、ステータスコード500のレスポンスを生成して処理を継続する。`ErrorResponseBuilder`の実装中に例外が発生しないよう注意すること。

参照:
- component/handlers/handlers-jaxrs-response-handler.json:s4
- component/handlers/handlers-jaxrs-response-handler.json:s5
- component/handlers/handlers-jaxrs-response-handler.json:s7
- component/handlers/handlers-jaxrs-response-handler.json:s8
- component/handlers/handlers-global-error-handler.json:s4
- processing-pattern/restful-web-service/restful-web-service-architecture.json:s3
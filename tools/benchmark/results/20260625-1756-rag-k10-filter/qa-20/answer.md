### Answer

RESTfulウェブサービスにおけるエラー処理とログ出力の仕組みは、主に以下の2つのハンドラが担っています。

---

## JaxRsResponseHandler（エラーログ出力）

RESTfulウェブサービスでは、`JaxRsResponseHandler` がエラーログ出力を担当します。ログ出力は `errorLogWriter` プロパティに設定された `JaxRsErrorLogWriter` によって行われます。

- 設定を省略した場合はデフォルト実装の `JaxRsErrorLogWriter` が使用されます
- プロジェクト要件を満たせない場合はデフォルト実装を継承してカスタマイズします

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorLogWriter">
    <component class="sample.SampleJaxRsErrorLogWriter" />
  </property>
</component>
```

---

## HttpErrorHandler（例外種別に応じたログとレスポンス）

後続ハンドラで発生した例外の種別に応じて、以下のようにログ出力とHTTPステータスコードが決まります。

| 例外クラス | ログレベル | ステータスコード | 備考 |
|---|---|---|---|
| `NoMoreHandlerException` | INFO | 404 | 処理すべきアクションが存在しなかったため証跡ログとして記録 |
| `HttpErrorResponse` | 出力なし | `HttpErrorResponse#getResponse()` のステータス | 業務例外のため出力不要 |
| `Result.Error` | 設定による（条件付きFATAL） | `Error#getStatusCode()` | `writeFailureLogPattern` の正規表現とステータスコードが一致した場合にFATAL出力 |
| `StackOverflowError` | FATAL | 500 | データ/実装バグの可能性があるため障害扱い |
| `ThreadDeath` / `VirtualMachineError`（StackOverflow以外） | — | — | このハンドラでは何もせず上位ハンドラに再送出 |
| 上記以外の例外・エラー | FATAL | 500 | 予期しない例外のため障害扱い |

`Result.Error` のログ出力は `writeFailureLogPattern` プロパティで制御します。このプロパティに正規表現を設定し、`Error#getStatusCode()` とマッチした場合にFATALログが出力されます。

---

## HTTPアクセスログ（JaxRsAccessLogHandler）

リクエストの開始・終了はアクセスログとして記録されます。

- **ログレベル**: INFO
- **ロガー名**: `HTTP_ACCESS`
- アクセスログハンドラは **スレッドコンテキスト変数管理ハンドラより後ろ**、かつ **HTTPエラー制御ハンドラより前** に配置する必要があります（完了時のログにエラーコードが必要なため）

JSON形式の構造化ログとして出力したい場合は、`JaxRsAccessJsonLogFormatter` を使用することで、HTTPアクセスログの各項目をJSONの値として出力できます。

---

## 処理フローのまとめ

```
リクエスト
  → JaxRsAccessLogHandler（アクセスログ開始）
    → HttpErrorHandler（例外をキャッチしてログ・ステータスコード決定）
      → JaxRsResponseHandler（errorLogWriterでエラーログ出力）
        → アクションクラス
  → JaxRsAccessLogHandler（アクセスログ終了・ステータスコード記録）
```

エラー画面（エラーレスポンス）の内容は `HttpErrorResponse` が保持するレスポンス内容か、予期しないエラーの場合はステータスコード500のレスポンスがクライアントに返されます。
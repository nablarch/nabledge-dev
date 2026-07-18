### Answer

RESTfulウェブサービスにおけるエラー処理とログ出力の仕組みは、主に以下のコンポーネントが連携して実現されています。

---

## エラー処理の中心：JaxRsResponseHandler

RESTfulウェブサービスでは、**`JaxRsResponseHandler`** がエラー処理とログ出力の中心的な役割を担います。

### 例外の種類に応じた処理

例外・エラーの種類ごとに、ログレベルとHTTPステータスコードが決まります。

| 例外・エラー | ログレベル | ステータスコード | 補足 |
|---|---|---|---|
| `NoMoreHandlerException` | INFO | 404 | 処理すべきハンドラ不在 → 証跡ログとして記録 |
| `HttpErrorResponse` | ログなし | `HttpErrorResponse#getResponse()` | 業務例外（バリデーションエラー等）のため出力不要 |
| `Result.Error` | 設定による | `Error#getStatusCode()` | `writeFailureLogPattern` の設定次第 |
| `StackOverflowError` | FATAL | 500 | 障害として通知 |
| `ThreadDeath` / `VirtualMachineError`（StackOverflow以外） | — | — | 上位ハンドラに再送出 |
| 上記以外の例外・エラー | FATAL | 500 | 予期しない例外として障害扱い |

`HttpErrorResponse` の原因例外が `ApplicationException` の場合は、エラーメッセージをViewで扱えるよう `ErrorMessages` に変換してリクエストスコープに設定します（デフォルトキー名: `errors`）。

---

## エラーログのカスタマイズ：JaxRsErrorLogWriter

ログ出力は `JaxRsResponseHandler` の **`errorLogWriter`** プロパティに設定された **`JaxRsErrorLogWriter`** が行います。

- 設定を省略するとデフォルト実装が使われます
- プロジェクト要件を満たせない場合はデフォルト実装クラスを継承してカスタマイズします

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorLogWriter">
    <component class="sample.SampleJaxRsErrorLogWriter" />
  </property>
</component>
```

---

## Result.Error のログ出力制御

`Result.Error` のログ出力は **`writeFailureLogPattern`** プロパティで制御します。

- 正規表現を設定し、`Error#getStatusCode()` がマッチした場合に **FATAL** レベルのログを出力します
- マッチしない場合はログ出力されません

---

## HTTPアクセスログ

アクセスログはアプリケーションログ（ロガー名: `HTTP_ACCESS`、ログレベル: **INFO**）に出力されます。

JSON形式で出力したい場合は `JaxRsAccessJsonLogFormatter` を使用します。`app-log.properties` で `httpAccessLogFormatter.className` に指定することで、各アクセスログ項目をJSONの値として出力できます。

---

## ハンドラの配置制約

アクセスログハンドラ（`JaxRsAccessLogHandler`）は以下の順序で配置する必要があります：

1. **スレッドコンテキスト変数管理ハンドラより後ろ**（`ThreadContext` の情報が必要なため）
2. **HTTPエラー制御ハンドラより前**（完了時ログにエラーコードが必要なため）

---

## 致命的エラー時の固定レスポンス

ハンドラ内部で `ServletException`・`RuntimeException`・`Error` が発生した場合、クライアントには**ステータスコード500の固定HTMLレスポンス**が返されます。このHTMLは設定で変更できません。どんな状況でもこのレスポンスを出せないシステムでは、ハンドラを自作する必要があります。
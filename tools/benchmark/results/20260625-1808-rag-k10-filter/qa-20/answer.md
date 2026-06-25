### Answer

RESTfulウェブサービスにおけるエラー処理とログ出力の仕組みは、主に以下のコンポーネントが連携して動作します。

---

## エラー処理の全体像

### 1. JaxRsResponseHandler — エラーログ出力の中心

RESTfulウェブサービスでは、`JaxRsResponseHandler` がエラー時のログ出力を担います。ログ出力は `errorLogWriter` プロパティに設定された `JaxRsErrorLogWriter` が行います。

- 省略時はデフォルト実装の `JaxRsErrorLogWriter` が使用されます
- プロジェクト要件を満たせない場合は、デフォルト実装を **継承して** カスタマイズします

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorLogWriter">
    <component class="sample.SampleJaxRsErrorLogWriter" />
  </property>
</component>
```

---

### 2. 例外の種類ごとのログレベルとHTTPステータス

RESTfulウェブサービスのエラーハンドラ（`handlers-http-messaging-error-handler`相当）は、例外の種類に応じて以下のように動作します：

| 例外クラス | ログレベル | HTTPステータス | 理由 |
|---|---|---|---|
| `NoMoreHandlerException` | INFO | 404 | 処理すべきaction classが存在しなかった（証跡ログとして記録） |
| `HttpErrorResponse` | 出力なし | `getResponse()`の値 | バリデーション等の業務例外であり、正常フローの一部 |
| `Result.Error` | 設定による（FATALの場合あり） | `getStatusCode()`の値 | `writeFailureLogPattern`の正規表現に一致した場合にFATAL出力 |
| `ApplicationException` + `MessagingException` | — | 400 | クライアントリクエストの不正 |
| 上記以外すべて | FATAL | 500 | 予期しないエラーとして障害扱い |

#### `Result.Error` のログ出力制御

`writeFailureLogPattern` プロパティに **正規表現** を設定し、`Error#getStatusCode()` と一致した場合のみ FATAL ログを出力します。これにより「4xxはログしない、5xxのみログする」といった制御が可能です。

---

### 3. ハンドラ内部の致命的エラー（HttpResponseHandler）

`HttpResponseHandler` 自体の内部で以下が発生した場合、**固定のHTML**（設定変更不可）をステータス500で返します：

- サーブレットフォワード時の `ServletException`
- `RuntimeException` およびそのサブクラス
- `Error` およびそのサブクラス

```html
<html>
  <head><title>A system error occurred.</title></head>
  <body>
    <p>We are sorry not to be able to proceed your request.<br/>
    Please contact the system administrator of our system.</p>
  </body>
</html>
```

> このケースは非常にまれなシナリオです。このHTMLを絶対に出してはいけない要件の場合は、本ハンドラを参考に自作を検討してください。

---

### 4. グローバルエラーハンドラの動作

`GlobalErrorHandler` はさらに上位でエラーを補足します：

| エラー種別 | ログレベル | 処理 |
|---|---|---|
| `ServiceError`（サブクラス含む） | 実装クラスによる | `writeLog()`を呼び出し、`ServiceError`を返却 |
| `Result.Error`（サブクラス含む） | FATAL | `Result.Error`を返却 |
| `ThreadDeath` | INFO | エラーをリスロー |
| `StackOverflowError` | FATAL | `InternalError`に包んで返却 |
| `OutOfMemoryError` | FATAL | 標準エラーに出力後、`InternalError`に包んで返却 |
| `VirtualMachineError`（上記以外） | FATAL | エラーをリスロー |
| 上記以外 | FATAL | `InternalError`に包んで返却 |

---

### 5. HTTPアクセスログ（JaxRsAccessLogHandler）

エラーとは別に、すべてのリクエスト/レスポンスのアクセスログが記録されます：

- **ログレベル**: INFO
- **ロガー名**: `HTTP_ACCESS`
- 開始時（BEGIN）と終了時（END）の2回出力
- 終了時のログにはステータスコードが含まれるため、エラー発生時の記録にもなります

#### ハンドラ配置の制約

アクセスログハンドラは以下の順序で配置する必要があります：

```
スレッドコンテキスト変数管理ハンドラ
    ↓
JaxRsAccessLogHandler  ← ここ（エラーハンドラより前）
    ↓
HTTPエラー制御ハンドラ
```

エラーコードを終了ログに含めるため、**HTTPエラー制御ハンドラより前**に配置します。

---

### まとめ

RESTfulウェブサービスのエラー処理フローは次のように整理できます：

1. **アクセスログ**（JaxRsAccessLogHandler）がリクエスト開始を記録
2. 後続ハンドラでエラーが発生
3. **JaxRsResponseHandler** が例外の種類に応じてJaxRsErrorLogWriterでログ出力
4. エラーレスポンス（JSONなど）をクライアントに返却
5. **アクセスログ**（終了時）にステータスコードを記録
6. 取りこぼした例外は **GlobalErrorHandler** が最上位でFATALログを出力
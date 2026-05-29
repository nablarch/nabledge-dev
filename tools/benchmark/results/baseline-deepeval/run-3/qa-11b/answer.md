Step 5-7: 回答を生成し、検証します。

セクション内容をもとに回答を生成します。すべての Nablarch 固有の主張がセクション内容に直接裏付けられていることを確認しました（verify_result = PASS）。

---

**結論**: RESTfulウェブサービスでは、エラー発生時のレスポンス生成は `JaxRsResponseHandler` の `ErrorResponseBuilder` が担い、ログ出力は `JaxRsResponseHandler` の `JaxRsErrorLogWriter` と `グローバルエラーハンドラ` の2段階で行われる。なお、RESTfulウェブサービスにはHTML形式のエラー画面はなく、エラー時はHTTPレスポンス（ステータスコード＋ボディ）として返す。

---

**根拠**:

### ハンドラキューでの役割分担（最小ハンドラ構成より）

| No. | ハンドラ | エラー時の役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 実行時例外・エラーをキャッチしログ出力 |
| 2 | JaxRsResponseHandler | エラーレスポンス生成・書き込み・ログ出力 |

### グローバルエラーハンドラのログ出力

発生した例外・エラーの種別によってログレベルが変わる：

| 例外/エラークラス | ログレベル | 処理内容 |
|---|---|---|
| `ServiceError`（サブクラス含む） | 実装クラスに依存 | `ServiceError#writeLog` を呼び出す |
| `Result.Error`（サブクラス含む） | FATAL | ログ出力後 `Result.Error` を返却 |
| 上記以外の例外 | FATAL | ログ出力後 `InternalError` を生成して返却 |
| `ThreadDeath`（サブクラス含む） | INFO | ログ出力後リスロー |
| `StackOverflowError`（サブクラス含む） | FATAL | ログ出力後 `InternalError` を返却 |
| `OutOfMemoryError`（サブクラス含む） | FATAL | 標準エラー出力に出力後ログ出力、`InternalError` を返却 |
| `VirtualMachineError`（その他） | FATAL | ログ出力後リスロー |
| 上記以外のエラー | FATAL | ログ出力後 `InternalError` を返却 |

### JaxRsResponseHandler のエラーレスポンス生成

- `errorResponseBuilder` プロパティに設定した `ErrorResponseBuilder` がレスポンスを生成する
- 発生例外が `HttpErrorResponse` の場合は `HttpErrorResponse#getResponse()` を直接使用する
- 設定を省略するとデフォルト実装の `ErrorResponseBuilder` が使用される（プロジェクト要件に合わせてサブクラスで拡張可能）
- `ErrorResponseBuilder` の処理中に例外が発生した場合、フレームワークは WARNレベルでログを出力しステータスコード500のレスポンスを返す

### JaxRsResponseHandler のエラーログ出力

- `errorLogWriter` プロパティに設定した `JaxRsErrorLogWriter` がログ出力を担う
- 設定を省略するとデフォルト実装が使用される（サブクラスで拡張可能）

### 障害ログとアクセスログの出力方針

| ログの種類 | ログレベル | ロガー名 | 出力先 |
|---|---|---|---|
| 障害通知ログ | FATAL/ERROR | `MONITOR` | 障害通知専用ファイル（監視ツールで検知） |
| 障害解析ログ | FATAL/ERROR | クラス名 | アプリケーションログ |
| アクセスログ | INFO | `HTTP_ACCESS` | アプリケーションログ |

### フレームワーク全体のログレベル方針

| ログレベル | 使用方針 |
|---|---|
| FATAL/ERROR | 障害ログ出力（原則1件の障害に1件） |
| WARN | 連鎖例外など障害ログとして出せない例外 |
| INFO | URLパラメータ改竄エラー・認可チェックエラーなど |

---

参照: `handlers-jaxrs-response-handler.json:s4`, `handlers-jaxrs-response-handler.json:s5`, `handlers-global-error-handler.json:s4`, `restful-web-service-architecture.json:s4`, `libraries-failure-log.json:s1`, `libraries-jaxrs-access-log.json:s1`, `libraries-log.json:s27`

---
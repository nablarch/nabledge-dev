十分な情報が揃いました。回答を生成します。

---

**結論**: RESTfulウェブサービスでのエラー処理は、主に **Jakarta RESTful Web Servicesレスポンスハンドラ（`JaxRsResponseHandler`）** と **グローバルエラーハンドラ（`GlobalErrorHandler`）** の2つが担う。前者がエラーレスポンス生成とログ出力を、後者が未捕捉の実行時例外・エラーのログ出力を担当する。

---

**根拠**:

### 1. Jakarta RESTful Web Servicesレスポンスハンドラ（`JaxRsResponseHandler`）

最小ハンドラ構成の **No.2** に位置し、後続ハンドラ（リソース/アクション、リクエストボディ変換ハンドラ）で例外が発生した際に、**エラーレスポンス生成**と**ログ出力**の両方を担う。

#### エラーレスポンスの生成

`errorResponseBuilder` プロパティに設定された `ErrorResponseBuilder` がレスポンスを生成する。

- 発生例外が `HttpErrorResponse` の場合 → `HttpErrorResponse#getResponse()` の戻り値をそのままクライアントに返す
- それ以外 → `ErrorResponseBuilder`（デフォルト実装）がレスポンスを生成する

デフォルト実装を変更したい場合は継承クラスを設定する：

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

**拡張例1: バリデーションエラー時にJSONメッセージをレスポンスに含める**

```java
public class SampleErrorResponseBuilder extends ErrorResponseBuilder {
    @Override
    public HttpResponse build(final HttpRequest request,
            final ExecutionContext context, final Throwable throwable) {
        if (throwable instanceof ApplicationException) {
            return createResponseBody((ApplicationException) throwable);
        } else {
            return super.build(request, context, throwable);
        }
    }
    // ...
}
```

**拡張例2: 特定例外に個別ステータスコードを返す**

```java
public class SampleErrorResponseBuilder extends ErrorResponseBuilder {
    @Override
    public HttpResponse build(final HttpRequest request,
            final ExecutionContext context, final Throwable throwable) {
        if (throwable instanceof NoDataException) {
            return new HttpResponse(404);
        } else {
            return super.build(request, context, throwable);
        }
    }
}
```

> **注意**: `ErrorResponseBuilder` の処理中に例外が発生した場合、フレームワークはその例外を **WARNレベル** でログ出力し、**ステータスコード500** のレスポンスを生成して処理を続行する。

#### ログの出力

`errorLogWriter` プロパティに設定された `JaxRsErrorLogWriter` がログを出力する。

- `ApplicationException` の場合 → デフォルト実装では**ログ出力しない**（`writeApplicationExceptionLog` は何もしない）
- それ以外の例外 → `FailureLogUtil` を使用してログ出力する

カスタマイズが必要な場合は同様に継承クラスを設定する：

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorLogWriter">
    <component class="sample.SampleJaxRsErrorLogWriter" />
  </property>
</component>
```

---

### 2. グローバルエラーハンドラ（`GlobalErrorHandler`）

最小ハンドラ構成の **No.1（先頭）** に位置し、後続で捕捉されなかった例外・エラーを捕捉してログ出力を行う。

| 例外/エラークラス | 処理内容 |
|---|---|
| `ServiceError`（サブクラス含む） | `ServiceError#writeLog` を呼び出しログ出力。ログレベルは実装クラスによる |
| `Result.Error`（サブクラス含む） | **FATAL**レベルでログ出力 |
| 上記以外の例外 | **FATAL**レベルでログ出力後、`InternalError` を生成して返却 |
| `StackOverflowError` / `OutOfMemoryError` | **FATAL**レベルでログ出力後、`InternalError` を生成して返却 |
| `VirtualMachineError`（上記2つ以外） | **FATAL**レベルでログ出力後、リスロー |
| `ThreadDeath` | **INFO**レベルでログ出力後、リスロー |

---

### 最小ハンドラ構成での役割分担

| No. | ハンドラ | 例外処理での役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 実行時例外・エラーの**ログ出力** |
| 2 | **Jakarta RESTful Web Servicesレスポンスハンドラ** | 例外に対応した**エラーレスポンス生成 + ログ出力** |

---

**注意点**:
- RESTfulウェブサービスには「エラー画面への遷移」という概念はなく、エラーの場合は **HTTPステータスコードとレスポンスボディ** で表現する
- `ApplicationException`（バリデーションエラー等）はデフォルトでログ出力されない。ログが必要な場合は `JaxRsErrorLogWriter` をカスタマイズする
- `GlobalErrorHandler` はハンドラキューの**できるだけ先頭**に配置すること

参照: `handlers-jaxrs-response-handler.json:s4`, `handlers-jaxrs-response-handler.json:s5`, `handlers-global-error-handler.json:s4`, `restful-web-service-architecture.json:s4`, `javadoc-nablarch-fw-jaxrs-JaxRsErrorLogWriter.json:s5`

---
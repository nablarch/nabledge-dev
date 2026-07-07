# qa-20 — run-1

## 質問

エラーが発生したときにエラー画面を表示したり、ログを出力する仕組みはどうなっている？

## 回答

**結論**: RESTfulウェブサービスのエラーハンドリングは、**Jakarta RESTful Web Servicesレスポンスハンドラ（`JaxRsResponseHandler`）** がエラーレスポンス生成とログ出力を担い、**グローバルエラーハンドラ（`GlobalErrorHandler`）** が未捕捉の例外・エラーをFATALログ出力する2段構成になっている。

**根拠**:

### 最小ハンドラ構成でのエラー処理の位置づけ

| No. | ハンドラ | 例外処理 |
|-----|---------|---------|
| 1 | グローバルエラーハンドラ | 実行時例外またはエラーの場合、ログ出力を行う |
| 2 | Jakarta RESTful Web Servicesレスポンスハンドラ | 例外(エラー)に対応したレスポンス生成・書き込み・ログ出力処理を行う |

---

### Jakarta RESTful Web Servicesレスポンスハンドラ（`JaxRsResponseHandler`）

後続ハンドラで例外・エラーが送出された場合、以下の2つの委譲先クラスが処理を行う。

**① レスポンス生成: `ErrorResponseBuilder`**

`errorResponseBuilder` プロパティに設定された `ErrorResponseBuilder` によりレスポンスが生成される。省略時はデフォルト実装が使用される。なお、送出された例外が `HttpErrorResponse` の場合は、`HttpErrorResponse#getResponse()` が返す `HttpResponse` がそのままクライアントに返却される。

カスタマイズ例（`ApplicationException` 発生時に JSON でエラーメッセージを返す場合）:

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

特定の例外に個別のステータスコードを返す例:

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

設定例:

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

**② ログ出力: `JaxRsErrorLogWriter`**

`errorLogWriter` プロパティに設定された `JaxRsErrorLogWriter` によりログが出力される。省略時はデフォルト実装が使用される。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorLogWriter">
    <component class="sample.SampleJaxRsErrorLogWriter" />
  </property>
</component>
```

---

### グローバルエラーハンドラ（`GlobalErrorHandler`）

後続ハンドラで発生した未捕捉の例外・エラーを捕捉し、例外の種類に応じたログを出力する。

| 例外クラス | 処理内容 |
|-----------|---------|
| `ServiceError`（サブクラス含む） | `ServiceError#writeLog` を呼び出しログ出力（ログレベルは実装クラスにより異なる） |
| `Result.Error`（サブクラス含む） | FATALレベルのログを出力 |
| 上記以外の例外クラス | FATALレベルのログを出力し、`InternalError` を返却 |

---

**注意点**:
- `ErrorResponseBuilder` のカスタマイズ中に例外が発生すると、レスポンスを生成できなくなるため、`ErrorResponseBuilder` の処理中は例外が発生しないよう実装すること。なお、`ErrorResponseBuilder` 処理中に例外が発生した場合、フレームワークはWARNレベルのログを出力し、ステータスコード500のレスポンスを生成して処理を継続する
- グローバルエラーハンドラは設定による実装の切り替えができないため、要件に合わない場合（例: ログレベルを細かく切り替えたい）はプロジェクト固有のハンドラを作成すること

参照: handlers-jaxrs-response-handler.json:s4, handlers-jaxrs-response-handler.json:s5, handlers-jaxrs-response-handler.json:s7, handlers-jaxrs-response-handler.json:s8, handlers-global-error-handler.json:s4, handlers-global-error-handler.json:s5, restful-web-service-architecture.json:s3, restful-web-service-architecture.json:s4

## 参照ナレッジ

- [例外及びエラーに応じたレスポンスの生成](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-response-handler.md#例外及びエラーに応じたレスポンスの生成) (s4)
- [例外及びエラーに応じたログ出力](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-response-handler.md#例外及びエラーに応じたログ出力) (s5)
- [例外及びエラーに応じた処理内容](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-global-error-handler.md#例外及びエラーに応じた処理内容) (s4)
- [RESTfulウェブサービスで使用するハンドラ](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-architecture.md#restfulウェブサービスで使用するハンドラ) (s3)
- [最小ハンドラ構成](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-architecture.md#最小ハンドラ構成) (s4)
- [エラー時のレスポンスにメッセージを設定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-response-handler.md#エラー時のレスポンスにメッセージを設定する) (s7)
- [特定のエラーの場合に個別に定義したエラーレスポンスを返却する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-response-handler.md#特定のエラーの場合に個別に定義したエラーレスポンスを返却する) (s8)
- [グローバルエラーハンドラでは要件を満たせない場合](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-global-error-handler.md#グローバルエラーハンドラでは要件を満たせない場合) (s5)
- [エラー時に返却するレスポンス](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-feature-details.md#エラー時に返却するレスポンス) (s11)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output covers both expected facts clearly. It explains that JaxRsResponseHandler generates error responses via ErrorResponseBuilder (fact 1) and that JaxRsErrorLogWriter handles log output via the errorLogWriter property (fact 2). Both expected facts are present and accurately represented without contradiction. The coverage is 100% (2/2 facts found). |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the actual output is fully relevant to the input, which asks about the mechanism for displaying error screens and outputting logs when an error occurs. No irrelevant statements were found! |
| faithfulness | 0.99 | 0.67 | NG | The score is 0.67 because the actual output contains several misattributions of responsibilities between classes. Specifically, the actual output incorrectly attributes error response generation and log output solely to the Jakarta RESTful Web Services Response Handler, when these are actually delegated to ErrorResponseBuilder and JaxRsErrorLogWriter respectively. Additionally, the actual output incorrectly attributes FATAL level logging for uncaught exceptions, handling of Result.Error exceptions, and handling of other exception classes (including ServiceError#writeLog behavior) to GlobalErrorHandler, when the retrieval context clearly states these behaviors belong to JaxRsErrorLogWriter. The actual output also oversimplifies log level behavior by claiming FATAL level is used for all uncaught exceptions, when in reality log levels vary by exception type (e.g., ThreadDeath uses INFO level). |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「JaxRsResponseHandlerが例外に応じたエラーレスポンスを生成する」は回答の「① レスポンス生成: `ErrorResponseBuilder`」（`errorResponseBuilder` プロパティに設定された `ErrorResponseBuilder` によりレスポンスが生成される）に含まれており、参照事実「JaxRsErrorLogWriterが例外に応じたログ出力を行う」は回答の「② ログ出力: `JaxRsErrorLogWriter`」（`errorLogWriter` プロパティに設定された `JaxRsErrorLogWriter` によりログが出力される）に含まれている |
| answer_relevancy | NG | 回答末尾に「参照: handlers-jaxrs-response-handler.json:s4, handlers-jaxrs-response-handler.json:s5, handlers-jaxrs-response-handler.json:s7, handlers-jaxrs-response-handler.json:s8, handlers-global-error-handler.json:s4, handlers-global-error-handler.json:s5, restful-web-service-architecture.json:s3, restful-web-service-architecture.json:s4」という内部参照記法がユーザー向け回答に含まれており不適切 |
| faithfulness | OK | ナレッジ内容と矛盾なし。DeepEvalはGlobalErrorHandlerの動作（ServiceError#writeLog、Result.Error→FATAL、その他例外→FATALかつInternalError返却）をJaxRsErrorLogWriterに誤帰属させたと指摘したが、handlers-global-error-handler.mdの「例外及びエラーに応じた処理内容」を確認すると回答のGlobalErrorHandlerテーブルはナレッジの内容と一致しており、矛盾は存在しない |

### 参照事実（expected_facts）

- JaxRsResponseHandlerが例外に応じたエラーレスポンスを生成する
- JaxRsErrorLogWriterが例外に応じたログ出力を行う

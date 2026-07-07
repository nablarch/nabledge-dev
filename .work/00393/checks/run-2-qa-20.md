# qa-20 — run-2

## 質問

エラーが発生したときにエラー画面を表示したり、ログを出力する仕組みはどうなっている？

## 回答

**結論**: RESTfulウェブサービスでのエラー処理は、主に **`JaxRsResponseHandler`（Jakarta RESTful Web Servicesレスポンスハンドラ）** と **`GlobalErrorHandler`（グローバルエラーハンドラ）** の2つのハンドラが担う。エラーレスポンスの生成は `ErrorResponseBuilder`、ログ出力は `JaxRsErrorLogWriter` がそれぞれ担当する。

---

**根拠**:

#### ハンドラの役割分担

最小ハンドラ構成における2つのエラー処理ハンドラの役割は以下の通り。

| No. | ハンドラ | 例外処理 |
|---|---|---|
| 1 | `GlobalErrorHandler` | 実行時例外・Errorの場合にログ出力 |
| 2 | `JaxRsResponseHandler` | 例外(エラー)に対応したレスポンス生成・書き込み・ログ出力 |

#### JaxRsResponseHandler の仕組み

後続ハンドラ（アクションクラスなど）で例外が発生した際に、エラーレスポンスとログを処理する中心的なハンドラ。

**エラーレスポンス生成**:  
`errorResponseBuilder` プロパティに設定された `ErrorResponseBuilder` が生成を担当する。例外が `HttpErrorResponse` の場合は、その中の `HttpResponse` が直接クライアントに返される。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

**エラーログ出力**:  
`errorLogWriter` プロパティに設定された `JaxRsErrorLogWriter` がログ出力を担当する。デフォルト実装では `FailureLogUtil` を用いてログ出力を行う。`ApplicationException`（バリデーションエラー等）の場合はデフォルトでログ出力しない（`writeApplicationExceptionLog` は何もしない）。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorLogWriter">
    <component class="sample.SampleJaxRsErrorLogWriter" />
  </property>
</component>
```

#### GlobalErrorHandler の仕組み

未捕捉の例外・エラーを捕捉して処理する。ハンドラキューの先頭（最前）に配置する。

| 例外・エラークラス | ログレベル |
|---|---|
| `ServiceError`（サブクラス含む） | 実装クラスに依存（`ServiceError#writeLog` 呼び出し） |
| `Result.Error`（サブクラス含む） | FATAL |
| それ以外の例外 | FATAL |
| `ThreadDeath` / `VirtualMachineError` | INFO / FATAL（リスロー） |
| `StackOverflowError` / `OutOfMemoryError` | FATAL |

#### カスタマイズ

エラーレスポンスにメッセージを含めたい場合は、`ErrorResponseBuilder` を継承して `build` メソッドをオーバーライドする。

```java
public class SampleErrorResponseBuilder extends ErrorResponseBuilder {
    @Override
    public HttpResponse build(HttpRequest request, ExecutionContext context, Throwable throwable) {
        if (throwable instanceof ApplicationException) {
            // バリデーションエラー → 400 + JSON ボディ
            return createResponseBody((ApplicationException) throwable);
        } else if (throwable instanceof NoDataException) {
            return new HttpResponse(404);
        } else {
            return super.build(request, context, throwable);
        }
    }
}
```

---

**注意点**:
- `ErrorResponseBuilder` のカスタマイズ実装の中で例外が発生した場合、フレームワークはその例外をWARNレベルでログ出力し、ステータスコード500のレスポンスを返す。そのため `ErrorResponseBuilder` 内では例外が発生しない実装を徹底すること。
- `GlobalErrorHandler` より前に配置したハンドラで例外が発生した場合、ウェブアプリケーションサーバやJVMによって処理されるため、Nablarchのエラー処理は適用されない。

参照: handlers-jaxrs-response-handler.json:s4, handlers-jaxrs-response-handler.json:s5, handlers-jaxrs-response-handler.json:s7, handlers-jaxrs-response-handler.json:s8, handlers-global-error-handler.json:s4, restful-web-service-architecture.json:s4, javadoc-nablarch-fw-jaxrs-JaxRsErrorLogWriter.json:s4

## 参照ナレッジ

- [例外及びエラーに応じたレスポンスの生成](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-response-handler.md#例外及びエラーに応じたレスポンスの生成) (s4)
- [例外及びエラーに応じたログ出力](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-response-handler.md#例外及びエラーに応じたログ出力) (s5)
- [例外及びエラーに応じた処理内容](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-global-error-handler.md#例外及びエラーに応じた処理内容) (s4)
- [最小ハンドラ構成](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-architecture.md#最小ハンドラ構成) (s4)
- [エラー時のレスポンスにメッセージを設定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-response-handler.md#エラー時のレスポンスにメッセージを設定する) (s7)
- [特定のエラーの場合に個別に定義したエラーレスポンスを返却する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-response-handler.md#特定のエラーの場合に個別に定義したエラーレスポンスを返却する) (s8)
- [RESTfulウェブサービスで使用するハンドラ](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-architecture.md#restfulウェブサービスで使用するハンドラ) (s3)
- [制約](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-global-error-handler.md#制約) (s3)
- [errorLogWriter](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-fw-jaxrs-JaxRsResponseHandler.md#errorlogwriter) (s4)
- [write](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-fw-jaxrs-JaxRsErrorLogWriter.md#write) (s4)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output covers both expected facts: it clearly states that `ErrorResponseBuilder` (used by `JaxRsResponseHandler`) handles error response generation, and that `JaxRsErrorLogWriter` handles log output. The role of `JaxRsResponseHandler` in generating error responses is explicitly described, and `JaxRsErrorLogWriter` is identified as handling log output. Both expected facts are present and accurately represented without contradiction. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant, directly addressing the question about error handling mechanisms, including error screen display and log output. No irrelevant statements were found! |
| faithfulness | 0.99 | 0.96 | NG | The score is 0.96 because the actual output mostly aligns with the retrieval context, but contains a minor inaccuracy regarding VirtualMachineError handling. Specifically, the actual output claims all VirtualMachineErrors are rethrown, when in fact StackOverflowError results in an InternalError being returned rather than rethrown, and OutOfMemoryError is not described as being rethrown either — only the remaining VirtualMachineErrors follow the FATAL log and rethrow pattern. |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | — | — |
| answer_relevancy | — | — |
| faithfulness | — | — |

### 参照事実（expected_facts）

- JaxRsResponseHandlerが例外に応じたエラーレスポンスを生成する
- JaxRsErrorLogWriterが例外に応じたログ出力を行う

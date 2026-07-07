# qa-20 — run-3

## 質問

エラーが発生したときにエラー画面を表示したり、ログを出力する仕組みはどうなっている？

## 回答

**結論**: RESTfulウェブサービスでのエラー処理は、ハンドラキュー内の2つのハンドラが役割分担しており、`JaxRsResponseHandler`（Jakarta RESTful Web Servicesレスポンスハンドラ）がエラー応答の生成とログ出力を担い、`GlobalErrorHandler`（グローバルエラーハンドラ）が未捕捉の実行時例外・エラーのログ出力を担う。

**根拠**:

**ハンドラキューの構造（エラー関連の抜粋）**:

| No. | ハンドラ | 例外処理 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 実行時例外・エラーのログ出力 |
| 2 | Jakarta RESTful Web Servicesレスポンスハンドラ | 例外に対応したレスポンス生成・ログ出力 |

---

**① Jakarta RESTful Web Servicesレスポンスハンドラ（`JaxRsResponseHandler`）**

後続のハンドラ（リソースクラス等）で例外が発生した場合に、エラーレスポンスの生成とログ出力を行う中心的なハンドラ。

**レスポンスの生成**: `errorResponseBuilder` プロパティに設定された `ErrorResponseBuilder` が担う。

- 例外が `HttpErrorResponse` の場合: `HttpErrorResponse#getResponse()` の戻り値がそのままクライアントに返却される
- それ以外の例外: デフォルト実装の `ErrorResponseBuilder` が使用される

カスタマイズが必要な場合は継承クラスを作成する:
```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

例として `NoDataException` のとき404を返す実装:
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

**ログ出力**: `errorLogWriter` プロパティに設定された `JaxRsErrorLogWriter` が担う。プロジェクト要件を満たせない場合は継承クラスを作成する:
```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorLogWriter">
    <component class="sample.SampleJaxRsErrorLogWriter" />
  </property>
</component>
```

---

**② グローバルエラーハンドラ（`GlobalErrorHandler`）**

`JaxRsResponseHandler` より外側（ハンドラキューの先頭側）に配置し、未捕捉の例外・エラーを捕捉してログ出力する。

| 例外クラス | 処理内容 |
|---|---|
| `ServiceError`（サブクラス含む） | `ServiceError#writeLog` でログ出力。ログレベルは実装クラスにより異なる。 |
| `Result.Error`（サブクラス含む） | FATALレベルでログ出力 |
| 上記以外の例外 | FATALレベルでログ出力後、`InternalError` を生成して返却 |
| `OutOfMemoryError` | FATALログ出力前に標準エラー出力へ出力（再度OOMが発生する可能性のため） |

**注意点**:

- `ErrorResponseBuilder` のカスタマイズ実装の中で例外が発生した場合、フレームワークはWARNレベルでログ出力してステータスコード500のレスポンスを生成して処理を継続する
- グローバルエラーハンドラはできるだけハンドラキューの先頭に配置すること。このハンドラより手前で例外が発生した場合は、ウェブアプリケーションサーバやJVMにより例外処理が行われる

参照: handlers-jaxrs-response-handler.json:s4, handlers-jaxrs-response-handler.json:s5, handlers-jaxrs-response-handler.json:s7, handlers-jaxrs-response-handler.json:s8, handlers-global-error-handler.json:s4, handlers-global-error-handler.json:s3, restful-web-service-architecture.json:s4

## 参照ナレッジ

- [例外及びエラーに応じたレスポンスの生成](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-response-handler.md#例外及びエラーに応じたレスポンスの生成) (s4)
- [例外及びエラーに応じたログ出力](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-response-handler.md#例外及びエラーに応じたログ出力) (s5)
- [例外及びエラーに応じた処理内容](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-global-error-handler.md#例外及びエラーに応じた処理内容) (s4)
- [最小ハンドラ構成](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-architecture.md#最小ハンドラ構成) (s4)
- [エラー時のレスポンスにメッセージを設定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-response-handler.md#エラー時のレスポンスにメッセージを設定する) (s7)
- [特定のエラーの場合に個別に定義したエラーレスポンスを返却する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-response-handler.md#特定のエラーの場合に個別に定義したエラーレスポンスを返却する) (s8)
- [制約](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-global-error-handler.md#制約) (s3)
- [RESTfulウェブサービスで使用するハンドラ](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-architecture.md#restfulウェブサービスで使用するハンドラ) (s3)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output covers both expected facts. It explicitly mentions JaxRsResponseHandler generating error responses based on exceptions (covered under '① Jakarta RESTful Web Servicesレスポンスハンドラ' section discussing errorResponseBuilder and response generation). It also explicitly mentions JaxRsErrorLogWriter handling log output for exceptions (covered under the 'ログ出力' section stating 'errorLogWriter プロパティに設定された JaxRsErrorLogWriter が担う'). Both expected facts are present and clearly addressed. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the actual output is perfectly relevant to the input question about error handling mechanisms, including error screen display and log output. No irrelevant statements were found! |
| faithfulness | 0.99 | 0.95 | NG | The score is 0.95 because the actual output incorrectly states that the default ErrorResponseBuilder implementation is used for exceptions other than HttpErrorResponse, whereas the retrieval context specifies that the default ErrorResponseBuilder is simply used when no custom one is configured, without making any such distinction about exception types. |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「JaxRsResponseHandlerが例外に応じたエラーレスポンスを生成する」は回答の「① Jakarta RESTful Web Servicesレスポンスハンドラ（`JaxRsResponseHandler`）」セクションの「エラーレスポンスの生成とログ出力を行う」に含まれており、参照事実「JaxRsErrorLogWriterが例外に応じたログ出力を行う」は「`errorLogWriter` プロパティに設定された `JaxRsErrorLogWriter` が担う」に含まれている |
| answer_relevancy | — | —
| faithfulness | — | —

### 参照事実（expected_facts）

- JaxRsResponseHandlerが例外に応じたエラーレスポンスを生成する
- JaxRsErrorLogWriterが例外に応じたログ出力を行う

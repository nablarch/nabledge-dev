# qa-21 — run-1

## 質問

入力チェックでエラーがあったときに、エラーメッセージをユーザーに返す方法を教えてほしい

## 回答

**結論**: RESTfulウェブサービスでバリデーションエラーが発生した場合、リソースメソッドに`@Valid`アノテーションを設定してバリデーションを実行し、`ErrorResponseBuilder`を継承したクラスでエラーメッセージをJSONレスポンスに設定して返す。

---

**根拠**:

**1. バリデーションの実行**

リソース(アクション)クラスのメソッドに`@Valid`アノテーションを付与することで、`JaxRsBeanValidationHandler`がForm(Bean)に対してBean Validationを実行する。バリデーションエラー発生時は後続処理に委譲せず`ApplicationException`が送出される。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(ProjectForm project) {
    UniversalDao.insert(BeanUtil.createAndCopy(Project.class, project));
    return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode());
}
```

**2. エラーメッセージのレスポンス返却**

`ErrorResponseBuilder`を継承したクラスを作成し、`ApplicationException`発生時にエラーメッセージをJSON形式でレスポンスボディに設定する。

```java
public class SampleErrorResponseBuilder extends ErrorResponseBuilder {

    private final ObjectMapper objectMapper = new ObjectMapper();

    @Override
    public HttpResponse build(final HttpRequest request,
            final ExecutionContext context, final Throwable throwable) {
        if (throwable instanceof ApplicationException) {
            return createResponseBody((ApplicationException) throwable);
        } else {
            return super.build(request, context, throwable);
        }
    }

    private HttpResponse createResponseBody(final ApplicationException ae) {
        final HttpResponse response = new HttpResponse(400);
        response.setContentType(MediaType.APPLICATION_JSON);

        // エラーメッセージの生成処理は省略

        try {
            response.write(objectMapper.writeValueAsString(errorMessages));
        } catch (JsonProcessingException ignored) {
            return new HttpResponse(500);
        }
        return response;
    }
}
```

**3. コンポーネント設定**

作成した`SampleErrorResponseBuilder`を`JaxRsResponseHandler`の`errorResponseBuilder`プロパティに設定する。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

---

**注意点**:
- `ErrorResponseBuilder`の処理中に例外が発生するとクライアントにレスポンスを返せなくなるため、例外が発生しないよう実装すること。
- `JaxRsBeanValidationHandler`は`BodyConvertHandler`（リクエストボディ変換ハンドラ）よりも後ろに設定すること（リクエストボディ変換後にバリデーションを行うため）。

参照: handlers-jaxrs-bean-validation-handler.json:s4, handlers-jaxrs-response-handler.json:s7, libraries-bean-validation.json:s17, restful-web-service-getting-started-create.json:s1

## 参照ナレッジ

- [リソース(アクション)で受け取るForm(Bean)に対してバリデーションを実行する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-bean-validation-handler.md#リソースアクションで受け取るformbeanに対してバリデーションを実行する) (s4)
- [エラー時のレスポンスにメッセージを設定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-response-handler.md#エラー時のレスポンスにメッセージを設定する) (s7)
- [RESTfulウェブサービスのユーザ入力値のチェックを行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#restfulウェブサービスのユーザ入力値のチェックを行う) (s17)
- [プロジェクト情報を登録する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-getting-started-create.md#プロジェクト情報を登録する) (s1)
- [例外及びエラーに応じたレスポンスの生成](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-response-handler.md#例外及びエラーに応じたレスポンスの生成) (s4)
- [制約](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-bean-validation-handler.md#制約) (s3)
- [エラー時に返却するレスポンス](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-feature-details.md#エラー時に返却するレスポンス) (s11)
- [バリデーションエラー時のエラーメッセージを定義する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#バリデーションエラー時のエラーメッセージを定義する) (s7)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output covers both key facts from the Expected Output. It explains that @Valid annotation triggers automatic validation error handling (via JaxRsBeanValidationHandler throwing ApplicationException), and it thoroughly explains creating an ErrorResponseBuilder subclass to set error messages in the response body. Both expected facts are fully covered, with the Actual Output providing additional implementation details and code examples that reinforce the core claims. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant, directly addressing how to return error messages to users when input validation errors occur. No irrelevant statements were found! |
| faithfulness | 0.99 | 0.91 | NG | The score is 0.91 because the actual output incorrectly claims that no response can be returned to the client when an exception occurs during ErrorResponseBuilder processing. In contrast, the retrieval context states that the framework logs the exception at WARN level, generates a response with status code 500, and continues subsequent processing — meaning a response is indeed returned to the client. |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「@Validアノテーションによりバリデーションエラーが自動的にエラーレスポンスになる」は回答の「リソース(アクション)クラスのメソッドに`@Valid`アノテーションを付与することで、`JaxRsBeanValidationHandler`がForm(Bean)に対してBean Validationを実行する。バリデーションエラー発生時は後続処理に委譲せず`ApplicationException`が送出される」に含まれている。参照事実「ErrorResponseBuilderの継承クラスでエラーメッセージをレスポンスボディに設定する」は回答のステップ2「`ErrorResponseBuilder`を継承したクラスを作成し、`ApplicationException`発生時にエラーメッセージをJSON形式でレスポンスボディに設定する」とコード例に含まれている。 |
| answer_relevancy | — | —
| faithfulness | — | —

### 参照事実（expected_facts）

- @Validアノテーションによりバリデーションエラーが自動的にエラーレスポンスになる
- ErrorResponseBuilderの継承クラスでエラーメッセージをレスポンスボディに設定する

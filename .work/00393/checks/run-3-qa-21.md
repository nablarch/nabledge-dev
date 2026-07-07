# qa-21 — run-3

## 質問

入力チェックでエラーがあったときに、エラーメッセージをユーザーに返す方法を教えてほしい

## 回答

**結論**: RESTfulウェブサービスでバリデーションエラー時にエラーメッセージをクライアントに返すには、(1) リソースクラスのメソッドに `@Valid` アノテーションを付けてバリデーションを実行し、(2) `ErrorResponseBuilder` を継承してエラーメッセージをレスポンスボディに含める実装を追加します。

**根拠**:

**① バリデーションの実行（`@Valid` アノテーション）**

リソースクラスのメソッドに `@Valid` を付けると、`JaxRsBeanValidationHandler` がリクエストボディをバインドした Form に対して Bean Validation を実行します。バリデーションエラーが発生した場合、`ApplicationException` がスローされます。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

Form クラスには Bean Validation アノテーションを付けてバリデーションルールを定義します。

```java
public class SampleForm {
    @Length(max = 10)
    @Required
    private String userName;
    // getter、setter は省略
}
```

**② エラーメッセージの定義（プロパティファイル）**

エラーメッセージはプロパティファイルで定義します（デフォルトでは Nablarch のメッセージ管理機能を使用）。

```properties
nablarch.core.validation.ee.Required.message=入力してください。
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
```

**③ エラーレスポンスボディへのメッセージ設定（`ErrorResponseBuilder` の継承）**

デフォルトの `JaxRsResponseHandler` はエラーレスポンスにメッセージボディを含めません。JSON 形式でエラーメッセージを返すには `ErrorResponseBuilder` を継承したクラスを作成します。

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

作成したクラスをコンポーネント設定ファイルに登録します。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

**注意点**:
- `ErrorResponseBuilder` の処理中に例外が発生するとクライアントにレスポンスを返せなくなるため、例外が発生しないよう実装すること。
- Form クラスのプロパティはすべて `String` 型で定義すること（数値型などにすると変換失敗で予期せぬ例外が発生する）。
- `JaxRsBeanValidationHandler` は `BodyConvertHandler`（リクエストボディ変換ハンドラ）よりも後ろに設定すること。

参照: handlers-jaxrs-bean-validation-handler.json:s4, handlers-jaxrs-response-handler.json:s4, handlers-jaxrs-response-handler.json:s7, libraries-bean-validation.json:s7, libraries-bean-validation.json:s17

## 参照ナレッジ

- [リソース(アクション)で受け取るForm(Bean)に対してバリデーションを実行する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-bean-validation-handler.md#リソースアクションで受け取るformbeanに対してバリデーションを実行する) (s4)
- [エラー時のレスポンスにメッセージを設定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-response-handler.md#エラー時のレスポンスにメッセージを設定する) (s7)
- [例外及びエラーに応じたレスポンスの生成](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-response-handler.md#例外及びエラーに応じたレスポンスの生成) (s4)
- [バリデーションエラー時のエラーメッセージを定義する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#バリデーションエラー時のエラーメッセージを定義する) (s7)
- [RESTfulウェブサービスのユーザ入力値のチェックを行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#restfulウェブサービスのユーザ入力値のチェックを行う) (s17)
- [エラー時に返却するレスポンス](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-feature-details.md#エラー時に返却するレスポンス) (s11)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The actual output explicitly covers both key facts from the expected output: (1) it explains that @Valid annotation triggers validation and causes validation errors to become error responses (via ApplicationException being thrown), and (2) it provides detailed explanation and code examples for inheriting ErrorResponseBuilder to set error messages in the response body. Both expected facts are clearly addressed, with the actual output going into substantial additional detail. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant to the input, addressing exactly how to return error messages to users when input validation errors occur. No irrelevant statements were found! |
| faithfulness | 0.99 | 0.92 | NG | The score is 0.92 because the actual output incorrectly describes the behavior when an exception occurs during ErrorResponseBuilder processing. Specifically, it contradicts the retrieval context by misrepresenting how the framework handles such exceptions — the context states the framework logs the exception at WARN level, generates a 500 status code response, and continues subsequent processing, allowing the server to still return a response. |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | — | — |
| answer_relevancy | — | — |
| faithfulness | — | — |

### 参照事実（expected_facts）

- @Validアノテーションによりバリデーションエラーが自動的にエラーレスポンスになる
- ErrorResponseBuilderの継承クラスでエラーメッセージをレスポンスボディに設定する

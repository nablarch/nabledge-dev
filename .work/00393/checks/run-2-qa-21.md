# qa-21 — run-2

## 質問

入力チェックでエラーがあったときに、エラーメッセージをユーザーに返す方法を教えてほしい

## 回答

Step 5で回答を生成します。

**結論**: RESTfulウェブサービスでバリデーションエラー時にエラーメッセージをクライアントに返すには、(1) リソースメソッドに `@Valid` アノテーションを設定してバリデーションを実行し、(2) `ErrorResponseBuilder` を継承してエラーレスポンスのボディにメッセージを設定する実装を追加します。

**根拠**:

**① バリデーションの設定（JaxRsBeanValidationHandlerの利用）**

リソースクラスのメソッドに `@Valid` アノテーションを付与することで、ハンドラが自動的にBean Validationを実行します。エラー時は `ApplicationException` が送出されます。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

**② エラーメッセージをレスポンスに設定する**

`JaxRsResponseHandler` の `errorResponseBuilder` プロパティに `ErrorResponseBuilder` の継承クラスを設定します。`ApplicationException` を受け取ってJSON形式でエラーメッセージを返す実装例を示します。

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

コンポーネント設定ファイルで登録します。

```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

**③ エラーメッセージの定義**

バリデーションアノテーションの `message` 属性をメッセージIDとしてプロパティファイルに定義します。

```properties
nablarch.core.validation.ee.Length.max.message={max}文字以内で入力してください。
nablarch.core.validation.ee.Required.message=入力してください。
```

**注意点**:
- `JaxRsBeanValidationHandler` はリクエストボディ変換ハンドラ（`BodyConvertHandler`）より後ろに設定すること。
- `ErrorResponseBuilder` の実装中に例外が発生するとレスポンスを返せない状態になるため、例外が発生しないよう実装すること（発生した場合はフレームワークがWARNログを出してステータス500を返す）。
- FormクラスのプロパティはすべてString型として定義すること。

参照: handlers-jaxrs-bean-validation-handler.json:s4, handlers-jaxrs-response-handler.json:s7, handlers-jaxrs-response-handler.json:s4, libraries-bean-validation.json:s7, libraries-bean-validation.json:s17

## 参照ナレッジ

- [リソース(アクション)で受け取るForm(Bean)に対してバリデーションを実行する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-bean-validation-handler.md#リソースアクションで受け取るformbeanに対してバリデーションを実行する) (s4)
- [エラー時のレスポンスにメッセージを設定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-response-handler.md#エラー時のレスポンスにメッセージを設定する) (s7)
- [バリデーションエラー時のエラーメッセージを定義する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#バリデーションエラー時のエラーメッセージを定義する) (s7)
- [RESTfulウェブサービスのユーザ入力値のチェックを行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#restfulウェブサービスのユーザ入力値のチェックを行う) (s17)
- [制約](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-bean-validation-handler.md#制約) (s3)
- [例外及びエラーに応じたレスポンスの生成](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-response-handler.md#例外及びエラーに応じたレスポンスの生成) (s4)
- [バリデーションルールの設定方法](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#バリデーションルールの設定方法) (s8)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output covers both key facts from the Expected Output. First, it explains that the @Valid annotation causes validation errors to automatically become error responses (via ApplicationException being thrown and handled). Second, it explains how to inherit ErrorResponseBuilder to set error messages in the response body, with a concrete implementation example. Both expected facts are clearly addressed. |
| answer_relevancy | 0.95 | 0.95 | OK | The score is 0.95 because the response is highly relevant to explaining how to return error messages to users when input validation fails. It loses a small amount of points due to a minor tangential mention about Form class properties needing to be defined as String type, which relates more to form design conventions rather than directly addressing the core question of returning error messages to users. |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | — | — |
| answer_relevancy | — | — |
| faithfulness | — | — |

### 参照事実（expected_facts）

- @Validアノテーションによりバリデーションエラーが自動的にエラーレスポンスになる
- ErrorResponseBuilderの継承クラスでエラーメッセージをレスポンスボディに設定する

**結論**: REST APIでのJSON入力値検証には `JaxRsBeanValidationHandler` + `@Valid` アノテーションを使用する。バリデーションエラー時のエラーレスポンス（ボディにメッセージを含むJSON）は `ErrorResponseBuilder` を継承したカスタムクラスで実装するのが推奨。

---

**根拠**:

**① バリデーションの仕組み**

`JaxRsBeanValidationHandler`（クラス名: `nablarch.fw.jaxrs.JaxRsBeanValidationHandler`）は、`body_convert_handler` がリクエストボディから変換したForm (Bean) に対して Bean Validation を実行するハンドラ。バリデーションエラー発生時は後続ハンドラへ処理を委譲せず、`ApplicationException` を送出する。[component/handlers/handlers-jaxrs_bean_validation_handler.json:s1]

**② リソースクラスへの設定方法**

リソースクラスのメソッドに `@Valid` アノテーションを付けることでバリデーションが実行される。以下はJSON POSTを受け付けるアクションの例: [processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1]

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(ProjectForm project) {
    // ...
}
```

Formクラスのプロパティには `@Required` / `@Domain` 等のアノテーションでルールを定義する。

**③ エラーレスポンスのボディ設定**

`JaxRsResponseHandler` はデフォルトの `ErrorResponseBuilder` でエラーレスポンスを生成する。ボディにJSONエラーメッセージを含めたい場合は、`ErrorResponseBuilder` を継承したクラスを作成し、`errorResponseBuilder` プロパティに設定する。[component/handlers/handlers-jaxrs_response_handler.json:s5]

実装例（HTTP 400 + JSON形式のエラーメッセージ）: [component/handlers/handlers-jaxrs_response_handler.json:s7]

```java
public class SampleErrorResponseBuilder extends ErrorResponseBuilder {
    @Override
    public HttpResponse build(HttpRequest request, ExecutionContext context, Throwable throwable) {
        if (throwable instanceof ApplicationException) {
            HttpResponse response = new HttpResponse(400);
            response.setContentType(MediaType.APPLICATION_JSON);
            response.write(objectMapper.writeValueAsString(errorMessages));
            return response;
        }
        return super.build(request, context, throwable);
    }
}
```

コンポーネント設定:
```xml
<component class="nablarch.fw.jaxrs.JaxRsResponseHandler">
  <property name="errorResponseBuilder">
    <component class="sample.SampleErrorResponseBuilder" />
  </property>
</component>
```

---

**注意点**:
- `jaxrs_bean_validation_handler` は `body_convert_handler` より後ろに設定すること。先に変換されたFormに対してバリデーションを行うため順序が重要。[component/handlers/handlers-jaxrs_bean_validation_handler.json:s3]
- `jaxrs_adaptor` を使用した場合、`body_convert_handler` と `jaxrs_bean_validation_handler` は自動追加される。[processing-pattern/restful-web-service/restful-web-service-architecture.json:s3]
- `ErrorResponseBuilder` のカスタマイズ実装内で例外が発生すると、フレームワークはWARNログ出力後にステータスコード500を返す。実装時は例外が発生しないよう注意すること。[component/handlers/handlers-jaxrs_response_handler.json:s5]

参照: component/handlers/handlers-jaxrs_bean_validation_handler.json:s1, component/handlers/handlers-jaxrs_bean_validation_handler.json:s3, component/handlers/handlers-jaxrs_response_handler.json:s1, component/handlers/handlers-jaxrs_response_handler.json:s5, component/handlers/handlers-jaxrs_response_handler.json:s7, processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, processing-pattern/restful-web-service/restful-web-service-architecture.json:s3
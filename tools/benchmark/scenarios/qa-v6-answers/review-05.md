**質問**: REST API でクライアントから受け取る JSON の入力値を検証したい。不正な値のときにエラーをどう返すのが推奨？

---

**結論**: Nablarch の REST API では Bean Validation を推奨し、リソースメソッドの引数に `@Valid` を付けて有効化する。エラー応答は `JaxRsResponseHandler` が生成するが、バリデーションエラー時にボディへメッセージを入れるには `ErrorResponseBuilder` を継承して返す。 — `component/libraries/libraries-bean_validation.json#s14`、`component/handlers/handlers-jaxrs_response_handler.json#s7`

**① バリデーションの有効化**
リソースクラスのメソッド引数に `@Valid` アノテーションを設定する:

```java
@Path("/sample")
public class SampleResource {
    @POST
    public void register(@Valid SampleForm form) {
        // ...
    }
}
```
— `component/libraries/libraries-bean_validation.json#s14`

**② REST 側のパターン上の位置づけ**
REST ウェブサービスにおける入力値チェックは、Bean Validation を利用する標準機能で実装する。 — `processing-pattern/restful-web-service/restful-web-service-feature_details.json#s2`

**③ エラーレスポンスの基本**
エラー発生時のレスポンスは `JaxRsResponseHandler` の `errorResponseBuilder` プロパティに設定した `ErrorResponseBuilder` が生成する。指定しない場合はデフォルト実装が使われ、`HttpErrorResponse` がスローされれば `HttpErrorResponse#getResponse()` のレスポンスをそのまま返す。 — `component/handlers/handlers-jaxrs_response_handler.json#s5`

**④ バリデーションエラー時にメッセージを返す**
バリデーションエラー時にレスポンスボディへエラーメッセージを含めるには、`ErrorResponseBuilder` の継承クラスを作成して対応する:

```java
public class SampleErrorResponseBuilder extends ErrorResponseBuilder {
    private final ObjectMapper objectMapper = new ObjectMapper();

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
— `component/handlers/handlers-jaxrs_response_handler.json#s7`

**⑤ 特定の例外に個別レスポンスを返す**
特定の例外だけ独自のステータスコード・ボディで返したい場合も `ErrorResponseBuilder` を継承し、例外型で分岐する:

```java
if (throwable instanceof NoDataException) {
    return new HttpResponse(404);
}
return super.build(request, context, throwable);
```
— `component/handlers/handlers-jaxrs_response_handler.json#s8`、`processing-pattern/restful-web-service/restful-web-service-feature_details.json#s11`

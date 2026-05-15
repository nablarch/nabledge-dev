**結論**: Nablarch 6では、バリデーションエラー時のエラーメッセージをユーザーに返す方法は、Webアプリケーションか RESTful Webサービスかによって異なります。

## Webアプリケーションの場合

### 1. エラーメッセージの仕組み

バリデーションエラーが発生すると、フレームワークが自動的に以下の処理を行います。

1. バリデーション失敗時に `ApplicationException` がスローされる
2. HTTPエラー制御ハンドラが `ApplicationException` を `ErrorMessages` に変換し、リクエストスコープのキー `errors` に格納する
3. テンプレート側で `errors` オブジェクトを参照してエラーメッセージを表示する

リクエストスコープのキー名はデフォルト `errors`。変更したい場合はコンポーネント設定で変更可能：

```xml
<component name="webConfig" class="nablarch.common.web.WebConfig">
  <property name="errorMessageRequestAttributeName" value="messages" />
</component>
```

### 2. @OnError アノテーションで遷移先を指定する

```java
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse handle(HttpRequest request, ExecutionContext context) {
    // 業務処理
}
```

### 3. Thymeleafでエラーメッセージを表示する

特定プロパティのエラーを表示：
```html
<span class="error"
    th:if="${errors.hasError('form.userName')}"
    th:text="${errors.getMessage('form.userName')}">入力してください。</span>
```

グローバルメッセージを表示：
```html
<ul>
  <li th:each="message : ${errors.globalMessages}" th:text="${message}"></li>
</ul>
```

全エラーメッセージを表示：
```html
<ul>
  <li th:each="message : ${errors.allMessages}" th:text="${message}">エラーメッセージ</li>
</ul>
```

### 4. アクション内で特定項目のエラーメッセージを生成したい場合

```java
throw new ApplicationException(
    ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
```

## RESTful Webサービスの場合

`ErrorResponseBuilder` を継承したクラスを作成します：

```java
public class SampleErrorResponseBuilder extends ErrorResponseBuilder {
    @Override
    public HttpResponse build(HttpRequest request, ExecutionContext context, Throwable throwable) {
        if (throwable instanceof ApplicationException) {
            return createResponseBody((ApplicationException) throwable);
        }
        return super.build(request, context, throwable);
    }

    private HttpResponse createResponseBody(ApplicationException ae) {
        final HttpResponse response = new HttpResponse(400);
        response.setContentType(MediaType.APPLICATION_JSON);
        // エラーメッセージの生成・JSON変換処理
        return response;
    }
}
```

**注意点**:
- `@OnError` を設定し忘れると、バリデーションエラーがシステムエラー（500）扱いになります
- JSPのカスタムタグを使う場合はDOM構造に制約があり、CSSフレームワークとの相性問題が発生することがあります。リクエストスコープの `ErrorMessages` を直接使う方法が推奨されています

参照: processing-pattern/web-application/web-application-error-message.json, component/handlers/handlers-HttpErrorHandler.json#s4, component/handlers/handlers-InjectForm.json#s4, component/handlers/handlers-on-error.json#s3, component/libraries/libraries-bean-validation.json#s13, component/handlers/handlers-jaxrs-response-handler.json#s7
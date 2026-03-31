**結論**: 二重サブミット防止は、クライアント側とサーバ側の**両方を併用**して実装します。クライアント側はJSPカスタムタグの `allowDoubleSubmission="false"` 属性、サーバ側は `@OnDoubleSubmission` アノテーションとトークン機構を使用します。

**根拠**:

## クライアント側の二重サブミット防止

サブミットボタン/リンクのカスタムタグに `allowDoubleSubmission="false"` を指定します（デフォルトは `true`）。これにより、1回目のサブミット時にonclick属性が書き換えられ、2回目以降のリクエストがサーバに送信されなくなります。

```jsp
<n:submit type="button" name="back" value="戻る" uri="./back" />
<n:submit type="button" name="register" value="登録" uri="./register"
          allowDoubleSubmission="false" />
```

または確認画面の実装例（`<n:forConfirmationPage>` タグを使用）:

```jsp
<n:forConfirmationPage>
    <n:button uri="/action/client/back"
              cssClass="btn btn-lg btn-light">入力へ戻る</n:button>
    <n:button uri="/action/client/create"
              allowDoubleSubmission="false"
              cssClass="btn btn-lg btn-success">確定</n:button>
</n:forConfirmationPage>
```

## サーバ側の二重サブミット防止

サーバ側では一意なトークンを使用します。トークンは1回のチェックのみ有効です。

### 1. JSPでのトークン設定

`<n:form>` タグの `useToken="true"` を指定します（確認画面では共通化時にデフォルトで `true`）:

```jsp
<n:form useToken="true">
```

### 2. アクションへの @OnDoubleSubmission アノテーション付与

DBコミットを伴うアクションメソッドに `@OnDoubleSubmission` を付与します:

```java
@OnDoubleSubmission(path = "/WEB-INF/view/error/userError.jsp")
public HttpResponse register(HttpRequest req, ExecutionContext ctx) {
    // 省略
}
```

または `path` 省略（アプリケーション全体設定を使用する場合）:

```java
@OnDoubleSubmission
public HttpResponse update(HttpRequest request, ExecutionContext context) {
    Project targetProject = SessionUtil.delete(context, "project");
    UniversalDao.update(targetProject);
    return new HttpResponse(303, "redirect://completeOfUpdate");
}
```

### 3. アプリケーション全体のデフォルト設定（任意）

`BasicDoubleSubmissionHandler` をコンポーネント定義に追加することで、`@OnDoubleSubmission` の属性未指定時のデフォルト値を設定できます:

```xml
<component name="doubleSubmissionHandler"
           class="nablarch.common.web.token.BasicDoubleSubmissionHandler">
  <property name="path" value="/WEB-INF/view/error/userError.jsp" />
  <property name="messageId" value="DOUBLE_SUBMISSION_ERROR" />
  <property name="statusCode" value="200" />
</component>
```

### 4. JSP以外のテンプレートエンジン（Thymeleaf等）を使用する場合

`@UseToken` アノテーションでトークンを発行し、フォームに明示的に埋め込みます:

```java
@UseToken
public HttpResponse confirm(HttpRequest req, ExecutionContext ctx) {
    // 省略
}
```

```xml
<form th:action="@{/path/to/action}" method="post">
  <input type="hidden" name="nablarch_token" th:value="${nablarch_request_token}" />
```

**注意点**:
- クライアント側のみの場合、JavaScriptが無効な環境でリクエストが重複処理される恐れがあります
- サーバ側のみの場合、ダブルクリックで2回リクエストが送信されると処理順によっては二重サブミットエラーが返され、ユーザに処理結果が返されない恐れがあります
- **両方の併用が必須**です
- サーバ側トークンはセッションに格納されるため、同一ユーザが複数ウィンドウ/タブで並行して確認→完了画面遷移を行うことができません（後に遷移した画面のみ有効）
- `@OnDoubleSubmission` と `BasicDoubleSubmissionHandler` の両方で `path` が未指定の場合、システムエラーとなります。どちらかに必ず `path` を指定してください

参照: `component/handlers/handlers-on_double_submission.json#s1`, `component/handlers/handlers-on_double_submission.json#s3`, `component/handlers/handlers-on_double_submission.json#s4`, `component/handlers/handlers-use_token.json#s1`, `component/handlers/handlers-use_token.json#s3`, `component/libraries/libraries-tag.json#s1`

**質問**: 登録ボタンを連打されると二重に登録されてしまう。ボタンの連打を防止する仕組みは Nablarch にある？

---

**結論**: Nablarch はトークンベースの **2重サブミット防止機能** をビルトインで提供している。JSP を使っている場合は `form` タグの `useToken` 属性でトークン生成と hidden への埋め込みが自動で行われる。JSP 以外のテンプレートエンジンを使う場合は `@UseToken` インターセプタでアクションに明示的に付与する。どちらの場合も、後続のアクションには `@OnDoubleSubmission` インターセプタを付けてトークンをチェックする。 — `processing-pattern/web-application/web-application-feature_details.json#s8`

**① JSP を使う場合**
Web アプリケーション機能詳細の「2重サブミット防止」で紹介されており、`form` タグ側の機能として JSP に統合されている。JSP 以外のテンプレートエンジンを使う場合は `use_token_interceptor` を参照する、と明記されている。 — `processing-pattern/web-application/web-application-feature_details.json#s8`

**② JSP 以外（Thymeleaf など）で使う場合: `@UseToken`**
`@UseToken` アノテーションをアクションメソッドに付与し、入力フォームへ明示的にトークンを埋め込む:

```java
@UseToken
public HttpResponse confirm(HttpRequest req, ExecutionContext ctx) {
    // 省略
}
```

Thymeleaf での実装例:
```xml
<form th:action="@{/path/to/action}" method="post">
  <input type="hidden" name="nablarch_token" th:value="${nablarch_request_token}" />
```

`name` 属性は `"nablarch_token"`、`value` 属性はリクエストスコープのキー `"nablarch_request_token"` から取得した値にする（いずれも変更可能）。 — `component/handlers/handlers-use_token.json#s3`、`component/handlers/handlers-use_token.json#s1`

**③ トークンのチェック: `@OnDoubleSubmission`**
トークンをチェックするため、後続のアクションに `OnDoubleSubmission` インターセプタを設定する。`path` 属性で二重サブミット判定時の遷移先を指定する:

```java
@OnDoubleSubmission(path = "/WEB-INF/view/error/userError.jsp")
public HttpResponse register(HttpRequest req, ExecutionContext ctx) {
    // 省略
}
```

`OnDoubleSubmission` を使うには、`form` タグの `useToken` または `@UseToken` によるトークン設定が必要。 — `component/handlers/handlers-on_double_submission.json#s3`、`component/handlers/handlers-on_double_submission.json#s1`

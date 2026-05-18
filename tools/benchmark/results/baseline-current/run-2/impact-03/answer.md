**結論**: Bean Validationの中でカスタムバリデータを使ってDBアクセスすることは、Nablarchでは**明示的に禁止**されています。DB検索による重複チェックはBean Validation完了後、業務アクションの中で実装してください。

**根拠**:

Bean Validation実行中の値はバリデーション前の未検証値であるため、その値でDBアクセスを行うとSQLインジェクション等の脆弱性リスクがあります。

正しい実装パターン：

```java
@InjectForm(form = ProjectUpdateForm.class, prefix = "form")
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/update.jsp")
public HttpResponse confirmOfUpdate(HttpRequest request, ExecutionContext context) {
    ProjectUpdateForm form = context.getRequestScopedVar("form");

    // Bean Validation完了後、アクション内でDB検索して重複チェックを行う
    if (UniversalDao.exists(User.class, "FIND_BY_MAIL",
            new Object[] { form.getMailAddress() })) {
        throw new ApplicationException(
            ValidationUtil.createMessageForProperty(
                "form.mailAddress", "duplicate.mailAddress"));
    }
    // ...
}
```

重複エラーを特定の入力項目に紐づけて表示したい場合は、`ValidationUtil.createMessageForProperty` を使って `ApplicationException` をスローします。

**注意点**:
- カスタム `ConstraintValidator` の実装は、DBアクセスを伴わない検証ルール（形式チェック等）にのみ使用してください
- Bean Validation（`@InjectForm` / `@Valid`）→ DBアクセスチェック（アクション内）という順序を守ることで、検証済みの安全な値でDBにアクセスできます
- `UniversalDao#exists` を使った存在確認・重複チェックが推奨パターンです

参照: `component/libraries/libraries-bean-validation.json#s12`, `component/libraries/libraries-bean-validation.json#s13`, `processing-pattern/web-application/web-application-getting-started-project-update.json#s1`
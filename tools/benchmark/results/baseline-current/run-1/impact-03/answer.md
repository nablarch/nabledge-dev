**結論**: カスタムバリデータの中でDB検索する実装は**避けるべき**です。DBを使った重複チェックは、業務アクションメソッド内で実装してください。

**根拠**:

Nablarchの公式ドキュメント（Bean Validationガイド）では以下のように明示されています。

> データベースとの相関バリデーションは、業務アクション側で実装すること。
>
> **理由**: Bean Validationを使ってデータベースに対する相関バリデーションを実施した場合、バリデーション実施前の安全ではない値を使ってデータベースアクセスを行うことになる。（Bean Validation実行中のオブジェクトの値は、安全である保証がない。）これは、SQLインジェクションなどの脆弱性の原因となるため、避けるべき実装である。

推奨される実装パターン（Exampleアプリケーション `ProjectAction.java` より）:

```java
@InjectForm(form = ProjectUpdateForm.class, prefix = "form")
@OnError(type = ApplicationException.class,
        path = "/WEB-INF/view/project/update.jsp")
public HttpResponse confirmOfUpdate(HttpRequest request, ExecutionContext context) {
    ProjectUpdateForm form = context.getRequestScopedVar("form");

    // Bean Validationが完了したバリデーション済みの値を使ってDB検索
    if (form.hasClientId()) {
        if (!UniversalDao.exists(Client.class, "FIND_BY_CLIENT_ID",
                new Object[] {Integer.parseInt(form.getClientId())})) {
            throw new ApplicationException(
                MessageUtil.createMessage(MessageLevel.ERROR,
                    "errors.nothing.client", form.getClientId()));
        }
    }
}
```

エラー時に特定のフォーム項目をハイライトしたい場合は `ValidationUtil#createMessageForProperty` を使用します:

```java
throw new ApplicationException(
    ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
```

**注意点**:

- Bean Validationの実行順序は保証されない（Jakarta Bean Validation仕様）。このため、Bean Validation内でDB検索を行うと、他の単項目バリデーションが未実行の不正値でDBアクセスが発生する可能性がある
- `@InjectForm` を使うと Bean Validation 完了後のバリデーション済みオブジェクトがリクエストスコープに格納される。業務アクションメソッドではそのバリデーション済みの値を使ってDB検索する
- DBバリデーションエラーは `ApplicationException` をスローして `@OnError` でエラー画面へ遷移させる

参照: `libraries-bean-validation.json#s12`, `libraries-bean-validation.json#s13`, `web-application-getting-started-project-update.json#s1`
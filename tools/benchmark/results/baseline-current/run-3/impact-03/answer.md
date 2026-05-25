**結論**: カスタムバリデータ（`ConstraintValidator`）の中でDB検索する実装はNGです。DBを伴うバリデーションは業務アクションメソッド内で実装してください。

**根拠**:

Bean Validationの実行中はオブジェクトの値の安全性が保証されていません。バリデーション前の未検証な値でDB検索を行うと、SQLインジェクションなどの脆弱性につながるため、明示的に禁止されています。

**正しい実装パターン**:

① Bean Validationを通常どおり実行（フォームの単項目バリデーション）
② バリデーション通過後、業務アクションメソッド内でDBを検索して重複チェック

**実装例（業務アクションメソッド内でのDB存在確認）**:

```java
@InjectForm(form = ProjectUpdateForm.class, prefix = "form")
@OnError(type = ApplicationException.class,
        path = "/WEB-INF/view/project/update.jsp")
public HttpResponse confirmOfUpdate(HttpRequest request, ExecutionContext context) {
    ProjectUpdateForm form = context.getRequestScopedVar("form");

    // データベースを検索して入力されたIDを持つ顧客が存在するか確認する
    if (form.hasClientId()) {
        if (!UniversalDao.exists(Client.class, "FIND_BY_CLIENT_ID",
                new Object[] {Integer.parseInt(form.getClientId())})) {
            throw new ApplicationException(
                MessageUtil.createMessage(MessageLevel.ERROR,
                    "errors.nothing.client", form.getClientId()));
        }
    }
    // ...
}
```

重複チェック（既存レコードとの照合）も同様に `UniversalDao.exists()` を業務アクション内で呼び出します。

**エラーメッセージを特定の入力項目に紐づける場合**は、`ValidationUtil#createMessageForProperty` を使用します:

```java
throw new ApplicationException(
    ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
```

これにより、`form.mailAddress` フィールドをエラーハイライト表示させることができます。

**注意点**:

- Bean Validation（`@AssertTrue` など）は**項目間の相関チェック**（値同士の比較）には使えますが、DB検索を伴うチェックには使用禁止
- DB検索バリデーションを業務アクションで行う際は、Bean Validationが先に完了してからアクションが実行されるため、DBへ渡す値の安全性が確保されます
- `UniversalDao.exists()` の戻り値は boolean なので、存在チェック・重複チェックどちらにも使用可能

参照: `component/libraries/libraries-bean-validation.json#s12`, `component/libraries/libraries-bean-validation.json#s13`, `processing-pattern/web-application/web-application-getting-started-project-update.json#s1`
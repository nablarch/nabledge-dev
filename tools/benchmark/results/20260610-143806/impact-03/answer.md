**結論**: Bean Validationのカスタムバリデータ内でDB検索する実装は**推奨されません**。DB重複チェックは、Bean Validationが完了した後、業務アクション内で実装してください。

**根拠**:

Nablarchのドキュメントでは、Bean Validationを使ってDB相関バリデーションを行うことを明確に禁止しています。

> Bean Validationを使ってデータベースに対する相関バリデーションを実施した場合、バリデーション実施前の安全ではない値を使ってデータベースアクセスを行うことになる。(Bean Validation実行中のオブジェクトの値は、安全である保証がない。)これは、SQLインジェクションなどの脆弱性の原因となるため、さけるべき実装であるため。

正しい実装パターンは以下の通りです：

1. **Bean Validationで入力値の形式チェックを行う**（リソースクラスに `@Valid` を設定）

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(UserForm form) {
    // Bean Validationここで完了 → form内の値は安全
    // 以下でDB重複チェックを実施
    checkDuplicate(form);
    ...
}
```

2. **業務アクション内でバリデーション済みの値を使いDB重複チェックを実施**

```java
private void checkDuplicate(UserForm form) {
    // バリデーション済みの安全な値でDBアクセス
    long count = UniversalDao.count(User.class,
        new GenericArrayCondition("userId = ?", form.getUserId()));
    if (count > 0) {
        throw new ApplicationException(
            ValidationUtil.createMessageForProperty("form.userId", "duplicate.userId"));
    }
}
```

**注意点**:
- `ValidationUtil.createMessageForProperty` を使用することで、特定項目に紐づくバリデーションエラーメッセージをRESTfulウェブサービスの通常のエラーレスポンスと同じ形式で返せます。
- Bean Validation実行中（`ConstraintValidator`の `isValid` メソッド内）はオブジェクトの値の安全性が保証されないため、その中でのDBアクセスはSQLインジェクション脆弱性につながります。

参照: libraries-bean-validation.json:s12, libraries-bean-validation.json:s13, handlers-jaxrs-bean-validation-handler.json:s4
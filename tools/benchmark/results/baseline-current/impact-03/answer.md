**結論**: Bean Validationのカスタムバリデータ内でDB検索する実装は**避けるべき**です。DB重複チェックは、バリデーション完了後の**業務アクション側**で実装してください。

**根拠**:

Nablarchの公式方針として、DB相関バリデーションはBean Validationではなく業務アクションで行うよう明示されています。

> Bean Validationを使ってデータベースに対する相関バリデーションを実施した場合、バリデーション実施前の安全ではない値を使ってデータベースアクセスを行うことになる。（Bean Validation実行中のオブジェクトの値は、安全である保証がない。）これは、SQLインジェクションなどの脆弱性の原因となるため、避けるべき実装である。

**正しい実装パターン**（RESTfulウェブサービスの会員登録処理の場合）:

1. フォームに `@Valid` アノテーションでBean Validationを実行（入力チェック）
2. Bean Validationが通った後、アクションメソッド内でDB重複チェックを実施
3. 重複があった場合は `ValidationUtil#createMessageForProperty` でエラーメッセージを構築し、`ApplicationException` をスロー

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse register(MemberForm form) {
    // Bean Validation通過後 = バリデーション済みの安全な値でDBアクセス可能
    if (UniversalDao.exists(Member.class, "WHERE email = ?", form.getEmail())) {
        throw new ApplicationException(
            ValidationUtil.createMessageForProperty("form.email", "duplicate.email"));
    }
    UniversalDao.insert(BeanUtil.createAndCopy(Member.class, form));
    return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode());
}
```

**注意点**:
- Bean Validationのカスタムバリデータ内でDBアクセスすると、未検証の値でSQLが実行されるためSQLインジェクションのリスクがある
- `ValidationUtil#createMessageForProperty` を使うことで、アクション内のバリデーションエラーも特定フィールドに紐づけて返却できる
- `ApplicationException` をスローすることでフレームワークがエラーレスポンスに変換する

参照: `component/libraries/libraries-bean-validation.json#s12`, `component/libraries/libraries-bean-validation.json#s13`, `component/handlers/handlers-jaxrs-bean-validation-handler.json#s4`
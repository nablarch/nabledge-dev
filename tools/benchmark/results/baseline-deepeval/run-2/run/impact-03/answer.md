**結論**: カスタムバリデータ内でDB検索する実装は**推奨されません**。DBへの重複チェックはBean Validationのカスタムバリデータではなく、Bean Validation実行後の業務アクション内で行ってください。

**根拠**:

RESTfulウェブサービスでBean Validationは `@Valid` アノテーションにより実行されますが、**バリデーション実行中のオブジェクトの値は安全である保証がありません**。未バリデートの値でDBアクセスを行うとSQLインジェクションなどの脆弱性の原因となるため、Bean ValidationでのDB検索は避けるべきとされています。

**正しい実装パターン**:

**① RESTfulリソースメソッドに `@Valid` を設定**（Bean Validationによる基本チェック）:

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    // Bean Validationがここで実行される
    // DB重複チェックはここ以降（バリデーション済みの安全な値）で行う
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

**② 業務アクション内でDB重複チェックを行い、エラー時は特定フィールドにエラーを紐づけてスロー**:

```java
throw new ApplicationException(
        ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
```

**注意点**:
- Bean Validationのカスタムバリデータ（`@AssertTrue` 等）は、DBアクセスを伴わない項目単体チェックや項目間の相関チェックにのみ使用してください。
- DBとの相関バリデーションは、必ずBean Validation実行後の業務アクション内で行うことが原則です。

参照: `libraries-bean-validation.json:s12`, `libraries-bean-validation.json:s13`, `libraries-bean-validation.json:s17`, `handlers-jaxrs-bean-validation-handler.json:s4`
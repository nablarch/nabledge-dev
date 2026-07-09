**結論**: Bean Validationのカスタムバリデータ内でDB検索を行う実装は**してはいけない**。データベースとの相関バリデーション（重複チェックを含む）は、Bean Validation後に業務アクション側で実装すること。

**根拠**:

Nablarchの公式ドキュメント「Bean Validation > データベースとの相関バリデーションを行う」に明確に記載されている。

> Bean Validationを使ってデータベースに対する相関バリデーションを実施した場合、バリデーション実施前の安全ではない値を使ってデータベースアクセスを行うことになる。（Bean Validation実行中のオブジェクトの値は、安全である保証がない。）これは、SQLインジェクションなどの脆弱性の原因となるため、さけるべき実装であるため。

つまり、正しい実装の流れは以下のとおり。

1. **Bean Validationでフォームの項目バリデーション**（文字種・桁数等）を行う
   - RESTfulウェブサービスの場合、リソースクラスのメソッドに `@Valid` アノテーションを設定する

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    // Bean Validationが自動実行される
    // ...
}
```

2. **業務アクション内でDB重複チェックを実装する**（Bean Validationが通過した後）

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse register(UserForm form) {
    // ここに来た時点で form の値はバリデーション済みで安全
    // 重複チェックをここで実装する
    int count = UniversalDao.countBySqlFile(User.class, "FIND_BY_LOGIN_ID", form);
    if (count > 0) {
        throw new ApplicationException(
            ValidationUtil.createMessageForProperty("form.loginId", "duplicate.loginId"));
    }
    // 正常処理
    UniversalDao.insert(BeanUtil.createAndCopy(User.class, form));
    return new HttpResponse();
}
```

**注意点**:
- `ValidationUtil.createMessageForProperty` を使うと、アクションで発生したバリデーションエラーを特定の項目に紐づけてクライアントへ返せる
- `ApplicationException` をスローすることで、`JaxRsResponseHandler` がバリデーションエラーと同様にエラーレスポンスとして処理する

参照:
- Bean Validation
  .claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md
  データベースとの相関バリデーションを行う
  特定の項目に紐づくバリデーションエラーのメッセージを作りたい
  RESTfulウェブサービスのユーザ入力値のチェックを行う
- Jakarta RESTful Web Servcies Bean Validationハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-bean-validation-handler.md
  リソース(アクション)で受け取るForm(Bean)に対してバリデーションを実行する
**結論**: Bean ValidationのカスタムバリデータでDB検索するのは**推奨されない**実装です。DBへの重複チェックは、Bean Validationによる入力値検証が完了した後に、**業務アクション側**で実装してください。

**根拠**:

ドキュメントには以下のように明記されています。

> Bean Validationを使ってデータベースに対する相関バリデーションを実施した場合、バリデーション実施前の安全ではない値を使ってデータベースアクセスを行うことになる。(Bean Validation実行中のオブジェクトの値は、安全である保証がない。)
> これは、SQLインジェクションなどの脆弱性の原因となるため、さけるべき実装であるため。
>
> バリデーション実行後に業務アクションでバリデーションを行うことで、バリデーション済みの安全な値を使用してデータベースへアクセスできる。

**実装フロー（RESTfulウェブサービスの場合）**:

① リソースクラスのメソッドに `@Valid` を付けてBean Validationを実行する

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    // ここではpersonはバリデーション済み

    // ② バリデーション済みの値でDB重複チェックを実施
    if (UniversalDao.exists(...)) {
        throw new ApplicationException(
            ValidationUtil.createMessageForProperty("person.mailAddress", "duplicate.mailAddress"));
    }

    UniversalDao.insert(person);
    return new HttpResponse();
}
```

② DB重複チェックでエラーが発生した場合は、`ValidationUtil.createMessageForProperty` を使って対象項目に紐づくエラーメッセージを構築し、`ApplicationException` を送出する。

```java
throw new ApplicationException(
    ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
```

**注意点**:
- Bean Validation（`@Valid` によるフレームワーク自動実行）とDB重複チェック（アクション内の手動実装）は分けて実装する
- DB重複チェックは必ずBean Validationが正常終了した後に行うこと
- カスタムバリデータ（`ConstraintValidator` の実装）の中でDB検索を行ってはならない

参照:
- Bean Validation
  .claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md
  データベースとの相関バリデーションを行う
  特定の項目に紐づくバリデーションエラーのメッセージを作りたい
  RESTfulウェブサービスのユーザ入力値のチェックを行う
- Jakarta RESTful Web Servcies Bean Validationハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-bean-validation-handler.md
  リソース(アクション)で受け取るForm(Bean)に対してバリデーションを実行する
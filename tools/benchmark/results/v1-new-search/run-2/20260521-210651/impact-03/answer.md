回答を生成します。

---

**結論**: Bean Validationのカスタムバリデータ内でDB検索する実装は**行ってはいけません**。重複チェックのようなDBアクセスを伴うバリデーションは、Bean Validation完了後に**業務アクション側**で実装してください。

**根拠**:

Nablarchのドキュメントには明確な理由が記載されています。

> Bean Validationを使ってデータベースに対する相関バリデーションを実施した場合、バリデーション実施前の安全ではない値を使ってデータベースアクセスを行うことになる。(Bean Validation実行中のオブジェクトの値は、安全である保証がない。)これは、SQLインジェクションなどの脆弱性の原因となるため、さけるべき実装である。

バリデーション実行後に業務アクションでDBアクセスすることで、バリデーション済みの安全な値でDBを操作できます。

RESTfulウェブサービスの場合、通常のバリデーションはリソースクラスのメソッドに `@Valid` アノテーションを設定することで自動的に実行されます。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    // ここに来た時点でBean Validationは完了済み
    // DB重複チェックを業務アクション内で実装する
    if (/* 重複チェックSQL */) {
        throw new ApplicationException(
            ValidationUtil.createMessageForProperty("person.email", "duplicate.email"));
    }
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

**注意点**:
- DB重複チェックのエラーを特定フィールドのエラーとして扱いたい場合は、`ValidationUtil#createMessageForProperty` でエラーメッセージを構築し `ApplicationException` を送出する
- `ApplicationException` を送出すると、JAX-RSレスポンスハンドラがエラーレスポンスを生成する

参照: `libraries-bean-validation.json:s12`, `libraries-bean-validation.json:s13`, `handlers-jaxrs-bean-validation-handler.json:s4`

---
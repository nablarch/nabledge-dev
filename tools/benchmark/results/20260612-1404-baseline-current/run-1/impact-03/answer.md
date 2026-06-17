**結論**: Bean Validationのカスタムバリデータ内でDBアクセスを行う実装は、Nablarchでは**推奨されていません**。DBとの重複チェックはBean Validationが完了した後、**業務アクション（リソースクラス）側で実装**してください。

**根拠**:

Nablarchのドキュメントでは、Bean Validation内でのDB検索を以下の理由で明示的に禁止しています。

> Bean Validationを使ってデータベースに対する相関バリデーションを実施した場合、バリデーション実施前の安全ではない値を使ってデータベースアクセスを行うことになる。(Bean Validation実行中のオブジェクトの値は、安全である保証がない。) これは、SQLインジェクションなどの脆弱性の原因となるため、さけるべき実装であるため。

**正しい実装パターン（RESTfulウェブサービスの場合）**:

```java
// 1. リソースクラスのメソッドに @Valid を設定し、Bean Validationを実行
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    // 2. Bean Validation通過後（ここでは値が安全）にDB重複チェックを実施
    long count = UniversalDao.countBySqlFile(Person.class, "FIND_BY_EMAIL",
        new Object[]{person.getEmail()});
    if (count > 0) {
        // 3. エラーメッセージをApplicationExceptionとしてスロー
        throw new ApplicationException(
            ValidationUtil.createMessageForProperty("email", "duplicate.email"));
    }
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

**注意点**:
- Bean Validationハンドラ（`JaxRsBeanValidationHandler`）はリクエストボディ変換ハンドラより後に配置し、`@Valid`アノテーションが付いたメソッドのFormに対してバリデーションを実行します
- DB重複チェックは必ずBean Validationが完了した後に実施することで、バリデーション済みの安全な値でDBアクセスができます
- エラー発生時は`ValidationUtil.createMessageForProperty`でエラーを特定項目に紐づけることが可能です

参照: `component/libraries/libraries-bean-validation.json:s12`, `component/libraries/libraries-bean-validation.json:s13`, `component/handlers/handlers-jaxrs-bean-validation-handler.json:s4`
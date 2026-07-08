**結論**: カスタムバリデータの中でDB検索して重複チェックする実装は**避けるべき**です。重複チェックはBean Validationが完了した後、業務アクション側で実装してください。

**根拠**: Nablarchのドキュメントは「データベースとの相関バリデーションは業務アクション側で実装すること」と明記しています。

理由はセキュリティです。Bean Validation実行中のオブジェクトの値は「バリデーション前の安全ではない値」であるため、その値でDBアクセスを行うとSQLインジェクションなどの脆弱性の原因となります。

バリデーション後に業務アクションで実施することで、バリデーション済みの安全な値を使ってDBアクセスできます。

RESTfulウェブサービスでの実装例:

```java
// Step 1: @Valid でBean Validationを実行
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    // Step 2: Bean Validation通過後、業務アクションで重複チェック
    long count = UniversalDao.countBySqlFile(Person.class, "CHECK_DUPLICATE",
                                             person);
    if (count > 0) {
        // Step 3: 特定項目のエラーメッセージを生成してApplicationExceptionをスロー
        throw new ApplicationException(
            ValidationUtil.createMessageForProperty("person.email",
                                                    "duplicate.email"));
    }
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

**注意点**: 業務アクション側でエラーを検知した場合、`ValidationUtil.createMessageForProperty` を使うと特定の項目に紐づくバリデーションエラーメッセージを生成できます。これにより、Bean Validationと同様に項目単位のエラーレスポンスを返すことができます。

参照:
- Bean Validation
  .claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md
  データベースとの相関バリデーションを行う
  特定の項目に紐づくバリデーションエラーのメッセージを作りたい
  RESTfulウェブサービスのユーザ入力値のチェックを行う
- Jakarta RESTful Web Servcies Bean Validationハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-bean-validation-handler.md
  リソース(アクション)で受け取るForm(Bean)に対してバリデーションを実行する
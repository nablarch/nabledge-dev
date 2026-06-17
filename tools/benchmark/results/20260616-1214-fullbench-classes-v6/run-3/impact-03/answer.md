**結論**: カスタムバリデータの中でDB検索を行う実装はNablarchでは**禁止されています**。DB重複チェックは、Bean Validation完了後に**業務アクション側**で実装してください。

**根拠**:

Bean Validationの中でDBアクセスを行ってはいけない理由は、Bean Validation実行中はオブジェクトの値が安全である保証がないためです。バリデーション前の安全でない値でDBアクセスを行うと、SQLインジェクションなどの脆弱性の原因となります。

正しい実装の流れ（RESTfulウェブサービスの場合）:

**Step 1: リソースクラスで `@Valid` を設定してBean Validationを実行する**

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    // ここに来た時点でBean Validationは完了済み（安全な値）
    // Step 2: 業務アクション内でDB重複チェックを実施する
    checkDuplicate(person);
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

**Step 2: 業務アクション内でDB重複チェックを実施する**

バリデーション済みの安全な値を使ってDBアクセスできます。重複エラーを特定フィールドのエラーとして返したい場合は `ValidationUtil#createMessageForProperty` を使います。

```java
private void checkDuplicate(Person person) {
    // バリデーション済みの安全な値でDB検索
    if (UniversalDao.exists(...)) {
        throw new ApplicationException(
            ValidationUtil.createMessageForProperty("person.email", "duplicate.email"));
    }
}
```

**注意点**:
- `@Valid` を設定したリソースメソッドでは `JaxRsBeanValidationHandler` が自動的にBean Validationを実行します。バリデーションエラー時は `ApplicationException` が送出され、後続処理は実行されません。
- DB重複チェックは必ずBean Validation完了後（アクションメソッドの中）で行うこと。

参照: libraries-bean-validation.json:s12, libraries-bean-validation.json:s13, handlers-jaxrs-bean-validation-handler.json:s4
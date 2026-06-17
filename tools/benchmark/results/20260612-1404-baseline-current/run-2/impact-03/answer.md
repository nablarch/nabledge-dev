**結論**: Bean ValidationのカスタムバリデータでDB検索を行う実装は**推奨されない**。DBとの重複チェックは、Bean Validationが完了した後、業務アクション（リソースクラス）のメソッド内で実装すること。

**根拠**:

Bean Validationのカスタムバリデータ内でDBアクセスを行うと、バリデーション実行中のオブジェクトの値は安全であることが保証されていない状態でDBアクセスすることになる。これはSQLインジェクションなどの脆弱性の原因となるため、避けるべき実装とされている。

推奨される実装パターンは以下の通り：

1. リソースクラスのメソッドに `@Valid` を設定してBean Validationを実行する

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    // Bean Validationがここまでに完了している
    // バリデーション済みの安全な値でDB重複チェックを実装する
    if (UniversalDao.countBySqlFile(Person.class, "FIND_BY_EMAIL", person) > 0) {
        throw new ApplicationException(
            ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
    }
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

2. Bean Validationが完了した後、業務アクション内でバリデーション済みの安全な値を使ってDBアクセスし、重複チェックを行う。エラー時は `ValidationUtil#createMessageForProperty` でエラーメッセージを構築し `ApplicationException` を送出する。

**注意点**:
- `@Valid` アノテーションを設定したメソッドに渡ってきた時点で、Bean Validationは完了しており値は安全になっている
- カスタムバリデータ内ではDB検索を行わないこと（セキュリティ上のリスクがある）

参照: libraries-bean-validation.json:s12, libraries-bean-validation.json:s13, handlers-jaxrs-bean-validation-handler.json:s4
**結論**: Bean Validation（カスタムバリデータ）内でDBに問い合わせて重複チェックするのは**NG**。DB重複チェックは業務アクション側で、Bean Validationが完了した後に実装すること。

**根拠**:

Bean Validationの仕様では、バリデーション実行中のオブジェクトの値は「安全である保証がない」。この状態でDBアクセスを行うと、SQLインジェクションなどの脆弱性の原因となるため、避けるべき実装とされている。

**正しい実装方針（RESTfulウェブサービスの場合）**:

1. **Formのバリデーション**: `@Valid` アノテーションで通常のBean Validationを実行

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    // この時点でBean Validationは完了 → 安全な値のみが渡ってくる
    
    // DB重複チェックはここで行う
    if (UniversalDao.exists(Person.class, condition)) {
        throw new ApplicationException(
            ValidationUtil.createMessageForProperty("person.mailAddress", "duplicate.mailAddress"));
    }
    
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

2. **エラー表示**: アクション側でエラーが発生した場合、`ValidationUtil#createMessageForProperty` を使ってエラーメッセージを構築し、`ApplicationException` を送出することで、特定フィールドのエラーとしてクライアントに返せる。

```java
throw new ApplicationException(
    ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
```

**注意点**: Bean Validationのカスタムバリデータ（`ConstraintValidator` 実装クラス）でDBアクセスするコードを書くことは、NablarchのBean Validationの設計方針に反する。必ずバリデーション後の業務アクション内でDB検索を行うこと。

参照: libraries-bean-validation.json:s12, libraries-bean-validation.json:s13, handlers-jaxrs-bean-validation-handler.json:s4